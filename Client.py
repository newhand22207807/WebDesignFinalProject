############################################
# 2022/11/20
#
#
############################################
import pygame
import sys
import time
import numpy as np
import socket
import threading

# 棋盤 0,0(53,53) 到 19*19(647,647) 
# 圖片載入
# start 200*100
# exit  200*100
# options 300*100

goBoard         = pygame.image.load("c:\\Users\\User\\Desktop\\網路程式設計\\finalProject\\picture\\goBoard.png")
menuBackground  = pygame.image.load("c:\\Users\\User\\Desktop\\網路程式設計\\finalProject\\picture\\menuBackground.png")
startButton     = pygame.image.load("c:\\Users\\User\\Desktop\\網路程式設計\\finalProject\\picture\\start.png")
exitButton      = pygame.image.load("c:\\Users\\User\\Desktop\\網路程式設計\\finalProject\\picture\\exit.png")
optionsButton   = pygame.image.load("c:\\Users\\User\\Desktop\\網路程式設計\\finalProject\\picture\\options.png")
whiteChess      = pygame.image.load("c:\\Users\\User\\Desktop\\網路程式設計\\finalProject\\picture\\whiteChess.png")
blackChess      = pygame.image.load("c:\\Users\\User\\Desktop\\網路程式設計\\finalProject\\picture\\blackChess.png")
returnPic       = pygame.image.load("c:\\Users\\User\\Desktop\\網路程式設計\\finalProject\\picture\\return.png")
waitingForP     = pygame.image.load("c:\\Users\\User\\Desktop\\網路程式設計\\finalProject\\picture\\waitingForPlayer.png")
menu            = pygame.image.load("c:\\Users\\User\\Desktop\\網路程式設計\\finalProject\\picture\\menu.png")
# 變數
currentScene = "menuScene" 
currentPlayer = 1 # 1 : black, 0 : white
latestX=-1
latestY=-1 
BUF_SIZE = 1024
# 棋盤
board = np.zeros((18,18))
regard = np.zeros((18,18))

# 棋子位置 
chessX = np.linspace(53,647,19)
chessY = np.linspace(53,647,19)

# 黑跟白棋的 - | / \ quantity
blackQuantity = [0,0,0,0]
whiteQuantity = [0,0,0,0]
condition = [] # 儲存棋盤上黑跟白數量 [[3,0],...]

# 當前狀況
waitingForElse = False

# pygame 初始化
pygame.init()
pygame.font.init()
fontSize50 = pygame.font.SysFont("Arial",50)
fontSize100 = pygame.font.SysFont("Arial",100)
windowSurface = pygame.display.set_mode((1200,700))
pygame.display.set_caption("Client")

# create socket
client = ""
def createSocket():
    global client
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('127.0.0.1', 8888))

def createScene():
    global currentScene
    if currentScene == "menuScene":
        menuScene()
    elif currentScene == "optionScene":
        optionScene()
    elif currentScene == "wait":
        wait()
    elif currentScene == "playerScene":
        playerScene()
    elif currentScene == "winScene":
        winScene()
    elif currentScene == "loseScene":
        loseScene()

def findWinner(x,y,k,l):
    # x,y : 座標  k : 黑或白棋  l : 4個方向計算 
    global regard,blackQuantity,whiteQuantity
    if(x < 0 or y < 0 or x >= np.size(board,0) or y >= np.size(board,1) or board[x][y] != k or regard[x][y] == 1): return
    if k == 1: blackQuantity[l] += 1
    if k == 2: whiteQuantity[l] += 1

    regard[x][y] = 1
    if l == 0: findWinner(x,y-1,k,l)  ,findWinner(x,y+1,k,l)
    if l == 1: findWinner(x+1,y,k,l)  ,findWinner(x-1,y,k,l)
    if l == 2: findWinner(x+1,y+1,k,l),findWinner(x-1,y-1,k,l)
    if l == 3: findWinner(x+1,y-1,k,l),findWinner(x-1,y+1,k,l)

def find():
    global regard,condition
    for i in range(18):
        for j in range(18):
            initialValue()
            # 四個方向
            for k in range(4):
                # 黑跟白棋
                for l in range(1,3):
                    # 因為每一個方向要計算時要先把初始點歸零否則算完第一個方向後會無法再算其他方向
                    regard[i][j] = 0
                    findWinner(i,j,l,k) 

            temp = [max(blackQuantity),max(whiteQuantity)]
            condition.append(temp)   

    for i in range(len(condition)):
        theMax = max(condition[i])
        if theMax >= 5:
            return condition[i].index(theMax) + 1
    return 0

def initialValue():
    global regard,blackQuantity,whiteQuantity
    for i in range(18):
        for j in range(18):
            regard[i][j] = 0
    for i in range(4):
        blackQuantity[i] = 0
        whiteQuantity[i] = 0
    
def menuScene():
    try:
        windowSurface.fill((255,255,255))
        windowSurface.blit(menuBackground,(0,0))
        windowSurface.blit(startButton,(910,100))
        windowSurface.blit(exitButton,(890,200))
        windowSurface.blit(optionsButton,(900,300))
        pygame.display.update()
    except:
        print("enter menuscene error")
        errorMessage()
def optionScene():
    windowSurface.fill((255,255,255))
    windowSurface.blit(returnPic,(25,625))
    pygame.display.update()

def wait():
    global currentScene,currentPlayer,waitingForElse,client
    createSocket()
    try:
        windowSurface.fill((255,255,255))
        windowSurface.blit(waitingForP,(200,250))
        pygame.display.update()

        # 阻塞 發送消息 直到回應遊戲
        data = "1"
        data = data.encode('utf-8')
        client.sendall(data)   
        # 接收server的反饋數據
        while True:
                print("RECEIVE...")
                msg = client.recv(BUF_SIZE).decode(encoding='utf8')
                print(msg)
                if msg=="0":
                    print('game Start:',msg)
                    break
                else:
                    currentPlayer = 0
                    waitingForElse = True
                    break
        # 場景切換
        currentScene="playerScene"

        # 綁定二號先收訊息
        if not currentPlayer:
            print("not currentplayer------")
            #第一次消息
            print("first message")
            thread = threading.Thread(target = firstMessage)
            thread.start()
    except:
        print("enter menuscene error")
        errorMessage()    
def playerScene():
    try:
        global chessX,chessY,board

        windowSurface.fill((255,255,255))
        windowSurface.blit(goBoard,(0,0))

        TextYourChess = fontSize50.render("You Chess:",True,(0,0,0))
        windowSurface.blit(TextYourChess,(750,0))

        if currentPlayer:
            windowSurface.blit(blackChess,(980,20))
        else:
            windowSurface.blit(whiteChess,(980,20))

        # 把棋子填上去
        for i in range(18):
            for j in range(18):
                if board[j][i] == 1:
                    windowSurface.blit(blackChess,(chessX[i],chessY[j]))
                if board[j][i] == 2:
                    windowSurface.blit(whiteChess,(chessX[i],chessY[j]))

        if waitingForElse:
            titleText=fontSize50.render("Not Your Turn", 1, (0, 0, 0)) 
            windowSurface.blit(titleText,(750,200))
        else:
            titleText=fontSize50.render("Your Turn", 1, (255,0,0)) 
            windowSurface.blit(titleText,(750,200))    
        pygame.display.update()
    except:
        errorMessage()
def winScene():
    windowSurface.fill((255,255,255))
    text = fontSize100.render("YOU WIN......",True,(0,0,0))
    windowSurface.blit(text,(400,200))
    windowSurface.blit(exitButton,(300,400))
    windowSurface.blit(menu,(700,420))
    pygame.display.update()
       
    restartGame()
def loseScene():
    windowSurface.fill((255,255,255))
    titleText=fontSize100.render("YOU LOSE......", True, (0,255,255))
    windowSurface.blit(titleText,(300,200))
    windowSurface.blit(exitButton,(300,400))
    windowSurface.blit(menu,(700,420))
    pygame.display.update()    
    restartGame()
def exit():
    print("exit")
    errorMessage()
def restartGame():
    global board,regard,condition,waitingForElse,currentPlayer
    for i in range(18):
        for j in range(18):
            board[i][j] = 0
            regard[i][j] = 0
    condition.clear()
    initialValue()
    currentPlayer = 1
    waitingForElse = False

def errorMessage():
    global client
    msg = "Error"
    msg = msg.encode('utf-8')
    client.sendall(msg)
    pygame.quit()
    sys.exit()
   
def sendMessage(data):
    try:
        global waitingForElse,client,latestX,latestY
        waitingForElse = True
        data = data.encode('utf-8')
        client.sendall(data)

        # 接收server的反饋數據
        while True:
            rec_data = client.recv(BUF_SIZE).decode(encoding='utf8')
            if len(rec_data)>=3:
                rec_data=rec_data.split()

                latestX=int(rec_data[0])
                latestY=int(rec_data[1])
                if currentPlayer:
                    board[int(rec_data[0]),int(rec_data[1])]=2
                else:
                    board[int(rec_data[0]),int(rec_data[1])]=1
                break
        waitingForElse=False
    except:
        errorMessage()
    
def firstMessage():
    try:
        global waitingForElse
        while True:
            print("i am waiting for the first message")
            rec_data = client.recv(BUF_SIZE).decode(encoding='utf8')
            print(rec_data)
            if len(rec_data)>=3:
                rec_data=rec_data.split()
                # 接收server的反饋數據
                if currentPlayer:
                    board[int(rec_data[0]),int(rec_data[1])]=2
                else:
                    board[int(rec_data[0]),int(rec_data[1])]=1
                break

        waitingForElse=False
    except:
        errorMessage()

def changeCoordinate(x,y):
    # ex : [x,y] = [58,130]
    indexX = -1
    indexY = -1
    for i in range(18):
        if x >= chessX[i] and x <= chessX[i+1]:
            indexY = i
        if y >= chessY[i] and y <= chessY[i+1]:
            indexX = i             
    return indexX,indexY 

def buttonEvent(x,y):  
    try:
        global currentScene,waitingForElse,client
        print("[x,y] : ",x,",",y)
        print("currentscene: ",currentScene)
        if (currentScene == "menuScene" 
            and x >= 910 and x <= startButton.get_width()  + 910 
            and y >= 120 and y <= startButton.get_height() + 80):
            print("enter button start")
            currentScene = "wait"
        elif (currentScene == "menuScene" 
            and x >= 910 and x <= exitButton.get_width()  + 850  
            and y >= 220 and y <= exitButton.get_height() + 180):
            print("enter button exit")
            exit()
        elif (currentScene == "menuScene"  
            and x >= 900 and x <= optionsButton.get_width()  + 900  
            and y >= 320 and y <= optionsButton.get_height() + 280):
            currentScene = "optionScene"
            print("show option")
        elif (currentScene == "optionScene" 
            and x >= 25 and x <= returnPic.get_width() + 25  
            and y >= 625 and y <= returnPic.get_height() + 625):
            currentScene = "menuScene"
        elif ((currentScene == "winScene" or currentScene == "loseScene")
            and x >= 320 and x <= exitButton.get_width() + 260
            and y >= 420 and y <= exitButton.get_height() + 380):
            exit()
        elif ((currentScene == "winScene" or currentScene == "loseScene")
            and x >= 700 and x <= menu.get_width()  + 700
            and y >= 420 and y <= menu.get_height() + 420):
            # server 端表示為重新開始
            msg = "-1"
            msg = msg.encode('utf-8')
            client.sendall(msg)
            currentScene = "menuScene"
            restartGame()
        elif currentScene == "playerScene" and not waitingForElse: # 下棋介面
            i,j = changeCoordinate(x,y)
            if i != -1 and j != -1 and board[i,j] == 0:
                waitingForElse=True
                msg=str(i)+" "+str(j)
                print(msg)
                thread = threading.Thread(target = sendMessage,args = (msg,))
                thread.start()

                if currentPlayer: board[i,j] = 1    
                else: board[i,j] = 2  
    except:
        errorMessage()

def main():
    global currentScene
    try:
        while True:
            # 迭代整個事件迴圈，若有符合事件則對應處理
            for event in pygame.event.get():
                # 當使用者結束視窗，程式也結束
                if event.type == pygame.QUIT:
                    errorMessage()
                # 點擊
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # 取得滑鼠位置
                    x, y = pygame.mouse.get_pos()
                    buttonEvent(x,y)
            result = find()    
            if result != 0:
                if (result == 1 and currentPlayer) or (result == 2 and not currentPlayer): 
                    currentScene ="winScene"
                else: currentScene="loseScene"

            createScene()
    except:
        errorMessage()

if __name__ == "__main__":
    main()