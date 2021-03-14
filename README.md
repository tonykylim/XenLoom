# XenLoom: Custom looming stimuli and behavior tracking for Xenopus tadpoles

XenLoom is a software suite for presentation of customized looming stimuli, collection of visual-evoked responses, and automated tracking of Xenopus tadpoles with computer vision.
It builds on the beta version (https://github.com/tonykylim/XenLoom_beta) by allowing greater variety and control over the looming stimuli presented. Additionally, the data analysis interface has been simplified and made more user friendly.

New features of XenLoom include: <br/>

<h4>Different looming stimulus types</h4>

| <img src="https://github.com/tonykylim/XenLoom/blob/master/~example_stimuli/1-darkloom.gif"/> | <img src="https://github.com/tonykylim/XenLoom/blob/master/~example_stimuli/2-brightloom.gif"/> | <img src="https://github.com/tonykylim/XenLoom/blob/master/~example_stimuli/3-isoloom.gif"/> |
| :---: | :---: | :---: | 
| Dark looming stimulus | Bright looming stimulus | Isoluminant looming stimulus |

<h4>No looming control stimuli with only a change to screen luminance</h4>

| <img src="https://github.com/tonykylim/XenLoom/blob/master/~example_stimuli/4-darkloomcontrast.gif"/> | <img src="https://github.com/tonykylim/XenLoom/blob/master/~example_stimuli/5-brightloomcontrast.gif"/> | <img src="https://github.com/tonykylim/XenLoom/blob/master/~example_stimuli/6-isoloomcontrast.gif"/> |
| :---: | :---: | :---: | 
| Darkening luminance stimulus | Brightening luminance stimulus | Isoluminant luminance stimulus  |

<h4>Looming stimulus velocity</h4>

| <img src="https://github.com/tonykylim/XenLoom/blob/master/~example_stimuli/9-darkloomslow.gif"/> | <img src="https://github.com/tonykylim/XenLoom/blob/master/~example_stimuli/7-darkloomnormal.gif"/> | <img src="https://github.com/tonykylim/XenLoom/blob/master/~example_stimuli/8-darkloomfast.gif"/> |
| :---: | :---: | :---: | 
| Low speed | Medium speed | High speed  |

<h4>Looming stimulus contrast</h4>

| <img src="https://github.com/tonykylim/XenLoom/blob/master/~example_stimuli/12-darkloom20contrast.gif"/> | <img src="https://github.com/tonykylim/XenLoom/blob/master/~example_stimuli/11-darkloom80contrast.gif"/> | <img src="https://github.com/tonykylim/XenLoom/blob/master/~example_stimuli/10-darkloom100contrast.gif"/> |
| :---: | :---: | :---: | 
| Low contrast | Intermediate contrast | High contrast  |

<h4>Isoluminant stimulus noise grain</h4>

| <img src="https://github.com/tonykylim/XenLoom/blob/master/~example_stimuli/14-isoloom1.gif"/> | <img src="https://github.com/tonykylim/XenLoom/blob/master/~example_stimuli/13-isoloom4.gif"/> | <img src="https://github.com/tonykylim/XenLoom/blob/master/~example_stimuli/15-isoloom16.gif"/> |
| :---: | :---: | :---: | 
| Fine noise grain | Intermediate noise grain | Coarse noise grain  |

All stimuli are programmatically generated, so combinations of the above are also possible.

## Getting Started

The code has been partitioned into 3 modules (stim-present, loom-decision, tad-tracker). <br/>
'stimpresent-videocapture.py' is used to present customized looming stimuli while recording responses from a webcam. <br/>
'loom-decision.py' is used to evaluate the tadpole response to looming stimuli. <br/>
'tad-tracker.py' is used to extract tracking data from video data. <br/>

## Prerequisites and setup

Please see the prerequisites and setup listed at XenLoom beta. The requirements to the updated XenLoom scripts are the same as those found at: <br/>
https://github.com/tonykylim/XenLoom_beta#prerequisites <br/>
https://github.com/tonykylim/XenLoom_beta#installing <br/>
https://github.com/tonykylim/XenLoom_beta#experimental-setup <br/>

Additional prerequisite--contrast calibration:
For proper contrast calibration, a luminance meter is required. <br/>
Fill the glass bowl with buffer and aim the projector at the paper screen. <br/>
Aim the luminance meter at the side of the screen which the animal will see. <br/>
Psychopy (the library XenLoom uses to display stimuli), uses a brightness scale from -1 to +1. Use the 'contrast-measure' script to vary the screen brightness from -1 to +1 and record the resulting absolute luminance (in cd/m²).

Plot the absolute luminance against the psychopy screen brightness value. <br/>
<img src="https://github.com/tonykylim/XenLoom/blob/master/~contrast_calibration/absolute-luminance.png" width=33% height=33% /> <br/>
Fit the screen brightness data to a nonlinear four-parameter logistic equation.

Enter the following data into the 'contrast calibration variables' section of the 'stimpresent-videocapture.py' script <br/>
cc_low = luminance value when screen was set to -1 <br/>
cc_high = luminance value when screen was set to +1 <br/>
cc_bottom = the minimum value (obtained by curve fit) <br/>
cc_top = the maximum value (obtained by curve fit) <br/>
cc_halfway = the point of inflection (obtained by curve fit) <br/>
cc_hs = the Hill's slope (obtained by curve fit) <br/>

## How to use the new customized looming functions 

<h4>Experiment type </h4>
The 'experiment_types' variable sets the type of looming stimulus. <br/>
experiment_types[0] = dark looming stimulus <br/>
experiment_types[1] = bright looming stimulus <br/>
experiment_types[2] = isoluminant looming stimulus <br/>

<h4>Contrast only  mode </h4>
As a control, you can average out changes in luminance over the entire screen and disabling the looming animation. To use this, turn on contrast only mode by setting the variable 'contrast_only_mode' to True. Set it to False to disable this mode.

<h4>Looming speed</h4>
Changing looming speed is set by altering the 'loom_speed_modulation' variable. <br/>
The relationship between 'loom_speed_modulation' and the animation time is as so: <br/>
0.5 seconds / loom_speed_modulation = looming animation time in seconds <br/> 

For example, setting loom_speed_modulation to 0.5, results in a looming animation time of 1 second. Conversely, setting loom_speed_modulation to 2, results in a looming animation time of 0.25 seconds.

<h4>Relative contrast</h4>
Relative contrast according to the Michalson's equation is set by altering the 'contrast_percent' variable from 0 to 100.

<h4>Isoluminant looming noise size</h4>
Isoluminant looming stimuli are programatically generated and the size of the noise blocks can be varied using the 'noise_size' variable. This variable must be a number from 1-36 that is a perfect square, and corresponds to the size of the noise blocks.

<h4>Additional interval time</h4>
The default amount of time between looming stimuli is approximately 20 seconds. This time between trials can be extended by changing the 'trial_interval' value. For example, setting the value to 5 would increase the amount of time between trials by 5 seconds--for a total of 25 seconds.

## Recording data

Prepare the setup with the tadpole in the petri dish. The glass bowl is filled with buffer to prevent refraction index abberations.<br/>
<img src="https://github.com/tonykylim/XenLoom_beta/blob/master/~expected-results/diagram.png" width=50% height=50% />

Run 'videocapture-test.py' to ensure the webcam captures the view of the entire petri dish.<br/>
<img src="https://github.com/tonykylim/XenLoom/blob/master/~instruction_manual/webcam.png" width=33% height=33% />

When ready, run 'stimpresent-videocapture.py'. You will be prompted for the following information: <br/>
<img src="https://github.com/tonykylim/XenLoom/blob/master/~instruction_manual/prompt1.png" width=15% height=15% /><br/>
Animal ID -- Enter a unique alphanumeric string to identify the animal or group being tested. eg. 'E13'<br/>
Timepoint -- Enter any timepoint information, if required. eg. 'day2'<br/>
Treatment -- Enter any treatment information, if required. eg. 'vehicle'<br/>
XenLoom then presents stimuli according to the settings set above and generates avi video files of each trial, along with an csv file containing timing data.

## Data analysis

<h4>Escape probability</h4> 

To determine escape probability, use the 'escape=decision.py' script. Place all video files with timing csv files to be analyzed together in a folder containing 'escape-decision.py'. <br/>
Run 'escape-decision.py' and follow the prompts. <br/>
<img src="https://github.com/tonykylim/XenLoom/blob/master/~instruction_manual/prompt2.png" width=40% height=40% /><br/>
If the tadpole exhibited escape behaviour, press the green button. If it did not, press the red button. If it is unclear, press "Unable to determine".<br/>
You can also to play the video over again, or alter playback speed too. <br/><br/>

Once all the trials have been evaluated for escape behaviour by the user, open 'response_to_loom_sorted' to find a csv file containing all the escape behaviour data. The response rate can be calculated by dividing the number of positive responses by the combinded number of positive and negative responses. Responses where it was not clear whether or not the animal responded are discarded.

Example data examining the effect of different looming stimuli types on escape probability. <br/>
<img src="https://github.com/tonykylim/XenLoom/blob/master/~instruction_manual/stimtype.jpg" width=30% height=30% />

<h4>Tadpole tracker</h4>

The 'tadpole-tracker.py' script allows the user to gather data from individual trials, such as escape velocity, escape angle, and distance traveled. Instantaneous velocity 3 seconds before and after the looming stimulus is also gathered. Contrails are also obtained, which are a nice way of visually summarizing escape behaviour.

Copy the 'tadpole=tracker.py script to the folder with trial avi video files. After running this script, you will be prompted for the video file to be analyzed.<br/>
<img src="https://github.com/tonykylim/XenLoom/blob/master/~instruction_manual/prompt3.png" width=40% height=40% /> <br/>
Select a video file for analysis and continue.

The script will use the petri dish to set the scale of the video. You should see a green circle along the circumference of the petri dish. <br/>
<img src="https://github.com/tonykylim/XenLoom/blob/master/~instruction_manual/background_rem1.png" width=30% height=30% /> <br/>
If the circle is too small, stop the script and increase the pdmaxrad variable and try again. If the circle is too big, try reducing pdmaxrad. Press spacebar to continue.

Next, a background subtraction image is required in order to automatically track the tadpole. This background image is programatically generated by removing the tadpole from one frame of the video and splicing in a different video frame. If the tadpole moves to a new location, this method will work.<br/>
Select the tadpole using the mouse (click, drag, release) to define a region around the tadpole. Then press spacebar. <br/>
<img src="https://github.com/tonykylim/XenLoom/blob/master/~instruction_manual/background_rem2.png" width=50% height=50% /> <br/>

If successful, the tadpole will be removed from the image. <br/>
<img src="https://github.com/tonykylim/XenLoom/blob/master/~instruction_manual/background_rem3.png" width=50% height=50% /> <br/>
Press space to continue. <br/>

However, if the tadpole doesn't move between the two frames, the tadpole will not be removed from the image. <br/>
<img src="https://github.com/tonykylim/XenLoom/blob/master/~instruction_manual/background_rem4.png" width=78% height=78% /> <br/>
Press "No" and instead XenLoom will try to create a subtraction image by filling in the area where the tadpole is located with the surrounding pixels. Place another selection box as tightly around the tadpole as possible, and press space. <br/>

Now XenLoom will track the tadpole and prompt the user to confirm the start and end escape angles by clicking on the image and pressing space.<br/>
<img src="https://github.com/tonykylim/XenLoom/blob/master/~instruction_manual/background_rem5.png" width=40% height=40% /> <img src="https://github.com/tonykylim/XenLoom/blob/master/~instruction_manual/background_rem6.png" width=40% height=40% /><br/>
Then tell XenLoom whether the tadpole rotated clockwise or counterclockwise, and add in any extra rotations to confirm the escape angle.<br/>
<img src="https://github.com/tonykylim/XenLoom/blob/master/~instruction_manual/background_rem7.png" /><br/>

Now XenLoom will produce a csv file called 'data.csv' that includes the escape distance, escape velocity and escape angle. This csv file will be appended to with the data from each video file analyzed within the folder.

Instantaneous velocity is outputed in a folder called 'output_speed'.  Example results to dark looming stimuli: <br/>
<img src="https://github.com/tonykylim/XenLoom/blob/master/~instruction_manual/inst_vel.png" width=50% height=50% /><br/>

XenLoom will also produce annotated video files with tracking in the 'output_video' folder. Example:<br/>
<img src="https://github.com/tonykylim/XenLoom_beta/blob/master/~expected-results/looming-example.gif" />

Finally, in the 'output_contrails' folder, contrails are saved from each trial. Copy the 'contrails-merger.py' script to this folder and run it to merge contrails from the different trials to form one merged contrail file per animal. Example: <br/>
<img src="https://github.com/tonykylim/XenLoom/blob/master/~instruction_manual/contrails.jpg" width=63% height=63% /><br/>

## Versioning

The beta version of XenLoom is available here at https://github.com/tonykylim/XenLoom_beta <br/>
This newer version of XenLoom was developed in the Ruthazer lab in 2020 by Tony Lim. QA and bug reporting was performed by Jade Ho.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
