# app-command

app-command is a command-line tool for exerting fine-grained control over how to launch or give focus to applications when working with multiple Windows Virtual Desktops. It is designed for use with Stream Deck and similar macro utilities.

## Installation


Follow these steps to install and run the Python script:

### Prerequisites

This script requires Windows 10 or newer and Python 3.x.

You can verify that python is installed by running the following command in the windows command prompt:

```bash
python --version
```

If Python is not installed, download and install it from the official Python website.

### Steps

1. **Clone the repository**

    Open your terminal and run the following command:

    ```bash
    git clone https://github.com/machinebiology/app-command.git
    ```

2. **Navigate to the project directory**

    Change your current directory to the project's directory with:

    ```bash
    cd app-command
    ```

3. **Create a virtual environment (optional)**

    Creating a virtual environment is recommended in order to keep the dependencies required by different projects separate. Use the following command to create a virtual environment:

    ```bash
    python -m venv env
    ```

    To activate the virtual environment, run:

    ```bash
    .\env\Scripts\activate
    ```

4. **Install the dependencies**

   The dependencies are listed in the `requirements.txt` file. To install these dependencies, run:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

Syntax:

```bash
pythonw OPERATION  WINDOW_NAME  [DESKTOP_OPERATION]  [TARGET_DESKTOP]  [-p PATH]
```

### Arguments:
- **`OPERATION`:**
    - `find` or `find_anywhere`
        - Attempts to find the specified window on **any** desktop
            - All searches are case-insensitive and can match partial window titles (e.g. `calc` will match a window called `Calculator`)
        - If no matching window is found and a `path`` is specified, attempt to launch the app
    - `find_here`
        - Same as `find` but only attempts to find the window **on this desktop**
            - i.e. if the app is running on a different desktop, it will be treated as if it is not running, and if `path` is specified, it will attempt to launch another instance of the program.
    - `launch`
        - Force the launch of a new instance of the app without attempting to find running instances first

- **`WINDOW_NAME`:**
    - Specifies the title of the window to search for (case-insensitive)
    - Only a partial match is required (e.g. `calc` will match a window called `Calculator`)
    - If multiple windows match the search text, the first one found will be used

- **`DESKTOP_OPERATION`:**
    - `go_to_window`
        - Navigate to the desktop that contains the target window
    - `bring_to_user`
        - Move the target window to the current desktop
    - `take_to_desktop TARGET_DESKTOP`
        - Move to the specified desktop name or number
        - See below for information about `TARGET_DESKTOP`
    
- **`TARGET_DESKTOP`:**
    - Only used in conjunction with the `take_to_desktop` desktop operation above.
    - This value specifies a desktop to take both the app and the user to simultaneously.
        - An example use case is "Launch Excel on my Excel desktop and take me there"
    - This value can specify either the **name** or the **number** of a desktop
        - If a **name** is specified:
            - The desktop will be searched for by name (case-insensitive with partial matches)
        - If a desktop number is specified:
            - The *nth* desktop from the left will be used.
            - The leftmost desktop is number 1.
### Options:
- `-p, --path`:
    - Specifies the path to the program to run if either no matching window is found or if the `launch` operation is specified.

### Example usage

#### Find any `Calculator` window on any desktop and bring it to the user:

```bash
pythonw app-command.py find_anywhere calculator bring_to_user -p C:\windows\system32\calc.exe
```

- (Launch the app if it's not already running)

---

#### Find any `Calculator` window on any desktop and bring it to the user:

```bash
pythonw app-command.py find_anywhere calculator bring_to_user
```

- (DON'T launch the app if it's not already running)

---

#### Find any `Calculator` window on the current desktop and bring it to the user:

```bash
pythonw app-command.py find_here calculator bring_to_user -p calc.exe
```

- (Launch the app if it's not already running)

---

#### Find any `Calculator` window on any desktop, go to its desktop, and focus the app:

```bash
pythonw app-command.py find_anywhere calculator go_to_window -p C:\windows\system32\calc.exe
```

- (Launch the app on the current desktop if it isn't already running)

---

#### Find any `Excel` window on any desktop and move both the window & the user to the "Data" desktop:

```bash
pythonw app-command.py find_anywhere excel take_to_desktop data -p excel.exe
```

- (Launch the app on the "Data" desktop if it isn't already running)

---

#### Find any `Excel` window on any desktop and move both the window & the user to the third desktop from the left:

```bash
pythonw app-command.py find_anywhere excel take_to_desktop 3 -p excel.exe
```

- (Launch the app on desktop #3 if it isn't already running)