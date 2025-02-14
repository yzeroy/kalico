#pragma once

#include "itersolve.h" // stepper_kinematics

double input_shaper_get_step_generation_window(struct stepper_kinematics *sk);
int input_shaper_set_shaper_params(struct stepper_kinematics *sk, char axis,
                                   int n, double a[], double t[]);
int input_shaper_set_sk(struct stepper_kinematics *sk,
                        struct stepper_kinematics *orig_sk);
struct stepper_kinematics *input_shaper_alloc(void);