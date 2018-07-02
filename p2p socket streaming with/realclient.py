import speech_recognition
import cv2
from threading import Thread
from threading import Lock
import socket
import tkinter
import time
import pickle
from PIL import Image
from functools import partial
import numpy as np
from tkinter import *
import tkinter.messagebox
from random import randint

lock = Lock()
DANMU=list()
a=''

class menu:
    
    def __init__(self):

        self.person = list()
        self.root = tkinter.Tk()                                                                    #主GUI介面
        self.root.title("menu")
        self.root.maxsize(500,500)
        self.root.minsize(500,500)
        self.img = tkinter.PhotoImage(file = 'bufferfish.gif')  
        self.label_img = tkinter.Label(self.root, image = self.img)
        self.label_img.pack()
        self.label_account = tkinter.Label(self.root , text = "\nアカウント：" , fg="green" , font=('',17) )
        self.label_account.pack()
        self.account = tkinter.Entry(self.root , font=('',14) )
        self.account.pack()
        self.label_password = tkinter.Label(self.root , text = "パスワード：" ,  fg="green" , font=('',17) , width=15, height=2 )
        self.label_password.pack()
        self.password = tkinter.Entry(self.root , font=('',14) , show = 'Y')
        self.password.pack()        
        self.enter = tkinter.Button(self.root,command = self.login,text = "Log in" ,  fg="blue" , font=('Arial',20) )
        self.enter.pack() 
        self.about = tkinter.Label(self.root , text = "\n:::駝客記事:::臺北市立建國高級中學--首頁" )
        self.about.pack()
        self.root.mainloop()
        
    
    def login(self):                                                                                #連線到伺服器

        if self.connect( self.account.get() , self.password.get() ):                                #跳轉好友視窗
                    
            self.label_img.destroy()
            self.about.destroy()
            self.label_account.destroy()
            self.label_password.destroy()
            self.enter.destroy()
            self.password.destroy()
            self.account.destroy()

            database = pickle.loads(self.s.recv(2048))

            for friend in database:                                                                 #初始化好友列表

                self.person.append( tkinter.Label( self.root , text = '\n'+friend[:-1], font=('',16) ) )
                action = partial( self.servicerequest , friend )
                self.person.append( tkinter.Button( self.root ,command = action, text = '戳他' , fg="red" , font=('Arial',17) ) )

            for i in range(2*len(database)):
                self.person[i].pack()

            self.XD = tkinter.Checkbutton( self.root , text = "\n我已滿18歲\n" , font=('',12) ).pack()
            self.logout = tkinter.Button( self.root , command = self.exitquit , text = '登出' , fg="green" , font=('',24) ,  ).pack()

            Thread(target = self.waiting).start()                                                   #持續監聽伺服器訊息

        else:
            
            self.about['text'] = "無效的使用者"

        
    def connect( self , account , password ):                                                         #連線到伺服器

        HOST,PORT = "104.199.242.20",12345
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((HOST, PORT))
        print("verifying")
        self.s.sendall(str.encode(account+password+'\n'))                                              #傳送帳密道伺服器

        result = self.s.recv(1024).decode()                                                         #伺服器的認證訊息

        if result == 'invalid':                                                                         #伺服器表示密碼錯誤

            print('invalid')

            return False

        else:

            self.s.close()

            self.redirect(int(result))                                                          #重新連接到伺服器指定PORT
            
            return True


    def redirect(self,port):                                                                    #伺服器重新導向到穩定連線

        HOST,PORT = "104.199.242.20",port
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((HOST, PORT))
        print("reconnecting...")


    def servicerequest(self,friend):
        
        self.s.sendall(str.encode(friend))                                                           #發送目標好友名
        

    def chatroom(self):
        

        def sndtext():
            
            sentence = self.type.get()
            self.text.insert(INSERT,"You:"+ sentence +"\n")
            self.textclient.sendall( str.encode( sentence ) )
            self.type['text']=''
            print(sentence)
        
        self.chat = tkinter.Tk()
        self.text=Text(self.chat)
        self.text.pack()
        self.type = tkinter.Entry(self.chat , font=('',14) )
        self.type.pack()
        self.send = tkinter.Button(self.chat , command = sndtext , text = "Send" ,  fg="blue" , font=('Arial',20) )
        self.send.pack()

        def recvtext():

            while 1:

                global DANMU
                sentence = self.ttclient.recv(1024).decode()
                DANMU.append([sentence,0,randint(100,400)])
                        
                print(sentence)

                self.text.insert(INSERT , "object:"+ sentence +"\n")
        
        Thread(target = recvtext).start()
        
        self.chat.mainloop()

        


    def waiting(self):

        while 1:

            message = self.s.recv(1024).decode()                                                #一方先當server做p2p連線
            print(message)

            tkinter.messagebox.askquestion("DX"," a r e  y o u  s u r e    D: ?")
                
            if message == 'client':

                self.clientport = 11111
                self.serverport = 22222
                self.tclientport = 33333
                self.tserverport = 44444
                self.ip = self.s.recv(1024).decode()                                            #收到目標ip
                print(self.ip)
                self.ptopclient()
                self.ptopserver()
                self.video()
                self.chatroom()
                break
                    
            elif message == 'server':

                self.clientport = 22222
                self.serverport = 11111
                self.tclientport = 44444
                self.tserverport = 33333
                self.ip = self.s.recv(1024).decode()                                            #收到目標ip
                print(self.ip)
                self.ptopserver()
                print('server open!')
                self.ptopclient()
                self.video()
                self.chatroom()
                break

            else:
                
                time.sleep(1)
                continue
        

    def ptopserver(self):                                                                       #開啟接收端

        self.pserver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.pserver.bind(("",self.serverport))
        self.pserver.listen(5)
        self.ssclient , address = self.pserver.accept()
        print(str(address) +"has connect")
        
        self.textserver =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.textserver.bind(("",self.tserverport))
        self.textserver.listen(5)
        self.ttclient , address = self.textserver.accept()
        print("text requested")
        
                
    def ptopclient(self):                                                                       #開啟傳送端

        self.pclient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.pclient.connect((self.ip,self.clientport))
        print('ptopconnect to ')

        self.textclient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.textclient.connect((self.ip,self.tclientport))
        print("text connected")
        
                

    def video(self):                                                                            #streaming

        
        
        def sndvideo():                                                                         #傳

            global a
            cap = cv2.VideoCapture(0)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH,450)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT,450)
                                                                           
            resolution = 0                                                                      #解析度變數
            dev = 0
            estimate = 0.1                                                                      #設定的標準傳送秒數
            add = 0                                                                             #隨網路速度做視訊大小增減的變數(連續3包)
            sub = 0
            count = 0
            
            while cap.isOpened():
                
                ret, frame = cap.read()
                
                cv2.putText(frame, a, (100,250), cv2.FONT_HERSHEY_SIMPLEX,1,(0,71,171),2, cv2.LINE_AA)             
                cv2.imwrite('buffer.jpg',frame,[cv2.IMWRITE_JPEG_QUALITY, 25])

                if count > 30:
                    count = 0
                    a=''

                else:

                    count+=1
                                
                try:
                    
                    start = time.time()
                    with open('buffer.jpg','rb') as f:                
                        self.pclient.sendall(f.read())
                    
                    ack = self.pclient.recv(128)
                    sample = time.time()- start

                    #estimate = (1-0.125)*estimate + 0.125*sample
                    #dev = (1-0.25)*dev + 0.25*abs(sample - estimate)
                    timeout = estimate +4*dev

                    '''if sample < timeout - 0.07:                                                 #隨著偵測網路速度做視訊大小調整
                        add +=1
                        if(add >=5):
                            resolution += 10
                            cap.set(cv2.CAP_PROP_FRAME_WIDTH,400+resolution)
                            cap.set(cv2.CAP_PROP_FRAME_HEIGHT,400+resolution)

                    elif sample > timeout + 0.07:                                               #隨著網路速度做視訊大小調整
                        sub += 1
                        if(sub >=5):
                            resolution -= 10
                            cap.set(cv2.CAP_PROP_FRAME_WIDTH,400+resolution)
                            cap.set(cv2.CAP_PROP_FRAME_HEIGHT,400+resolution)

                    else:
                        add =0
                        sub =0'''
                                       
                    
                except:
                    pass
                    
                
        def recvideo():

            global lock
            kernel = np.array([[0,-1,0], [-1,5,-1], [0,-1,0]])
            i=0
            minute=0
            sec=0
            clock = time.time()                                                         #計時
            sliding = 0                                                                 #彈幕滑動

            while 1:                                                                    #讀取對方的視訊
                     
                data = self.ssclient.recv(3000000)
                
                try:                                                                    #將接收的RGB陣列寫到jpg檔中再打開
                    
                    with open('save.jpg','wb') as f:
                        f.write(data)

                    try:
                        
                        global frame
                        frame = cv2.imread('save.jpg')
                        #frame = cv2.medianBlur(frame, 5)  
                        #frame = cv2.filter2D(frame, -1, kernel)
                        counter = int (time.time()-clock)
                        minute = int (counter/60)
                        sec = int (counter%60)

                        for e in DANMU:
        
                            e[1] += 10
                            cv2.putText(frame, e[0], (550-e[1],e[2]), cv2.FONT_HERSHEY_SIMPLEX,2,(34,195,46),1, cv2.LINE_AA)

                            if e[1] == 550:
                                DANMU.pop(0)

                        cv2.putText(frame, str(minute) + ':' + str(sec), (0,86), cv2.FONT_HERSHEY_SIMPLEX,2,(34,195,46),1, cv2.LINE_AA)
                        cv2.putText(frame, str(i), (0,40), cv2.FONT_HERSHEY_SIMPLEX,2,(34,195,46),1, cv2.LINE_AA)
                        
                        cv2.imshow('hi',frame)                                          #顯示畫面

                        i+=1
                        
                        if cv2.waitKey(1) & 0xFF == ord('q'):
                            break
                            
                    except:
                             
                        data = self.ssclient.recv(6000000)                              #傳送中出現錯誤,清空buffer
                        print(":(")
                        
                except:
                    pass
                    
                self.ssclient.sendall(str.encode('ack'))                                   #回傳給伺服器說收到了
                
                    
        Thread(target = sndvideo).start()                                                #start streaming
        Thread(target = recvideo).start()
        Thread(target = recognition).start()                                            #語音辨識


    def exitquit(self):

        self.s.sendall(str.encode('close'))
        self.s.close()
        self.root.destroy()

        
def recognition():

    r = speech_recognition.Recognizer()
    with speech_recognition.Microphone() as source:        
        while 1:
            r.adjust_for_ambient_noise(source) 
            print("Say something!")
            audio=r.listen(source)
            try:
                global a
                a = r.recognize_google(audio)
                print(a)
            except speech_recognition.UnknownValueError:
                print("oops")


if __name__ == "__main__" :
    menu=menu()
