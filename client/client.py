import itertools
import socket
import json
import time
from payload import payload


def chunks(iterable, size):
    it = iter(iterable)
    while True:
        chunk = tuple(itertools.islice(it, size))
        if not chunk:
            break
        yield chunk


class Client:
    def __init__(self, server_host: str, server_port: int):
        self.host = server_host
        self.port = server_port

        self.outsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send_payload(self):
        for chunk in chunks(payload, 100):
            self.send_chunk(chunk)

    def send_message(self, message: bytes):
        self.outsocket.sendto(message, (self.host, self.port))

    def send_chunk(self, chunk):
        """
        :param chunk: Chunk of data of size 100 bytes
        """
        #
        # Write your code.
        # You can use privitive self.send_message to send a little chunk of data to the server.
        # Here you can wrap your data with some service data
        string_data = ''.join(chunk)

        bytesarray = self.recv_message()
        input_string = bytesarray.decode('utf-8')
        json_data = json.loads(input_string)
        json_data["body"] = string_data

        self.send_message(json.dumps(json_data).encode())

    def recv_message(self) -> bytes:
        service_data = '{"title": "A Fairy Song", "author": "William Shakespeare"}'.encode('utf-8')
        return bytes(service_data)


def main():
    client = Client('server', 5678)

    server_online = False
    print("Checking if server is online")
    while not server_online:
        client.outsocket.sendto("ping".encode(), ('server', 5678))

        message, server_address = client.outsocket.recvfrom(400)
        print("Received response from server:", message.decode())
        if message.decode() == "online":
            server_online = True
        time.sleep(2)
  
    client.send_payload()
    client.outsocket.sendto("end".encode(), ('server', 5678))


if __name__ == '__main__':
    main()
    time.sleep(10)
