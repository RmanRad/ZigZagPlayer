import numpy as np
import cv2
import mss
from SelectROI import SelectROI


class ZigZagPlayer:
    def __init__(self, cnf):
        self.debug_mode = cnf['debug_mode']

    def Feed(self):
        with mss.mss() as sct:
            monitor = SelectROI(sct)

            while True:
                if monitor is not None:
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
        for frame in feed:
            
            pass

            cv2.imshow('Live', frame)

        