""" Command line tool to switch to a Windows virtual desktop by number or name """
import click
from pyvda import AppView, get_apps_by_z_order, VirtualDesktop, get_virtual_desktops

@click.command()
@click.argument('number', default=1, type=int)
@click.option('-n', '--name', help='Select a desktop by name (accepts partial names)')
@click.option('-e', '--exact', is_flag=True, help='Only match desktop name exactly (case-insensitive)')
def main(number: int=None, name: str=None, exact: bool=False):
    """ Switch to a Windows virtual desktop by number or name """
    desktops = get_virtual_desktops()
    if name:
        for d in desktops:
            if exact:
                # Match only whole string (case-insensitive)
                if name.lower() == d.name.lower():
                    return d.go()
            else:
                # Match on substring
                if name.lower() in d.name.lower():
                    return d.go()

        print(f"Desktop {name} not found.")
        return

    else:
        if number <= len(desktops):
            # Go to specified desktop
            return VirtualDesktop(number).go()
        else:
            return print(f"Desktop {number} not found.")

if __name__ == '__main__':
    main()
