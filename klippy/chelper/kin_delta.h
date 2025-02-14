#pragma once

#include "itersolve.h" // stepper_kinematics

struct stepper_kinematics *delta_stepper_alloc(double arm2, double tower_x,
                                               double tower_y);