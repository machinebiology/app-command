""" Command line tool for launching and focusing Windows applications across virtual desktops """
import subprocess
from typing import Union

import click
import pygetwindow as gw
from pyvda import AppView, get_apps_by_z_order, VirtualDesktop, get_virtual_desktops

def str_to_int(s: str) -> Union[int, None]:
    """ Convert a string to an integer; return None if not possible """
    try:
        return int(s)
    except ValueError:
        return None

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
@click.argument('desktop_operation', type=str, default="go_to_window")
@click.argument('target_desktop', default="")
# @click.option('-x', '--exact_name_match', is_flag=True, help='If set, only match window title exactly')
@click.option('-p', '--path', help='Path to the executable to run if no matching window is found')
def main(operation: str, window_name: str, desktop_operation: str, target_desktop: Union[int, str, None], path: str=None):
    """ Finds an application by window title or launches it
    
    Syntax: OPERATION WINDOW_NAME [DESKTOP_OPERATION] [TARGET_DESKTOP] [-p PATH]

    NOTE: WINDOW_NAME must be specified even during a 'launch' operation

    ARGUMENTS:
    - operation:
        - 'find' or 'find_anywhere'
            - Attempts to find the window on any dekstop; if not found, launches the app (if path is specified)
        - 'find_here'
            - Attempts to find the window on this desktop only; if not found, launches the app (if path is specified)
        - 'launch'
            - Launches the app without attempting to find it
    
    - window_name:
        - The title of the window to search for (case-insensitive)
        - If multiple windows match, the first one found will be used
    
    - desktop_operation:
        - 'go_to_window'
            - Switch to the desktop containing the window
        - 'bring_to_user'
            - Bring the window to the current desktop
        - 'take_to_desktop' DESKTOP_NAME | DESKTOP_NUMBER
            - Move to the specified desktop name or number
        
        - NAME
            - Bring the window to the specified desktop name (case-insensitive, allows partial matches)
        - NUMBER
            - Bring the window to the specified desktop number
        
    OPTIONS:
    - -p, --path:
        - Path to the executable to run if no matching window is found
    """
    operation_synonyms = {
        'find': 'find_anywhere'
    }
    find_operations = ['find_anywhere', 'find_here']
    operations = [*find_operations, 'launch']
    desktop_operations = ['go_to_window', 'bring_to_user', 'take_to_desktop']

    # Cast operation name args to lowercase
    operation = operation.lower()
    desktop_operation = desktop_operation.lower()

    # Replace operation synonyms with the canonical operation name
    if operation in operation_synonyms:
        operation = operation_synonyms[operation]

    # Validate arguments
    if operation not in operations:
        raise ValueError(f"Invalid operation: {operation}")
    if desktop_operation not in desktop_operations:
        raise ValueError(f"Invalid desktop_operation: {desktop_operation}")

    # Assume no launch is required until we determine otherwise
    launch = False

    # If a target desktop was specified, find it
    if target_desktop:
        target_desktop_as_int = str_to_int(target_desktop)
        if target_desktop_as_int:
            d = find_desktop_by_number(number=target_desktop_as_int)
        else:
            d = find_desktop_by_name(name=target_desktop, exact=False)

    if operation == 'find_anywhere':
        # Search for the app across all desktops
        app = find_app_by_name_substr(window_name, current_desktop_only=False)
    
    if operation == 'find_here':
        # Search for the app only on the current desktop
        app = find_app_by_name_substr(window_name, current_desktop_only=True)
    
    if operation in find_operations:
        if app:
            # Window found
            if desktop_operation == 'go_to_window':
                # Switch to the desktop containing the window
                app.desktop.go()
            elif desktop_operation == 'bring_to_user':
                # Bring the window to the current desktop
                app.move(VirtualDesktop.current())
            elif desktop_operation == 'take_to_desktop':
                if d:
                    app.move(d)
                    d.go()
            # Focus the window
            app.switch_to()
        else:
            # Window not found, try to launch app
            launch = True

    if operation == 'launch' or launch == True:
        if desktop_operation == 'take_to_desktop':
            if d:
                d.go()
        launch_app(path=path)

if __name__ == '__main__':
    main()
