#pragma once

#include "itersolve.h" // stepper_kinematics

struct stepper_kinematics *deltesian_stepper_alloc(double arm2, double arm_x);