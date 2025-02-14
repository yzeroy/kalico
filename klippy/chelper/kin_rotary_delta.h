#pragma once

#include "itersolve.h" // stepper_kinematics

struct stepper_kinematics *
rotary_delta_stepper_alloc(double shoulder_radius, double shoulder_height,
                           double angle, double upper_arm, double lower_arm);