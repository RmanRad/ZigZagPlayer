import numpy as np
import cv2, mss, time, pyautogui
from SelectROI import SelectROI


def coordinate(event, x, y, flag, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print(f'location {x,y}')


def line_intersection(p1, p2, q1, q2):
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = q1
    x4, y4 = q2

    denominator = (x1-x2)*(y3-y4) - (y1-y2)*(x3-x4)

    if abs(denominator) < 1e-8:
        return None

    t = ((x1-x3)*(y3-y4) - (y1-y3)*(x3-x4)) / denominator

    u = ((x1-x3)*(y1-y2) - (y1-y3)*(x1-x2)) / denominator

    if t < 0 or u < 0 or u > 1:
        return None

    x = x1 + t*(x2-x1)
    y = y1 + t*(y2-y1)

    return int(x), int(y)


class ZigZagPlayer:
    def __init__(self):
        self.process_time = 0.001
        self.ball_cx = 155
        self.ball_cy = 295
        self.ball_contour = None
        self.velocity = 2500
        self.distance_buffer = [1000, 1000]
        self.blnk = None
        self.lastframeclicked = False
        # self.first_intersection = False

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
        # start_time = time.time()

        for frame in feed:
            t0 = time.time()

            frame = frame[150:300, :, :]

            frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
            # frame_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            t1 = time.time()


            # ball robust
            _, frame_ball_t = cv2.threshold(frame_gray, 60, 255, cv2.THRESH_BINARY_INV) 
            
            t2 = time.time()
            
            contours, _ = cv2.findContours(frame_ball_t, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
            
            t3 = time.time()

            # edges no shadow ----- no ball?
            clahe = cv2.createCLAHE(clipLimit=2, tileGridSize=(8,8))
            frame_gray = clahe.apply(frame_gray)
            # frame_equalized = cv2.equalizeHist(frame_gray)
            # frame_equalized = cv2.equalizeHist(frame_equalized)
            frame_blur = cv2.GaussianBlur(frame_gray, (7,7), 1)
            frame_canny = cv2.Canny(frame_blur, 60, 150)
            frame_canny = cv2.morphologyEx(frame_canny, cv2.MORPH_CLOSE, np.ones((3,3), 'uint8'), iterations=1)
            # diamond_mask = cv2.inRange(frame_hsv, np.array([150, 50, 50]), np.array([170, 255, 255]))
            # diamond_mask = cv2.dilate(diamond_mask, np.ones((3,3), 'uint8'), iterations=1)
            # frame_canny = cv2.bitwise_and(frame_canny, cv2.bitwise_not(diamond_mask), mask=None)
            # frame_canny_s = cv2.bitwise_and(frame_canny_s, frame_canny_gray, mask=None)
            t4 = time.time()
           
            # find the ball
            ball_cx = self.ball_cx # past
            ball_cy = self.ball_cy # doesnt change
            ball_contour = self.ball_contour # np.array([[[(self.velocity * self.process_time, 0)]]], 'uint8') # predicted

            if contours is not None:
                for contour in contours:
                    M = cv2.moments(contour)
                    if (90 <= cv2.contourArea(contour) <= 110) and (110 <= M['m01'] / M['m00'] <= 170):
                        ball_contour = contour
                        # print(f'area : {cv2.contourArea(ball_contour)}')
                        ball_cx = M['m10'] / M['m00'] 
                        ball_cy = M['m01'] / M['m00']
                        break

            # t5 = time.time()

            new_velocity = (ball_cx - self.ball_cx) / 0.001

            alpha = 0.25
            velocity = alpha * new_velocity + (1 - alpha) * self.velocity
        
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

            pt1 = (int(ball_cx), int(ball_cy + 4))
            pt2 = (int(ball_cx + length), int(ball_cy + (slope*length) + 4))

            frame = cv2.line(frame, pt1, pt2, (0,100,0), 3)
            # frame = cv2.line(frame, pt1, pt2, (0,100,0), 3)

            x_intersection, y_intersection = pt2
            blnk = np.zeros(frame_canny.shape)
            lines = cv2.HoughLinesP(frame_canny, 1, 1*np.pi/180, 20, minLineLength=10, maxLineGap=10)
            if lines is not None:
                for line in lines:
                    x1, y1, x2, y2 = line
                    line_slope = np.rad2deg(np.arctan2((y2 - y1), (x2 - x1)))
                    # print(line_slope)
                    
                    if -27 <= line_slope <= -24 or 24 <= line_slope <= 27:
                        blnk = cv2.line(blnk, (x1,y1), (x2,y2), (255,255,255), 2)
                        intersection = line_intersection(pt1, pt2, (x1,y1), (x2,y2))
    
                        if intersection is not None: # and not self.first_intersection:
                            condition = intersection[0] > pt1[0] + 3 if velocity > 0 else intersection[0] < pt1[0] - 3
                            if condition:
                                print('intersection found')
                                blnk = cv2.line(blnk, (x1,y1), (x2,y2), (255,255,255), 2)
                                x_intersection, y_intersection = intersection
                                cv2.circle(blnk, (x_intersection, y_intersection), 6, (255,255,255), -1)
                                # self.first_intersection = True

            # if not x_intersection and not y_intersection:
            #     x_intersection = self.x_intersection
            #     y_intersection = self.y_intersection
                           
            # self.x_intersection = x_intersection 
            # self.y_intersection = y_intersection
            
            # self.first_intersection = False

            # if self.blnk is not None:
            #     blnk = cv2.bitwise_and(blnk, self.blnk, mask=None)
            #     self.blnk = blnk
        

            # if velocity > 0:
            #     x_range = range(pt1[0] + 15, frame.shape[1])
                
            # else:
            #     x_range = range(pt1[0] - 15, -1, -1)

            # x_intersection, y_intersection = pt2[0], pt2[1]
            # for x in x_range:
            #     y = int(pt1[1] + (slope * (x - pt1[0])))
            #     if frame_gray[y,x] != 0 or frame_gray[y+1,x] != 0 or frame_gray[y-1,x] != 0:
            #         x_intersection, y_intersection = x, y
            #         break

            distance = np.linalg.norm([x_intersection - ball_cx, y_intersection - ball_cy])
            print(distance)

            t6 = time.time()
            # if ((self.distance_buffer[0] + self.distance_buffer[1]*2 + distance*3)/6) <= 35: #and self.lastframeclicked == 0:
            # if (self.distance_buffer[1] + distance*3)/4 <= 30:# and self.lastframeclicked == 0:
            if distance <= 30: # and not self.lastframeclicked:
                print('click')
                # self.lastframeclicked += 1
                self.velocity = -self.velocity
                pyautogui.click()

            # if self.lastframeclicked == 1:
            #     self.lastframeclicked = 0

            t7 = time.time()

            # self.distance_buffer[0] = self.distance_buffer[1]
            # self.distance_buffer[1] = distance

            frame = cv2.line(frame, pt1, (x_intersection, y_intersection), (0,0,200), 2)

            # self.process_time = time.time() - start_time

            cv2.imshow('hough_line', blnk)
            cv2.imshow('frame', frame)
            cv2.imshow('blurred', frame_blur)
            cv2.imshow('ball', frame_ball_t)
            cv2.imshow('gray', frame_gray)
            cv2.imshow('frame_canny', frame_canny)

            # cv2.setMouseCallback('frame', coordinate, frame)

            # print(f'timers : transformation: {t1 - t0}, thresholding: {t2 - t1}, getting contours {t3  - t2},  s_canny, morphology: {t4 - t3}, ball detection: {t5 - t4} click_time: {t7 - t6}')

            # if cv2.waitKey(0) & 0xFF == ord('n'):
            #     pass

            # if cv2.waitKey(100) & 0xFF == ord('q'):
            #     cv2.destroyAllWindows()
            #     break