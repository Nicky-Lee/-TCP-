import socket
import threading
from datetime import datetime


def gettime():
    time = datetime.now()
    return time.strftime('%d %b %Y %H:%H:%S')


class Message:
    def __init__(self, username, message):
        self.username = username
        self.data = message
        self.is_edited = "no"
        self.timeStamp = gettime()


class MessageManagement:
    def __init__(self):
        self.MessageList = list()

    def add(self, username, message):
        new_message = Message(username, message)
        self.MessageList.append(new_message)
        self.Writelog()
        messageNumber = len(self.MessageList)
        message_lastModifyTime = new_message.timeStamp

        self.Writelog()
        return ("success", [messageNumber, message_lastModifyTime])

        pass

    def delete(self, username, messageNumber, message_LastModiyTime):
        if int(messageNumber) < len(self.MessageList):
            storageMessage = self.MessageList[int(messageNumber) - 1]
            storageTime = storageMessage.timeStamp

            if message_LastModiyTime == storageTime:
                if username == storageMessage.username:
                    message = storageMessage.data
                    self.MessageList.remove(storageMessage)
                    self.Writelog()
                    deletTime =gettime()
                    return ('success', [messageNumber, deletTime,message])
                return ('False, username error', [])
            return ('False, time error', [])
        return ('False, message number error.', [])

    def edite(self, username, messageNumber, original_timestamp, newMessage):
        if int(messageNumber) < len(self.MessageList):
            storageMessage = self.MessageList[int(messageNumber) - 1]
            storageTime = storageMessage.timeStamp
            if original_timestamp == storageTime:
                if username == storageMessage.username:
                    storageMessage.data = newMessage
                    storageMessage.timeStamp = gettime()
                    storageMessage.is_edited = "yes"
                    self.Writelog()
                    return ('success',[messageNumber,storageMessage.timeStamp])
                return ('False, username error',[])
            return ('False, time error',[])
        return ('False, message number error.',[])

    def read(self,timestamp):
        logList=list()
        timestamp = datetime.strptime(timestamp, "%d %b %Y %H:%M:%S")
        with open('messagelog.txt','r') as f:
            for log in f.readlines():
                content = log.split('\n')[0]
                logtime = datetime.strptime(content.split(';')[1], " %d %b %Y %H:%M:%S")
                if timestamp < logtime:
                    # #3 Obi-wan, Computer Network Rocks, edited at 23 Feb 2021 16: 01:10.
                    # #4 Obi-wan, IoT Rocks, posted at 23 Feb 2021 16: 01:30
                    # 1; 19 Feb 2021 21:39:10; yoda; do or do not; yes
                    messagenumber = '#'+content.split(';')[0]
                    time = content.split(';')[1]
                    username = content.split(';')[2]
                    message = content.split(';')[3]
                    edtYN = content[-1]
                    if edtYN=='yes':
                        logcontent = '{} , {}, {}, edited at {}.'.format(messagenumber,username,message,time)
                    else:
                        logcontent = '{} , {}, {}, posted at {}.'.format(messagenumber, username, message, time)
                    logList.append(logcontent)
        if len(logList):
            return ('success',logList)
        else:
            return ('False',['no message'])



    def Writelog(self):
        with open("messagelog.txt", 'w') as f:
            Messagenumber = 1
            # Messagenumber; timestamp; username; message; edited
            for i, message in enumerate(self.MessageList):
                line = '{}; {}; {}; {}; {}\n'.format(Messagenumber,message.timeStamp,message.username,message.data,message.is_edited)
                f.write(line)
                Messagenumber += 1
