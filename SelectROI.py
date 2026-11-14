import cv2
import numpy as np


def SelectROI(sct):
    blank = np.zeros((100, 500, 3), dtype=np.uint8)
    blank = cv2.putText(blank, 'Press S to select ROI', (10,50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (200,0,0), 2)
    cv2.imshow('Waiting for the call', blank)

    while True:
        if cv2.waitKey(1) & 0xFF == ord('s'):
            break

    cv2.destroyWindow('Waiting for the call')

    screenshot = np.array(sct.grab(sct.monitors[1]))

    cv2.imshow('Select The ROI', screenshot)
    
    roi = cv2.selectROI('Select The ROI', screenshot, False)

    cv2.destroyWindow('Select The ROI')

    x, y, w, h = roi

    if w <= 200 and h <= 200:
        print('roi too small to be valid')
        return

    return {'left': x, 'top': y, 'width': w, 'height': h}
    