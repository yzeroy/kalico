from klippy.kalico import stubgen
import io
import pytest
import typing as t
import collections as c

# Some types for later testing


class Point(t.NamedTuple):
    x: float
    y: float


class Status(t.TypedDict):
    enabled: t.Optional[bool]
    status: t.Annotated[
        t.Literal["running", "stopped", "complete", "failed"], "Job lifecycle"
    ]


@pytest.mark.parametrize(
    "typ, expected",
    [
        (str, "str"),
        (int, "int"),
        (float, "float"),
        (bool, "bool"),
        (dict, "dict"),
        (list, "list"),
        (tuple, "tuple"),
        (list[str], "list[str]"),
        (
            t.Annotated[str, "this is a test"],
            "typing.Annotated[str, 'this is a test']",
        ),
        # Check order is preserved
        (t.Union[int, float], "int | float"),
        (t.Union[float, int], "float | int"),
        #
        (t.Callable[[], None], "collections.abc.Callable[[], None]"),
    ],
)
def test_basic_types(typ, expected):
    assert stubgen.serialize_type(typ) == expected


@pytest.mark.parametrize(
    "typ, expected",
    [
        (  # base collections namedtuple
            c.namedtuple("Point", ["x", "y"]),
            "class TestStubgenPoint(typing.NamedTuple):\n"
            "    x: typing.Any\n"
            "    y: typing.Any\n",
        ),
        (  # functional typing.NamedTuple
            t.NamedTuple("Point", [("x", float), ("y", float)]),
            "class TestStubgenPoint(typing.NamedTuple):\n"
            "    x: float\n"
            "    y: float\n",
        ),
        (  # class typing.NamedTuple
            Point,
            "class TestStubgenPoint(typing.NamedTuple):\n"
            "    x: float\n"
            "    y: float\n",
        ),
        (  # functional typeddict
            t.TypedDict("Point", {"x": float, "y": float}),
            "class TestStubgenPoint(typing.TypedDict):\n"
            "    x: float\n"
            "    y: float\n",
        ),
        (  # functional with invalid identifiers
            t.TypedDict("Bad", {"⚠️": bool}),
            "TestStubgenBad = typing.TypedDict(\n"
            '    "Bad",\n'
            "    {\n"
            '        "⚠️": bool,\n'
            "    },\n"
            ")\n",
        ),
        (  # functional with invalid identifiers
            t.TypedDict("Bad", {" ": bool}),
            "TestStubgenBad = typing.TypedDict(\n"
            '    "Bad",\n'
            "    {\n"
            '        " ": bool,\n'
            "    },\n"
            ")\n",
        ),
        (  # Class with complex status type
            Status,
            "class TestStubgenStatus(typing.TypedDict):\n"
            "    enabled: bool | None\n"
            "    status: typing.Annotated[typing.Literal['running', 'stopped', 'complete', 'failed'], 'Job lifecycle']\n",
        ),
    ],
)
def test_printing_types(typ, expected):
    buffer = io.StringIO()
    stubgen.print_type(typ, buffer)
    assert buffer.getvalue() == expected


# This simulates stubgen.write_types
@pytest.mark.parametrize(
    "typ, expected",
    [
        (
            t.TypedDict("Printer", {"namedtuple": Point, "typeddict": Status}),
            "class TestStubgenPoint(typing.NamedTuple):\n"
            "    x: float\n"
            "    y: float\n"
            "class TestStubgenStatus(typing.TypedDict):\n"
            "    enabled: bool | None\n"
            "    status: typing.Annotated[typing.Literal['running', 'stopped', 'complete', 'failed'], 'Job lifecycle']\n"
            "class TestStubgenPrinter(typing.TypedDict):\n"
            "    namedtuple: TestStubgenPoint\n"
            "    typeddict: TestStubgenStatus\n",
        ),
    ],
)
def test_walking_nested_types(typ, expected):
    buffer = io.StringIO()
    for item in stubgen.walk_type(typ):
        stubgen.print_type(item, buffer)
    assert buffer.getvalue() == expected
