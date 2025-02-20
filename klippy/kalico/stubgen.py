from __future__ import annotations

import functools
import datetime
import pathlib
import re
import sys
import types
import typing
import textwrap

import klippy.printer

# Helpers
indent = functools.partial(textwrap.indent, prefix=" " * 4)

# I think we *could* use types.xxx directly, but typing uses type(list[int]) internally, so it's probably safer
_type_generic_alias = (
    type(list[int]),  # types.GenericAlias
    type(typing.List[int]),  # typing._GenericAlias
)

_type_typeddict = type(typing.TypedDict("", {}))
_type_union = type(typing.Union[int, float])


def is_generic(t):
    return isinstance(t, _type_generic_alias)


def is_typeddict(t):
    return isinstance(t, _type_typeddict)


def is_namedtuple(typ):
    if not isinstance(typ, type):
        return is_namedtuple(type(typ))
    return issubclass(typ, tuple) and hasattr(typ, "_fields")


def _merge_unioned_dicts(union_t):
    if not isinstance(union_t, _type_union):
        return union_t

    args = set(typing.get_args(union_t))
    dict_args = set(arg for arg in args if typing.get_origin(arg) is dict)
    if len(dict_args) <= 1:
        return union_t

    key_types = set()
    value_types = set()

    for dict_arg in dict_args:
        args.remove(dict_arg)

        key_type, value_type = typing.get_args(dict_arg)
        key_types.add(key_type)
        value_types.add(value_type)

    args.add(alias(dict, (union(key_types), union(value_types))))

    return union(args)


def union(types: typing.Iterable[type]):
    # Union[str, Union[int, float]] returns Union[str, int, float]

    union_typ = next(iter(types), None)

    for typ in types:
        union_typ = typing.Union[union_typ, typ]

    return _merge_unioned_dicts(union_typ)


def alias(typ: type[type], args: tuple[type, ...]):
    return types.GenericAlias(typ, args)


def infer_tuple_type(value: tuple[typing.Any, ...], *, max_depth) -> type:
    if not value:
        return tuple

    # Otherwise...
    return alias(tuple, tuple(infer_type(val) for val in value))


def infer_list_type(values: list[typing.Any], *, max_depth) -> type:
    if not values:
        return list

    return alias(
        list, (union(infer_type(t, max_depth=max_depth) for t in values),)
    )


def infer_dict_type(values: dict[str, typing.Any], *, max_depth) -> type:
    if not values:
        return dict

    key_type = union(type(key) for key in values.keys())
    value_type = union(
        infer_type(value, max_depth=max_depth) for value in values.values()
    )
    return alias(dict, (key_type, value_type))


def infer_type(typ, *, max_depth=5):
    if max_depth > 0:
        if isinstance(typ, dict):
            return infer_dict_type(typ, max_depth=max_depth - 1)

        elif isinstance(typ, (list)):
            return infer_list_type(typ, max_depth=max_depth - 1)

        elif isinstance(typ, tuple):
            return infer_tuple_type(typ, max_depth=max_depth - 1)

    if typ is None:
        return typing.Any

    return type(typ)


def infer_typeddict(name, values: dict[str, typing.Any]) -> type:
    value_types = {}

    for key, value in values.items():
        if value is None:
            value_types[key] = typing.Any

        else:
            value_types[key] = infer_type(value)

    return typing.TypedDict(name, value_types)


def build_printer_status_type(printer: klippy.printer.Printer):
    eventtime = printer.get_reactor().monotonic()

    # Arguments to the runtime-generated TypedDict
    printer_status: dict[str, type[typing.Any]] = {}
    object_types: dict[type, type] = {}

    for obj_name, obj in printer.lookup_objects():
        if not hasattr(obj, "get_status"):
            continue

        annotation = typing.get_type_hints(obj.get_status, include_extras=True)
        if annotation and "return" in annotation:
            printer_status[obj_name] = annotation["return"]
            continue

        obj_status = obj.get_status(eventtime)
        printer_status[obj_name] = infer_typeddict(
            pascal_case(f"{obj_name}_status"),
            obj_status,
        )

    return typing.TypedDict("PrinterStatus", printer_status)


def walk_type(
    typ: type, *, depth: int = 0, seen_types: set = None
) -> typing.Generator[type]:
    "Walk a type, yielding all dependent types"

    if seen_types is None:
        # We're going to ignore these anyway, so they're
        seen_types = {str, int, float, bool}

    # Ignore literal values
    if not (isinstance(typ, (type)) or is_generic(typ)):
        return

    if typ in seen_types or typing.get_origin(typ) in seen_types:
        return

    seen_types.add(typ)

    args = typing.get_args(typ)
    if args:
        for arg in typing.get_args(typ):
            yield from walk_type(arg, depth=depth + 1, seen_types=seen_types)

    else:
        try:
            for val in typing.get_type_hints(typ, include_extras=True).values():
                yield from walk_type(
                    val, depth=depth + 1, seen_types=seen_types
                )
        except:
            raise

    # Finally, yield the type itself if we need it
    if is_namedtuple(typ) or is_typeddict(typ):
        yield (typ)


def pascal_case(string: str) -> str:
    return "".join(
        s[0].upper() + s[1:]
        for s in re.split(r"[^a-zA-Z0-9]+", string, flags=re.IGNORECASE)
    )


def qualified_name(typ):
    if not isinstance(typ, type):
        typ = type(typ)

    if typ.__module__ == "typing":
        return f"typing.{typ.__name__}"

    if typ.__module__ != __name__:
        return pascal_case(f"{typ.__module__}.{typ.__name__}")

    return typ.__name__


def serialize_type(typ: typing.Any) -> str:
    """Serialize a type to a hint string"""

    if typ is None:
        return "None"

    if typ is Ellipsis:
        return "..."

    # Pass through literals.
    if not (isinstance(typ, type) or is_generic(typ)):
        # TODO: Make this more robust
        return repr(typ)

    if typ in (str, int, float, bool, dict, list, tuple):
        return str(typ.__name__)

    origin = typing.get_origin(typ)
    args = typing.get_args(typ)

    if origin is typing.Union:
        return " | ".join(serialize_type(arg) for arg in args)

    if origin and args:
        # Generic type
        return (
            serialize_type(origin)
            + "["
            + ", ".join(serialize_type(arg) for arg in args)
            + "]"
        )

    try:
        return qualified_name(typ)

    except Exception as e:
        raise


def print_type(typ, file=sys.stdout):
    if is_typeddict(typ):
        annotation = typing.get_type_hints(typ)

        fields = {
            key: serialize_type(value)
            for key, value in typing.get_type_hints(
                typ, include_extras=True
            ).items()
        }
        for key in typ.__optional_keys__:
            fields[key] = f"typing.NotRequired[{fields[key]}]"

        print(
            f"{qualified_name(typ)} = typing.TypedDict(",
            indent(
                "\n".join(
                    [
                        f'"{typ.__name__}",',
                        "{",
                        "\n".join(
                            [f'    "{k}": {v},' for k, v in fields.items()]
                        ),
                        "},",
                    ]
                ),
            ),
            ")",
            sep="\n",
            file=file,
        )

    elif is_namedtuple(typ):
        annotation = typing.get_type_hints(typ)
        print(
            f"class {qualified_name(typ)}(typing.NamedTuple):",
            *[
                f"{field}: {serialize_type(annotation.get(field, typing.Any))}"
                for field in typ._fields
            ],
            sep="\n    ",
            file=file,
        )

    else:
        raise ValueError(f"Unable to serialize type {typ}")


def write_types(printer, stub_filename):
    config_file = pathlib.Path(printer.get_start_args()["config_file"])

    if not stub_filename:
        stub_filename = config_file.parent / "__builtins__.pyi"

    else:
        stub_filename = pathlib.Path(stub_filename)

    printer_status_type = build_printer_status_type(printer)

    macro_stubs_file = pathlib.Path(__file__).parent.parent / "macro.pyi"
    with stub_filename.open("w", encoding="utf-8") as ofp:
        print(
            '"""',
            "Kalico Python type stubs",
            "",
            f"Generated {datetime.datetime.now().strftime('on %x at %X')}",
            f"Based on {config_file}",
            '"""',
            sep="\n",
            file=ofp,
        )

        for line in macro_stubs_file.read_text().splitlines(keepends=True):
            if line.startswith("##"):
                continue

            if not line.startswith("PrinterStatus = typing"):
                ofp.write(line)
                continue

            for typ in walk_type(printer_status_type):
                print_type(typ, file=ofp)


__all__ = ("write_types",)
