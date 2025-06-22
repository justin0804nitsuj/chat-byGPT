import asyncio

clients = set()

async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    addr = writer.get_extra_info('peername')
    name_line = await reader.readline()
    if not name_line:
        return
    username = name_line.decode().strip()
    print(f"{username} connected from {addr}")
    clients.add(writer)
    try:
        while True:
            header = await reader.readline()
            if not header:
                break
            header = header.decode().rstrip()
            if header.startswith("MSG "):
                msg = header[4:]
                broadcast = f"{username}: {msg}\n"
                for w in list(clients):
                    if w is not writer:
                        w.write(broadcast.encode())
                        await w.drain()
            elif header.startswith("FILE "):
                parts = header.split(" ", 2)
                if len(parts) < 3:
                    continue
                filename = parts[1]
                size = int(parts[2])
                data = await reader.readexactly(size)
                for w in list(clients):
                    if w is not writer:
                        w.write(f"FILE {username} {filename} {size}\n".encode())
                        w.write(data)
                        await w.drain()
    finally:
        clients.remove(writer)
        writer.close()
        await writer.wait_closed()
        print(f"{username} disconnected")

async def main(host="0.0.0.0", port=12345):
    server = await asyncio.start_server(handle_client, host, port)
    print(f"Chat server running on {host}:{port}")
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Server stopped")
