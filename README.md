# ICN-Final-Project

RTSP RTP video streaming

## modeule installations

type the following command to install required modules  
`python -m pip install -r requirements.txt`

## videos

since sizes of videos are too large for github  
you may have to add those manually under the "videos" directory

the file are uploaded to the following link:  
https://drive.google.com/drive/folders/1u76WTNTrJL4REcyMdd30NiesyH3vWSXY

notions

if you want to add your own .mp4 file  
please put the file in ./server/videos along with its .mp3 file  
( mp4 to mp3 transform can be done by executing the file mp4_to_mp3.py in ./server )

after adding the required file to ./server/videos, please modify the FILE_LIST list in ./server/MainServer.py.

## SERVER

### How to start server

`cd server`  
under ./server  
`python MainServer.py`

## CLIENT

### How to start client

`cd client`  
under ./client  
`python MainClient.py`

ps. 初次啟動 PyQt5 介面可能會閃退，再次執行即可解決
