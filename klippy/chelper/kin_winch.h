#pragma once

#include "itersolve.h" // stepper_kinematics

struct stepper_kinematics *winch_stepper_alloc(double anchor_x, double anchor_y,
                                               double anchor_z);