#pragma once

#include <stdbool.h>

enum
{
    HUBCTRL_HUB_NOT_FOUND = 1,
    HUBCTRL_FAILED_TO_OPEN_DEVICE,
    HUBCTRL_FAILED_TO_CONTROL,
};

int hubctrl_set_power(int hub, int port, bool value);