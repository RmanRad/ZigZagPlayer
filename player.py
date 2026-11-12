import numpy as np
import cv2, mss, time, pyautogui
from SelectROI import SelectROI

class ZigZagPlayer:
    def __init__(self, cnf):
        self.debug_mode = cnf['debug_mode']
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
            frame_canny = cv2.Canny(frame, 60, 150)

            contours, _ = cv2.findContours(frame_canny, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

            ball_cx = self.ball_cx + (self.velocity * self.process_time)
            ball_cy = self.ball_cy
            ball_contour = self.ball_contour
            if contours is not None:
                for contour in contours:
                    M = cv2.moments(contour)
                    if (200 <= cv2.contourArea(contour) <= 260) and (285 <= M['m01'] / M['m00'] <= 315):
                        ball_contour = contour
                        ball_cx = M['m10'] / M['m00'] if M['m00'] > 0 else 155
                        ball_cy = M['m01'] / M['m00'] if M['m00'] > 0 else 295
                        print('found ball')
                        break

        
            velocity = (ball_cx - self.ball_cx) / self.process_time

            self.ball_cx = ball_cx
            self.ball_cy = ball_cy
            self.ball_contour = ball_contour
            self.velocity = velocity

            blank = np.zeros(frame.shape, 'uint8')
            frame_ball = cv2.drawContours(blank, [ball_contour], -1, (0,255,255), 1)
            cv2.putText(frame_ball, f'ball speed: {int(velocity)}px/sec', (2,15), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0,200,0), 1)

            angle = -26.5 if velocity > 0 else -153.5 # values I tested and found to be best
            angle_rad = np.deg2rad(angle)

            slope = np.tan(angle_rad)
            length = 500 if velocity > 0 else -500

            pt1 = (int(ball_cx), int(ball_cy + 10))
            pt2 = (int(ball_cx + length), int(ball_cy + (slope*length) + 10))
            # print(f'point1 : {pt1}, point2: {pt2}')

            frame_trajectory = cv2.line(frame, pt1, pt2, (0,100,0), 3)

            if velocity > 0:
                x_range = range(pt1[0] + 10, frame.shape[1])
            else:
                x_range = range(pt1[0] - 10, -1, -1)

            x_intersection, y_intersection = pt2[0], pt2[1]
            for x in x_range:
                y = int(pt1[1] + (slope * (x - pt1[0])))
                if frame_canny[y,x] != 0 or frame_canny[y+1,x] != 0 or frame_canny[y-1,x] != 0:
                    x_intersection, y_intersection = x, y
                    break

            # print(f'intersection: {x_intersection, y_intersection}')

            distance = np.linalg.norm([x_intersection - ball_cx, y_intersection - ball_cy])
            # print(distance)


            if ((self.distance_buffer[0] + self.distance_buffer[1]*2 + distance*3)/6) <= 30 and not self.lastframeclicked:
                print('click')
                self.lastframeclicked = True
                pyautogui.click()

            else:
                self.lastframeclicked = False

            self.distance_buffer[0] = self.distance_buffer[1]
            self.distance_buffer[1] = distance
            

            frame_trajectory = cv2.line(frame_trajectory, pt1, (x_intersection, y_intersection), (0,0,200), 2)

            self.process_time = time.perf_counter() - start_time

            # cv2.imshow('result1', frame)
            cv2.imshow('result2', frame_ball)
            # cv2.imshow('result3', frame_canny)
            # cv2.imshow('result4', frame_trajectory)