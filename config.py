import os

# Constant (Settings)
TCN_OUT_CHANNEL = 64                        # Num of channels of output of TCN
KNN_IN_DIM = 64                             # Dim of input of KNN
RELATION_DIM = 32                           # Dim of one layer of relation net
CLASS_NUM = 5                               # <X>-way  | Num of classes
SAMPLE_NUM = 1                              # <Y>-shot | Num of supports per class
QUERY_NUM = 3                               # Num of instances for query per class
TRAIN_EPISODE = 30000                       # Num of training episode 
VALIDATION_EPISODE = 50                     # Num of validation episode
VALIDATION_FREQUENCY = 200                  # After each <X> training episodes, do validation once
LEARNING_RATE = 0.0005                      # Initial learning rate
FRAME_NUM = 10                              # Num of frames per clip
CLIP_NUM = 5                                # Num of clips per window
WINDOW_NUM = 3                              # Num of processing window per video
INST_NUM = 10                               # Num of videos selected in each class
CLUSTER_NUM = 9                            # Num of clusters in KNN
GPU = "4,5,6,7"                               # Index of GPU to be used
EXP_NAME = "CTC_MOT_Kinetics400_KNN_5W1S"                # Name of this experiment

# Dataset
##################################################################################################################
DATASET = "kinetics"             # "kinetics" or "haa" or "full_kinetics"

TRAIN_SPLIT = "splits/tmp_train.txt"                
VAL_SPLIT = "splits/tmp_val.txt"
TEST_SPLIT = "splits/test.txt"                    

KINETICS_DATA_FOLDERS = ["/data/ssongad/kinetics400/frame/train"] #,
                         #"/data/ssongad/kinetics400/new_mot_normalized_frame/test"]

HAA_DATA_FOLDERS = ["/data/ssongad/haa/new_normalized_frame/",        # For HAA dataset only
                    "/data/ssongad/haa/normalized_frame_scale2",      # Order => [original (1x), 2x, 3x]
                    "/data/ssongad/haa/normalized_frame_scale3"]      # If a certain speed is missing, just put the path of 1x there
                                                                  # Don't leave an invalid path, including blank strings
##################################################################################################################

# Saved Models & Optimizers & Schedulers
##################################################################################################################
MAX_ACCURACY = 0.0            # Accuracy of the loaded model
                                             # Leave 0 if N/A

CHECKPOINT = "/data/ssongad/codes/alignment/models/CTC_MOT_Kinetics400_KNN_5W1S/0.32799999999999996"             # Path of a folder, if you put everything in this folder with their DEFAULT names
                            # If you have such a path, paths below are not necessary then
                            # Leave a blank string if N/A

ENCODER_MODEL = ""          # 
RN_MODEL = ""               # Path of saved models
TCN_MODEL = ""              # Leave a blank string if N/A            
RN0_MODEL = ""              # 
KNNC_MODEL = ""             # 

ENCODER_OPTIM = ""          # 
RN_OPTIM = ""               # Path of saved optimizers                                      
TCN_OPTIM = ""              # Leave a blank string if N/A
RN0_OPTIM = ""              # 
KNNC_OPTIM = ""             # 

ENCODER_SCHEDULER = ""      # 
RN_SCHEDULER = ""           # Path of saved schedulers
TCN_SCHEDULER = ""          # Leave a blank string if N/A
RN0_SCHEDULER = ""          #
KNNC_SCHEDULER = ""         # 


# If CHECKPOINT is given, then use files under CHECKPOINT first
# Only use the specific path of a file when it's missing under CHECKPOINT 
if os.path.exists(CHECKPOINT):
    results = []
    default_names = ("encoder.pkl", "rn.pkl", "tcn.pkl", "rn0.pkl", "encoder_optim.pkl", "rn_optim.pkl", "tcn_optim.pkl",
                     "rn0_optim.pkl", "encoder_scheduler.pkl", "rn_scheduler.pkl", "tcn_scheduler.pkl", "rn0_scheduler.pkl",
                     "knnc.pkl", "knnc_optim.pkl", "knnc_scheduler.pkl")
    for default_name in default_names:
        tmp = os.path.join(CHECKPOINT, default_name)
        results.append(tmp if os.path.exists(tmp) else "")
    
    ENCODER_MODEL = results[0] if results[0] != "" else ENCODER_MODEL
    RN_MODEL = results[1] if results[1] != "" else RN_MODEL
    TCN_MODEL = results[2] if results[2] != "" else TCN_MODEL
    RN0_MODEL = results[3] if results[3] != "" else RN0_MODEL
    KNNC_MODEL = results[12] if results[12] != "" else KNNC_MODEL

    ENCODER_OPTIM = results[4] if results[4] != "" else ENCODER_OPTIM
    RN_OPTIM = results[5] if results[5] != "" else RN_OPTIM
    TCN_OPTIM = results[6] if results[6] != "" else TCN_OPTIM
    RN0_OPTIM = results[7] if results[7] != "" else RN0_OPTIM
    KNNC_OPTIM = results[13] if results[13] != "" else KNNC_OPTIM

    ENCODER_SCHEDULER = results[8] if results[8] != "" else ENCODER_SCHEDULER
    RN_SCHEDULER = results[9] if results[9] != "" else RN_SCHEDULER
    TCN_SCHEDULER = results[10] if results[10] != "" else TCN_SCHEDULER
    RN0_SCHEDULER = results[11] if results[11] != "" else RN0_SCHEDULER
    KNNC_SCHEDULER = results[14] if results[14] != "" else KNNC_SCHEDULER
##################################################################################################################


# Dataset Split
##################################################################################################################
def read_split(file_path):
    result = []
    if os.path.exists(file_path):
        file = open(file_path, "r")
        lines = file.readlines()
        file.close()

        for line in lines:
            result.append(line.rstrip())
            
    return result

TRAIN_SPLIT = read_split(TRAIN_SPLIT)
VAL_SPLIT = read_split(VAL_SPLIT)
TEST_SPLIT = read_split(TEST_SPLIT)
##################################################################################################################
