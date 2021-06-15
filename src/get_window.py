import time
import platform
from pprint import pprint

p = platform.system()

if p == 'Windows':
    import wmi
    import win32process
    import pygetwindow as gw
elif p == 'Darwin':
    from AppKit import NSWorkspace
    import Quartz

def get_active_window():
    if p == 'Windows':
        return win_get_active_window()
    elif p == 'Darwin':
        return darwin_get_active_window()
    raise 'Platform %s not supported' % p

def get_list_of_all_windows():
    if p == 'Windows':
        return win_get_list_of_all_windows()
    elif p == 'Darwin':
        return darwin_get_list_of_all_windows()
    raise 'Platform %s not supported' % p

def darwin_get_active_window():
    # print(dir(NSWorkspace))
    # print(dir(NSWorkspace.sharedWorkspace()))
    # print(type(NSWorkspace.sharedWorkspace().activeApplication()))
    # print(dir(NSWorkspace.sharedWorkspace().activeApplication()))
    # print(type(NSWorkspace.sharedWorkspace().frontmostApplication()))
    # print(dir(NSWorkspace.sharedWorkspace().frontmostApplication()))
    # exit(1)
    
    active_application = NSWorkspace.sharedWorkspace().frontmostApplication()
    print(type(active_application))
    pprint(dir(active_application))

    return active_application.localizedName(), ""
    
    # windows = Quartz.CGWindowListCopyWindowInfo(
    #     Quartz.kCGWindowListExcludeDesktopElements | Quartz.kCGWindowListOptionOnScreenOnly, Quartz.kCGNullWindowID)
    # for window in windows:
    #     if window[Quartz.kCGWindowLayer] == 0:
    #         return window[Quartz.kCGWindowOwnerName], NSWorkspace.sharedWorkspace().activeApplication()['NSApplicationName']
    return '', ''

def darwin_get_list_of_all_windows():
    apps = []
    windows = Quartz.CGWindowListCopyWindowInfo(
        Quartz.kCGWindowListExcludeDesktopElements | Quartz.kCGWindowListOptionOnScreenOnly, Quartz.kCGNullWindowID)

    for window in windows:
        apps.append((window[Quartz.kCGWindowOwnerName],
                    window.get(Quartz.kCGWindowName, 'unknown')))
    apps = list(set(apps))
    apps = sorted(apps, key=lambda x: x[0])
    return apps

def win_get_app_name(hwnd):
    """Get application name given hwnd."""
    c = wmi.WMI()
    try:
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        for p in c.query('SELECT Name FROM Win32_Process WHERE ProcessId = %s' % str(pid)):
            exe = p.Name.rsplit('.', 1)[0]
            break
    except:
        return 'unknown'
    else:
        return exe

def win_get_list_of_all_windows():
    ret = set()
    for item in gw.getAllWindows():
        ret.add((win_get_app_name(item._hWnd), item.title))
    ret = sorted(list(ret), key=lambda x: x[0])
    return ret

def win_get_active_window():
    active_window = gw.getActiveWindow()
    if active_window is None:
        return '', ''
    return (win_get_app_name(active_window._hWnd), active_window.title)
