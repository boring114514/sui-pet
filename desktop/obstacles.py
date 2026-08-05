import ctypes
from ctypes import wintypes

user32 = ctypes.windll.user32
WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)


class RECT(ctypes.Structure):
    _fields_ = [('left', ctypes.c_long), ('top', ctypes.c_long),
                ('right', ctypes.c_long), ('bottom', ctypes.c_long)]


_collected = []


def _cb(hwnd, lparam):
    if not user32.IsWindowVisible(hwnd):
        return True
    if user32.IsIconic(hwnd):
        return True
    ex = user32.GetWindowLongW(hwnd, -20)
    if ex & 0x00000080:
        return True
    n = user32.GetWindowTextLengthW(hwnd)
    if n == 0:
        return True
    r = RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(r))
    _collected.append((r.left, r.top, r.right, r.bottom))
    return True


def get_obstacles():
    del _collected[:]
    user32.EnumWindows(WNDENUMPROC(_cb), 0)
    return list(_collected)


def get_work_area():
    r = RECT()
    user32.SystemParametersInfoW(0x0030, 0, ctypes.byref(r), 0)
    return (r.left, r.top, r.right, r.bottom)


class POINT(ctypes.Structure):
    _fields_ = [('x', ctypes.c_long), ('y', ctypes.c_long)]


def get_cursor_pos():
    pt = POINT()
    user32.GetCursorPos(ctypes.byref(pt))
    return pt.x, pt.y
