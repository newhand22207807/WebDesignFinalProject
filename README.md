# 網路程式設計期末專題:五子棋  
## Client  
* Menu Screen  
  - [x] START : 開始遊戲
  - [x] EXIT : 離開遊戲
  - [ ] OPTION
* Menu Screen  
  - [x] Your Chess : 顯示你的棋子
  - [x] Your Turn : 顯示是否為你的回合
  - [x] Time Left : 下棋剩餘時間
  - [x] Surrender : 投降 
* End Screen
  - [x] MENU : 回到Menu畫面
  - [x] EXIT : 離開遊戲
  
## Server
## Bug
1. 發現重新開始後，如果不是按照當初的順序按下START，會造成兩方都是白棋的情況  
  已修正
2. 五秒未下，自動下有可能選到重覆位置時間會重新計算
  已修正
