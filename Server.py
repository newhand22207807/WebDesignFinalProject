from concurrent.futures import thread
import socket
import threading
import time

serverSockot = None
serverConnectionPool = []
backUppool = []
PORT = 8888
backlog = 5
BUF_SIZE = 1024
count = 0
playerOneReady = False
playerTwoReady = False

def init():
    # initial Server 

    global serverSockot
    # Create a TCP Server socket
    serverSockot = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

    # Bind on any incoming interface with PORT, '' is any interface
    serverSockot.bind(('127.0.0.1',PORT))

    # Listen incoming connecttion, connection number = backlog(5)
    serverSockot.listen(backlog)

def clientAccept():
    global serverConnectionPool,serverConnectionPoolBackup

    # 接收新連線
    while True:
        # Accept the imcoming connection
        client, (rip, rport) = serverSockot.accept()   
        # join to connection pool     
        serverConnectionPool.append(client)
        backUppool.append(client)
        # 開始執行
        newThread = threading.Thread(target=messageHandle, args=(client,len(serverConnectionPool)-1,))
        newThread.setDaemon(True)
        newThread.start()

def messageHandle(client, index):
    global playerOneReady,playerTwoReady,serverConnectionPool,count

    while True:
        while True:
            bytes = client.recv(BUF_SIZE)
            clientMsg = bytes.decode('UTF-8')
            if clientMsg == "1":
                if index == 0 :
                    playerOneReady = True
                    print("0 ok")       
                if index == 1 :
                    playerTwoReady = True
                    print("1 ok")
                break
        # waiting for else      
        while count % 2 != 0 and len(serverConnectionPool) < 2 or playerOneReady == False or playerTwoReady == False:
            pass
        time.sleep(1)
   
        clientMsgs = str(index)
        print("index :",str(index))
        serverConnectionPool[index].sendall(clientMsgs.encode('UTF-8'))
        
        # 消息處理
        while True:
            print(index,"waitting for message")
            bytes = client.recv(BUF_SIZE)
            print("客户端",index,"消息:", bytes.decode(encoding='utf8'))
            clientMsg = bytes.decode("UTF-8")
            
            # client遊戲結束，回傳重新開始
            if clientMsg == "-1":
                print("enter the reset")
                reSet(client)
                break
            # client 發出 surrender 
            if clientMsg == '1':
                serverConnectionPool[1].sendall(clientMsg.encode("UTF-8"))
                reSet(client)
                break
            if clientMsg == '0':
                serverConnectionPool[0].sendall(clientMsg.encode("UTF-8"))  
                reSet(client)
                break

            if index == 0:
                print("send to 1")
                serverConnectionPool[1].sendall(clientMsg.encode("UTF-8"))
            else:
                print("send to 0")
                serverConnectionPool[0].sendall(clientMsg.encode("UTF-8"))

            if clientMsg == "Error":
                print("有一個客戶端下線了")
                print(index," 刪除")
                if index == 0: playerOneReady = False
                if index == 1: playerTwoReady = False
                
                # close client
                client.close()
                # delete connection
                serverConnectionPool.remove(client)
                return
                            
def main():
    init()
    newThread = threading.Thread(target=clientAccept)
    newThread.setDaemon(True)
    newThread.start()
    while True:
        cmd = input("-------------------------\n輸入1: 請查看當前在線人數\n輸入2: 關閉伺服器端\n")
        if cmd == '1':
            print("----------------------------")
            print("當前在線人數: ",len(serverConnectionPool))
        elif cmd == '2':
            exit()       
        print("[playerOneReady,playerTwoReady,count]: ",playerOneReady,playerTwoReady,count)
    
def reSet(client):
    global serverConnectionPool, playerOneReady, playerTwoReady,count
    count += 1
    if backUppool.index(client) == 0:
        playerOneReady = False
    if backUppool.index(client) == 1:
        playerTwoReady  = False
    if count % 2 == 1:
        serverConnectionPool.clear()

if __name__ == "__main__":
    main()