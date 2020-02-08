import numpy, cv2, datetime, threading, time, csv, math
from psychopy import visual, core, event, gui
from psychopy.visual import ShapeStim

experiment_types = ['darkloom', 'brightloom']
experiment_type = experiment_types[0]
loom_speed_modulation = 0.0625
if experiment_type == 'darkloom':
    background_colour = (1, 1, 1)
    loom_colour = (-1, -1, -1)
if experiment_type == 'brightloom':
    background_colour = (-1, -1, -1)
    loom_colour = (1, 1, 1)
cap = cv2.VideoCapture(0+cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
cap.set(cv2.CAP_PROP_FOCUS, 40)
cap.set(cv2.CAP_PROP_FPS, 30)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
switch = False
while True:
    ret, frame = cap.read()
    if ret==False:
        continue
    break
expInfo = {'Animal ID':'', 'timepoint':'', 'treatment':''}
expInfo['exp_type'] = experiment_type
expInfo['dateStr'] = str(datetime.date.today())
dlg = gui.DlgFromDict(expInfo, fixed=['exp_type', 'dateStr'])
if dlg.OK:
    pass 
else:
    core.quit()
capture_data = []
def capture(trial_num):
    global switch
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(expInfo['Animal ID'] + '_'+ expInfo['timepoint'] + '_' + expInfo['treatment'] +'_trial' + str(trial_num)+'.avi',fourcc, 30, (640,480))
    trial_dict = {}
    trial_dict['trial num'] = trial_num
    length = 0
    frame_timer = 0
    frame_count = 0
    start = time.time()
    trial_dict['start'] = start
    while switch == False:
        ret, frame = cap.read()
        out.write(frame)
        frame_count += 1
        length = time.time() - start
    else:
        frame_timer = frame_count + 150
        while frame_count < frame_timer:
            ret, frame = cap.read()
            out.write(frame)
            frame_count += 1
            length = time.time() - start
    trial_dict['frames'] = frame_count
    trial_dict['duration'] = length
    trial_dict['fps'] = frame_count/length
    capture_data.append(trial_dict)
mywin = visual.Window([800, 600], monitor="projector", screen=1, fullscr=True, units="pix", pos=None, color=background_colour, colorSpace='rgb')
stim_time =[]
stim_end = []
def stimulus():
    global switch
    myradius = 1.0
    mysize = 1.0
    mycircle = visual.Circle(win = mywin, radius = myradius, edges = 128, color=loom_colour, size = mysize )
    mycircle.draw()
    mywin.flip()
    core.wait(2)
    for i in range(250):
        mysize += 0.1
        mycircle.size = mysize
        mycircle.draw()
        mywin.flip()
    core.wait(2)
    stim_time.append(time.time())
    while math.sqrt((mywin.size[0]/2)**2+(mywin.size[1]/2)**2) > mycircle.size:
        mycircle.setSize(1 + (0.1*loom_speed_modulation), '*')
        mycircle.draw()
        mywin.flip()
    stim_end.append(time.time())
    switch = True
    for i in range(50):
        mycircle.draw()
        mywin.flip()
    core.wait(0.5)
    mycircle.size = 1
    mycircle.draw()
    mywin.flip()
    switch = False
for trial in range(10):
    mythread = threading.Thread(target=capture,args=[trial])
    mythread.start()  
    stimulus()
    mythread.join()
    core.wait(1)
cap.release()
cv2.destroyAllWindows()
for x in range(len(stim_time)):
    capture_data[x].update( {'stim begin': stim_time[x] } )
for x in range(len(stim_end)):
    capture_data[x].update( {'stim end': stim_time[x] } )
keys = capture_data[0].keys()
with open(expInfo['Animal ID'] + '_'+ expInfo['timepoint'] + '_' + expInfo['treatment'] + '_' +  expInfo['exp_type'] + '_timings.csv', 'w') as output_file:
    dict_writer = csv.DictWriter(output_file, keys)
    dict_writer.writeheader()
    dict_writer.writerows(capture_data)
mywin.close()
core.quit()