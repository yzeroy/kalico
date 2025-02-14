#pragma once

#include "itersolve.h" // stepper_kinematics

void dual_carriage_set_sk(struct stepper_kinematics *sk,
                          struct stepper_kinematics *orig_sk);
int dual_carriage_set_transform(struct stepper_kinematics *sk, char axis,
                                double scale, double offs);
struct stepper_kinematics *dual_carriage_alloc(void);