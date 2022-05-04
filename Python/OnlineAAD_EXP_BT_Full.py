""""""""""""""""""""""""""""""""""""""""""
#        A cost-effective device        #
#           For Online AAD              #
""""""""""""""""""""""""""""""""""""""""""

###### Imports #####
import librosa, warnings, random, time, os, sys, serial, logging, argparse, scipy.io
import numpy as np
import pandas as pd
#from helper import *
from pymtrf import *
from PreProcessing import *
from Comments import *
from Direction import *
from Brainflow_stream import *
from EMA import *

#################################################################################################
#---------------------------------- Experimental SETTING ---------------------------------------#
#################################################################################################
# set info
subject = '001'             # Subject number
original = 'R'   # or L     # First attention direction
opposite = 'L'   # or R     # opposite direction
arduino = 'COM10'            # Arduino serial port number
cyton = 'COM4'              # OpenBCI board Bluetooth port number
path = 'C:/Users/LeeJiWon/Desktop/OpenBCI/AAD/Python'          # Base Directory

# Connection
port = serial.Serial(arduino, 9600)     # Connect to port of arduino
board, args = Brainflow_stream(cyton)   # Connect to Cyton with Brainflow network
# Set channels number & sampling rate
eeg_channels = board.get_eeg_channels(args.board_id)
aux_channels = board.get_analog_channels(args.board_id)
srate = board.get_sampling_rate(args.board_id)
# ----------------------------------- Load Speech segment data -----------------------------------#
# Load Stimulus data
allspeech = np.load(path + '/Allspeech.npy')
# 60 by 3840 / trial by time / 1-30 : Twenty / 31-60 Journey // sampling rate : 64 Hz
stim_T = allspeech[:30, :]
stim_J = allspeech[30:, :]
# ---------------------------------------- Parameter Setting -------------------------------------#
tmin = 0
tmax = 250          # Time-lag
Dir = -1            # Backward
reg_lambda = 10     # Lambda value
fs = 64             # post sampling rate

# Set int
ACC = []
Correct = []
Answer = []
start = []
end = []
#############################################################################################################
# Make the window for visual presentation
screen = visual.Window([960, 900], screen=2, pos=[600, 0], fullscr=False,
                       winType='pyglet', allowGUI=False, allowStencil=False,
                       monitor='testMonitor', color=[-1, -1, -1], blendMode='avg',
                       units='pix')
# ------------------------------------------- Intro -------------------------------------------------#
# Load Intro command file
file = pd.read_excel(path + "/question.xlsx")
file_3 = pd.read_excel(path + "/prePractice.xlsx")

event.waitKeys(keyList=['space'], clearEvents=True)
Comments('intro', path, screen, original)
# -------------------------------------------- Practice --------------------------------------------#
# Presentation Command for practice before experiment
text = visual.TextStim(screen, text=file_3.comment[0], height=50, color=[1, 1, 1], wrapWidth=2000)
text.draw()
screen.flip()
event.waitKeys(keyList=['space'], clearEvents=True)

for p in range(0, 2):
    port.write(b'3')            # For practice speech
    practice(p, path, screen)

# ==================================================================================================#
# -------------------------------------- START EXPERIMENT ------------------------------------------#
# ==================================================================================================#
RAWData = np.zeros((16, 0))    # EEG 16 channel by 1
AUXData = np.zeros((3, 0))     # Trigger 3 channel by 1
corr_T = np.zeros((16, 46))
corr_J = np.zeros((16, 46))
acc = np.zeros((16, 46))
model_wt = np.zeros([15,17,1])
inter_wt = np.zeros([15,1])
EmaCorr_j = np.zeros((16,46))
EmaCorr_t = np.zeros((16,46))

tr = 0  # trial number
z = 1   # To avoid repeat when detect trigger
j = 0   # Question number

# Comment before first session.
Comments(tr, path, screen, original)

# ----------------------------------------- Start 30 trial ------------------------------------------#
# Throw data which don't need
input = board.get_board_data()

while tr < 30:
    if z == 1:
        Direction(tr, original, opposite, screen, port)
        port.write(b'1')        # Signal for trial onset to arduino
        z = 0

    # For Next trial, reset the data format
    eeg_record = np.zeros((16, 0))
    aux_record = np.zeros((3, 0))
    model_w = np.zeros([15, 17, 1])  # reset
    inter_w = np.zeros([15, 1])

    # Data acquisition
    input = board.get_board_data()
    eeg_record = np.concatenate((eeg_record, -input[eeg_channels, :]), axis=1)   #If you connected with cathode electrode on openBCI board, you should transmit cathode of EEG data
    aux_record = np.concatenate((aux_record, input[aux_channels, :]), axis=1)

    # ----------------------------- Trigger detection -----------------------------#
    if 1 in input[aux_channels, :][1, :]:   # if the trigger is detected at 12 pin, start process. (include beep sound)
        print("Input Trigger {0}".format(tr + 1))
        print("Start Sound")
        # Find onset point
        index = np.where(aux_record[1, :] != 0)
        onset = index[0][0]
        # Format per trial
        i = 0       # Window number
        work = 0    # Time count
        check = -3  # attention cue sound 3 second

        # ----------------------------- Working while 60s = one trial-----------------------------#
        # Find speech onset point exclude attention cue sound
        speech = onset + (srate * 3) + 1
        while i != 46:          # During 46 windows

            # If the processing time exceeds 1s, no time sleep
            if work > 1:
                work = 1
            # Wait 1 second to be stacked EEG data and update EEG data per 1 second
            time.sleep(1 - work)
            # Visualize Time
            check = check + 1
            print("Running Time : {0}s".format(check))
            # Time counting
            start = time.perf_counter()

            # Acquire data
            input = board.get_board_data()
            eeg_record = np.concatenate((eeg_record, -input[eeg_channels, :]), axis=1)  # channel by time
            aux_record = np.concatenate((aux_record, input[aux_channels, :]), axis=1)

            # Work time
            end = time.perf_counter()
            work = end - start
            # Stack data until 15s and window sliding per 1s
            # Go to next step after 15s.
            if check >= 15:
                # Adjust data as acquired from that time.
                win = eeg_record[:, speech + srate * (i):]      # channel by time

                if len(win.T) > srate * (15):   # when exceed long of 15 second
                    win = eeg_record[:, speech + srate * (i): speech + srate * (15 + i)]      # 15 by 1875

                # ----------------------------- Pre-processing -----------------------------#
                win = np.delete(win, 7, axis=0)                 # delete 7 row ( 8 channel/Fp1 )
                win = Preproccessing(win, srate, 0.5, 8, 601)   # data, sampling rate, low-cut, high-cut, filter order
                data_l = len(win.T)                             # To check the length of inputted data
                # ============================== Train set ==================================#
                if tr < 14:  # int train
                    state = "Train set"
                    # Train decode model
                    model, tlag, inter = mtrf_train(stim_J[tr:tr + 1, 64 * (i):64 * (i) + data_l].T, win.T, fs, Dir,
                                                            tmin, tmax, reg_lambda)
                    model_w = np.add(model_w, model)
                    inter_w = np.add(inter_w, inter)
                # ============================== Test set ===================================#
                else:
                    state = "Test set"
                    # Reconstruct speech
                    pred, corr_j, p, mse = mtrf_predict(stim_J[tr:tr + 1, 64 * (i):64 * (i) + data_l].T, win.T, model, fs,
                                                     Dir, tmin, tmax, inter)
                    pred, corr_t, p, mse = mtrf_predict(stim_T[tr:tr + 1, 64 * (i):64 * (i) + data_l].T, win.T, model, fs,
                                                     Dir, tmin, tmax, inter)
                    '''
                    # Compare with both correlation values
                    if corr_j > corr_t:
                        acc[tr-14,i] = 1
                    else:
                        acc[tr-14,i] = 0

                    # Stock correlation value per window(i)
                    corr_J[tr-14,i] = np.array(corr_j)
                    corr_T[tr-14,i] = np.array(corr_t)
                    '''
                    # Exponential Moving Average
                    EmaCorr_j, EmaCorr_t = EMA(corr_j, corr_t, EmaCorr_j, EmaCorr_t, i, tr)

                    # Compare with both correlation values
                    if EmaCorr_j[tr - 14, i] > EmaCorr_t[tr - 14, i]:
                        acc[tr-14, i] = 1
                    else:
                        acc[tr-14, i] = 0

                # Plus window number
                i = i + 1

                # In trial 27~30, switch direction
                if tr + 1 >= 27 and check > 25:
                    switching(tr, check, original, opposite, screen)
                # Time count
                end = time.perf_counter()
                work = end - start
        # ------------------------ End one trial ------------------------#
        # Calculate per trial
        if state == "Train set":
            # Sum decoder model to average
            model_wt = np.add(model_wt, model_w)
            inter_wt = np.add(inter_wt, inter_w)

            # Average at last train trial
            if tr == 13:
                model = model_wt / (46 * 14)    # number of window * of trial
                inter = inter_wt / (46 * 14)

        elif state == "Test set":
            # Collect Accuracy per trial
            ACC = np.append(ACC, np.mean(acc[tr-14:tr-13,:]))
            print("\n==================================\n")
            print("Present Accuracy = {0}%".format(ACC[-1] * 100))
            print("\n==================================\n")

        # --------------------------- Questions --------------------------- #
        try:
            print("Question Time")
            correct, answer = Question(j, path, screen)
            Correct.append(correct)
            #Answer.append(answer)
            j = j + 1
        except KeyError:  # for error once present last question
            pass

        #=======  Data acquisition for rest  =======#
        input = board.get_board_data()
        eeg_record = np.concatenate((eeg_record, -input[eeg_channels, :]), axis=1)  # channel by time
        aux_record = np.concatenate((aux_record, input[aux_channels, :]), axis=1)

        #===== Stack eeg_record per trial & Save =====#
        RAWData = np.concatenate((RAWData, eeg_record), axis=1)
        AUXData = np.concatenate((AUXData, aux_record), axis=1)

        # =================================== SAVE DATA ===================================== #
        # Save per trial - RAW data, AUX data, accuracy ,behavior
        # numpy file
        np.save(path + '/save_data/RAW_' + subject, RAWData)
        np.save(path + '/save_data/AUX_' + subject, AUXData)
        np.save(path + '/save_data/Corr_att_' + subject, corr_J)
        np.save(path + '/save_data/Corr_unatt_' + subject, corr_T)
        np.save(path + '/save_data/EMACorr_att_' + subject, EmaCorr_j)
        np.save(path + '/save_data/EMACorr_unatt_' + subject, EmaCorr_t)
        np.save(path + '/save_data/Accuracy_' + subject, ACC)
        np.save(path + '/save_data/Behavior_' + subject, Correct)
        #np.save(path + '/save_data/Answer_' + subject, Answer)

        # Format current trial
        tr = tr + 1
        z = 1
        # ------------------ comment about next session ---------------------#
        Comments(tr, path, screen, original)

#################################################################################################
#                                       EXPERIMENT FINISH                                       #
#################################################################################################

# END
print("The End")
final = visual.TextStim(screen, text="The End \n\n Thank you", height=50, color=[1, 1, 1], wrapWidth=2000)
final.draw()
screen.flip()
time.sleep(3)

# Total accuracy
print("\n===================================\n")
print("=== Total Accuracy = {0}% ===".format(mean(ACC)*100))
print("\n===================================\n")

port.close()
screen.close()
board.stop_stream()
board.release_session()
