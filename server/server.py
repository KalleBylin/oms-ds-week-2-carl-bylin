import json
import socket


class UDPCommunicator:
    def __init__(self, sock: socket.socket):
        self._socket = sock
        self._input = sock.makefile("r")
        self._output = sock.makefile("w")

        # We are limiting size of messages with 400 octets.
        # Globally in the internet we have the notion of MTU (Maximum transmission unit) of an
        # IP packet equals to 576 bytes. Thus any IP packet which length is less that 576 will be
        # transmitted with no packet fragmentation. Notice that the length of __whole__ packet is
        # considered when dealing with fragmentation. If we limiti message size to 400 we are
        # playing safe game -- we leave 176 bytes on the table for all the IP header stuff.
        #
        # When implementing ClientHandler class you need to be aware of message size limit, so
        # it is declared as object field.
        self.message_size_limit = 400

    def send(self, message: str):
        if len(message) > self.message_size_limit:
            raise RuntimeError(f"Message has more characters than allowed ({len(message)} > {self.message_size_limit})")

    def recv(self) -> str:
        pass

    def close(self):
        self._input.close()
        self._output.flush()
        self._output.close()
        self._socket.close()


class ClientHandler:
    def __init__(
        self, message_size_limit
    ):
        # Dictionary with state for every client currently sending data to the server
        self._state = dict()
        self._message_size_limit = message_size_limit

    def handle_message(self, addrinfo, message):
        if addrinfo not in self._state:
            self._state[addrinfo] = self.init_context(addrinfo, message)

        context = self._state[addrinfo]
        self.process_message(addrinfo, message, context)

    def init_context(self, addrinfo, message):
        """
        Called when first connection with us is made. This function should not alter self._context
        object in any way as it is done outside the function.

        :param addrinfo:
        :param message:
        :return: Context object to save for this paticular client. Can be any object imaginable
        """

        # Change initialization for something that you feel is ok for you
        context = []

        return context

    def process_message(self, addrinfo, message, context):
        """
        Processes message sent from client.

        :param addrinfo: Addrinfo tuple (host, port) of client
        :param message: String with data sent from client
        :param context: Dictionary object associated with this client, initialized with
                        init_context method
        """
        self._state[addrinfo].append(json.loads(message.decode())["body"])

    def clear_context(self, addrinfo):
        """
        Remove all context associated with addrinfo when called. Use this function to process next
        message from client as new message without any prior connection

        :param addrinfo: Addrinfo tuple of client
        :return:
        """
        del self._state[addrinfo]


class Server:
    def __init__(
        self,
        host: str,
        port: int,
    ):
        self.host = host
        self.port = port

        # Open socket usign Datagrams as transport. With probability of 1 this is
        # UDP implementation
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Binding socket for address
        self._socket.bind((self.host, self.port))

        # We are limiting size of messages with 400 octets.
        # Globally in the internet we have the notion of MTU (Maximum transmission unit) of an
        # IP packet equals to 576 bytes. Thus any IP packet which length is less that 576 will be
        # transmitted with no packet fragmentation. Notice that the length of __whole__ packet is
        # considered when dealing with fragmentation. If we limiti message size to 400 we are
        # playing safe game -- we leave 176 bytes on the table for all the IP header stuff.
        #
        # When implementing ClientHandler class you need to be aware of message size limit, so
        # it is declared as object field.
        self.message_size_limit = 400

        self._client_handler = ClientHandler(self.message_size_limit)

    def serve(self):
        print("Server is online and listening for messages")
        while True:
            # Another client has connected. Notice that for the sake of simplicity
            # we are a single-threaded application
            message, addrinfo = self._socket.recvfrom(self.message_size_limit)
            
            if message.decode() == "ping":
                self._socket.sendto("online".encode(), addrinfo)

            elif message.decode() == "end":
                print('\n'.join(self._client_handler._state[addrinfo]))

            else:
                self._client_handler.handle_message(addrinfo, message)


if __name__ == '__main__':
    s = Server('0.0.0.0', 5678)
    s.serve()
