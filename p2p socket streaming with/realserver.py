import socket
from threading import Thread
import pickle
#import time

global person
global ipset

person = dict()                                                     #會員的socket,name陣列
ipset = dict()                                                      #記錄會員socket ip的變數

with open('database.txt','r') as f:                                 #讀取database 會員資料
    
    global database
    database = f.readlines()



def listen(i):                                                      #對外預設port,做認證與重新導向

    HOST,PORT = "",12345
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    print('waiting')
    s.listen(5)

    while 1:
        
        client, address = s.accept()
        global ip
        print(address[0])                                           #記錄用戶ip
        ip = address[0]
        
        message = client.recv(1024).decode()                        #接受客戶端帳密做認證

        if message in database:                                     #認證完傳PORT給他
            
            global name                                             #會員帳號當辨識名稱
            name = message
            print('accept')
            client.send( str.encode(str(i)) )                       #傳送指定port給客戶端
            client.close()
            break

        else:                                                       #無效帳號

            client.send( str.encode('invalid') )
            print('invalid')
            client.close()
            
    return 


def creatconnection(HOST,port):                                     #動態的creat一個socket

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, port))
    s.listen(5)
    client , address = s.accept()

    client.sendall(pickle.dumps(database))                          #傳送資料庫中其他會員資料

    return client


def mutilistening(name):                                          #持續監聽,如果有好友請求

    while 1:

        dst = person[name].recv(1024).decode()                      #等待接受各用戶的請求
        print('action received')
        print(name+dst)
        
        if dst in database:                                         #name請求與dst做p2p連線
            
            print('exchanging')
            person[name].sendall(str.encode('client'))
            person[dst].sendall(str.encode('server'))
            person[name].sendall(str.encode(ipset[dst]))                    #發給雙方ip使他們可連線
            person[dst].sendall(str.encode(ipset[name]))
            break
    

def mainloop():

    i = 10000
        
    while 1:
        
        if i != 12345 and i != 11111 and i != 22222:
            
            listen(i)                                                   #listening
            person[name] = creatconnection( "" , i )                    #重新導向,新的instance
            ipset[name] = ip
            listening = Thread( target = lambda : mutilistening(name) )                      #開始持續監聽
            listening.start()

        i+=1



if __name__ == '__main__':
            
    main = Thread(target = mainloop)
    main.start()
