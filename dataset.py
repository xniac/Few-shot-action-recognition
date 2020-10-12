# Public Packages
import torch                                         #
import torchvision                                   #  Torch
from torch.utils.data import DataLoader,Dataset      #
from torch.utils.data.sampler import Sampler         #

import cv2                                           #
import numpy as np                                   #  Image

import random                                        #  OS
import os                                            #

WIDTH = HEIGHT = 128

class HAADataset(Dataset):
    def __init__(self, data_folders, mode, splits, class_num, video_num, inst_num, frame_num, clip_num, window_num):
        self.mode = mode
        assert mode in ["train", "test"]

        self.class_num = class_num
        self.video_num = video_num
        self.inst_num = inst_num
        self.frame_num = frame_num
        self.clip_num = clip_num
        self.window_num = window_num
        self.data_folder_1 = data_folders[0]
        self.data_folder_2 = data_folders[1]
        self.data_folder_3 = data_folders[2]

        all_class_names = splits[0] if self.mode == "train" else splits[1]
        self.class_names = random.sample(all_class_names, self.class_num)
        self.labels = dict()
        for i, class_name in enumerate(self.class_names):
            self.labels[class_name] = i+1

        self.video_folders = []
        self.video_labels = []
        for class_name in self.class_names:
            label = self.labels[class_name]
            class_folders = [os.path.join(self.data_folder_1, class_name), os.path.join(self.data_folder_2, class_name), os.path.join(self.data_folder_3, class_name)]
            video_names = os.listdir(class_folders[0])
            random.shuffle(video_names)
            video_names = video_names[:self.inst_num]

            for video_name in video_names:
                random_stretch = random.randint(1,5)
                random_stretch = max(0, random_stretch-3)
                self.video_folders.append(os.path.join(class_folders[random_stretch], video_name))

                self.video_labels.append(label)
    
    def __str__(self):
        output = ""
        output += "Task -> mode={}; {}-way {}-shot\n".format(self.mode, self.class_num, self.video_num)
        return output
    
    def print_dataset(self):
        for i in range(len(self)):
            print("[{}]\t{}\t{}".format(i, self.video_labels[i], self.video_folders[i]))
    
    def __len__(self):
        return len(self.video_folders)
    
    def get_classes(self):
        return self.class_names.copy()

    def __getitem__(self, idx):
        video_folder = self.video_folders[idx]
        video_label = self.video_labels[idx]

        all_frames = [os.path.join(video_folder, frame_name) for frame_name in os.listdir(video_folder)]
        all_frames.sort()


        length = len(all_frames)
        stride = round((length - self.frame_num)/(self.clip_num*self.window_num-1))
        expected_length = (self.clip_num*self.window_num-1)*stride + self.frame_num
        
        # Deal with length difference
        if expected_length <= length:
            all_frames = all_frames[:expected_length]
        else:
            tmp = all_frames[-1]
            for _ in range(expected_length - length):
                all_frames.append(tmp)
        
        selected_frames = []
        for i in range(self.clip_num*self.window_num):
            selected_frames.extend(list(range(i*stride, i*stride+self.frame_num)))
        
        # Process frames
        flip = random.randint(0,1)
        processed_frames = []
        for frame in all_frames:
            img = cv2.imread(frame)
            img = cv2.resize(img, (WIDTH, HEIGHT))
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img = cv2.flip(img, 1) if flip else img
            processed_frames.append(img)

        frames = []
        for i, frame_idx in enumerate(selected_frames):
            j = i % self.frame_num
            if j == 0:
                frames.append([])
            
            frame = processed_frames[frame_idx].copy()
            frames[-1].append(frame)
        
        frames = np.array(frames) / 127.5 - 1           # -1 to 1 # [num_frame, h, w, channel]
        frames = np.transpose(frames, (0, 4, 1, 2, 3))     # [video_clip, RGB, frame_num, H, W]
        frames = torch.Tensor(frames.copy())

        # noise = random.randint(0,1)
        # if self.mode == "train" and noise:
        #     frames = frames + 0.1 * torch.randn(self.clip_num, 3, self.frame_num, WIDTH, HEIGHT)

        return frames, video_label

class KineticsDataset(Dataset):
    def __init__(self, data_folders, mode, splits, class_num, video_num, inst_num, frame_num, clip_num, window_num):
        self.mode = mode
        assert mode in ["train", "val", "test"]

        # Attribute
        self.class_num = class_num
        self.video_num = video_num
        self.inst_num = inst_num
        self.frame_num = frame_num
        self.clip_num = clip_num
        self.window_num = window_num
        self.data_folders = data_folders

        # Mode & Split
        if self.mode == "train":
            all_class_names = splits[0]
        elif self.mode == "val":
            all_class_names = splits[1]
        else:
            all_class_names = splits[2]
        random.shuffle(all_class_names)
        self.class_names = all_class_names[:class_num+1]

        # Pick Classes
        self.labels = dict()
        for i, class_name in enumerate(self.class_names):
            self.labels[class_name] = i

        # Find all videos
        self.video_folders = []
        self.video_labels = []
        for class_name in self.class_names:
            video_folders = []
            video_labels = []
            label = self.labels[class_name]

            for data_folder in self.data_folders:
                class_folder = os.path.join(data_folder, class_name)
                video_names = os.listdir(class_folder) if os.path.exists(class_folder) else []

                for video_name in video_names:
                    video_path = os.path.join(class_folder, video_name)
                    if len(os.listdir(video_path)) >= self.frame_num:
                        video_folders.append(video_path)
                        video_labels.append(self.labels[class_name])

            # Pick <self.inst_num> random videos
            zip_list = list(zip(video_folders, video_labels))
            random.shuffle(zip_list)
            zip_list = zip_list[:self.inst_num]
            video_folders, video_labels = zip(*zip_list)

            self.video_folders.extend(video_folders)
            self.video_labels.extend(video_labels)

        self.scales = []
        for i in range(len(self.video_folders)):
            self.scales.append(random.randint(2,4))

    def __len__(self):
        return len(self.video_folders)
    
    def print_dataset(self):
        string = ""
        for i in range(len(self)):
            string += "[{}] {} {} {}\n".format(i, self.video_labels[i], self.video_folders[i], self.scales[i])
        
        print(string)
        return string
    
    def get_labels(self):
        if self.mode == "test":
            return self.labels
        return None

    def __getitem__(self, idx):
        video_folder = self.video_folders[idx]
        video_label = self.video_labels[idx]
        scale = self.scales[idx]

        all_frames = [os.path.join(video_folder, frame_name) for frame_name in os.listdir(video_folder)]
        all_frames.sort()
        all_frames = all_frames[::scale]

        length = len(all_frames)
        stride = round((length - self.frame_num)/(self.clip_num*self.window_num-1))
        
        selected_frames = []
        for i in range(self.clip_num*self.window_num):
            selected_frames.extend(list(range(i*stride, i*stride+self.frame_num)))
        for i in range(len(selected_frames)):
            if selected_frames[i] >= length:
                selected_frames[i] = length - 1
        
        # Process frames
        processed_frames = [None] * length
        flip = random.randint(0,1)
        # trans = random.randint(0,1)
        # T = np.float32([[1,0,random.randint(-25,25)],[0,1,random.randint(-25,25)]])
        for idx in selected_frames:
            if processed_frames[idx] is None:
                frame = all_frames[idx]
                img = cv2.imread(frame)
                img = cv2.resize(img, (WIDTH, HEIGHT))   
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                img = cv2.flip(img, 1) if flip else img
                # img = cv2.warpAffine(img, T, (WIDTH, HEIGHT)) if trans else img
                processed_frames[idx] = img

        frames = []
        for i, frame_idx in enumerate(selected_frames):
            j = i % self.frame_num
            if j == 0:
                frames.append([])
            
            frame = processed_frames[frame_idx].copy()
            frames[-1].append(frame)
        
        frames = np.array(frames) / 127.5 - 1              # -1 to 1 # [num_frame, h, w, channel]
        frames = np.transpose(frames, (0, 4, 1, 2, 3))     # [window*clip, RGB, frame_num, H, W]
        frames = torch.Tensor(frames.copy())
        
        noise = random.randint(0,1)
        if self.mode == "train" and noise:
            frames = frames + 0.1 * torch.randn(self.window_num*self.clip_num, 3, self.frame_num, WIDTH, HEIGHT)

        return frames, video_label

class AVADataset(Dataset):
    def __init__(self, data_folder, mode, splits, class_num, video_num, inst_num, frame_num, clip_num, window_num):
        self.mode = mode
        assert mode in ["train", "test"]

        self.class_num = class_num
        self.video_num = video_num
        self.inst_num = inst_num
        self.frame_num = frame_num
        self.clip_num = clip_num
        self.window_num = window_num
        self.data_folder = data_folder

        all_class_names = splits[0] if self.mode == "train" else splits[1]
        while True:
            done = True
            self.class_names = random.sample(all_class_names, self.class_num)
            for class_name in self.class_names:
                class_folder = os.path.join(self.data_folder, class_name)
                if len(os.listdir(class_folder)) < self.inst_num:
                    done = False
                    break
            if done:
                break
        self.labels = dict()
        for i, class_name in enumerate(self.class_names):
            self.labels[class_name] = i+1

        self.video_folders = []
        self.video_labels = []
        for class_name in self.class_names:
            label = self.labels[class_name]
            class_folder = os.path.join(self.data_folder, class_name)
            video_names = os.listdir(class_folder)
            random.shuffle(video_names)
            video_names = video_names[:self.inst_num]

            for video_name in video_names:
                self.video_folders.append(os.path.join(class_folder, video_name))
                self.video_labels.append(label)

    def __len__(self):
        return len(self.video_folders)
    
    def print_dataset(self):
        for i in range(len(self)):
            print("[{}] {} {} {}".format(i, self.video_labels[i], self.video_folders[i], self.scales[i]))

    def __getitem__(self, idx):
        video_folder = self.video_folders[idx]
        video_label = self.video_labels[idx]

        all_frames = [os.path.join(video_folder, frame_name) for frame_name in os.listdir(video_folder)]
        all_frames.sort()

        length = len(all_frames)
        stride = round((length - self.frame_num)/(self.clip_num*self.window_num-1))
        expected_length = (self.clip_num*self.window_num-1)*stride + self.frame_num
        
        # Deal with length difference
        if expected_length <= length:
            all_frames = all_frames[:expected_length]
        else:
            tmp = all_frames[-1]
            for _ in range(expected_length - length):
                all_frames.append(tmp)
        
        selected_frames = []
        for i in range(self.clip_num*self.window_num):
            selected_frames.extend(list(range(i*stride, i*stride+self.frame_num)))
        
        # Process frames
        flip = random.randint(0,1)
        processed_frames = []
        for frame in all_frames:
            img = cv2.imread(frame)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img = cv2.flip(img, 1) if flip else img
            processed_frames.append(img)

        frames = []
        for i, frame_idx in enumerate(selected_frames):
            j = i % self.frame_num
            if j == 0:
                frames.append([])
            
            frame = processed_frames[frame_idx].copy()
            frames[-1].append(frame)
        
        frames = np.array(frames) / 127.5 - 1              # -1 to 1 # [num_frame, h, w, channel]
        frames = np.transpose(frames, (0, 4, 1, 2, 3))     # [video_clip, RGB, frame_num, H, W]
        frames = torch.Tensor(frames.copy())

        noise = random.randint(0,1)
        if self.mode == "train" and noise:
            frames = frames + 0.1 * torch.randn(self.window_num*self.clip_num, 3, self.frame_num, 128, 128)

        return frames, video_label, video_folder

class ClassBalancedSampler(Sampler):

    def __init__(self, support, mode, num_per_class, class_num, inst_num, shuffle):
        self.support = support
        self.mode = mode
        assert mode in ["train", "val", "test"]

        self.num_per_class = num_per_class
        self.class_num = class_num
        self.inst_num = inst_num
        self.shuffle = shuffle

    def __iter__(self):
        # return a single list of indices, assuming that items will be grouped by class
        batch = []
        for j in range(self.class_num + 1):
            sublist = []
            for i in range(self.inst_num):
                sublist.append(i+j*self.inst_num)
            random.shuffle(sublist)
            sublist = sublist[:self.num_per_class]
            batch.append(sublist)

        batch = batch[1:]
        batch = [item for sublist in batch for item in sublist]

        if self.shuffle:
            random.shuffle(batch)
        
        return iter(batch)

    def __len__(self):
        return 1

def get_data_loader(dataset, support, num_per_class, shuffle=False, num_workers=0):
    if dataset.mode == "train" and not support:
        sampler = ClassBalancedSampler(support, dataset.mode, num_per_class, dataset.class_num, dataset.inst_num, shuffle)
        loader = DataLoader(dataset, batch_size=num_per_class*(dataset.class_num+1), sampler=sampler, num_workers=num_workers)
    else:
        sampler = ClassBalancedSampler(support, dataset.mode, num_per_class, dataset.class_num, dataset.inst_num, shuffle)
        loader = DataLoader(dataset, batch_size=num_per_class*dataset.class_num, sampler=sampler, num_workers=num_workers)
    return loader

# TCN_OUT_CHANNEL = 64                        # Num of channels of output of TCN
# RELATION_DIM = 32                           # Dim of one layer of relation net
# CLASS_NUM = 5                               # <X>-way  | Num of classes
# SAMPLE_NUM = 5                              # <Y>-shot | Num of supports per class
# QUERY_NUM = 3                               # Num of instances for query per class
# TRAIN_EPISODE = 30000                       # Num of training episode 
# VALIDATION_EPISODE = 50                     # Num of validation episode
# VALIDATION_FREQUENCY = 200                  # After each <X> training episodes, do validation once
# LEARNING_RATE = 0.0001                      # Initial learning rate
# FRAME_NUM = 10                              # Num of frames per clip
# CLIP_NUM = 5                                # Num of clips per window
# WINDOW_NUM = 3                              # Num of processing window per video
# INST_NUM = 15                               # Num of videos selected in each class
# GPU = "4,5,6,7,8"                           # Index of GPU to be used
# EXP_NAME = "(tmp)CTC_Blank_MOT_Kinetics400_Attention_v2_5W5S"                # Name of this experiment

# # Dataset
# ##################################################################################################################
# DATASET = "kinetics"             # "kinetics" or "haa" or "full_kinetics"

# TRAIN_SPLIT = "splits/tmp_train.txt"                
# VAL_SPLIT = "splits/tmp_val.txt"
# TEST_SPLIT = "splits/test.txt"                    

# KINETICS_DATA_FOLDERS = ["/data/ssongad/kinetics400/frame/train",
#                          "/data/ssongad/kinetics400/frame/test"]
# def read_split(file_path):
#     result = []
#     if os.path.exists(file_path):
#         file = open(file_path, "r")
#         lines = file.readlines()
#         file.close()

#         for line in lines:
#             result.append(line.rstrip())
            
#     return result

# TRAIN_SPLIT = read_split(TRAIN_SPLIT)
# VAL_SPLIT = read_split(VAL_SPLIT)
# TEST_SPLIT = read_split(TEST_SPLIT)
# the_dataset = KineticsDataset(KINETICS_DATA_FOLDERS, "train", (TRAIN_SPLIT, VAL_SPLIT, TEST_SPLIT), CLASS_NUM, SAMPLE_NUM, INST_NUM, FRAME_NUM, CLIP_NUM, WINDOW_NUM)
# sample_dataloader = get_data_loader(the_dataset, True, num_per_class=SAMPLE_NUM, num_workers=5)
# samples, _ = sample_dataloader.__iter__().next()