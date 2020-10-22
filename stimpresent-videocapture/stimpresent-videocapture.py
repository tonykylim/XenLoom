import numpy, cv2, datetime, threading, time, csv, math
from psychopy import visual, core, event, gui
from psychopy.visual import ShapeStim
import PIL.ImageOps
from PIL import Image, ImageDraw

experiment_types = ['darkloom', 'brightloom', 'isoluminant']

## Here, choose the experiment type. 0 = dark looming stimuli; 1 = bright looming stimuli; 2 = isoluminant looming stimuli
## Contrast only mode is 'True' (if on) or 'False' (if off) -- for dark and bright looming only
experiment_type = experiment_types[0]
contrast_only_mode = False

## Here, set the looming speed. 1 is a 0.5 second loom, 0.5 is a 1 second loom, 2 is a 0.5 second loom, etc
loom_speed_modulation = 1

## Here, set the relative contrast in % (for dark looming and bright looming)
contrast_percent = 100

## Here, set the noise size in pixels (for isoluminant looming)
noise_size = 4

# capture settings
cap = cv2.VideoCapture(0+cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
cap.set(cv2.CAP_PROP_FOCUS, 40)
cap.set(cv2.CAP_PROP_FPS, 30)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# contrast
if experiment_type == 'darkloom':
    contrast_value = round(0.5164-(numpy.log10(229.67/((207.68*(1-0.75644*contrast_percent/100)/(0.75644*contrast_percent/100+1))-25.53)-1)/1.21),2)
    background_colour = (1, 1, 1)
    loom_colour = (contrast_value,contrast_value,contrast_value)
if experiment_type == 'brightloom':
    contrast_value = round(0.5164-(numpy.log10(229.67/((-28.8*(1+contrast_percent/100*0.75644)/(contrast_percent/100*0.75644-1))-25.53)-1)/1.21),2)
    background_colour = (-1,-1,-1)
    loom_colour = (contrast_value,contrast_value,contrast_value)
if experiment_type == 'isoluminant':
    background_colour = (-1, -1, -1)
    loom_colour = (1, 1, 1)

# turn on camera
while True:
    ret, frame = cap.read()
    if ret==False:
        continue
    break

# experiment info (animal ID, timepoint, treatment)
expInfo = {'Animal ID':'', 'timepoint':'', 'treatment':''}
expInfo['exp_type'] = experiment_type
expInfo['dateStr'] = str(datetime.date.today())
dlg = gui.DlgFromDict(expInfo, fixed=['exp_type', 'dateStr'])
if dlg.OK:
    pass 
else:
    core.quit()

# timing data by trial
capture_data = []

# capture function
switch = False
def capture(trial_num):
    global switch
    # codec
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    # filename
    out = cv2.VideoWriter(expInfo['Animal ID'] + '_'+ expInfo['timepoint'] + '_' + expInfo['treatment'] +'_trial' + str(trial_num)+'.avi',fourcc, 30, (640,480))
    # timing data
    trial_dict = {}
    trial_dict['trial num'] = trial_num
    # instantiate variables
    length = 0
    frame_timer = 0
    frame_count = 0
    #trial start
    start = time.time()
    trial_dict['start'] = start
    # capturing frames
    while switch == False:
        ret, frame = cap.read()
        out.write(frame)
        frame_count += 1
        length = time.time() - start
    else:
        frame_timer = frame_count + 90
        while frame_count < frame_timer:
            ret, frame = cap.read()
            out.write(frame)
            frame_count += 1
            length = time.time() - start
    # store timing data
    trial_dict['frames'] = frame_count
    trial_dict['duration'] = length
    trial_dict['fps'] = frame_count/length
    capture_data.append(trial_dict)
# stimulus setup
mywin = visual.Window([800, 600], monitor="projector", screen=1, fullscr=False, units="pix", pos=None, color=background_colour, colorSpace='rgb')
mywin.mouseVisible = False
# timing of the looming stimulus
stim_time = []
stim_end = []
# noise function
def generate_noise():
    global generated_noise
    global inverse_noise
    background_noise = visual.NoiseStim(win=mywin, units='pix', ori=0, pos=(0, 0), size=(1024, 1024), color=[1, 1, 1], colorSpace='rgb', opacity=1, blendmode='avg', contrast=1.0, texRes=512, noiseType='Binary', noiseElementSize=noise_size)
    background_noise.draw()
    generated_noise = mywin.getMovieFrame(buffer='back')
    inverse_noise = PIL.ImageOps.invert(generated_noise)
# noise loom
def noise_circle(circle_size):
    global generated_noise
    global inverse_noise
    myradius = 1.0
    blank_image = Image.new('1', (800, 600))
    draw_circle = ImageDraw.Draw(blank_image)
    draw_circle.ellipse((800 / 2 - myradius * circle_size, 600 / 2 - myradius * circle_size, 800 / 2 + myradius * circle_size, 600 / 2 + myradius * circle_size), fill=(1))
    noise_loom = Image.composite(generated_noise, inverse_noise, blank_image)
    noisycircle = visual.ImageStim(mywin, image=noise_loom)
    noisycircle.draw()
    mywin.flip()
# looming function
def stimulus():
    global switch
    global contrast_only_mode
    # circle variables
    myradius = 1.0
    mysize = 1.0
    # draw circle
    mycircle = visual.Circle(win = mywin, radius = myradius, edges = 128, color=loom_colour, size = mysize )
    mycircle.draw()
    if contrast_only_mode == True:
        rect_colour = round(np.mean(np.array(mywin._getFrame(buffer='back'))) / 255 * 2 - 1,1)
        myrect = visual.Rect(win = mywin, width=800, height=600, fillColor=(rect_colour, rect_colour, rect_colour), pos=(0,0))
        myrect.draw()
    mywin.flip()
    # wait
    core.wait(2)
    # increase size of circle
    for i in range(250):
        mysize += 0.1
        mycircle.size = mysize
        mycircle.draw()
        if contrast_only_mode == True:
            rect_colour = round(np.mean(np.array(mywin._getFrame(buffer='back'))) / 255 * 2 - 1,1)
            myrect.color = (rect_colour,rect_colour,rect_colour)
            myrect.draw()
        mywin.flip()
    # wait
    core.wait(2)
    # stim start time
    stim_time.append(time.time())
    # looming loop
    while math.sqrt((mywin.size[0]/2)**2+(mywin.size[1]/2)**2) > mycircle.size:
        mycircle.setSize(1 + (0.1*loom_speed_modulation), '*')
        mycircle.draw()
        if contrast_only_mode == True:
            rect_colour = round(np.mean(np.array(mywin._getFrame(buffer='back'))) / 255 * 2 - 1,1)
            myrect.color = (rect_colour,rect_colour,rect_colour)
            myrect.draw()
        mywin.flip()
    stim_end.append(time.time())
    # wait
    for i in range(50):
        mycircle.draw()
        if contrast_only_mode == True:
            rect_colour = round(np.mean(np.array(mywin._getFrame(buffer='back'))) / 255 * 2 - 1,1)
            myrect.color = (rect_colour,rect_colour,rect_colour)
            myrect.draw()
        mywin.flip()
    core.wait(3)
    switch = True
    # reset
    mycircle.size = 1
    mycircle.draw()
    if contrast_only_mode == True:
        rect_colour = round(np.mean(np.array(mywin._getFrame(buffer='back'))) / 255 * 2 - 1,1)
        myrect.color = (rect_colour,rect_colour,rect_colour)
        myrect.draw()
    mywin.flip()
    core.wait(0.5)
    switch = False
# noise loom
if experiment_type == 'isoluminant':
    steps = 0
    measure = 26
    while math.sqrt((mywin.size[0]/2)**2+(mywin.size[1]/2)**2) > measure:
        measure = measure * (1 + (0.1*loom_speed_modulation))
        steps += 1
    steps = math.ceil(steps)
def stimulus_noise():
    global stim_time
    global switch
    mysize = 1.0
    noise_circle(mysize)
    core.wait(2)
    [noise_circle(mysize + 0.1 * (l+1)) for l in range(250)]
    core.wait(2)
    mysize = 1 + 25
    stim_time.append(time.time())
    [noise_circle(mysize * (1+(0.1*loom_speed_modulation)) ** (m+1)) for m in range(steps)]
    stim_end.append(time.time())
    [noise_circle(math.sqrt((mywin.size[0]/2)**2+(mywin.size[1]/2)**2)) for x in range(50)]
    core.wait(3)
    switch = True
    mysize = 1.0
    noise_circle(mysize)
    core.wait(0.5)
    switch = False
# trial loop
for trial in range(10):
    mythread = threading.Thread(target=capture,args=[trial])
    mythread.start()
    if trial == 0 and experiment_type == 'isoluminant':
        generate_noise()
    if experiment_type == 'isoluminant':
        stimulus_noise()
    if experiment_type == 'darkloom' or experiment_type == 'brightloom':
        stimulus()
    mythread.join()
    core.wait(1)
# clean up
cap.release()
cv2.destroyAllWindows()
# update timing data
for x in range(len(stim_time)):
    capture_data[x].update( {'stim begin': stim_time[x] } )
for x in range(len(stim_end)):
    capture_data[x].update( {'stim end': stim_end[x] } )
keys = capture_data[0].keys()
# create timing csv file
with open(expInfo['Animal ID'] + '_'+ expInfo['timepoint'] + '_' + expInfo['treatment'] + '_' +  expInfo['exp_type'] + '_timings.csv', 'w') as output_file:
    dict_writer = csv.DictWriter(output_file, keys)
    dict_writer.writeheader()
    dict_writer.writerows(capture_data)
# close psychopy
mywin.close()
core.quit()