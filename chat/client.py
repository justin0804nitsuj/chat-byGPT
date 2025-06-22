import asyncio
import os
import sys

async def read_server(reader: asyncio.StreamReader):
    while True:
        header = await reader.readline()
        if not header:
            print("Disconnected from server")
            os._exit(0)
        header = header.decode().rstrip()
        if header.startswith("FILE "):
            parts = header.split(" ", 3)
            if len(parts) < 4:
                continue
            sender, filename, size = parts[1], parts[2], int(parts[3])
            data = await reader.readexactly(size)
            outname = f"{sender}_" + filename
            with open(outname, "wb") as f:
                f.write(data)
            print(f"Received file from {sender}: saved as {outname}")
        else:
            print(header)

async def user_input(writer: asyncio.StreamWriter):
    loop = asyncio.get_event_loop()
    while True:
        line = await loop.run_in_executor(None, input)
        if line.startswith("/file "):
            path = line[6:].strip()
            if not os.path.isfile(path):
                print("File does not exist")
                continue
            size = os.path.getsize(path)
            filename = os.path.basename(path)
            writer.write(f"FILE {filename} {size}\n".encode())
            with open(path, "rb") as f:
                writer.write(f.read())
            await writer.drain()
        else:
            writer.write(f"MSG {line}\n".encode())
            await writer.drain()

async def main(host: str, username: str):
    reader, writer = await asyncio.open_connection(host, 12345)
    writer.write(f"{username}\n".encode())
    await writer.drain()
    asyncio.create_task(read_server(reader))
    await user_input(writer)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python client.py <server_host> <username>")
        sys.exit(1)
    asyncio.run(main(sys.argv[1], sys.argv[2]))
