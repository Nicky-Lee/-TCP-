import socket
import threading
import sys
import re
import json
import os


class Client:
    def __init__(self, serverIP, serverPort, clientUDPport):
        self.username = ''
        self.serverIP = serverIP
        self.serverPort = serverPort
        self.clientUDPport = clientUDPport
        # create a client
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((serverIP, serverPort))
        self.active_clinet = dict()
        self.UDPclient = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.UDPclient.bind(('127.0.0.1', clientUDPport))
        self.UDP_message_total = 0
        self.newfilename = ''
        self.UDP_receiveuser = ''

    def sendPacket(self, request):
        packet = json.dumps(request)
        # print(packet)
        self.client.send(packet.encode())

    def receivePacket(self):
        message = self.client.recv(1024)
        message = message.decode()
        response = json.loads(message)
        # print(response)
        return response

    def P2PreceivePacket(self):
        while True:
            message, address = self.UDPclient.recvfrom(1024)
            receive = json.loads(message[1:].decode())
            command = receive['command']
            # print(receive)
            if command == 'UPD':
                self.UDP_receiveuser = receive['content'][0]
                filename = receive['content'][1]
                self.newfilename = self.UDP_receiveuser + '_' + filename
                self.UDP_message_total = receive['content'][2]
                # print(address)
                self.UDPclient.sendto(b"ACK", address)
                with open(self.newfilename, 'wb') as fp:
                    while True:
                        message, address = self.UDPclient.recvfrom(10241)
                        # print(message)
                        if message[0] == b'd'[0]:
                            data = message[1:]
                            fp.write(data)
                            self.UDPclient.sendto(b"ACK", address)
                        elif message[0] == b'e'[0]:
                            break
                self.UDPclient.sendto(b"ACK", address)
                print('> Received {} from {}'.format(self.newfilename, self.UDP_receiveuser))
                self.newfilename = ''
                self.UDP_message_total = 0
                self.UDP_receiveuser = ''

    def remove_space(self, string):
        while string[0] == " ":
            string = string[1:]
        while string[-1] == " ":
            string = string[:-2]
        return string

    def beginning(self):
        while True:
            request = dict()
            if self.username == '':
                username = input('username:')
                password = input('password:')
                request["command"] = "LOGIN"
                request["content"] = [username, password, self.clientUDPport]
                self.sendPacket(request)
                response = self.receivePacket()

                if response["content"][0] == 'E':
                    print('> Failure. Invalid number of allowed failed consecutive attempt: {}'.format(
                        response["content"][1]))

                elif response["content"] == 'B':
                    print('> Failure. Since username does not exist.')
                elif response["content"] == 'C':
                    print('> Failure. Since user is logged in.')
                elif response["content"] == 'D':
                    print('> Failure. Since user is blocked, please waite for 10 second.')
                else:
                    print('> User login successfully.')
                    self.username = username
                P2PreceivePacket_threading = threading.Thread(target=self.P2PreceivePacket)
                P2PreceivePacket_threading.start()
            else:
                message = input(">> Enter one of the following commands (MSG, DLT, EDT, RDM, ATU, OUT, UPD):")
                if message.isspace() or not message:
                    print('> Error. Invalid command!')
                else:
                    command = message.split()[0]
                    request["command"] = command
                    if command == 'OUT':
                        request["content"] = [self.username]

                        self.sendPacket(request)
                        response = self.receivePacket()

                        content = response["content"]
                        if content == "success":
                            print('> User logged out successfully')
                            self.username = ''

                            self.client.close()
                            return

                        else:
                            print('> Logout failed.')
                    elif command == 'MSG':
                        message = message.replace("MSG", "", 1)
                        if message.isspace() or not message:
                            print('> Error. Invalid command!')
                        else:
                            request["content"] = [self.username, self.remove_space(message)]
                            if message.isspace():
                                print("> Error message.")
                            else:
                                self.sendPacket(request)
                                response = self.receivePacket()
                                content = response["content"]
                                if content == "success":
                                    print('> Message sent successfully.')
                                    messageNumber = int(response["information"][0])
                                    message_lastModifyTime = response["information"][1]
                                    print('> Message #{}, posted at'.format(messageNumber),
                                          message_lastModifyTime)
                    elif command == 'DLT':
                        # DLT messagenumber timestamp
                        message = message.replace('DLT ', '', 1)
                        if message.isspace() or not message:
                            print('> Error. Invalid command!')
                        else:
                            messagenumber = message.split()[0]
                            timestamp = message.replace(messagenumber, '', 1)
                            request["content"] = [self.username, messagenumber, self.remove_space(timestamp)]
                            self.sendPacket(request)
                            response = self.receivePacket()
                            content = response["content"]
                            if content == 'success':
                                print('> Message delete successfully.')
                            else:
                                print(content)
                    elif command == 'EDT':
                        # EDT messagenumber timestamp message
                        message = message.replace('EDT ', '', 1)
                        if message.isspace() or not message:
                            print('> Error. Invalid command!')
                        else:
                            messageNumber = message.split()[0]
                            message = self.remove_space(message.replace(messageNumber, '', 1))
                            try:
                                original_timestamp = re.search(r'^\d\d ... \d\d\d\d \d\d:\d\d:\d\d', message).group()
                            except AttributeError:
                                print('> Error. Invalid command!')
                                continue
                            newMessage = message.replace(original_timestamp, '', 1)
                            # the message number, the original message’s timestamp, the
                            # new message and the username
                            request["content"] = [self.username, messageNumber, self.remove_space(original_timestamp),
                                                  self.remove_space(newMessage)]
                            self.sendPacket(request)
                            response = self.receivePacket()
                            content = response["content"]
                            if content == 'success':
                                print("Message edit successfully.")
                                messageNumber = int(response["information"][0])
                                message_lastModifyTime = response["information"][1]
                                print('The messagenumber is {}, and the last modify time is'.format(messageNumber),
                                      message_lastModifyTime)
                            else:
                                print(content)
                    elif command == 'RDM':
                        # command (RDM) and a timestamp
                        message = message.replace('RDM ', '', 1)
                        if message.isspace() or not message:
                            print('> Error. Invalid command!')
                        else:
                            try:
                                original_timestamp = re.search(r'\d\d ... \d\d\d\d \d\d:\d\d:\d\d', message).group()
                            except AttributeError:
                                print('> Error. Invalid command!')
                                continue
                            if original_timestamp:
                                request["content"] = [self.username, original_timestamp]
                                self.sendPacket(request)
                                response = self.receivePacket()
                                content = response['content']
                                if content == 'success':
                                    for log in response["information"]:
                                        print('> ', end='')
                                        print(log)
                                else:
                                    print('“no new message')
                    elif command == 'ATU':
                        request["content"] = [self.username]
                        self.sendPacket(request)
                        response = self.receivePacket()
                        content = response["content"]
                        if content == 'success':
                            # print('Return active user list: ', end='')
                            # Obi-wan;
                            # 129.129.2.1; 8001; active
                            # since 23 Feb 2021
                            # 16:00:01.
                            for user in response["information"]:
                                # user.username, user.clientIP, user.clientUDPport,user.onlinetime
                                print('> {}; {}; {}; active since {}'.format(user[0], user[1], user[2], user[3]))
                                self.active_clinet[user[0]] = [user[1], user[2]]
                        else:
                            print('> no other active user')
                    elif command == 'UPD':
                        message = message.replace('UPD ', '', 1)
                        if message.isspace() or not message:
                            print('> Error. Invalid command!')
                        else:
                            Pclient = message.split()[0]
                            if len(self.active_clinet) == 0:
                                request["content"] = [self.username]
                                self.sendPacket(request)
                                response = self.receivePacket()
                                for user in response["information"]:
                                    # user.username, user.clientIP, user.clientUDPport,user.onlinetime
                                    # print(f'{user[0]}; {user[1]}; {user[2]}; active since {user[3]}')
                                    self.active_clinet[user[0]] = [user[1], user[2]]

                            if Pclient in self.active_clinet:
                                Pclient_IP = self.active_clinet[Pclient][0]
                                Pclient_Port = self.active_clinet[Pclient][1]
                                message = message.replace(Pclient, '', 1)
                                fileName = self.remove_space(message)
                                # make a temp UDP as receive problem
                                # print(self.active_clinet[Pclient])
                                Temp_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                                # send head
                                total_lengh = os.path.getsize(fileName)
                                request['content'] = [self.username, fileName, total_lengh]
                                packet = b"h" + json.dumps(request).encode()
                                Temp_udp.sendto(packet, (Pclient_IP, Pclient_Port))
                                # print(Temp_udp)
                                ack = self.UDPclient.recv(20)  # self.UDPclient.recv() can not receive message, due to  self.P2PreceivePacket(self) is always on
                                # print(ack)
                                if ack == b'ACK':
                                    with open(fileName, 'rb') as fp:
                                        while True:
                                            content = fp.read(10240)
                                            # print(content)
                                            if content != b"":
                                                Temp_udp.sendto(b"d" + content, (Pclient_IP, Pclient_Port))
                                                ack = Temp_udp.recv(20)
                                                if ack == b'ACK':
                                                    pass
                                            else:
                                                break
                                Temp_udp.sendto(b"e", (Pclient_IP, Pclient_Port))
                                ack = Temp_udp.recv(20)
                                if ack == b'ACK':
                                    print('> {} has been uploaded.'.format(fileName))

                            else:
                                print('{} is not active.'.format(Pclient))
                    else:  # error command
                        print('> Error. Invalid command!')

    # def receive(self):
    #    message = self.client.recv(1024).decode()

    #    print('Server:', message)

    # receive_threading = threading.Thread(target=self.receive)
    # receive_threading.start()


# python  client.py      server_IP     server_port    client_udp_server_port
if __name__ == '__main__':
    serverIP = sys.argv[1]
    serverPort = int(sys.argv[2])
    clientUDPport = int(sys.argv[3])
    client = Client(serverIP, serverPort, clientUDPport)
    client.beginning()
