""" Command line tool for launching and focusing Windows applications across virtual desktops """
import subprocess
from typing import Union

import click
import pygetwindow as gw
from pyvda import AppView, get_apps_by_z_order, VirtualDesktop, get_virtual_desktops

# current_desktop = VirtualDesktop.current()
# print(f"Current desktop is number {current_desktop.number}")

# current_window = AppView.current()
# print(f"current window: {current_window}")

def find_desktop_by_name(name: str, exact: bool=False) -> Union[VirtualDesktop, None]:
    """ Get a Windows virtual desktop by name (case-insensitive; return None if not found) """
    desktops = get_virtual_desktops()
    for d in desktops:
        if exact:
            # Match only whole string (case-insensitive)
            if name.lower() == d.name.lower():
                return d
        else:
            # Match on substring
            if name.lower() in d.name.lower():
                return d
    return None

def find_desktop_by_number(number: int) -> Union[VirtualDesktop, None]:
    """ Get a Windows virtual desktop by number (return None if not found) """
    desktops = get_virtual_desktops()
    if number <= len(desktops):
        return VirtualDesktop(number)
    else:
        return None

def find_app_by_name_substr(name: str, current_desktop_only: bool=False) -> Union[AppView, None]:
    """ Get an app by partial name (case-insensitive; return None if not found) """
    
    # Gets window objects including desktop info from the pyvda library
    apps: list[AppView] = get_apps_by_z_order(switcher_windows=True, current_desktop=current_desktop_only)
    # Gets windows matching the specified title from the pygetwindow library
    windows: list[gw.Window] = gw.getWindowsWithTitle(name)
    for app in apps:
        for w in windows:
            if app.hwnd == w._hWnd:
                # TODO: Handle multiple matches
                return app
    return None
    
def print_not_found_and_no_path():
    print("Window not found and no launch path specified.")

def launch_app(path: str=None):
    """ Launch an application by path """
    if path:
        subprocess.run(path)
    else:
        print_not_found_and_no_path()


@click.command()
@click.argument('operation', type=str)
@click.argument('window_name', type=str, default="")
@click.argument('desktop', default='go')
# @click.option('-x', '--exact_name_match', is_flag=True, help='If set, only match window title exactly')
@click.option('-p', '--path', help='Path to the executable to run if no matching window is found')
def main(operation: str, window_name: str, desktop, path: str=None):
    """ Finds an application by window title or launches it
    
    Syntax: [OPERATION] WINDOW_NAME [DESKTOP] [-p PATH]
    
    ARGUMENTS:
    - operation:
        - 'find'
            - Attempts to find the window and focus it; if not found, launches the app (if path is specified)
        - 'launch'
            - Launches the app without attempting to find it
    
    - window_name:
        - The title of the window to search for (case-insensitive)
        - If multiple windows match, the first one found will be used
    
    - desktop:
        - 'go'
            - Switch to the desktop containing the window
        - 'bring'
            - Bring the window to the current desktop
        - 'only_current'
            - Only search for windows on the current desktop
        - NAME
            - Bring the window to the specified desktop name (case-insensitive, allows partial matches)
        - NUMBER
            - Bring the window to the specified desktop number
        
    OPTIONS:
    - -p, --path:
        - Path to the executable to run if no matching window is found
    """
    operations = ['find', 'launch']
    desktop_operations = ['go', 'bring', 'only_current']

    operation = operation.lower()
    desktop = desktop.lower()

    search_current_desktop_only = (desktop == 'only_current')

    launch = False

    if operation == 'find':
        # Search for the app, constraining to the current desktop if appropriate
        app = find_app_by_name_substr(window_name, current_desktop_only=search_current_desktop_only)
        if app:
            if desktop == 'go':
                # App found; switch to the desktop containing the window
                app.desktop.go()
            elif desktop == 'bring':
                # App found; bring the window to the current desktop
                app.move(VirtualDesktop.current())
            elif type(desktop) == str:
                d = find_desktop_by_name(name=desktop, exact=False)
                app.move(d)
            elif type(desktop) == int:
                d = find_desktop_by_number(number=desktop)
                app.move(d)
            # Focus the window
            app.switch_to()
        else:
            launch = True

    if operation == 'launch' or launch == True:
        if desktop not in desktop_operations:
            if type(desktop) == str:
                d = find_desktop_by_name(name=desktop, exact=False)
                d.go()
            elif type(desktop) == int:
                d = find_desktop_by_number(number=desktop)
                d.go()
        launch_app(path=path)

    if operation not in operations:
        raise ValueError(f"Invalid operation: {operation}")

    # Use cases:
    # 1. Find app anywhere, switch to its desktop and focus it. Fail -> launch it
    #       find WINDOW 
    # 2. Find app anywhere, bring to current desktop and focus it. Fail -> launch it
    # 3. Find app on this desktop and focus it. Fail -> launch it
    # 4. Launch new instance of app regardless of whether it's already open (if app supports it)

    # print(f"operation: {operation}")
    # print(f"window_name: {window_name}")
    # print(f"desktop: {desktop}")
    # print(f"path: {path}")

if __name__ == '__main__':
    main()
