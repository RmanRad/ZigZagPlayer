import numpy as np
import cv2
import mss
from SelectROI import SelectROI


class ZigZagPlayer:
    def __init__(self, cnf):
        self.debug_mode = cnf['debug_mode']
        # self.frame = None

    def Play(self):
        with mss.mss() as sct:
            monitor = SelectROI(sct)

            if monitor is not None:
                while True:
                    frame = np.array(sct.grab(monitor))
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

                    cv2.imshow('Live', frame)

                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break