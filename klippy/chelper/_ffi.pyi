from typing import Protocol, ClassVar
import cffi
import ctypes

# Exposed structures
class StepCompress(ctypes.Structure):
    first_clock: ctypes.c_uint64
    last_clock: ctypes.c_uint64
    start_position: ctypes.c_int64
    step_count: ctypes.c_int
    interval: ctypes.c_int
    add: ctypes.c_int

class PullMove(ctypes.Structure):
    print_time: ctypes.c_double
    move_t: ctypes.c_double
    start_v: ctypes.c_double
    accel: ctypes.c_double
    start_x: ctypes.c_double
    start_y: ctypes.c_double
    start_z: ctypes.c_double
    x_r: ctypes.c_double
    y_r: ctypes.c_double
    z_r: ctypes.c_double

class PullQueueMessage(ctypes.Structure):
    msg: ctypes.ARRAY[ctypes.c_uint8]
    len: ctypes.c_int
    sent_time: ctypes.c_double
    receive_time: ctypes.c_double
    notify_id: ctypes.c_uint64

# Opaque structures
class StepperSync(ctypes.Structure): ...
class PullHistorySteps(ctypes.Structure): ...
class StepperKinematics(ctypes.Structure): ...
class TrapQ(ctypes.Structure): ...
class SerialQueue(ctypes.Structure): ...
class CommandQueue(ctypes.Structure): ...
class TRDispatch(ctypes.Structure): ...
class TRDispatchMCU(ctypes.Structure): ...

class LibStepcompress(Protocol):
    def stepcompress_alloc(
        oid: ctypes.c_int32,
    ) -> ctypes._Pointer[StepCompress]: ...
    def stepcompress_fill(
        sc: ctypes._Pointer[StepCompress],
        max_error: ctypes.c_uint32,
        queue_step_msgtag: ctypes.c_int32,
        set_next_step_dir_msgtag: ctypes.c_int32,
    ) -> None: ...
    def stepcompress_set_invert_sdir(
        self, sc: ctypes._Pointer[StepCompress], invert_sdir: ctypes.c_uint32
    ) -> None: ...
    def stepcompress_free(
        self,
        sc: ctypes._Pointer[StepCompress],
    ) -> None: ...
    def stepcompress_reset(
        self,
        sc: ctypes._Pointer[StepCompress],
        last_step_clock: ctypes.c_uint64,
    ) -> ctypes.c_int: ...
    def stepcompress_set_last_position(
        self,
        sc: ctypes._Pointer[StepCompress],
        clock: ctypes.c_uint64,
        last_position: ctypes.c_int64,
    ) -> ctypes.c_int: ...
    def stepcompress_find_past_position(
        self, sc: ctypes._Pointer[StepCompress], clock: ctypes.c_uint64
    ) -> ctypes.c_int64: ...
    def stepcompress_queue_msg(
        self,
        sc: ctypes._Pointer[StepCompress],
        data: ctypes._Pointer[ctypes.c_uint32],
        len: ctypes.c_int,
    ) -> ctypes.c_int: ...
    def stepcompress_queue_mq_msg(
        self,
        sc: ctypes._Pointer[StepCompress],
        req_clock: ctypes.c_uint64,
        data: ctypes._Pointer[ctypes.c_uint32],
        len: ctypes.c_int,
    ) -> ctypes.c_int: ...
    def stepcompress_extract_old(
        self,
        sc: ctypes._Pointer[StepCompress],
        p: ctypes._Pointer[PullHistorySteps],
        max: ctypes.c_int,
        start_clock: ctypes.c_uint64,
        end_clock: ctypes.c_uint64,
    ) -> ctypes.c_int: ...
    def steppersync_alloc(
        self,
        sq: ctypes._Pointer[LibSerialqueue.SerialQueue],
        sc_list: ctypes._Pointer[ctypes._Pointer[StepCompress]],
        sc_num: ctypes.c_int,
        move_num: ctypes.c_int,
    ) -> ctypes._Pointer[StepperSync]: ...
    def steppersync_free(
        self,
        ss: ctypes._Pointer[StepperSync],
    ) -> None: ...
    def steppersync_set_time(
        self,
        ss: ctypes._Pointer[StepperSync],
        time_offset: ctypes.c_double,
        mcu_freq: ctypes.c_double,
    ) -> None: ...
    def steppersync_flush(
        self,
        ss: ctypes._Pointer[StepperSync],
        move_clock: ctypes.c_uint64,
        clear_history_clock: ctypes.c_uint64,
    ) -> ctypes.c_int: ...

class LibItersolve(Protocol):
    def itersolve_generate_steps(
        self,
        sk: ctypes._Pointer[StepperKinematics],
        flush_time: ctypes.c_double,
    ) -> ctypes.c_int32: ...
    def itersolve_check_active(
        self,
        sk: ctypes._Pointer[StepperKinematics],
        flush_time: ctypes.c_double,
    ) -> ctypes.c_double: ...
    def itersolve_is_active_axis(
        self, sk: ctypes._Pointer[StepperKinematics], axis: ctypes.c_char
    ) -> ctypes.c_int32: ...
    def itersolve_set_trapq(
        self,
        sk: ctypes._Pointer[StepperKinematics],
        tq: ctypes._Pointer[LibTrapq.TrapQ],
    ): ...
    def itersolve_set_stepcompress(
        self,
        sk: ctypes._Pointer[StepperKinematics],
        sc: ctypes._Pointer[LibStepcompress.StepCompress],
        step_dist: ctypes.c_double,
    ): ...
    def itersolve_calc_position_from_coord(
        self,
        sk: ctypes._Pointer[StepperKinematics],
        x: ctypes.c_double,
        y: ctypes.c_double,
        z: ctypes.c_double,
    ) -> ctypes.c_double: ...
    def itersolve_set_position(
        self,
        sk: ctypes._Pointer[StepperKinematics],
        x: ctypes.c_double,
        y: ctypes.c_double,
        z: ctypes.c_double,
    ): ...
    def itersolve_get_commanded_pos(
        self, sk: ctypes._Pointer[StepperKinematics]
    ) -> ctypes.c_double: ...

class LibTrapq(Protocol):
    def trapq_alloc(self) -> ctypes._Pointer[TrapQ]: ...
    def trapq_free(self, tq: ctypes._Pointer[TrapQ]): ...
    def trapq_append(
        self,
        tq: ctypes._Pointer[TrapQ],
        print_time: ctypes.c_double,
        accel_t: ctypes.c_double,
        cruise_t: ctypes.c_double,
        decel_t: ctypes.c_double,
        start_pos_x: ctypes.c_double,
        start_pos_y: ctypes.c_double,
        start_pos_z: ctypes.c_double,
        axes_r_x: ctypes.c_double,
        axes_r_y: ctypes.c_double,
        axes_r_z: ctypes.c_double,
        start_v: ctypes.c_double,
        cruise_v: ctypes.c_double,
        accel: ctypes.c_double,
    ): ...
    def trapq_finalize_moves(
        self,
        tq: ctypes._Pointer[TrapQ],
        print_time: ctypes.c_double,
        clear_history_time: ctypes.c_double,
    ): ...
    def trapq_set_position(
        self,
        tq: ctypes._Pointer[TrapQ],
        print_time: ctypes.c_double,
        pos_x: ctypes.c_double,
        pos_y: ctypes.c_double,
        pos_z: ctypes.c_double,
    ): ...
    def trapq_extract_old(
        self,
        tq: ctypes._Pointer[TrapQ],
        p: ctypes._Pointer[PullMove],
        max: ctypes.c_int,
        start_time: ctypes.c_double,
        end_time: ctypes.c_double,
    ) -> ctypes.c_int: ...

class LibKinCartesian(Protocol):
    def cartesian_stepper_alloc(
        self,
        axis: ctypes.c_char,
    ) -> ctypes._Pointer[LibItersolve.StepperKinematics]: ...

class LibKinCorexy(Protocol):
    def corexy_stepper_alloc(
        self, type: ctypes.c_char
    ) -> ctypes._Pointer[LibItersolve.StepperKinematics]: ...

class LibKinCorexz(Protocol):
    def corexz_stepper_alloc(
        self, type: ctypes.c_char
    ) -> ctypes._Pointer[LibItersolve.StepperKinematics]: ...

class LibKinDelta(Protocol):
    def delta_stepper_alloc(
        self,
        arm2: ctypes.c_double,
        tower_x: ctypes.c_double,
        tower_y: ctypes.c_double,
    ) -> ctypes._Pointer[LibItersolve.StepperKinematics]: ...

class LibKinDeltesian(Protocol):
    def deltesian_stepper_alloc(
        self, arm2: ctypes.c_double, arm_x: ctypes.c_double
    ) -> ctypes._Pointer[LibItersolve.StepperKinematics]: ...

class LibKinPolar(Protocol):
    def polar_stepper_alloc(
        self, type: ctypes.c_char
    ) -> ctypes._Pointer[LibItersolve.StepperKinematics]: ...

class LibKinRotaryDelta(Protocol):
    def rotary_delta_stepper_alloc(
        self,
        shoulder_radius: ctypes.c_double,
        shoulder_height: ctypes.c_double,
        angle: ctypes.c_double,
        upper_arm: ctypes.c_double,
        lower_arm: ctypes.c_double,
    ) -> ctypes._Pointer[LibItersolve.StepperKinematics]: ...

class LibKinWinch(Protocol):
    def winch_stepper_alloc(
        self,
        anchor_x: ctypes.c_double,
        anchor_y: ctypes.c_double,
        anchor_z: ctypes.c_double,
    ) -> ctypes._Pointer[LibItersolve.StepperKinematics]: ...

class LibKinExtruder(Protocol):
    def extruder_stepper_alloc(
        self,
    ) -> ctypes._Pointer[LibItersolve.StepperKinematics]: ...
    def extruder_set_pressure_advance(
        self,
        sk: ctypes._Pointer[LibItersolve.StepperKinematics],
        pressure_advance: ctypes.c_double,
        smooth_time: ctypes.c_double,
    ): ...

class LibKinShaper(Protocol):
    def input_shaper_alloc(
        self,
    ) -> ctypes._Pointer[LibItersolve.StepperKinematics]: ...
    def input_shaper_get_step_generation_window(
        self, sk: ctypes._Pointer[LibItersolve.StepperKinematics]
    ) -> ctypes.c_double: ...
    def input_shaper_set_shaper_params(
        self,
        sk: ctypes._Pointer[LibItersolve.StepperKinematics],
        axis: ctypes.c_char,
        n: ctypes.c_int,
        a: ctypes.ARRAY[ctypes.c_double],
        t: ctypes.ARRAY[ctypes.c_double],
    ) -> ctypes.c_int: ...
    def input_shaper_set_sk(
        self,
        sk: ctypes._Pointer[LibItersolve.StepperKinematics],
        orig_sk: ctypes._Pointer[LibItersolve.StepperKinematics],
    ) -> ctypes.c_int: ...

class LibKinIdex(Protocol):
    def dual_carriage_alloc(
        self,
    ) -> ctypes._Pointer[LibItersolve.StepperKinematics]: ...
    def dual_carriage_set_sk(
        self,
        sk: ctypes._Pointer[LibItersolve.StepperKinematics],
        orig_sk: ctypes._Pointer[LibItersolve.StepperKinematics],
    ): ...
    def dual_carriage_set_transform(
        sk: ctypes._Pointer[LibItersolve.StepperKinematics],
        axis: ctypes.c_char,
        scale: ctypes.c_double,
        offs: ctypes.c_double,
    ) -> ctypes.c_int: ...

class LibSerialqueue(Protocol):
    MESSAGE_MAX: ClassVar[int] = 64

    def serialqueue_alloc(
        self,
        serial_fd: ctypes.c_int,
        serial_fd_type: ctypes.c_char,
        client_id: ctypes.c_int,
    ) -> ctypes._Pointer[SerialQueue]: ...
    def serialqueue_exit(self, sq: ctypes._Pointer[SerialQueue]): ...
    def serialqueue_free(self, sq: ctypes._Pointer[SerialQueue]): ...
    def serialqueue_alloc_commandqueue(
        self,
    ) -> ctypes._Pointer[CommandQueue]: ...
    def serialqueue_free_commandqueue(
        self,
        cq: ctypes._Pointer[CommandQueue],
    ): ...
    def serialqueue_send(
        self,
        sq: ctypes._Pointer[SerialQueue],
        cq: ctypes._Pointer[CommandQueue],
        msg: ctypes.ARRAY[ctypes.c_uint8],
        len: ctypes.c_int,
        min_clock: ctypes.c_uint64,
        req_clock: ctypes.c_uint64,
        notify_id: ctypes.c_uint64,
    ): ...
    def serialqueue_pull(
        self,
        sq: ctypes._Pointer[SerialQueue],
        pqm: ctypes._Pointer[PullQueueMessage],
    ): ...
    def serialqueue_set_wire_frequency(
        self,
        sq: ctypes._Pointer[SerialQueue],
        frequency: ctypes.c_double,
    ): ...
    def serialqueue_set_receive_window(
        self,
        sq: ctypes._Pointer[SerialQueue],
        receive_window: ctypes.c_int,
    ): ...
    def serialqueue_set_clock_est(
        self,
        sq: ctypes._Pointer[SerialQueue],
        est_freq: ctypes.c_double,
        conv_time: ctypes.c_double,
        conv_clock: ctypes.c_uint64,
        last_clock: ctypes.c_uint64,
    ): ...
    def serialqueue_get_stats(
        self,
        sq: ctypes._Pointer[SerialQueue],
        buf: ctypes.c_char_p,
        len: ctypes.c_int,
    ): ...
    def serialqueue_extract_old(
        self,
        sq: ctypes._Pointer[SerialQueue],
        sentq: ctypes.c_int,
        q: ctypes._Pointer[PullQueueMessage],
        max: ctypes.c_int,
    ) -> ctypes.c_int: ...

class LibTrdispatch(Protocol):
    def trdispatch_alloc(self) -> ctypes._Pointer[TRDispatch]: ...
    def trdispatch_mcu_alloc(
        self,
        td: ctypes._Pointer[TRDispatch],
        sq: ctypes._Pointer[LibSerialqueue.SerialQueue],
        cq: ctypes._Pointer[LibSerialqueue.CommandQueue],
        trsync_oid: ctypes.c_uint32,
        set_timeout_msgtag: ctypes.c_uint32,
        trigger_msgtag: ctypes.c_uint32,
        state_msgtag: ctypes.c_uint32,
    ) -> ctypes._Pointer[TRDispatchMCU]: ...
    def trdispatch_start(
        self,
        td: ctypes._Pointer[TRDispatch],
        dispatch_reason: ctypes.c_uint32,
    ): ...
    def trdispatch_stop(self, td: ctypes._Pointer[TRDispatch]): ...
    def trdispatch_mcu_setup(
        self,
        tdm: ctypes._Pointer[TRDispatchMCU],
        last_status_clock: ctypes.c_uint64,
        expire_clock: ctypes.c_uint64,
        expire_ticks: ctypes.c_uint64,
        min_extend_ticks: ctypes.c_uint64,
    ): ...

class LibPyhelper(Protocol):
    def set_python_logging_callback(self, cb: callable[[ctypes.c_char_p]]): ...
    def get_monotonic(self) -> ctypes.c_double: ...

class LibHubCtrl(Protocol):
    HUBCTRL_HUB_NOT_FOUND: int = 1
    HUBCTRL_FAILED_TO_OPEN_DEVICE: int = 2
    HUBCTRL_FAILED_TO_CONTROL: int = 3

    def hubctrl_set_power(
        self, hub: ctypes.c_int, port: ctypes.c_int, power: ctypes.c_bool
    ) -> ctypes.c_int: ...

class LibStd(Protocol):
    def free(self, p: ctypes.c_void_p): ...

class LibCHelper(
    LibStepcompress,
    LibItersolve,
    LibTrapq,
    LibKinCartesian,
    LibKinCorexy,
    LibKinCorexz,
    LibKinDelta,
    LibKinDeltesian,
    LibKinPolar,
    LibKinRotaryDelta,
    LibKinWinch,
    LibKinExtruder,
    LibKinShaper,
    LibKinIdex,
    LibSerialqueue,
    LibTrdispatch,
    LibPyhelper,
    LibStd,
    LibHubCtrl,
): ...

ffi: cffi.FFI
lib: LibCHelper

__all__ = ("ffi", "lib")
