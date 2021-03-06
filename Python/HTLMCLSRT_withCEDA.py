
# Most Comfortable Level Test
# up 5dB

from math import log10, sqrt
import numpy as np
from scipy import stats
from scipy.io import wavfile
from playsound import playsound
from psychopy import sound,visual, core,event
import time, serial, logging, scipy.io
from sklearn.metrics import mean_squared_error
from math import sqrt
import serial, string, math
import pandas as pd

# Set
#path = 'C:/Users/Jae Ho/Desktop/hy-kist/Matrix_sound/test source_matixAADC'
path = 'C:/Users/LeeJiWon/Desktop/hykist/AAD/MatrixSentence'
subject = '0429_hjy'
arduino = 'COM10'            # Arduino serial port number (BT)

# Connection
port = serial.Serial(arduino, 9600)     # Connect to port of arduino

# Make the window for visual presentation
screen = visual.Window([960, 900], screen=2, pos=[600, 0], fullscr=False,
                       winType='pyglet', allowGUI=False, allowStencil=False,
                       monitor='testMonitor', color=[-1, -1, -1], blendMode='avg',
                       units='pix')

file = pd.read_excel(path + "/intro_HTLMCLSRT.xlsx")

####### Intro exp #######
for i in range(0,len(file)):
    text = visual.TextStim(screen, text=file.Intro[i], height=30, color=[1, 1, 1], wrapWidth=2000)
    n = file.Intro[i]

    try:    # nan 즉 comment 끝이면 break
        np.isnan(n)
        break
    except:
        text.draw()
        screen.flip()

    key = event.waitKeys(keyList=["space", "escape"], clearEvents=True)
    if key == ["escape"]:
        core.quit()

#####################################  HTL  ######################################################
#text = visual.TextStim(screen, text="HTL \n\n puss space ", height=50, color=[1, 1, 1], wrapWidth=2000)
#text.draw()
#screen.flip()
#event.waitKeys(keyList=['space'], clearEvents=True)
port.write('H'.encode())

####### Intro HTL #######
for i in range(0,len(file)):
    text = visual.TextStim(screen, text=file.HTL[i], height=30, color=[1, 1, 1], wrapWidth=2000)
    n = file.HTL[i]

    try:    # nan 즉 comment 끝이면 break
        np.isnan(n)
        break
    except:
        text.draw()
        screen.flip()

    key = event.waitKeys(keyList=["space", "escape"], clearEvents=True)
    if key == ["escape"]:
        core.quit()

    while file.Num[i] == 4:    # 더미
        port.write('0'.encode())

        text = visual.TextStim(screen, text=" + ", height=150, color=[1, 1, 1], wrapWidth=2000)
        text.draw()
        screen.flip()
        time.sleep(5)

        text = visual.TextStim(screen, text=" 한번 더 들으시겠습니까? ", height=30, color=[1, 1, 1], wrapWidth=2000)
        text.draw()
        screen.flip()
        key = event.waitKeys(keyList=["space", "1"], clearEvents=True)

        if key == ["space"]:
            break



time.sleep(3)
H_SPL = 0      # 첫 시작 SPL
## start HTL test
while True:

    text = visual.TextStim(screen, text=" + ", height=150, color=[1, 1, 1], wrapWidth=2000)
    text.draw()
    screen.flip()

    # Write serial command
    port.write('1'.encode())

    # Play sound
    print("SPL : {0} dB".format(int(H_SPL)))
    time.sleep(5)

    # Question
    text = visual.TextStim(screen, text="들리나요? \n\n NO - 1 / OK - 2", height=50, color=[1, 1, 1], wrapWidth=2000)
    text.draw()
    screen.flip()

    resp = event.waitKeys(keyList=['1','2'], clearEvents=True)
    print("Respond : {0}".format(int(resp[0])))

    # Responding
    if int(resp[0]) == 1:      # -5
        H_SPL = H_SPL + 5

    elif int(resp[0]) == 2:    # +5
        port.write('X'.encode())
        break

    # Stock Respond

    text = visual.TextStim(screen, text="next ㄱㄷ", height=50, color=[1, 1, 1], wrapWidth=2000)
    text.draw()
    screen.flip()
    time.sleep(1)
    print("-------------------")


print("HTL = {0}  dB SPL".format(int(H_SPL)))
HTL = H_SPL
scipy.io.savemat(path + '/hjy/SAVE/HTL_' + subject + '.mat', {'HTL_SPL': H_SPL})
text = visual.TextStim(screen, text="최소가청역치 검사가 끝났습니다.", height=50, color=[1, 1, 1], wrapWidth=2000)
text.draw()
screen.flip()
#time.sleep(3)

######################################  MCL  ################################################################

#text = visual.TextStim(screen, text="MCL \n\n puss space ", height=50, color=[1, 1, 1], wrapWidth=2000)
#text.draw()
#screen.flip()
event.waitKeys(keyList=['space'], clearEvents=True)
print("========== MCL ===========")
# HTL + 30 dB 부터
H_SPL = HTL + 30

# list
Alph_list = list(string.ascii_lowercase)
MCL_list = np.array([35,40,45,50,55,60,65,70,75,80])
# for first track of MCL test

idx = np.where(MCL_list == H_SPL)
track = idx[0][0]+8

####### Intro MCL #######
for i in range(0,len(file)):
    text = visual.TextStim(screen, text=file.MCL[i], height=30, color=[1, 1, 1], wrapWidth=2000)
    n = file.MCL[i]

    try:  # nan 즉 comment 끝이면 break
        np.isnan(n)
        break
    except:
        text.draw()
        screen.flip()

    key = event.waitKeys(keyList=["space", "escape"], clearEvents=True)
    if key == ["escape"]:
        core.quit()


time.sleep(3)

## start MCL test
port.write('M'.encode())        # !! callibration 후에 첫 트랙번호가 두자리수 안넘아가는지 확인 !!
while True:

    print("Track = {0}".format(track))
    print("SPL : {0} dB".format(H_SPL))
    toArdCom = Alph_list[track - 1] # 증가 + HTL 5 track
    port.write(str(toArdCom).encode())
    text = visual.TextStim(screen, text=" + ", height=150, color=[1, 1, 1], wrapWidth=2000)
    text.draw()
    screen.flip()

    time.sleep(5)

    # Question
    text = visual.TextStim(screen, text="어떤가요? \n\n 1. 너무 작다  2. 작다. \n 3. 편하지만 약간 작다.  4. 편하다. \n 5. 편하지만 약간 크다. 6. 크지만 괜찮다. \n 7. 불편할 정도로 크다.", height=50, color=[1, 1, 1], wrapWidth=2000)
    text.draw()
    screen.flip()

    resp = event.waitKeys(keyList=['1', '2', '3', '4', '5', '6', '7', '0'], clearEvents=True)
    print("Respond : {0}".format(int(resp[0])))

    #
    text = visual.TextStim(screen, text="next ㄱㄷ", height=50, color=[1, 1, 1], wrapWidth=2000)
    text.draw()
    screen.flip()

    #
    resp = event.waitKeys(keyList=['1', '2', '0'], clearEvents=True)
    print("My key : {0}".format(int(resp[0])))
    time.sleep(1)

    # Responding
    if int(resp[0]) == 1:   # -1 track
        track = track - 1
        H_SPL = H_SPL - 5

    elif int(resp[0]) == 2: # +1 track
        track = track + 1
        H_SPL = H_SPL + 5

    elif int(resp[0]) == 0:
        port.write('0'.encode())
        break

    print("-------------")

MCL = H_SPL
print("** MCL == {0} dB **".format(MCL))
scipy.io.savemat(path + '/hjy/SAVE/MCL_' + subject + '.mat',
                 {'MCL_SPL': MCL})
text = visual.TextStim(screen, text="쾌적역치레벨 검사가 끝났습니다", height=50, color=[1, 1, 1], wrapWidth=2000)
text.draw()
screen.flip()
event.waitKeys(keyList=['space'], clearEvents=True)
########################################  SRT_LEFT  ##############################################################

# SRT test - LEFT
# correct - 5 up / incorrect - 1 down
text = visual.TextStim(screen, text="쉬는 시간입니다. \n\n 안내에 따라주세요.", height=50, color=[1, 1, 1], wrapWidth=2000)
text.draw()
screen.flip()
print("================================")
print("========== SRT_LEFT  ===========")
print("=======  Change SD card! =======")
print("================================")
event.waitKeys(keyList=['space'], clearEvents=True)

####### Intro SRT_L #######
for i in range(0,len(file)):
    text = visual.TextStim(screen, text=file.SRT_L[i], height=30, color=[1, 1, 1], wrapWidth=2000)
    n = file.SRT_L[i]

    try:    # nan 즉 comment 끝이면 break
        np.isnan(n)
        break
    except:
        text.draw()
        screen.flip()

    while file.Num[i] == len(file.SRT_L)-1:    # practice
        time.sleep(3)
        p = 1
        # play
        port.('P'.encode())
        if p == 1:
            text = visual.TextStim(screen, text="<<<", height=150, color=[1, 1, 1], wrapWidth=2000)

        else:
            text = visual.TextStim(screen, text=">>>", height=150, color=[1, 1, 1], wrapWidth=2000)

        text.draw()
        screen.flip()
        time.sleep(4)
        # respond
        text = visual.TextStim(screen, text="따라해 \n\n 빨리", height=50, color=[1, 1, 1], wrapWidth=2000)
        text.draw()
        screen.flip()
        # 내가 입력, 맞은 갯수를
        resp = event.waitKeys(keyList=['0', '1', '2', '3', '4', '5'], clearEvents=True)    # correct
        print('Correct = '+str(resp))
        text = visual.TextStim(screen, text="next", height=50, color=[1, 1, 1], wrapWidth=2000)
        text.draw()
        screen.flip()
        event.waitKeys(keyList=['space'], clearEvents=True)

        p = p+1
        if p == 3:
            break

    key = event.waitKeys(keyList=["space", "escape"], clearEvents=True)
    if key == ["escape"]:
        core.quit()

time.sleep(3)

#
SRT_list = np.array([0,10,20,30,32,34,36,38,40,42,44,46,48,50])
# Start SRT
# LEFT attention
ChargedB = 0
H_SNR = 0     # first dB SNR
track = 1
case = 0
SNRIdx = 0
ChargeTrk = 0   # first track
#port.write('S'.encode())
SRTresp_L = np.zeros([14,])
SRTfreq_L = np.zeros([14,])
port.write('S'.encode())

while track < 13*21:  # 20 track

    text = visual.TextStim(screen, text="<<<", height=150, color=[1, 1, 1], wrapWidth=2000)
    text.draw()
    screen.flip()

    print(str(track)+'_SNR = '+str(H_SNR)+' dB')
    # Serial command
    toArdCom = Alph_list[ChargeTrk]

    CurrentTrack = track + SNRIdx
    print("Current Track = {0}".format(CurrentTrack))
    print("To Ard = {0}".format(toArdCom))
    print(" + track = {0}".format(ChargeTrk))
    port.write(toArdCom.encode())   # arduino track에서 +할 숫자 보내

    time.sleep(5)

    # Repeat
    text = visual.TextStim(screen, text="따라해 \n\n 빨리", height=50, color=[1, 1, 1], wrapWidth=2000)
    text.draw()
    screen.flip()
    # 내가 입력, 맞은 갯수를
    resp = event.waitKeys(keyList=['0', '1', '2', '3', '4', '5'], clearEvents=True)    # correct
    print('Correct = '+str(resp))

    # dB 에 맞게 반응 넣기
    SNRIdx = int(np.where(SRT_list == -H_SNR)[0][0])
    SRTfreq_L[SNRIdx] = SRTfreq_L[SNRIdx] + 1
    SRTresp_L[SNRIdx] = SRTresp_L[SNRIdx] + int(resp[0])/5

    if case == 0:

        if int(resp[0]) < 3:    # correct = 0 / 1 / 2
            ChargedB = +2
            case = 1
        elif 2 < int(resp[0]):  # correct = 3 / 4 / 5
            ChargedB = -10

    elif case == 1:

        if int(resp[0]) < 3:
            ChargedB = +2
        elif 2 < int(resp[0]):
            ChargedB = -2

    H_SNR = H_SNR + ChargedB
    SNRIdx = int(np.where(SRT_list == -H_SNR)[0][0])
    track = track + 14
    ChargeTrk = (track + SNRIdx) - CurrentTrack     # 현재 arduino의 track 에서 + 시켜야할 num

    text = visual.TextStim(screen, text="next", height=50, color=[1, 1, 1], wrapWidth=2000)
    text.draw()
    screen.flip()
    event.waitKeys(keyList=['space'], clearEvents=True)

    print("----------------")

#print('SRT = ' + str(SRT) + ' dB SNR')
scipy.io.savemat(path + '/hjy/SAVE/SRTfreq_L' + subject + '.mat', {'SRTfreq_L': SRTfreq_L})
scipy.io.savemat(path + '/hjy/SAVE/SRTresp_L' + subject + '.mat', {'SRTresp_L': SRTresp_L})
text = visual.TextStim(screen, text="End", height=50, color=[1, 1, 1], wrapWidth=2000)
text.draw()
screen.flip()
port.write('0'.encode())
time.sleep(3)

########################################  SRT_RIGHT  ##############################################################

# SRT test - RIGHT
# correct - 5 up / incorrect - 1 down
text = visual.TextStim(screen, text="SRT_RIGHT \n\n press space", height=50, color=[1, 1, 1], wrapWidth=2000)
text.draw()
screen.flip()
event.waitKeys(keyList=['space'], clearEvents=True)
print("================================")
print("========== SRT_RIGHT ===========")
print("=======  Change SD card! =======")
print("================================")
#

####### Intro SRT_R #######
for i in range(0,len(file)):
    text = visual.TextStim(screen, text=file.SRT_R[i], height=30, color=[1, 1, 1], wrapWidth=2000)
    n = file.SRT_R[i]

    try:    # nan 즉 comment 끝이면 break
        np.isnan(n)
        break
    except:
        text.draw()
        screen.flip()

    key = event.waitKeys(keyList=["space", "escape"], clearEvents=True)
    if key == ["escape"]:
        core.quit()

time.sleep(3)

# Start SRT
# LEFT attention
ChargedB = 0
H_SNR = 0     # first dB SNR
track = 1
case = 0
SNRIdx = 0
ChargeTrk = 0   # first track
#port.write('S'.encode())
SRTresp_R = np.zeros([14,])
SRTfreq_R = np.zeros([14,])
port.write('S'.encode())

while track < 13*20:  # 30 track

    text = visual.TextStim(screen, text=">>>", height=150, color=[1, 1, 1], wrapWidth=2000)
    text.draw()
    screen.flip()

    print(str(track)+'_SNR = '+str(H_SNR)+' dB')
    # Serial command
    toArdCom = Alph_list[ChargeTrk]

    CurrentTrack = track + SNRIdx
    print("Current Track = {0}".format(CurrentTrack))
    print("To Ard = {0}".format(toArdCom))
    port.write(toArdCom.encode())   # arduino track에서 +할 숫자 보내

    time.sleep(5)

    # Repeat
    text = visual.TextStim(screen, text="따라해 \n\n 빨리", height=50, color=[1, 1, 1], wrapWidth=2000)
    text.draw()
    screen.flip()
    # 내가 입력, 맞은 갯수를
    resp = event.waitKeys(keyList=['0', '1', '2', '3', '4', '5'], clearEvents=True)    # correct
    print('Correct = '+str(resp))

    # dB 에 맞게 반응 넣기
    SNRIdx = int(np.where(SRT_list == -H_SNR)[0][0])
    SRTfreq_R[SNRIdx] = SRTfreq_R[SNRIdx] + 1
    SRTresp_R[SNRIdx] = SRTresp_R[SNRIdx] + int(resp[0])/5

    if case == 0:

        if int(resp[0]) < 3:    # correct = 0 / 1 / 2
            ChargedB = +2
            case = 1
        elif 2 < int(resp[0]):  # correct = 3 / 4 / 5
            ChargedB = -10

    elif case == 1:

        if int(resp[0]) < 3:
            ChargedB = +2
        elif 2 < int(resp[0]):
            ChargedB = -2

    H_SNR = H_SNR + ChargedB
    SNRIdx = int(np.where(SRT_list == -H_SNR)[0][0])  # exclude 0 dB
    track = track + 14
    ChargeTrk = (track + SNRIdx) - CurrentTrack     # 현재 arduino의 track 에서 + 시켜야할 num

    text = visual.TextStim(screen, text="next", height=50, color=[1, 1, 1], wrapWidth=2000)
    text.draw()
    screen.flip()
    event.waitKeys(keyList=['space'], clearEvents=True)

    print("----------------")

#print('SRT = ' + str(SRT) + ' dB SNR')
scipy.io.savemat(path + '/hjy/SAVE/SRTfreq_R' + subject + '.mat', {'SRTfreq_R': SRTfreq_R})
scipy.io.savemat(path + '/hjy/SAVE/SRTresp_R' + subject + '.mat', {'SRTresp_R': SRTresp_R})
text = visual.TextStim(screen, text="End", height=50, color=[1, 1, 1], wrapWidth=2000)
text.draw()
screen.flip()
port.write('0'.encode())
time.sleep(3)

'''

def sigmoid(x):
    return 1 / (1 +np.exp(-x))

sigm_val = np.zeros([len(SRTfreq),1])
xx = np.array([])

for i in range(len(SRTfreq)):
    sigm_val[i] = SRTresp[i]/SRTfreq[i]

check = np.isnan(sigm_val) # true = nan


y = sigm_val[np.logical_not(np.isnan(sigm_val))]
x = np.arange(1,8,1)


x = np.arange(-5, 5, 1)
sigm = sigmoid(y.T)


a = np.radians()
'''