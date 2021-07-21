import pyudev
import psutil

context = pyudev.Context()

def find_removable_usb_storage():
    usb_devices = {}
    removable = [device for device in context.list_devices(subsystem='block', DEVTYPE='disk') if device.attributes.asstring('removable') == "1"]
    for device in removable:
        partitions = [device.device_node for device in context.list_devices(subsystem='block', DEVTYPE='partition', parent=device)]
        for p in psutil.disk_partitions():
            if p.device in partitions:
                usb_devices[p.device] = p.mountpoint
    if not usb_devices:
        return {'No usb insterted': ''}
    return usb_devices
