import cv2
import mss
import numpy as np
from Solver import ZigZagPlayer

config = {
    'debug_mode': True
}

Player1 = ZigZagPlayer(config)

feed = Player1.Feed()

Player1.Play(feed)