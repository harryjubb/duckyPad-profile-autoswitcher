import time
import platform

p = platform.system()

if p == 'Windows':
    import wmi
    import win32process
    import pygetwindow as gw
elif p == 'Darwin':
    import subprocess
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

def darwin_run_applescript(script):
    process = subprocess.Popen('osascript -', stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    stdout, stderr = process.communicate(script)

    return stdout.decode('utf-8'), stderr.decode('utf-8')

def darwin_parse_applescript_output(output):
    return [item.strip() for item in output.strip().split(', ')]

def darwin_get_active_window():

    print()
    print('called darwin_get_active_window')

    # https://stackoverflow.com/a/44229825/1108828
    app = NSWorkspace.sharedWorkspace().frontmostApplication()
    active_app_name = app.localizedName()
    active_app_pid = NSWorkspace.sharedWorkspace().activeApplication()['NSApplicationProcessIdentifier']

    windows = Quartz.CGWindowListCopyWindowInfo(
        Quartz.kCGWindowListExcludeDesktopElements | Quartz.kCGWindowListOptionOnScreenOnly,
        Quartz.kCGNullWindowID
    )

    for window in windows:

        window_pid = window[Quartz.kCGWindowOwnerPID]
        window_owner_name = window[Quartz.kCGWindowOwnerName]
        window_title = str(window.get(Quartz.kCGWindowName, 'unknown'))

        if (
            window_owner_name == active_app_name and
            window_pid == active_app_pid and
            window_title != 'unknown'
        ):
            active_window = (window_owner_name, window_title)
            print('active_window is', active_window)
            print('returning')
            return active_window
        elif (
            window_owner_name == active_app_name and
            window_pid == active_app_pid
        ):
            print('active window has title', window_title)


    print('no quartz window found, running applescript')

    script = """
    tell application "System Events"
        set frontproc to first application process whose frontmost is true
        set appDisplayedName to displayed name of frontproc
        if exists (front window of frontproc) then
            set winName to name of front window of frontproc
        else
            set winName to "unknown"
        end if
        return {appDisplayedName, winName}
    end tell
    """.encode('utf-8')

    active_window = tuple(
        darwin_parse_applescript_output(
            darwin_run_applescript(script)[0]
        )
    )

    print(active_window)
    return active_window

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
