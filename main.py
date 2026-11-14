from player import ZigZagPlayer
import cv2


Player1 = ZigZagPlayer()
# Player1.Play(Player1.Feed())


video = cv2.VideoCapture('AurigaTasks/ZigZagPlayer/Recording 2026-11-10 003117.mp4')

def read_video():
     while True:
        ret, frame = video.read()

        if not ret:
            break

        yield frame

Player1.Play(read_video())