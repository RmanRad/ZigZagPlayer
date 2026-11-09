import cv2
import numpy as np

def SelectROI(sct):
    screenshot = np.array(sct.grab(sct.monitors[1]))

    cv2.imshow('Select The ROI', screenshot)
    
    roi = cv2.selectROI('Select The ROI', screenshot)

    cv2.destroyWindow('Select The ROI')

    x, y, w, h = roi

    if w <= 100 and h <= 100:
        print('roi not valid')
        return

    return {'left': x, 'top': y, 'width': w, 'height': h}
    