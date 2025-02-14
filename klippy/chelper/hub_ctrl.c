/*
 * Copyright (C) 2006 Free Software Initiative of Japan
 *
 * Author: NIIBE Yutaka  <gniibe at fsij.org>
 *
 * This file can be distributed under the terms and conditions of the
 * GNU General Public License version 2 (or later).
 *
 */

#include <errno.h>
#include <usb.h>
#include <stdio.h>
#include <string.h>
#include <stdbool.h>

#include "hub_ctrl.h"
#include "compiler.h" // __visible
#include "pyhelper.h" // errorf, report_errno


#define USB_RT_HUB (USB_TYPE_CLASS | USB_RECIP_DEVICE)
#define USB_RT_PORT (USB_TYPE_CLASS | USB_RECIP_OTHER)
#define USB_PORT_FEAT_POWER 8
#define USB_PORT_FEAT_INDICATOR 22
#define USB_DIR_IN 0x80 /* to host */

#define COMMAND_SET_NONE 0
#define COMMAND_SET_LED 1
#define COMMAND_SET_POWER 2
#define HUB_LED_GREEN 2

#define HUB_CHAR_LPSM 0x0003
#define HUB_CHAR_PORTIND 0x0080

struct usb_hub_descriptor
{
	unsigned char bDescLength;
	unsigned char bDescriptorType;
	unsigned char bNbrPorts;
	unsigned char wHubCharacteristics[2];
	unsigned char bPwrOn2PwrGood;
	unsigned char bHubContrCurrent;
	unsigned char data[0];
};

#define CTRL_TIMEOUT 1000
#define USB_STATUS_SIZE 4

#define MAX_HUBS 128
struct hub_info
{
	int busnum, devnum;
	struct usb_device *dev;
	int nport;
	int indicator_support;
};

static struct hub_info hubs[MAX_HUBS];
static int number_of_hubs_with_feature;

static int
usb_find_hubs(int hub)
{
	struct usb_bus *busses;
	struct usb_bus *bus;

	number_of_hubs_with_feature = 0;
	busses = usb_get_busses();
	if (busses == NULL)
	{
		errorf("failed to access USB");
		return -1;
	}

	for (bus = busses; bus; bus = bus->next)
	{
		struct usb_device *dev;

		for (dev = bus->devices; dev; dev = dev->next)
		{
			usb_dev_handle *uh;

			if (dev->descriptor.bDeviceClass != USB_CLASS_HUB)
				continue;

			uh = usb_open(dev);

			if (uh != NULL)
			{
				char buf[1024];

				int nport;
				struct usb_hub_descriptor *uhd = (struct usb_hub_descriptor *)buf;
				if (usb_control_msg(uh, USB_DIR_IN | USB_RT_HUB,
									USB_REQ_GET_DESCRIPTOR,
									USB_DT_HUB << 8, 0,
									buf, sizeof(buf), CTRL_TIMEOUT) > (int)sizeof(struct usb_hub_descriptor))
				{
					if (!(uhd->wHubCharacteristics[0] & HUB_CHAR_PORTIND) && (uhd->wHubCharacteristics[0] & HUB_CHAR_LPSM) >= 2)
						continue;
				}
				else
				{
					errorf("Can't get hub descriptor");
					usb_close(uh);
					continue;
				}

				nport = buf[2];
				hubs[number_of_hubs_with_feature].busnum = atoi(bus->dirname);
				hubs[number_of_hubs_with_feature].devnum = dev->devnum;
				hubs[number_of_hubs_with_feature].dev = dev;
				hubs[number_of_hubs_with_feature].indicator_support = (uhd->wHubCharacteristics[0] & HUB_CHAR_PORTIND) ? 1 : 0;
				hubs[number_of_hubs_with_feature].nport = nport;

				number_of_hubs_with_feature++;

				usb_close(uh);
			}
		}
	}

	return number_of_hubs_with_feature;
}

/*
 * HUB-CTRL  -  program to control port power/led of USB hub
 *
 *   # hub-ctrl                    // List hubs available
 *   # hub-ctrl -P 1               // Power off at port 1
 *   # hub-ctrl -P 1 -p 1          // Power on at port 1
 *   # hub-ctrl -P 2 -l            // LED on at port 1
 *
 * Requirement: USB hub which implements port power control
 *
 *      Work fine:
 *         Elecom's U2H-G4S: www.elecom.co.jp (indicator depends on power)
 *         04b4:6560
 *
 *	   Sanwa Supply's USB-HUB14GPH: www.sanwa.co.jp (indicators don't)
 *
 *	   Targus, Inc.'s PAUH212: www.targus.com (indicators don't)
 *         04cc:1521
 *
 *	   Hawking Technology's UH214: hawkingtech.com (indicators don't)
 *
 */

__visible int hubctrl_set_power(int hub, int port, bool value)
{
	static bool usb_initialized = false;
	if (!usb_initialized)
	{
		usb_init();

		usb_initialized = true;
	}

	usb_find_busses();
	usb_find_devices();

	int hub_count = usb_find_hubs(-1);
	if (hub_count <= 0 || hub >= hub_count)
	{
		report_errno("Hub not found", HUBCTRL_HUB_NOT_FOUND);
		return HUBCTRL_HUB_NOT_FOUND;
	}

	usb_dev_handle *hdl = usb_open(hubs[hub].dev);
	if (hdl == NULL)
	{
		report_errno("Failed to open device", HUBCTRL_FAILED_TO_OPEN_DEVICE);
		return HUBCTRL_FAILED_TO_OPEN_DEVICE;
	}

	int result = 0;

	int feature = USB_PORT_FEAT_POWER;
	int request = value ? USB_REQ_SET_FEATURE : USB_REQ_CLEAR_FEATURE;

	if (usb_control_msg(hdl, USB_RT_PORT, request, feature, port, NULL, 0, CTRL_TIMEOUT) < 0)
	{
		report_errno("Failed to control usb hub", HUBCTRL_FAILED_TO_CONTROL);
		result = HUBCTRL_FAILED_TO_CONTROL;
	}

	usb_close(hdl);
	return result;
}
