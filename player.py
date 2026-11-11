import numpy as np
import cv2
import mss
from SelectROI import SelectROI
import time

class ZigZagPlayer:
    def __init__(self, cnf):
        self.debug_mode = cnf['debug_mode']

    def Feed(self, recording = None):
        if recording is None:
            with mss.mss() as sct:
                monitor = SelectROI(sct)

                while True:
                    if monitor:
                        frame = np.array(sct.grab(monitor))
                        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

                        yield frame

                        if cv2.waitKey(1) & 0xFF == ord('q'):
                            print('done')
                            break

                    else:
                        print('No feed')
                        continue



    def Play(self, frame, feed = None):
        start_time = time.perf_counter()

        # for frame in feed:
        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        ball_mask = cv2.inRange(frame_gray, 0, 70)

        contours, _ = cv2.findContours(ball_mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

        ball_contour = contours[0]
        for contour in contours:
            M = cv2.moments(contour)
            if 100 <= cv2.contourArea(contour) <= 160 and 290 <= (M["m01"] / M["m00"]) <= 300:
                ball_contour = contour

        blank = np.zeros(frame.shape, 'uint8') 
        frame_contoured = cv2.drawContours(blank, [ball_contour], -1, (255,0,0), 1)

        return frame, frame_gray, ball_mask, frame_contoured