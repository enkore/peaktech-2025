
import struct
import sys
from datetime import datetime

import pyudev

context = pyudev.Context()


def dbg(*args):
    sys.stderr.write(" ".join(args) + "\n")
    sys.stderr.flush()


def find_dmm():
    for device in context.list_devices(subsystem="hidraw"):
        usb_device = device.find_parent("usb", "usb_device")
        if usb_device["ID_VENDOR_ID"] == "2571" and usb_device["ID_MODEL_ID"] == "4100":
            return device.device_node


def format_report(report):
    if report[1] == 0x4C and report[2] == 0x4F:
        value = float("inf")
    else:
        value = float((report[1] >> 4) * 1000 + (report[1] & 0xF) * 100 +
                      (report[2] >> 4) * 10 + (report[2] & 0xF))
    if report[0] & 1:
        value /= 1000
    elif report[0] & 2:
        value /= 100
    elif report[0] & 4:
        value /= 10
    if report[0] & 0x40:
        value *= -1

    if report[5] & 0x04:  # (!) do not reorder, report[6] & 0x80 will be set
        unit = "Vdiode"
    elif report[6] & 0x80:
        unit = "V"
    elif report[6] & 0x40:
        unit = "A"
    #elif (report[7] & 0x3D) == 0x3D:
    #    unit = "Ω"
    elif report[6] & 1:
        unit = "°F"
    elif report[6] & 2:
        unit = "°C"
    elif report[6] & 4:
        unit = "F"
    elif report[6] & 8:
        unit = "Hz"
    elif report[6] & 0x10:
        unit = "hFE"

    prefix = ""
    if report[4] & 2:
        prefix = "n"
    elif report[5] & 0x10:
        prefix = "M"
    elif report[5] & 0x20:
        prefix = "k"
    elif report[5] & 0x40:
        prefix = "m"
    elif report[5] & 0x80:
        prefix = "µ"

    autorange = report[3] & 0x20

    if autorange and unit in "VA":  # only m, µ
        if prefix == "m":
            value *= 1e-3
        elif prefix == "µ":
            value *= 1e-6
        prefix = ""

    if report[3] & 0x08:
        unit += "AC"
    elif report[3] & 0x10:
        unit += "DC"

    timestamp = datetime.now().isoformat()
    return "{timestamp},{value},{prefix}{unit}".format(**locals())

dmm_path = find_dmm()
if not dmm_path:
    dbg("No DMM detected.")
    dbg("Have you tried turning it off and on again?")
    sys.exit(1)

dbg("Opening DMM at", dmm_path, "...")
with open(dmm_path, "rb") as fd:
    while True:
        report = fd.read(8)

        print(format_report(report))
