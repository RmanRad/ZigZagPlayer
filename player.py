import numpy as np
import cv2, mss, time, pyautogui
from SelectROI import SelectROI


def coordinate(event, x, y, flag, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print(f'location {x,y}')



def location(event, x, y, flag, param):
    if event == cv2.EVENT_RBUTTONDOWN:
        print(f'coordinates: {x, y} or {x/param.shape[1], y/param.shape[0]}')

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
        # fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        # fps = 30

        # width = 800  # replace with your actual frame width
        # height = 600 # replace with your actual frame height

        # out = cv2.VideoWriter('recording.mp4', fourcc, fps, (width, height))

        for frame in feed:
            frame_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            frame_canny = cv2.Canny(frame, 60, 150)
            frame_canny_s = cv2.Canny(frame_hsv[:, :, 1], 60, 120)
            frame_canny_and = cv2.bitwise_and(frame_canny, frame_canny_s)

            contours, _ = cv2.findContours(frame_canny, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

            # find the ball
            ball_cx = self.ball_cx + (self.velocity * self.process_time) # prediction
            ball_cy = self.ball_cy # doesnt change
            ball_contour = self.ball_contour # np.array([[[(self.velocity * self.process_time, 0)]]], 'uint8') # predicted
            ball_cx = self.ball_cx # prediction
            ball_cy = self.ball_cy # doesnt change
            ball_contour = self.ball_contour # np.array([[[(self.velocity * self.process_time, 0)]]], 'uint8') # predicted

            if contours is not None:
                for contour in contours:
                    M = cv2.moments(contour)
                    if (200 <= cv2.contourArea(contour) <= 220) and (280 <= M['m01'] / M['m00'] <= 320):
                        ball_contour = contour
                        print(f'area : {cv2.contourArea(ball_contour)}')
                        ball_cx = M['m10'] / M['m00'] if M['m00'] > 0 else 155
                        ball_cy = M['m01'] / M['m00'] if M['m00'] > 0 else 295
                        break

        
            velocity = (ball_cx - self.ball_cx) / self.process_time

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

            frame_trajectory = cv2.line(frame_ball, pt1, pt2, (0,100,0), 3)
            frame_trajectory_2 = cv2.line(frame, pt1, pt2, (0,100,0), 3)
            frame = cv2.line(frame, pt1, pt2, (0,100,0), 3)

            if velocity > 0:
                x_range = range(pt1[0] + 10, frame.shape[1])
            else:
                x_range = range(pt1[0] - 10, -1, -1)

            x_intersection, y_intersection = pt2[0], pt2[1]
            for x in x_range:
                y = int(pt1[1] + (slope * (x - pt1[0])))
                if frame_canny_and[y,x] != 0 or frame_canny_and[y+1,x] != 0 or frame_canny_and[y-1,x] != 0:
                    x_intersection, y_intersection = x, y
                    break

            distance = np.linalg.norm([x_intersection - ball_cx, y_intersection - ball_cy])
            print(distance)

            if ((self.distance_buffer[0] + self.distance_buffer[1]*2 + distance*3)/6) <= 35 and not self.lastframeclicked:
                print('click')
                self.lastframeclicked = True
                self.velocity = -self.velocity
                pyautogui.click()
                # self.velocity = -self.velocity
                # pyautogui.click()

            else:
                self.lastframeclicked = False

            self.distance_buffer[0] = self.distance_buffer[1]
            self.distance_buffer[1] = distance
            

            frame_trajectory = cv2.line(frame_trajectory, pt1, (x_intersection, y_intersection), (0,0,200), 2)
            frame_trajectory_2 = cv2.line(frame_trajectory, pt1, (x_intersection, y_intersection), (0,0,200), 2)
            frame = cv2.line(frame, pt1, (x_intersection, y_intersection), (0,0,200), 2)

            self.process_time = time.perf_counter() - start_time

            # cv2.imshow('result1', frame)
            cv2.imshow('result2', frame_ball)
            # cv2.imshow('result3', frame_canny)
            cv2.imshow('result4', frame_trajectory)
            # cv2.imshow('result5', frame_trajectory_2)

            # cv2.setMouseCallback('result4', location, frame)

            # if cv2.waitKey(0) & 0xFF == ord('n'):
            #     pass
            cv2.imshow('frame', frame)
            cv2.imshow('ball', frame_ball)
            cv2.imshow('canny', frame_canny)
            cv2.imshow('canny_s', frame_canny_and)

            cv2.setMouseCallback('frame', coordinate, frame)

            if cv2.waitKey(0) & 0xFF == ord('n'):
                pass

            # if cv2.waitKey(100) & 0xFF == ord('q'):
            #     cv2.destroyAllWindows()
            #     break