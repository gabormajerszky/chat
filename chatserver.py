#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket
import threading


host = socket.gethostbyname(socket.gethostname())
port = 50000
encoding = "utf-8"


class ClientsThread(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.socket = socket.socket()
        self.socket.bind((host, port))
        self.socket.listen(5)
        print("Address: {}:{}".format(host, port))
        print("Server is ready, waiting for clients...")

    def run(self):
        """Listen to and manage new client connections."""

        while True:
            if len(ConnectionThread.threads) < 5:
                connection, address = self.socket.accept()
                print("client from {}:{} connected".format(
                    address[0], address[1]))
                newthread = ConnectionThread(connection)
                newthread.start()
                newthread.connection.send(
                    bytes("Successfully connected to the server.", encoding))


class ConnectionThread(threading.Thread):

    """Communicate with a client. Each client will have their own thread."""

    threads = []

    def __init__(self, connection):
        threading.Thread.__init__(self)
        # this is a temporary solution, I'll use names later on
        self.clientid = len(ConnectionThread.threads)
        self.connection = connection
        # store every existing connection in a list
        ConnectionThread.threads.append(self)

    def run(self):
        """Ensure communication with a certain client."""

        while True:

            clientmessage = self.connection.recv(1024).decode(encoding)
            print(clientmessage)
            if "CLIENT_EXIT_MESSAGE" in clientmessage:
                print("client #{} disconnected".format(self.clientid))
                # send a message to the client that it can close the thread
                self.connection.send(bytes("REMOTECLOSE_THREAD", encoding))
                # send a message about this client leaving to everyone else
                msg = "{} disconnected.".format(clientmessage.split(":")[0])

                # remove the disconnecting client from the thread's list
                ConnectionThread.threads.remove(self)
                for client in ConnectionThread.threads:
                    client.connection.send(bytes(msg, encoding))
                # close the client's connection with the server
                break

            # send the client's message to everyone
            for client in ConnectionThread.threads:
                if client != self:
                    client.connection.send(bytes(clientmessage, encoding))

if __name__ == "__main__":
    listen = ClientsThread()
    listen.start()
