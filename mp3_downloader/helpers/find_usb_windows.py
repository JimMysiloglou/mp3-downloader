import win32file


def find_removable_usb_storage():
    usb_devices = {}
    drivebits = win32file.GetLogicalDrives()
    for d in range(1, 26):
        mask = 1 << d
        if drivebits & mask:
            # here if the drive is at least there
            drname = '%c:\\' % chr(ord('A') + d)
            t = win32file.GetDriveType(drname)
            if t == win32file.DRIVE_REMOVABLE:
                usb_devices[chr(ord('A') + d)] =  drname
    if not usb_devices:
        return {'No usb inserted': ''}
    return usb_devices
