import cv2, sys, time, math, numpy, imutils, csv, os, glob, pygame
from datetime import datetime
from psychopy import gui
import numpy as np
import pandas as pd
from collections import deque
import tkinter as tk
from tkinter import messagebox, filedialog
from pygame.locals import *
from tkinter import *

root = tk.Tk()
root.filename = filedialog.askopenfilename(initialdir = os.getcwd(), title = "Select AVI video file", filetypes=[("AVI video files",".avi")])
filename = root.filename[:-4]
root.destroy()

# values to play with to improve tracking if required
## increase alpha to increase automatic thresholding
## decrease alpha to decrease automatic thresholding
alpha = 3

## beta has a minimal impact on tracking. Sets the "floor" of thresholding algorhythm
beta = 0

# if escape angle doesn't seem right, change these numbers to improve escape angle extraction
## only ellipses more elliptical than the value set in ellipse_quality are used to calculate angle
ellipse_quality = 1.05
## vertical is 0 or 180, so when the tadpole heading crosses from 5 degrees to 175 degrees the actual change in heading was 10 degrees.
## Any |change| greater than the crossover_angle assumes a crossover through the 0/180 vertical line occured
crossover_angle = 70

## playback speed can be changed here. 1 = 1X real-time speed.
playback_speed = 1

## on this line, enter the size of petri dish bottom in mm
diameter = 52
## if petri dish detection is not working properly, increase pdmaxrad slighly if circle is too small, and decrease slightly if circle is too large
pdmaxrad = 200

# filename processing
filenamefolder = filename.split("/")
animalID, timepoint, treatment, trial = filenamefolder[-1].split("_")
#animalID, timepoint, treatment, trial = filename.split("_")
trial_num = int(trial[-1:])
timingscsvlist = glob.glob(f'{animalID}_{timepoint}_{treatment}_*_timings.csv')
splitcsv = timingscsvlist[0].split("_")
exp_type = splitcsv[3]

# data to save
capture_data = []

# open the csv file associated with thie video and save it
with open(animalID + '_' + timepoint + '_' + treatment + '_' + exp_type + '_timings.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        capture_data.append(row)

# timing data 
stim_start = float(capture_data[trial_num]['stim begin'])
trial_start = float(capture_data[trial_num]['start'])
stim_time = stim_start-trial_start
videofps = float(capture_data[trial_num]['fps'])
stim_frame = int(stim_time*videofps) 
stim_end = float(capture_data[trial_num]['stim end'])
stim_end_time = stim_end-trial_start
stim_end_frame = int(stim_end_time*videofps)

# angle timing
if exp_type == 'darkloom':
    buffer_3 = int(videofps * 2)
if exp_type == 'brightloom':
    buffer_3 = int(videofps * 2)

# Read video
video = cv2.VideoCapture(filename + ".avi")

# Exit if video not opened
if not video.isOpened():
        print("Could not open video")
        sys.exit()

# Read first frame
ok, frame = video.read()
if not ok:
    print('Cannot read video file')
    sys.exit()

# determine subtraction frames
frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
if exp_type == 'darkloom':
    subframe1 = 0
    subframe2 = frame_count-1
if exp_type == 'brightloom':
    subframe1 = stim_end_frame + 3
    subframe2 = stim_end_frame + 47
video.set(cv2.CAP_PROP_POS_FRAMES, subframe1)
ok, frame = video.read()
first_frame = frame.copy()
video.set(cv2.CAP_PROP_POS_FRAMES, subframe2)
ok, frame = video.read()
last_frame = frame.copy()
img_output = np.zeros((last_frame.shape[0], last_frame.shape[1], 3), np.uint8)

# set scale
scale = frame.copy()
petri_dish = 560
gray_scale = cv2.cvtColor(scale, cv2.COLOR_BGR2GRAY)
circles = cv2.HoughCircles(gray_scale, cv2.HOUGH_GRADIENT, 1.2, 800, param1=50,param2=30,minRadius=80,maxRadius=pdmaxrad)

# determine scale using detected petri dish size
if circles is not None:
    # grab circle properties
    circles = np.round(circles[0, :]).astype("int")
    largest_r = 0
    # loop over the circles
    for (x, y, r) in circles:
        # draw the circle in the output image
        cv2.circle(scale, (x, y), r, (0, 255, 0), 4)
        cv2.rectangle(scale, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)
        if largest_r < r:
            largest_r = r
    petri_dish = r * 2
    # show the output image
    cv2.imshow("Circle detection", scale)
    cv2.waitKey(0)
cv2.destroyWindow("Circle detection")

# Tadpole ROI
print("Select the tadpole and press SPACE or ENTER.")
tad_ROI = cv2.selectROI(last_frame, False)
last_frame[tad_ROI[1]:tad_ROI[1]+tad_ROI[3], tad_ROI[0]:tad_ROI[0]+tad_ROI[2]] = first_frame[tad_ROI[1]:tad_ROI[1]+tad_ROI[3], tad_ROI[0]:tad_ROI[0]+tad_ROI[2]]
cv2.destroyWindow("ROI selector")
cv2.imshow("Subtraction frame", last_frame)

# confirm successful removal of tadpole
my_w = tk.Tk()
my_var=messagebox.askyesno("Prompt", "Has the tadpole been removed from the image?")
if my_var == True:
    bg_img = last_frame
    cv2.destroyWindow("Subtraction frame")
    my_w.destroy()
if my_var == False:
    print("Select a bright area of background and press SPACE or ENTER.")
    bg_ROI =  cv2.selectROI(first_frame, False)
    bg_img = last_frame[tad_ROI[1]:tad_ROI[1] + tad_ROI[3], tad_ROI[0]:tad_ROI[0] + tad_ROI[2]].copy()
    bg_av = bg_img.mean(axis=0).mean(axis=0)
    cv2.rectangle(last_frame, (tad_ROI[0], tad_ROI[1]), (tad_ROI[0] + tad_ROI[2] , tad_ROI[1] + tad_ROI[3]), bg_av, -1)
    cv2.destroyWindow("ROI selector")
    my_w.destroy()
my_w.mainloop()

# thresholding
ret, last_frame = cv2.threshold(last_frame, 230, 255,cv2.THRESH_TRUNC)
last_frame = last_frame + 25

# save tracked video
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('output_videos/' + filename + '_tracked.avi',fourcc, 30, (640,480))

# return to beginning of video
video.set(cv2.CAP_PROP_POS_FRAMES, 0)
ok, frame = video.read()

# subtraction
subtracted = cv2.subtract(frame, last_frame)
blurred = cv2.GaussianBlur(subtracted, (11, 11), cv2.BORDER_DEFAULT)
contrast = cv2.addWeighted(blurred, alpha, np.zeros(blurred.shape, frame.dtype), 0, beta)
bw = cv2.cvtColor(contrast, cv2.COLOR_BGR2GRAY)

# masking
ret,mask = cv2.threshold(bw,50,255,cv2.THRESH_BINARY)
mask = cv2.erode(mask, None, iterations=1)
mask = cv2.dilate(mask, None, iterations=3)

# contrail 1
buffer = 30
pts = deque(maxlen= buffer )

# contrail 2
buffer_2 = int(videofps * 2)
pts2 = deque(maxlen= buffer_2 )

# distance
buffer_4 = int(videofps * 3)

# location and heading data
counter = 0
counter2 = 0
(dX, dY) = (0, 0)
direction = ""
frame_num = 0
totaldis = 0
before_loom = 0
after_loom = 0
max_v = 0
curr_vel = 0
last_head = None
ellipse = None
stim_angle_start = None
deviation = 0
pixels = petri_dish 
# speed data
speed_dict = {}
speed_time = -3

while True:
    # Read a new frame
    ok, frame = video.read()
    if not ok:
        break
    # preprocess the read frame
    subtracted = cv2.subtract(frame, last_frame)
    blurred = cv2.GaussianBlur(subtracted, (11, 11), cv2.BORDER_DEFAULT)
    contrast = cv2.addWeighted(blurred, alpha, np.zeros(blurred.shape, frame.dtype), 0, beta)
    bw = cv2.cvtColor(contrast, cv2.COLOR_BGR2GRAY)
    ret,mask = cv2.threshold(bw,50,255,cv2.THRESH_BINARY)
    mask = cv2.erode(mask, None, iterations=1)
    mask = cv2.dilate(mask, None, iterations=3)
    # find contours
    contours = cv2.findContours(mask.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(contours)
    # increment frame counter
    frame_num += 1
    # draw contours
    if len(contours) > 0:
        # largest contour
        c = max(contours, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        contour_center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
        areas = [cv2.contourArea(c) for c in contours]
        max_index = np.argmax(areas)
        cv2.drawContours(frame, contours, max_index, (255, 0, 0),2)
        pts.appendleft(contour_center)
        # fit to ellipse
        if len(contours[max_index]) > 4:
            ellipse = cv2.fitEllipse(contours[max_index])
        else:
            ellipse = None
        # contrail 2
        if frame_num >= stim_frame and counter2 <= buffer_2:
            pts2.appendleft(contour_center)
            counter2 += 1
    else:
        pts.appendleft(None)
        if frame_num >= stim_frame and counter2 <= buffer_2:
            pts2.appendleft(None)
            counter2 += 1
    # location and speed
    for i in np.arange(1, len(pts)):
        if pts[i - 1] is None or pts[i] is None:
            continue
        if frame_num >= 10 and i == 1 and pts[-10] is not None:
            dX = pts[-10][0] - pts[i][0]
            dY = pts[-10][1] - pts[i][1]
            (dirX, dirY) = ("", "")
            dxy = math.sqrt(dX**2 + dY**2)
            curr_vel = (dxy / (pixels / diameter)) / (10 / videofps)
            if frame_num >= stim_frame and frame_num <= stim_frame + buffer_2:
                if curr_vel > max_v:
                    max_v = curr_vel
            if np.abs(dX) > 20:
                dirX = "East" if np.sign(dX) == 1 else "West"
            if np.abs(dY) > 20:
                dirY = "North" if np.sign(dY) == 1 else "South"
            if dirX != "" and dirY != "":
                direction = "{}-{}".format(dirY, dirX)
            else:
                direction = dirX if dirX != "" else dirY
        # draw contrail 1
        thickness = int(np.sqrt( buffer / float(i + 1)) * 2)
        cv2.line(frame, pts[i - 1], pts[i], (0, 0, 255), thickness)
    # draw contrail 2
    if frame_num > stim_frame and frame_num <= stim_frame + buffer_2:
        if pts2[0] is None or pts2[1] is None:
            continue
        distance = math.sqrt( (pts2[1][0] - pts2[0][0])**2 + (pts2[1][1] - pts2[0][1])**2 ) / (pixels / diameter)
        totaldis += distance
    # distance traveled before and after looming
    if frame_num > stim_frame - buffer_4  and frame_num <= stim_frame :
        if pts[0] is None or pts[1] is None:
            continue
        bl = math.sqrt( (pts[1][0] - pts[0][0])**2 + (pts[1][1] - pts[0][1])**2 ) / (pixels / diameter)
        before_loom += bl
    if frame_num > stim_frame and frame_num <= stim_frame + buffer_4:
        if pts[0] is None or pts[1] is None:
            continue
        al = math.sqrt( (pts[1][0] - pts[0][0])**2 + (pts[1][1] - pts[0][1])**2 ) / (pixels / diameter)
        after_loom += al
    # angle analysis
    if frame_num >= stim_frame and frame_num <= stim_frame + buffer_3:
        if ellipse != None:
            if ellipse[1][1] / ellipse[1][0]  > ellipse_quality:
                if stim_angle_start == None:
                    stim_angle_start = ellipse[2]
                    last_head = ellipse[2]
                else:
                    if abs(ellipse[2] - last_head) < crossover_angle:
                        deviation += ellipse[2] - last_head
                        last_head = ellipse[2]
                    elif ellipse[2] - last_head >= crossover_angle:
                        deviation +=  ellipse[2] - last_head - 180
                        last_head = ellipse[2]
                    elif ellipse[2] - last_head <= (-1 * crossover_angle):
                        deviation +=  ellipse[2] - last_head + 180
                        last_head = ellipse[2]
                    else:
                        pass
        else:
            pass
    # start and end frames for escape angle
    if frame_num == stim_frame:
        start_frame = frame.copy()
        frame0 = frame.copy()
        start_tad_position = contour_center       
        if ellipse[0][0] < contour_center[0]:
            start_tad_angle = ellipse[2]
        else:
            start_tad_angle = ellipse[2] + 180
    if frame_num == stim_frame + round(buffer_3 * 1/4):
        frame1 = frame.copy()
    if frame_num == stim_frame + round(buffer_3 * 1/2):
        frame2 = frame.copy()
    if frame_num == stim_frame + buffer_3:
        end_frame = frame.copy()
        frame3 = frame.copy()
        end_tad_position = contour_center
        if ellipse[0][0] < contour_center[0]:
            end_tad_angle = round(ellipse[2])
        else:
            end_tad_angle = round(ellipse[2]) + 180
    # drawing escape contrail
    for i in np.arange(1, len(pts2)):
        if pts2[i - 1] is None or pts2[i] is None:
            continue
        thickness2 = int(np.sqrt( buffer_2 / float(i + 1)) * 2)
        cv2.line(frame, pts2[i - 1], pts2[i], (0, 255, 0), thickness2)
    # heading data
    if ellipse != None:
        cv2.putText(frame, "Current Heading: {}".format(round(ellipse[2], 1)),
        (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
        0.65, (0, 255, 255), 2)
    elif last_head != None:
        cv2.putText(frame, "Current Heading: {}".format(round(last_head, 1)),
        (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
        0.65, (0, 255, 255), 2)
    else:
        cv2.putText(frame, "Current Heading: N/A",
        (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
        0.65, (0, 255, 255), 2)
    cv2.putText(frame, "Deviation: {}".format(round(deviation,1)),
        (10, 55), cv2.FONT_HERSHEY_SIMPLEX,
        0.65, (0, 255, 255), 2)
    # looming text
    if frame_num >= stim_frame and frame_num <= stim_frame + buffer_2:
        cv2.putText(frame, "LOOMING", (frame.shape[1] - 180, 40), cv2.FONT_HERSHEY_SIMPLEX, 
        1.2, (255, 0, 0), 4)
    # display velocity
    cv2.putText(frame, "Vel: " + str(round(curr_vel,1)) ,
    (int(frame.shape[1]-140), frame.shape[0]-70), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 255), 2)
    # instantaneous velocity data
    if speed_time <= 3 and frame_num >= speed_time * videofps + stim_frame:
        speed_dict[speed_time] = round(curr_vel,1)
        print = round(curr_vel,1)
        speed_time += 0.1
        speed_time = round(speed_time, 1)
    # display distance travelled during loom
    cv2.putText(frame, "Dist: " + str(round(totaldis,1)),
    (int(frame.shape[1]-140), frame.shape[0]-40), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 0), 2)
    # display max velocity
    cv2.putText(frame, "Vmax: " + str(round(max_v,1)),
    (int(frame.shape[1]-140), frame.shape[0]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 0), 2)
    # display frame number
    cv2.putText(frame, "Frame: " + str(frame_num),
    (int(10), frame.shape[0]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 0), 2)
    # write video
    cv2.imshow("Video", frame)
    out.write(frame)
    k = cv2.waitKey(playback_speed) & 0xff
    if k == 27 : break

# confirm initial angle
pygame.init()
tadpole_angle_1 = 0
screen1 = pygame.display.set_mode((640, 480))
screen1.fill( (0,0,0) )
start_frame = cv2.cvtColor(start_frame, cv2.COLOR_BGR2RGB)
start_frame = start_frame.swapaxes(0, 1)
pygame.surfarray.blit_array(screen1, start_frame)
pygame.display.update()
tadpole_position_1 = start_tad_position
if start_tad_angle < 90:
    mouse_position_1 = (start_tad_position[0] + 100*math.sin(math.radians(start_tad_angle)), start_tad_position[1] - 100*math.cos(math.radians(start_tad_angle)) )
elif start_tad_angle < 180:
    mouse_position_1 = (start_tad_position[0] + 100*math.sin(math.radians(start_tad_angle)), start_tad_position[1] + 100*math.cos(math.radians(start_tad_angle)) )
elif start_tad_angle < 270:
    mouse_position_1 = (start_tad_position[0] - 100*math.sin(math.radians(start_tad_angle-180)), start_tad_position[1] + 100*math.cos(math.radians(start_tad_angle-180)) )
else:
    mouse_position_1 = (start_tad_position[0] - 100*math.sin(math.radians(start_tad_angle-180)), start_tad_position[1] - 100*math.cos(math.radians(start_tad_angle-180)) )
pygame.display.set_caption("Confirm initial angle - Press space to continue")
mouseclick = False
running = True
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            running = False
        elif event.type == KEYDOWN:
            if event.key == K_SPACE:
                pygame.quit()
                running = False
        elif event.type == MOUSEMOTION:
            if (mouseclick):
                mouse_position_1 = pygame.mouse.get_pos()
        elif event.type == MOUSEBUTTONUP:
            mouseclick = False
        elif event.type == MOUSEBUTTONDOWN:
            mouseclick = True
            mouse_position_1 = pygame.mouse.get_pos()  
    if running == False:
        break
    pygame.surfarray.blit_array(screen1, start_frame)
    pygame.draw.line(screen1, (255,255,0), tadpole_position_1, mouse_position_1, 3)   
    arrowhead_rotation = math.degrees(math.atan2(tadpole_position_1[1]-mouse_position_1[1], mouse_position_1[0]-tadpole_position_1[0]))+90
    pygame.draw.polygon(screen1, (255, 255, 0), ((mouse_position_1[0]+20*math.sin(math.radians(arrowhead_rotation)), mouse_position_1[1]+20*math.cos(math.radians(arrowhead_rotation))), (mouse_position_1[0]+20*math.sin(math.radians(arrowhead_rotation-120)), mouse_position_1[1]+20*math.cos(math.radians(arrowhead_rotation-120))), (mouse_position_1[0]+20*math.sin(math.radians(arrowhead_rotation+120)), mouse_position_1[1]+20*math.cos(math.radians(arrowhead_rotation+120)))))
    pygame.display.update()
    tadpole_angle_1 = math.degrees(math.atan2( (mouse_position_1[0]-tadpole_position_1[0]),(tadpole_position_1[1]-mouse_position_1[1]) ))
    if tadpole_angle_1 < 0:
        tadpole_angle_1 += 360

#confirm escape angle
tadpole_angle_2 = 0
screen2 = pygame.display.set_mode((640, 480))
screen2.fill( (0,0,0) )
end_frame = cv2.cvtColor(end_frame, cv2.COLOR_BGR2RGB)
end_frame = end_frame.swapaxes(0, 1)
pygame.surfarray.blit_array(screen2, end_frame)
pygame.display.update()
tadpole_position_2 = end_tad_position
if end_tad_angle < 90:
    mouse_position_2 = (end_tad_position[0] + 100*math.sin(math.radians(end_tad_angle)), end_tad_position[1] - 100*math.cos(math.radians(end_tad_angle)) )
elif start_tad_angle < 180:
    mouse_position_2 = (end_tad_position[0] + 100*math.sin(math.radians(end_tad_angle)), end_tad_position[1] + 100*math.cos(math.radians(end_tad_angle)) )
elif start_tad_angle < 270:
    mouse_position_2 = (end_tad_position[0] - 100*math.sin(math.radians(end_tad_angle-180)), end_tad_position[1] + 100*math.cos(math.radians(end_tad_angle-180)) )
else:
    mouse_position_2 = (end_tad_position[0] - 100*math.sin(math.radians(end_tad_angle-180)), end_tad_position[1] - 100*math.cos(math.radians(end_tad_angle-180)) )
pygame.display.set_caption("Confirm escape angle - Press space to continue")
mouseclick = False
running = True
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            running = False
        elif event.type == KEYDOWN:
            if event.key == K_SPACE:
                pygame.quit()
                running = False
        elif event.type == MOUSEMOTION:
            if (mouseclick):
                mouse_position_2 = pygame.mouse.get_pos()
        elif event.type == MOUSEBUTTONUP:
            mouseclick = False
        elif event.type == MOUSEBUTTONDOWN:
            mouseclick = True
            mouse_position_2 = pygame.mouse.get_pos()  
    if running == False:
        break
    pygame.surfarray.blit_array(screen2, end_frame)
    pygame.draw.line(screen2, (255,255,0), tadpole_position_2, mouse_position_2, 3)   
    arrowhead_rotation = math.degrees(math.atan2(tadpole_position_2[1]-mouse_position_2[1], mouse_position_2[0]-tadpole_position_2[0]))+90
    pygame.draw.polygon(screen2, (255, 255, 0), ((mouse_position_2[0]+20*math.sin(math.radians(arrowhead_rotation)), mouse_position_2[1]+20*math.cos(math.radians(arrowhead_rotation))), (mouse_position_2[0]+20*math.sin(math.radians(arrowhead_rotation-120)), mouse_position_2[1]+20*math.cos(math.radians(arrowhead_rotation-120))), (mouse_position_2[0]+20*math.sin(math.radians(arrowhead_rotation+120)), mouse_position_2[1]+20*math.cos(math.radians(arrowhead_rotation+120)))))
    pygame.display.update()
    tadpole_angle_2 = math.degrees(math.atan2( (mouse_position_2[0]-tadpole_position_2[0]),(tadpole_position_2[1]-mouse_position_2[1]) ))
    if tadpole_angle_2 < 0:
        tadpole_angle_2 += 360

# escape direction
summary = np.hstack([frame0, frame1, frame2, frame3])
cv2.imshow("Rotation direction", cv2.resize( summary, (int(summary.shape[1] * 1/2), int(summary.shape[0] * 1/2)), interpolation = cv2.INTER_AREA ) )
escape_angle = 0
def zero():
    global escape_angle
    escape_angle = 0
    text.set(escape_angle)
def clockwise():
    global escape_angle
    global tadpole_angle_1
    global tadpole_angle_2
    if tadpole_angle_1 > tadpole_angle_2:
        escape_angle = round(360-tadpole_angle_1+tadpole_angle_2, 1)
    elif tadpole_angle_1 <=  tadpole_angle_2:
        escape_angle = round(tadpole_angle_1 - tadpole_angle_2, 1)
    text.set(escape_angle)
def counterclockwise():
    global escape_angle
    global tadpole_angle_1
    global tadpole_angle_2
    if tadpole_angle_1 >= tadpole_angle_2:
        escape_angle = round(tadpole_angle_1 - tadpole_angle_2, 1)
    elif tadpole_angle_1 < tadpole_angle_2:
        escape_angle = round(360-tadpole_angle_2+tadpole_angle_1, 1)
    text.set(escape_angle)
def add360():
    global escape_angle
    escape_angle = escape_angle + 360
    text.set(escape_angle)
def add180():
    global escape_angle
    escape_angle = escape_angle + 180
    text.set(escape_angle)
def sub360():
    global escape_angle
    escape_angle = escape_angle - 360
    text.set(escape_angle)
def sub180():
    global escape_angle
    escape_angle = escape_angle - 180
    text.set(escape_angle)
def save():
    win.destroy()
win = Tk()
text = StringVar()
text.set("")
f = Frame(win)
Label(win, text="Direction of escape", font=("Helvetica", 14)).pack()
f2 = Frame(win)
b1 = Button(f2, text="Counter-clockwise", fg="black", command=counterclockwise)
b1.pack(side=LEFT)
b2 = Button(f2, text="Zero", fg="black", command=zero)
b2.pack(side=LEFT)
b3 = Button(f2, text="Clockwise", fg="black", command=clockwise)
b3.pack(side=LEFT)
f2.pack(pady=10)
f3 = Frame(win)
Label(win, textvariable=text, font=("Helvetica", 14)).pack()
f3.pack(pady=10)
f4 = Frame(win)
b4 = Button(f4, text="-360", command=sub360)
b4.pack(side=LEFT)
b5 = Button(f4, text="-180", command=sub180)
b5.pack(side=LEFT)
b6 = Button(f4, text="+180", command=add180)
b6.pack(side=LEFT)
b7 = Button(f4, text="+360", command=add360)
b7.pack(side=LEFT)
f4.pack(pady=10)
b8 = Button(win, text="Save", command=save)
b8.pack(pady=10)
windowWidth = win.winfo_reqwidth()
windowHeight = win.winfo_reqheight()
positionRight = int(win.winfo_screenwidth()/(1.8) - windowWidth/2)
positionDown = int(win.winfo_screenheight()/3 - windowHeight/2)
win.geometry("+{}+{}".format(positionRight, positionDown))
f.mainloop()

# output escape contrail
for i in np.arange(1, len(pts2)):
    if pts2[i - 1] is None or pts2[i] is None:
        continue
    thickness2 = int(np.sqrt( buffer_2 / float(i + 1)) * 5)
    cv2.line(img_output, pts2[i - 1], pts2[i], (255, 255, 255), thickness2)

# save data
now = datetime.now()
data_to_save = [ animalID, timepoint, treatment, trial[-1:], round(totaldis,1), round(max_v,1), abs(escape_angle), round(before_loom,1), round(after_loom,1), now.strftime("%y/%m/%d %H:%M") ]
cv2.imshow("contrail", img_output)
save_or_not = gui.Dlg()
save_or_not.addText('Save data?')
save_or_not.show()
if save_or_not.OK:
    cv2.imwrite('output_contrails/' + filenamefolder[-1] + '.jpg',img_output)
    if os.path.exists('data.csv') == False:
        with open ('data.csv', 'w', newline='') as datafileinit:
            datafileinitwriter = csv.writer(datafileinit)
            datafileinitwriter.writerow( [ 'Animal ID', 'Timepoint', 'Treatment', 'Trial #', 'Esc Dist', 'Esc Vel', 'Esc Ang', 'Before Dist', 'After Dist', 'Timestamp' ] )
    with open('data.csv', 'a', newline='') as datafile:
        datafilewriter = csv.writer(datafile)
        datafilewriter.writerow( data_to_save )
    if os.path.exists('output_speed/' + animalID + '_' + timepoint + '_' + treatment + '.csv') == False:
        with open ('output_speed/' + animalID + '_' + timepoint + '_' + treatment + '.csv', 'w', newline='') as datafileinit:
            datafileinitwriter = csv.writer(datafileinit)
            datafileinitwriter.writerow( [ 'Time'] )
            for key, value in speed_dict.items():
                datafileinitwriter.writerow([key])
    speed_df = pd.read_csv('output_speed/' + animalID + '_' + timepoint + '_' + treatment + '.csv')
    speed_list = []
    for key, value in speed_dict.items():
        speed_list.append(value)
    speed_df[trial] = speed_list
    speed_df.to_csv('output_speed/' + animalID + '_' + timepoint + '_' + treatment + '.csv', index=False)
    cv2.destroyAllWindows()
else:
    cv2.destroyAllWindows()
    
