import numpy as np
import cv2
import mss
from SelectROI import SelectROI
import time

class ZigZagPlayer:
    def __init__(self, cnf):
        self.debug_mode = cnf['debug_mode']

    def Feed(self):
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

    def Play(self, feed):
        start_time = time.perf_counter()
        
        for frame in feed:
            frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            frame_blur = cv2.GaussianBlur(frame_gray, (3,3), 0)
            frame_canny = cv2.Canny(frame_blur, 30, 120)

            kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (3,3))
            frame_closed = cv2.morphologyEx(frame_canny, cv2.MORPH_CLOSE, kernel, iterations=1)

            

            cv2.imshow('Live', frame_closed)

            fps = 1 / (time.perf_counter() - start_time)

        