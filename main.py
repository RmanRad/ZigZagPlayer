from player import ZigZagPlayer
import cv2

config = {
    'debug_mode': True
}

# def _on_mouse(event, x, y, flags, param):
#     if event == cv2.EVENT_LBUTTONDOWN:
#         print(f"clicked: x={x}, y={y}, or {x/frame.shape[1], y/frame.shape[0]}")

Player1 = ZigZagPlayer(config)

# video = cv2.VideoCapture('AurigaTasks/ZigZagPlayer/Recording 2026-11-10 003117.mp4')

# while True:
#     ret, frame = video.read()

#     if ret:
#         result1, result2, result3, result4, result5 = Player1.Play(frame)
#         cv2.imshow('result1', result1)
#         cv2.imshow('result2', result2)
#         cv2.imshow('result3', result3)
#         cv2.imshow('result4', result4)
#         cv2.imshow('result5', result5)

#         cv2.setMouseCallback('result3', _on_mouse, frame)

#     if cv2.waitKey(0) & 0xFF == ord('n'):
#         pass

#     if cv2.waitKey(100) & 0xFF == ord('q'):
#         cv2.destroyAllWindows()
#         break



Player1.Play(Player1.Feed())