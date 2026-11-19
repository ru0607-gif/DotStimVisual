import pandas as pd
from psychopy.gui import DlgFromDict
from psychopy.visual import Window, TextStim, ImageStim, Rect, TextBox, DotStim
from psychopy.core import Clock, quit, wait
from psychopy.event import Mouse
from psychopy.hardware.keyboard import Keyboard
from psychopy import event, data
import random

### DIALOG BOX ROUTINE ###
exp_info = {'participant_nr': '', 'age': '21','number of trials':[10,50,100,150]}
dlg = DlgFromDict(exp_info)
trialn= exp_info['number of trials']
p_name= exp_info['participant_nr']

# Initialize a fullscreen window with my monitor (HD format) size
# and my monitor specification called "samsung" from the monitor center
win = Window(size=(1200, 800), fullscr=False, monitor='samsung')

# Also initialize a mouse, although we're not going to use it
mouse = Mouse(visible=False)

# Initialize a (global) clock
clock = Clock()

# Initialize Keyboard
kb = Keyboard()
kb.clearEvents()

### WELCOME ROUTINE ###
# Create a welcome screen and show for 2 seconds
welcome_txt_stim = TextStim(win, text="Welcome to this experiment!", color=(1, 0, -1), font='Calibri')
welcome_txt_stim.draw()
win.flip()
wait(2)


### INSTRUCTION ROUTINE ###
task_instruct_txt = """ 
In this experiment, you will see a collection of moving dots.

On each trial the predominant movement of the dots will either be towards the left or the right.

You should indicate with the arrow keys which direction the motion is in. 

Sometimes it may be hard to tell; go with your best guess! Hit return to start!
    
 """

# Show instructions and wait until response (return)
task_instruct_txt = TextStim(win, task_instruct_txt, alignText='left', height=0.085)
task_instruct_txt.draw()
win.flip()

# Initialize keyboard and wait for response
kb = Keyboard()
while True:
    keys = kb.getKeys()
    if 'return' in keys:
        break  # break out of the loop!

# Configuration parameters
N_TRIALS = trialn
N_DOTS = 150
DOT_SIZE = 5  # in pixels
DOT_SPEED = 0.1  # degrees/frame
DOT_FIELD_SIZE = 2  # degrees
COHERENCE_LEVELS = [0.05, 0.1, 0.2, 0.4, 0.8]  # Fixed coherence levels
DIRECTIONS = [0, 180]  # Right (0°) and Left (180°)
FIXATION_MIN = 0.5  # seconds
FIXATION_MAX = 1.5  

# Create fixation and dots stimuli once (more efficient)
fix = TextStim(win, "+", height=1)\

dots = DotStim(
    win,
    fieldShape='circle', 
    nDots=N_DOTS,
    fieldSize=DOT_FIELD_SIZE,
    dotSize=DOT_SIZE,
    speed=DOT_SPEED,
    dotLife=-1,  # infinite lifetime
    noiseDots='direction',
    signalDots='same'
)

trialn=int(trialn)
# Create trial handler for proper randomization and data collection
trial_list = []
for coherence in COHERENCE_LEVELS:
    for direction in DIRECTIONS:
        # Multiple repetitions of each condition
        for rep in range(0,trialn//10):  
            trial_list.append({
                'coherence': coherence,
                'direction': direction,
                'correct_response': 'left' if direction == 180 else 'right'
            })

trials = data.TrialHandler(trial_list, nReps=1, method='random')

ITI_clock=Clock()
df=pd.DataFrame(columns=['direction','coherence','correct','resp','rt','fixation_dur'])
# Main experiment loop
for trial in trials:
    ITI_clock.reset()
    # Variable fixation period (prevents anticipation)
    fixation_time = random.uniform(FIXATION_MIN, FIXATION_MAX)
    
    # Show fixation
    while ITI_clock.getTime() < fixation_time:
        fix.draw()
        win.flip()
 
    # Set dot parameters for this trial
    dots.coherence = trial['coherence']
    dots.dir = trial['direction']
    
    # Reset keyboard and clock
    kb.clock.reset()
    kb.clearEvents()
    
    # Present dots and collect response
    response = None
    rt = None
    
    while response is None:
        dots.draw()
        win.flip()
        
        # Check for response
        keys = kb.getKeys(['left', 'right', 'escape'], waitRelease=False)
        if keys:
            response = keys[0].name
            rt = keys[0].rt
            
            # Allow escape to quit
            if response == 'escape':
                win.close()
                quit()
    
    # Record trial data
    correct = response == trial['correct_response']
    trials.addData('fixation_duration', fixation_time)
    df.loc[len(df)]=[trial['direction'], trial['coherence'], correct,response,rt,fixation_time]
    # Brief inter-trial interval
    win.flip()
    wait(0.5)
# Save data
filename = p_name + '_random_dot_motion'
trials.saveAsExcel(filename + '.xlsx')

# Show completion message
end_text = TextStim(win, "Task complete! Thank you.", height=1)
end_text.draw()
win.flip()
wait(1)

win.close()

# 1. Grab your original condition parameters in the EXACT order they were presented



## now we will add some visualization outputs
import matplotlib.pyplot as plt
plt.scatter(x='coherence',y='rt',c='correct',data=df,cmap='viridis')
plt.show()
wait(5)

plt.hist(df['rt'])
plt.show()
wait(5)

plt.bar(['Correct', 'Incorrect'], [df['correct'].sum(), len(df) - df['correct'].sum()])
plt.show()
wait(5)
quit()

