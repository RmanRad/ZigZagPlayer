import numpy as np
import cv2, mss, time, pyautogui
from SelectROI import SelectROI


def coordinate(event, x, y, flag, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print(f'location {x,y}')



class ZigZagPlayer:
    def __init__(self):
        self.process_time = 0.001
        self.ball_cx = 155
        self.ball_cy = 295
        self.ball_contour = None
        self.velocity = 2500
        self.distance_buffer = [1000, 1000]
        self.lastframeclicked = False

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
            frame_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            frame_canny_s = cv2.Canny(frame_hsv[:, :, 1], 60, 120)

            _, frame_ball_t = cv2.threshold(frame_gray, 50, 255, cv2.THRESH_BINARY_INV)
            # frame_canny_and = cv2.bitwise_and(frame_canny, frame_ball_t, mask=None)

            contours, _ = cv2.findContours(frame_ball_t, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

            # find the ball
            ball_cx = self.ball_cx # past
            ball_cy = self.ball_cy # doesnt change
            ball_contour = self.ball_contour # np.array([[[(self.velocity * self.process_time, 0)]]], 'uint8') # predicted

            if contours is not None:
                for contour in contours:
                    M = cv2.moments(contour)
                    if (90 <= cv2.contourArea(contour) <= 100) and (280 <= M['m01'] / M['m00'] <= 320):
                        ball_contour = contour
                        # print(f'area : {cv2.contourArea(ball_contour)}')
                        ball_cx = M['m10'] / M['m00'] 
                        ball_cy = M['m01'] / M['m00']
                        break
        
            velocity = (ball_cx - self.ball_cx) / 0.001

            # set to the memory
            self.ball_cx = ball_cx
            self.ball_cy = ball_cy
            self.ball_contour = ball_contour
            self.velocity = velocity

            # draw the ball
            blank = np.zeros(frame.shape, 'uint8')
            frame_ball = cv2.drawContours(blank, [ball_contour], -1, (0,255,255), 1)
            cv2.putText(frame_ball, f'ball speed: {int(velocity)}px/sec', (2,15), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0,200,0), 1)

            angle = -26.5 if velocity > 0 else -153.5 # values I tested and found to be best
            angle_rad = np.deg2rad(angle)

            slope = np.tan(angle_rad)
            length = 500 if velocity > 0 else -500

            pt1 = (int(ball_cx), int(ball_cy + 8))
            pt2 = (int(ball_cx + length), int(ball_cy + (slope*length) + 8))

            frame = cv2.line(frame, pt1, pt2, (0,100,0), 3)

            if velocity > 0:
                x_range = range(pt1[0] + 10, frame.shape[1])
                
            else:
                x_range = range(pt1[0] - 10, -1, -1)

            x_intersection, y_intersection = pt2[0], pt2[1]
            for x in x_range:
                y = int(pt1[1] + (slope * (x - pt1[0])))
                if frame_canny_s[y,x] != 0 or frame_canny_s[y+1,x] != 0 or frame_canny_s[y-1,x] != 0:
                    x_intersection, y_intersection = x, y
                    break

            distance = np.linalg.norm([x_intersection - ball_cx, y_intersection - ball_cy])
            print(distance)

            if self.lastframeclicked == 1:
                self.lastframeclicked = 0

            if ((self.distance_buffer[0] + self.distance_buffer[1]*2 + distance*3)/6) <= 35 and self.lastframeclicked == 0:
                print('click')
                self.lastframeclicked += 1
                # self.velocity = -self.velocity
                pyautogui.click()

            self.distance_buffer[0] = self.distance_buffer[1]
            self.distance_buffer[1] = distance

            frame = cv2.line(frame, pt1, (x_intersection, y_intersection), (0,0,200), 2)

            self.process_time = time.perf_counter() - start_time

            cv2.imshow('frame', frame)
            cv2.imshow('ball', frame_ball)
            # cv2.imshow('canny', frame_canny_s)
            # cv2.imshow('canny_ball', frame_ball_t)

            cv2.setMouseCallback('frame', coordinate, frame)

            # if cv2.waitKey(0) & 0xFF == ord('n'):
            #     pass

            # if cv2.waitKey(100) & 0xFF == ord('q'):
            #     cv2.destroyAllWindows()
            #     break