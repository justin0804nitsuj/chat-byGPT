import asyncio
import os
import tkinter as tk
from tkinter import filedialog, scrolledtext
import sys

class ChatGUI:
    def __init__(self, loop, writer):
        self.loop = loop
        self.writer = writer
        self.root = tk.Tk()
        self.root.title("Chat Client")

        self.text = scrolledtext.ScrolledText(self.root, state='disabled', width=50, height=20)
        self.text.pack(padx=5, pady=5)

        self.entry = tk.Entry(self.root, width=40)
        self.entry.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
        self.entry.bind('<Return>', self.send_message)

        self.send_button = tk.Button(self.root, text='Send', command=self.send_message)
        self.send_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.file_button = tk.Button(self.root, text='Send File', command=self.send_file)
        self.file_button.pack(side=tk.LEFT, padx=5, pady=5)

    def display(self, msg: str):
        self.text.configure(state='normal')
        self.text.insert(tk.END, msg + '\n')
        self.text.see(tk.END)
        self.text.configure(state='disabled')

    def send_message(self, event=None):
        msg = self.entry.get()
        if not msg:
            return
        self.entry.delete(0, tk.END)
        self.writer.write(f"MSG {msg}\n".encode())
        self.loop.create_task(self.writer.drain())

    def send_file(self):
        path = filedialog.askopenfilename()
        if not path:
            return
        size = os.path.getsize(path)
        filename = os.path.basename(path)
        self.writer.write(f"FILE {filename} {size}\n".encode())
        with open(path, 'rb') as f:
            self.writer.write(f.read())
        self.loop.create_task(self.writer.drain())
        self.display(f"Sent file {filename}")

async def read_server(reader: asyncio.StreamReader, gui: ChatGUI):
    while True:
        header = await reader.readline()
        if not header:
            gui.display("Disconnected from server")
            os._exit(0)
        header = header.decode().rstrip()
        if header.startswith("FILE "):
            parts = header.split(" ", 3)
            if len(parts) < 4:
                continue
            sender, filename, size = parts[1], parts[2], int(parts[3])
            data = await reader.readexactly(size)
            outname = f"{sender}_" + filename
            with open(outname, 'wb') as f:
                f.write(data)
            gui.display(f"Received file from {sender}: saved as {outname}")
        else:
            gui.display(header)

async def run_tk(root: tk.Tk):
    while True:
        root.update()
        await asyncio.sleep(0.05)

async def main(host: str, username: str):
    reader, writer = await asyncio.open_connection(host, 12345)
    writer.write(f"{username}\n".encode())
    await writer.drain()

    gui = ChatGUI(asyncio.get_event_loop(), writer)
    asyncio.create_task(read_server(reader, gui))
    await run_tk(gui.root)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python gui_client.py <server_host> <username>")
        sys.exit(1)
    asyncio.run(main(sys.argv[1], sys.argv[2]))
