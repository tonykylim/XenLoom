from psychopy import visual, event


contrast = 1

background_colour = (contrast, contrast, contrast)
mywin = visual.Window([800, 600], monitor="projector", screen=1, fullscr=True, units="pix", pos=None, color=background_colour, colorSpace='rgb')

while event.waitKeys() == False:
    continue
