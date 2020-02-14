import cv2, sys, time, math, numpy, imutils, csv, os, glob
from datetime import datetime
from psychopy import gui
import numpy as np
from collections import deque
import tkinter as tk
from tkinter import messagebox

filename = "23_D6_Control_trial6"
animalID, timepoint, treatment, trial = filename.split("_")
trial_num = int(trial[-1:])
timingscsvlist = glob.glob(f'{animalID}_{timepoint}_{treatment}_*_timings.csv')
splitcsv = timingscsvlist[0].split("_")
exp_type = splitcsv[3]
alpha = 8
beta = 0
ellipse_quality = 1.2
crossover_angle = 70
playback_speed = 1
tracker_types = ['home brew', 'CSRT']
tracker_type = tracker_types[0]
if tracker_type == 'CSRT':
    tracker = cv2.TrackerCSRT_create()
else:
    pass
capture_data = []
with open(animalID + '_' + timepoint + '_' + treatment + '_timings.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        capture_data.append(row)
stim_start = float(capture_data[trial_num]['stim begin'])
trial_start = float(capture_data[trial_num]['start'])
stim_time = stim_start-trial_start
videofps = float(capture_data[trial_num]['fps'])
stim_frame = int(stim_time*videofps)
stim_end = float(capture_data[trial_num]['stim end']
stim_end_time = stim_end-trial_start
stim_end_frame = int(stim_end_time*videofps)
video = cv2.VideoCapture(filename + ".avi")
if not video.isOpened():
        print("Could not open video")
        sys.exit()
ok, frame = video.read()
if not ok:
    print('Cannot read video file')
    sys.exit()
frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
if exp_type == darkloom:
    subframe1 = 0
    subframe2 = frame_count-1
if exp_type == brightloom:
    subframe1 = stim_end_frame + 3
    subframe2 = stim_end_frame + 47
video.set(cv2.CAP_PROP_POS_FRAMES, subframe1)
ok, frame = video.read()
first_frame = frame.copy()
video.set(cv2.CAP_PROP_POS_FRAMES, subframe2)
ok, frame = video.read()
last_frame = frame.copy()
img_output = np.zeros((last_frame.shape[0], last_frame.shape[1], 3), np.uint8)
scale = frame.copy()
gray_scale = cv2.cvtColor(scale, cv2.COLOR_BGR2GRAY)
petri_dish = 560 
circles = cv2.HoughCircles(gray_scale, cv2.HOUGH_GRADIENT, 1.2, 800, param1=50,param2=30,minRadius=80,maxRadius=230)
if circles is not None:
    circles = np.round(circles[0, :]).astype("int")
    largest_r = 0
    for (x, y, r) in circles:
        cv2.circle(scale, (x, y), r, (0, 255, 0), 4)
        cv2.rectangle(scale, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)
        if largest_r < r:
            largest_r = r
    petri_dish = r * 2
    cv2.imshow("Circle detection", scale)
    cv2.waitKey(0)
cv2.destroyWindow("Circle detection")
print("Select the tadpole and press SPACE or ENTER.")
tad_ROI = cv2.selectROI(last_frame, False)
last_frame[tad_ROI[1]:tad_ROI[1]+tad_ROI[3], tad_ROI[0]:tad_ROI[0]+tad_ROI[2]] = first_frame[tad_ROI[1]:tad_ROI[1]+tad_ROI[3], tad_ROI[0]:tad_ROI[0]+tad_ROI[2]]
cv2.destroyWindow("ROI selector")
cv2.imshow("Subtraction frame", last_frame)
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
ret, last_frame = cv2.threshold(last_frame, 230, 255,cv2.THRESH_TRUNC)
last_frame = last_frame + 25
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('output_videos/' + filename + '_tracked.avi',fourcc, 30, (640,480))
video.set(cv2.CAP_PROP_POS_FRAMES, 0)
ok, frame = video.read()
subtracted = cv2.subtract(frame, last_frame)
blurred = cv2.GaussianBlur(subtracted, (11, 11), cv2.BORDER_DEFAULT)
contrast = cv2.addWeighted(blurred, alpha, np.zeros(blurred.shape, frame.dtype), 0, beta)
bw = cv2.cvtColor(contrast, cv2.COLOR_BGR2GRAY)
ret,mask = cv2.threshold(bw,50,255,cv2.THRESH_BINARY)
mask = cv2.erode(mask, None, iterations=1)
mask = cv2.dilate(mask, None, iterations=3)
buffer = 30
pts = deque(maxlen= buffer )
buffer_2 = int(videofps * 2)
pts2 = deque(maxlen= buffer_2 )
counter = 0
counter2 = 0
(dX, dY) = (0, 0)
direction = ""
frame_num = 0
totaldis = 0
max_v = 0
curr_vel = 0
last_head = None
ellipse = None
stim_angle_start = None
deviation = 0
diameter = 52
pixels = petri_dish 
if tracker_type == 'CSRT':
    bbox = cv2.selectROI(contrast, False)
    ok = tracker.init(contrast, bbox)
while True:
    ok, frame = video.read()
    if not ok:
        break
    subtracted = cv2.subtract(frame, last_frame)
    blurred = cv2.GaussianBlur(subtracted, (11, 11), cv2.BORDER_DEFAULT)
    contrast = cv2.addWeighted(blurred, alpha, np.zeros(blurred.shape, frame.dtype), 0, beta)
    bw = cv2.cvtColor(contrast, cv2.COLOR_BGR2GRAY)
    ret,mask = cv2.threshold(bw,50,255,cv2.THRESH_BINARY)
    mask = cv2.erode(mask, None, iterations=1)
    mask = cv2.dilate(mask, None, iterations=3)
    contours = cv2.findContours(mask.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(contours)
    frame_num += 1
    if len(contours) > 0:
        c = max(contours, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        contour_center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
        areas = [cv2.contourArea(c) for c in contours]
        max_index = np.argmax(areas)
        if tracker_type == 'home brew':
            cv2.drawContours(frame, contours, max_index, (255, 0, 0),2)
            pts.appendleft(contour_center)
        if len(contours[max_index]) > 4:
            ellipse = cv2.fitEllipse(contours[max_index])
        else:
            ellipse = None
        if tracker_type == 'home brew':
            if frame_num >= stim_frame and counter2 < buffer_2:
                pts2.appendleft(contour_center)
                counter2 += 1
    else:
        if tracker_type == 'home brew':
            pts.appendleft(None)
            if frame_num >= stim_frame and counter2 < buffer_2:
                pts2.appendleft(None)
                counter2 += 1
    if tracker_type == 'CSRT':
        ok, bbox = tracker.update(contrast)
        if ok:
            p1 = (int(bbox[0]), int(bbox[1]))
            p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
            cv2.rectangle(frame, p1, p2, (255,255,0), 2, 1)
            bbox_center = ( int( int(bbox[0]) + 0.5 * bbox[2] ) , int(int(bbox[1]) + 0.5 * bbox[3] ))
            pts.appendleft(bbox_center)
            counter += 1
            if frame_num >= stim_frame and counter2 < buffer_2:
                pts2.appendleft(bbox_center)
                counter2 += 1
        else :
            tracker = cv2.TrackerCSRT_create()
            bbox = cv2.selectROI(contrast, False)
            ok = tracker.init(contrast, bbox)
            p1 = (int(bbox[0]), int(bbox[1]))
            p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
            cv2.rectangle(frame, p1, p2, (255,0,0), 2, 1)
            bbox_center = ( int( int(bbox[0]) + 0.5 * bbox[2] ) , int(int(bbox[1]) + 0.5 * bbox[3] ))
            pts.appendleft(bbox_center)
            counter += 1
            if frame_num >= stim_frame and counter2 < buffer_2:
                pts2.appendleft(bbox_center)
                counter2 += 1
    for i in np.arange(1, len(pts)):
        if pts[i - 1] is None or pts[i] is None:
            continue
        if frame_num >= 10 and i == 1 and pts[-10] is not None:
            dX = pts[-10][0] - pts[i][0]
            dY = pts[-10][1] - pts[i][1]
            (dirX, dirY) = ("", "")
            dxy = math.sqrt(dX**2 + dY**2)
            curr_vel = (dxy / (pixels / diameter)) / (10 / videofps)
            if frame_num > stim_frame and frame_num < stim_frame + buffer_2:
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
        thickness = int(np.sqrt( buffer / float(i + 1)) * 2)
        cv2.line(frame, pts[i - 1], pts[i], (0, 0, 255), thickness)
    if frame_num > stim_frame and frame_num < stim_frame + buffer_2:
        if pts[0] is None or pts[1] is None:
            continue
        distance = math.sqrt( (pts2[1][0] - pts2[0][0])**2 + (pts2[1][1] - pts2[0][1])**2 ) / (pixels / diameter)
        totaldis += distance
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
    if frame_num == stim_frame:
        start_frame = frame.copy()
    if frame_num == stim_frame + buffer_2:
        end_frame = frame.copy()
    for i in np.arange(1, len(pts2)):
        if pts2[i - 1] is None or pts2[i] is None:
            continue
        thickness2 = int(np.sqrt( buffer_2 / float(i + 1)) * 2)
        cv2.line(frame, pts2[i - 1], pts2[i], (0, 255, 0), thickness2)
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
    if frame_num > stim_frame and frame_num < stim_frame + buffer_2:
        cv2.putText(frame, "LOOMING", (frame.shape[1] - 180, 40), cv2.FONT_HERSHEY_SIMPLEX, 
        1.2, (255, 0, 0), 4)
    cv2.putText(frame, "Vel: " + str(round(curr_vel,1)) ,
    (int(frame.shape[1]-140), frame.shape[0]-70), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 255), 2)
    cv2.putText(frame, "Dist: " + str(round(totaldis,1)),
    (int(frame.shape[1]-140), frame.shape[0]-40), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 0), 2)
    cv2.putText(frame, "Vmax: " + str(round(max_v,1)),
    (int(frame.shape[1]-140), frame.shape[0]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 0), 2)
    cv2.putText(frame, "Frame: " + str(frame_num),
    (int(10), frame.shape[0]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 0), 2)
    cv2.imshow("Video", frame)
    out.write(frame)
    k = cv2.waitKey(playback_speed) & 0xff
    if k == 27 : break
cv2.imshow("Start and End", np.vstack([start_frame, end_frame]))
for i in np.arange(1, len(pts2)):
    if pts2[i - 1] is None or pts2[i] is None:
        continue
    thickness2 = int(np.sqrt( buffer_2 / float(i + 1)) * 5)
    cv2.line(img_output, pts2[i - 1], pts2[i], (255, 255, 255), thickness2)
now = datetime.now()
print('Animal ID. Timepoint, Treatment, Trial #, Esc Dis, Esc Vel, Esc Ang, Timestamp')
data_to_save = [ animalID, timepoint, treatment, trial[-1:], round(totaldis,1), round(max_v,1), abs(round(deviation,1)), now.strftime("%y/%m/%d %H:%M") ]
print(data_to_save)
save_or_not = gui.Dlg()
save_or_not.addText('Save data?')
save_or_not.show()
if save_or_not.OK:
    cv2.imwrite('output_contrails/' + filename + '.jpg',img_output)
    if os.path.exists('data.csv') == False:
        with open ('data.csv', 'w', newline='') as datafileinit:
            datafileinitwriter = csv.writer(datafileinit)
            datafileinitwriter.writerow( [ 'Animal ID', 'Timepoint', 'Treatment', 'Trial #', 'Esc Dis', 'Esc Vel', 'Esc Ang', 'Timestamp' ] )
    with open('data.csv', 'a', newline='') as datafile:
        datafilewriter = csv.writer(datafile)
        datafilewriter.writerow( data_to_save )
        print("Data saved to: data.csv")
else:
    print("Data not saved.")
cv2.destroyAllWindows()