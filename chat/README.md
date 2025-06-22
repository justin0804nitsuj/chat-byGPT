# Simple Chat Application

This repository contains a minimal chat server and client built with Python.
It allows sending text messages and files between multiple users without any
explicit file size limits.

## Requirements

- Python 3.11 or later

No external packages are required.

## Usage

1. **Start the Server**

   ```bash
   python server.py
   ```

   The server listens on port `12345`.

2. **Run a Client**

   ```bash
   python client.py <server_host> <username>
   ```

   Replace `<server_host>` with the IP address or hostname where the server is
   running, and `<username>` with the name you want to use in the chat.

   A simple Tkinter-based interface is available as `gui_client.py`:

   ```bash
   python gui_client.py <server_host> <username>
   ```

3. **Sending Messages and Files**

   - Type messages and press Enter to send them to all connected users.
   - To send a file, use the `/file` command followed by the path:

     ```
     /file path/to/your/file
     ```

     Received files are saved with the sender's name prefixed to the filename.

## Notes

This is a simple example meant for small groups on a trusted network. It does
not implement encryption or authentication, so avoid using it over the public
Internet.

## Packaging as Executables

To create standalone Windows executables, install **PyInstaller** and run:

```bash
pip install pyinstaller
pyinstaller --onefile server.py
pyinstaller --onefile client.py
```

The generated `.exe` files will be placed in the `dist` directory.
