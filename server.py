import socket
import threading
import sys
from UserManagement import *
from MessageManagement import *
import json


class Server:
    #  Setting up initial information
    def __init__(self, ServerPort, attempt_times):
        self.ServerPort = ServerPort
        self.attempt_times = attempt_times
        # local server
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(('127.0.0.1', self.ServerPort))
        self.socket.listen(10)
        self.UserManagement = UserManagement(attempt_times)
        self.MessageManagement = MessageManagement()

    def beginning(self):
        print('The server(Nicky) is beginning and waiting for the client......')
        while True:
            client, address = self.socket.accept()
            print('A new client has entered the server.')
            # multithreading :serving more then one client at the same time
            receive_threading = threading.Thread(target=self.receive, args=(client, address))
            receive_threading.start()

            # send_threading = threading.Thread(target=self.send, args=(client,))
            # send_threading.start()

    # always online
    def receive(self, clientSocket, clientIP):
        while True:
            try:
                receive_message = clientSocket.recv(1024)
                request = json.loads(receive_message)
            except Exception:
                print('> A client has  leaved the server.')
                return
            username = request["content"][0]
            command = request["command"]
            response = dict()
            if request["command"] == "LOGIN":
                print('>', username, 'apply for', command)
                password = request["content"][1]
                clientUDP = request["content"][2]
                # username, password, clientUDPport, clientIP, clientSocket
                content = self.UserManagement.login(username, password, clientUDP, clientIP[0])

                # request["command"] = "LOGIN"
                response["content"] = content
                response["information"] = []

            elif request["command"] == "OUT":
                print('>', username, 'apply for', command)
                # print('dao out le!!!!!!!')
                content = self.UserManagement.logout(username)
                # request["command"] = "OUT"
                response["content"] = content
                response["information"] = []

            elif request["command"] == "MSG":
                message = request["content"][1]
                content, information = self.MessageManagement.add(username, message)
                response["content"] = content
                response["information"] = information
                messagenumber = '#' + str(response["information"][0])
                messagetime = response["information"][1]
                message = '"' + message + '"'
                print('>', username, 'posted MSG', messagenumber, message, 'at', messagetime)

            elif request["command"] == "DLT":
                messageNumber = request["content"][1][1:]
                message_LastModifyTime = request["content"][2]
                content, information = self.MessageManagement.delete(username, messageNumber, message_LastModifyTime)
                response["content"] = content
                response["information"] = information
                if content == 'success':
                    messagenumber = '#'+str(response["information"][0])
                    deletTime = response["information"][1]
                    message = '"' + response["information"][2] + '"'
                    print('>', username, 'deleted MSG', messagenumber, message, 'at', deletTime)
                else:
                    print('>', username, 'deleted MSG. Authorisation fails.')
            elif request["command"] == "EDT":
                # self.usernamemessageNumber,original_timestamp,newMessage
                messageNumber = request["content"][1][1:]
                original_timestamp = request["content"][2]
                newMessage = request["content"][3]
                content, information = self.MessageManagement.edite(username, messageNumber, original_timestamp,
                                                                    newMessage)
                response["content"] = content
                response["information"] = information
                if content == 'success':
                    messagenumber = '#'+str(response["information"][0])
                    EDTTime = response["information"][1]
                    print('>', username, 'deleted MSG', messagenumber,'at', EDTTime)
                else:
                    print('>', username, 'deleted MSG. Authorisation fails.')


            elif request["command"] == "RDM":
                # command (RDM) and a timestamp
                print('>', username, 'issued RDM command')
                timestamp = request["content"][1]
                content, information = self.MessageManagement.read(timestamp)
                response["content"] = content
                response["information"] = information
                print('> Return messages:')
                for i in information:
                    print(i)

            elif request["command"] == "UPD":
                content, information = self.UserManagement.ATU(username)
                response["content"] = content
                response['information'] = information

            else:  # request["command"] == "ATU":
                print('>', username, 'posted issued ATU command ATU')
                content, information = self.UserManagement.ATU(username)

                response["content"] = content
                response['information'] = information

            response = json.dumps(response).encode()

            clientSocket.send(response)

    # always online
    # def send(self, client):
    #    while True:
    #        send_message = input('server:').encode()
    #        client.send(send_message)


# python   server.py    server_port    number_of_consecutive_failed_attempts
if __name__ == '__main__':
    ServerPort = int(sys.argv[1])
    number_of_consecutive_failed_attempts = int(sys.argv[2])
    server = Server(ServerPort, number_of_consecutive_failed_attempts)
    server.beginning()
