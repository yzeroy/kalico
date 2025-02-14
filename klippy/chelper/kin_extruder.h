#pragma once

#include "itersolve.h" // stepper_kinematics

struct stepper_kinematics *extruder_stepper_alloc(void);
void extruder_set_pressure_advance(struct stepper_kinematics *sk,
                                   double pressure_advance, double smooth_time);