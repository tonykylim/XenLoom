import glob, random, cv2, csv, os
from datetime import datetime
from tkinter import *
from win32api import GetSystemMetrics
import pandas as pd

def user_yes():
    global replay
    replay = False
    input = 1
    now = datetime.now()
    data_to_save = [ animalID, timepoint, treatment, trial[-1:], input, now.strftime("%y/%m/%d %H:%M") ]
    with open('response_to_loom.csv', 'a', newline='') as datafile:
        datafilewriter = csv.writer(datafile)
        datafilewriter.writerow( data_to_save )
        print("Trial data saved to response_to_loom.csv")
    win.destroy()
    
def user_no():
    global replay
    replay = False
    input = 0
    now = datetime.now()
    data_to_save = [ animalID, timepoint, treatment, trial[-1:], input, now.strftime("%y/%m/%d %H:%M") ]
    with open('response_to_loom.csv', 'a', newline='') as datafile:
        datafilewriter = csv.writer(datafile)
        datafilewriter.writerow( data_to_save )
        print("Trial data saved to response_to_loom.csv")
    win.destroy()
    
def user_unsure():
    global replay
    replay = False
    input = ''
    now = datetime.now()
    data_to_save = [ animalID, timepoint, treatment, trial[-1:], input, now.strftime("%y/%m/%d %H:%M") ]
    with open('response_to_loom.csv', 'a', newline='') as datafile:
        datafilewriter = csv.writer(datafile)
        datafilewriter.writerow( data_to_save )
        print("Trial data saved to response_to_loom.csv")
    win.destroy()
       
def user_replay():
    global replay
    replay = True
    win.destroy()
    
playback_speed = 3
def set_playback_speed():
    global playback_speed
    playback_speed = playback_slider.get()
    print("Playback speed set to " + str(playback_speed) + "x")
    
if os.path.exists('response_to_loom.csv') == False:
        with open ('response_to_loom.csv', 'w', newline='') as datafileinit:
            datafileinitwriter = csv.writer(datafileinit)
            datafileinitwriter.writerow( [ 'Animal ID', 'Timepoint', 'Treatment', 'Trial #', 'Response', 'Timestamp' ] )
video_file_list = glob.glob("*.avi")
random.shuffle(video_file_list)
num_videos = len(video_file_list)
video_num_counter = 0
for video_file in video_file_list:
    video_num_counter += 1
    print('Playing video ' + str(video_num_counter) + ' of ' + str(num_videos))
    video = cv2.VideoCapture(video_file)
    if not video.isOpened():
        print("Could not open video")
        sys.exit()
    ok, frame = video.read()
    if not ok:
        print('Cannot read video file')
        sys.exit()
    video.set(cv2.CAP_PROP_POS_FRAMES, 0)
    filename = video_file[:-4]
    animalID, timepoint, treatment, trial = filename.split("_")
    trial_num = int(trial[-1:])
    capture_data = []
    timingscsvlist = glob.glob(f'{animalID}_{timepoint}_{treatment}_*_timings.csv')
    with open(timingscsvlist[0], newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            capture_data.append(row)
    stim_start = float(capture_data[trial_num]['stim begin'])
    stim_end = float(capture_data[trial_num]['stim end'])
    trial_start = float(capture_data[trial_num]['start'])
    stim_time = stim_start-trial_start
    videofps = float(capture_data[trial_num]['fps'])
    stim_frame = int(stim_time*videofps)
    stim_end_time = stim_end-trial_start
    stim_end_frame = int(stim_end_time*videofps)
    replay = True
    while replay == True:
        video.set(cv2.CAP_PROP_POS_FRAMES, 0)
        frame_num = 0
        while True:
            ok, frame = video.read()
            if not ok:
                break
            frame_num += 1
            if frame_num > stim_frame and frame_num < stim_end_frame+1:
                cv2.putText(frame, "LOOMING", (frame.shape[1] - 180, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 0, 0), 4)
            cv2.imshow("Video", frame)
            k = cv2.waitKey(int(30/playback_speed)) & 0xff
            if k == 27 : break      
        win = Tk()
        f = Frame(win)
        Label(win, text="Did the tadpole respond to the looming stimulus?", font=("Helvetica", 14)).pack()
        f2 = Frame(win)
        b1 = Button(f2, text="Evasive Maneuvers!", fg="green", command=user_yes)
        b1.pack(side=LEFT)
        b2 = Button(f2, text="No Response", fg="red", command=user_no)
        b2.pack(side=LEFT)
        f2.pack()
        b3 = Button(win, text='Unable to determine', command=user_unsure)
        b3.pack(pady=10)
        Label(win, text="Replay controls", font=("Helvetica", 14)).pack()
        b5 = Button(win, text="Replay", command=user_replay)
        b5.pack()
        playback_slider = Scale(win, from_=1, to=4, length=100,tickinterval=1, orient=HORIZONTAL)
        playback_slider.pack()
        b6 = Button(win, text='Set Playback Speed', command=set_playback_speed)
        b6.pack(pady=10)
        windowWidth = win.winfo_reqwidth()
        windowHeight = win.winfo_reqheight()
        positionRight = int(win.winfo_screenwidth()/(1.8) - windowWidth/2)
        positionDown = int(win.winfo_screenheight()/3 - windowHeight/2)
        win.geometry("+{}+{}".format(positionRight, positionDown))
        f.mainloop()
cv2.destroyAllWindows()
with open('response_to_loom.csv', mode='rt', newline='') as data, open('response_to_loom_sorted.csv', 'w', newline='') as sorted_data:
    writer = csv.writer(sorted_data, delimiter=',')
    reader = csv.reader(data, delimiter=',')
    writer.writerow(next(reader))
    data = sorted(reader, key=lambda row: ((row[0], row[2], int(row[3]))))
    for row in data:
        writer.writerow(row)
df = pd.read_csv("response_to_loom_sorted.csv")
df["Response Rate"]=""
animals = df['Animal ID'].unique()
timepoints = df['Timepoint'].unique()
treatments = df['Treatment'].unique()
df2 = pd.DataFrame({"Animal ID":[],"Timepoint":[],"Treatment":[],"Response Rate":[]})
for animal in animals:
    print(animal)
    animal_df = df.loc[df['Animal ID'] == animal]
    for timepoint in timepoints:
        timepoint_df = animal_df.loc[animal_df['Timepoint'] == timepoint ]
        for treatment in treatments:
            treatment_df = timepoint_df.loc[timepoint_df['Treatment'] == treatment ]
            pr = treatment_df[treatment_df['Response'] == 1].shape[0]
            nr = treatment_df[treatment_df['Response'] == 0].shape[0]
            rr = round(100 * pr / (pr + nr), 2)
            df2 = df2.append({"Animal ID":animal,"Timepoint":timepoint,"Treatment":treatment,"Response Rate":rr},ignore_index=True)
df2.sort_values(by=['Treatment','Timepoint','Animal ID'], inplace=True)
df2.to_csv('response_rate.csv', index=False)