from psychopy import visual, event, core

## vary the value of contrast_value from -1 to 1 and record screen luminance with a luminance meter
contrast_value = 1

mywin = visual.Window([800, 600], monitor="projector", screen=1, fullscr=True, units="pix", pos=None, color=(contrast_value, contrast_value, contrast_value), colorSpace='rgb')
mywin.flip()
print("press any key to quit")
event.waitKeys()
mywin.close()
core.quit()