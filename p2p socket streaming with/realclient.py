import speech_recognition
import cv2
from threading import Thread
import socket
import tkinter
import time
import pickle
from PIL import Image
from functools import partial
import numpy as np
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
        print("reconnecting")


    def servicerequest(self,friend):
        
        self.s.sendall(str.encode(friend))                                                           #發送目標好友名        


    def waiting(self):

        while 1:

            message = self.s.recv(1024).decode()                                                #一方先當server做p2p連線
            print(message)
                
            if message == 'client':

                self.clientport = 11111
                self.serverport = 22222
                self.ip = self.s.recv(1024).decode()                                            #收到目標ip
                print(self.ip)
                self.ptopclient()
                self.ptopserver()
                self.video()
                break
                    
            elif message == 'server':

                self.clientport = 22222
                self.serverport = 11111
                self.ip = self.s.recv(1024).decode()                                            #收到目標ip
                print(self.ip)
                self.ptopserver()
                print('server open!')
                self.ptopclient()
                self.video()
                break

            else:
                
                time.sleep(1)
                continue
        

    def ptopserver(self):                                                                       #開啟接收端

        HOST,PORT = "",self.serverport
        self.pserver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.pserver.bind((HOST,PORT))
        self.pserver.listen(5)
        self.ssclient , address = self.pserver.accept()
        print(address)

                
    def ptopclient(self):                                                                       #開啟傳送端

        HOST,PORT = self.ip,self.clientport
        self.pclient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.pclient.connect((HOST,PORT))
        print('ptopconnect')
        

    def video(self):                                                                            #streaming

        
        
        def sndvideo():                                                                         #傳
            
            cap = cv2.VideoCapture(0)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH,400)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT,400)
            i=0
            minute=0
            sec=0
            clock = time.time()                                                               #計時
            resolution = 0                                                                      #解析度變數
            dev = 0
            estimate = 0.1                                                                      #設定的標準傳送秒數
            add = 0                                                                             #隨網路速度做視訊大小增減的變數(連續3包)
            sub = 0
            
            while cap.isOpened():
                
                ret, frame = cap.read()
                frame = cv2.medianBlur(frame, 5)                                            #影像處理 ,平滑
                kernel = np.array([[0,-1,0], [-1,5,-1], [0,-1,0]])                          #銳化kernel
                frame = cv2.filter2D(frame, -1, kernel)
                counter = time.time()-clock
                minute = int(counter/60)
                sec = int(counter%60)
                

                cv2.putText(frame, str(i), (0,50), cv2.FONT_HERSHEY_SIMPLEX,1,(34,195,46),1, cv2.LINE_AA)
                cv2.putText(frame, a, (100,250), cv2.FONT_HERSHEY_SIMPLEX,1,(34,195,46),1, cv2.LINE_AA)             
                cv2.imwrite('buffer.jpg',frame,[cv2.IMWRITE_JPEG_QUALITY, 22])
                                
                try:
                    
                    start = time.time()
                    with open('buffer.jpg','rb') as f:                
                        self.pclient.sendall(f.read())
                    
                    ack = self.pclient.recv(128)
                    sample = time.time()- start

                    #estimate = (1-0.125)*estimate + 0.125*sample
                    #dev = (1-0.25)*dev + 0.25*abs(sample - estimate)
                    timeout = estimate +4*dev

                    if sample < timeout - 0.05:                                                 #隨著偵測網路速度做視訊大小調整
                        add +=1
                        if(add >=5):
                            resolution += 10
                            cap.set(cv2.CAP_PROP_FRAME_WIDTH,400+resolution)
                            cap.set(cv2.CAP_PROP_FRAME_HEIGHT,400+resolution)

                    elif sample > timeout + 0.05:                                               #隨著網路速度做視訊大小調整
                        sub += 1
                        if(sub >=5):
                            resolution -= 10
                            cap.set(cv2.CAP_PROP_FRAME_WIDTH,400+resolution)
                            cap.set(cv2.CAP_PROP_FRAME_HEIGHT,400+resolution)

                    else:
                        add =0
                        sub =0
                                       
                    i+=1
                    
                except:
                    pass
                    
                
        def recvideo():

            while 1:                                                                    #讀取對方的視訊
     
                data = self.ssclient.recv(3000000)
                
                try:                                                                    #將接收的RGB陣列寫到jpg檔中再打開
                    
                    with open('save.jpg','wb') as f:
                        f.write(data)

                    try:
                        
                        cv2.imshow('hi',cv2.imread('save.jpg'))                         #顯示畫面
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


    def text(self):
        pass

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
