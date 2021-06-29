from datetime import datetime
import threading


# Active user sequence number: timestamp: username: client IP address:client UDP server port number

def gettime():
    time = datetime.now()
    return time.strftime('%d %b %Y %H:%H:%S')


class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.clientIP = ''
        self.clientUDPport = 0
        self.is_blocked = False
        self.attempt_times = 0
        self.onlinetime = None

        self.is_online = False


class UserManagement:
    def __init__(self, max_attempt_times):
        self.max_attempt_times = max_attempt_times
        self.userListINorder = list()
        self.userDiction = dict()

        with open("credentials.txt", 'r') as f:
            for line in f.readlines():
                content = line.split('\n')[0].split()
                username = content[0]
                password = content[1]
                new_user = User(username, password)
                self.userDiction[username] = new_user

    def login(self, username, password, clientUDPport, clientIP):
        # if username not in userDiction
        if username not in self.userDiction:
            return 'B'
        user = self.userDiction[username]
        if user.is_online:
            return 'C'
        if user.is_blocked:
            return 'D'
        if password != user.password:
            user.attempt_times += 1
            if user.attempt_times >= self.max_attempt_times:
                user.is_blocked = True
                unblocked_threading = threading.Timer(10, self.unblocked, args=(username,))
                unblocked_threading.start()
            return ["E", user.attempt_times]
        self.userListINorder.append(username)
        user.is_online = True
        user.attempt_times = 0
        user.clientIP = clientIP

        user.clientUDPport = clientUDPport
        user.onlinetime = gettime()
        self.Writelog()
        return "A"

    def logout(self, username):
        user = self.userDiction[username]
        self.userListINorder.remove(username)
        user.clientIP = ''
        user.clientUDPport = 0
        user.is_blocked = False
        user.attempt_times = 0
        user.onlinetime = None
        user.clientSocket = False
        user.is_online = False
        self.Writelog()
        return 'success'

    def Writelog(self):
        with open("userlog.txt", 'w') as f:
            for order, username in enumerate(self.userListINorder):
                user = self.userDiction[username]
                # Active user sequence number: timestamp: username: client IP address:clientUDP
                if user.is_online:
                    line = '{}; {}; {}; {}; {}\n'.format(order+1,user.onlinetime,user.username,user.clientIP,user.clientUDPport)
                    f.write(line)


    def ATU(self, username):
        onlineList = list()
        for key in self.userDiction:
            user = self.userDiction[key]
            if user.is_online and user.username != username:
                onlineList.append([user.username, user.clientIP, user.clientUDPport,user.onlinetime])

        if onlineList:
            return ('success', onlineList)
        else:
            return ('False', onlineList)

    def unblocked(self, username):
        self.userDiction[username].is_blocked = False
        self.userDiction[username].attempt_times = 0
