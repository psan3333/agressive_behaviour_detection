import torch
import torch.nn as nn
import torch.optim as optim
import torchvision
import torchvision.transforms as transforms
import cv2
from torch.utils.data import Dataset
import pandas as pd
import numpy as np
from torch.utils.data import DataLoader
import torch.nn.functional as F


class GodHelpMe(nn.Module):
    
    def __init__(self):
        super(GodHelpMe, self).__init__()
        self.relu = nn.ReLU()
        self.sigmoid = nn.Sigmoid()
        # Part 1
        self.conv_layer1 = nn.Conv2d(in_channels=3, out_channels=12, kernel_size=3)
        self.conv_layer1_batch = nn.BatchNorm2d(12, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True)
        self.conv_layer2 = nn.Conv2d(in_channels=12, out_channels=16, kernel_size=3)
        self.conv_layer2_batch = nn.BatchNorm2d(16, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True)
        self.conv_layer3 = nn.Conv2d(in_channels=16, out_channels=32, kernel_size=3)
        self.conv_layer3_batch = nn.BatchNorm2d(32, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True)
        self.conv_layer4 = nn.Conv2d(in_channels = 32, out_channels=64, kernel_size=3)
        self.conv_layer4_batch = nn.BatchNorm2d(64, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True)
        self.conv_layer5 = nn.Conv2d(in_channels=64, out_channels=128, kernel_size=3)
        self.conv_layer5_batch = nn.BatchNorm2d(128, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True)
        self.conv_layer6 = nn.Conv2d(in_channels=128, out_channels=32, kernel_size=3)
        self.conv_layer6_batch = nn.BatchNorm2d(32, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True)
        self.conv_layer7 = nn.Conv2d(in_channels=32, out_channels=16, kernel_size=3)
        self.conv_layer7_batch = nn.BatchNorm2d(16, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True)
        self.conv_layer8 = nn.Conv2d(in_channels=16, out_channels=1, kernel_size=3)
        self.conv_layer8_batch = nn.BatchNorm2d(1, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True)

        # Part 2
        self.conv2_layer1 = nn.Conv2d(in_channels=100, out_channels=128, kernel_size=3)
        self.conv2_layer1_batch = nn.BatchNorm2d(128, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True)
        self.conv2_layer2 = nn.Conv2d(in_channels=128, out_channels=256, kernel_size=3)
        self.conv2_layer2_batch = nn.BatchNorm2d(256, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True)
        self.conv2_layer3 = nn.Conv2d(in_channels=256, out_channels=512, kernel_size=3)
        self.conv2_layer3_batch = nn.BatchNorm2d(512, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True)
        self.conv2_layer4 = nn.Conv2d(in_channels=512, out_channels=1024, kernel_size=5)
        self.conv2_layer4_batch = nn.BatchNorm2d(1024, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True)
        self.conv2_layer5 = nn.Conv2d(in_channels=1024, out_channels=1024, kernel_size=5)
        self.conv2_layer5_batch = nn.BatchNorm2d(1024, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True)
        self.conv2_layer6 = nn.Conv2d(in_channels=1024, out_channels=1024, kernel_size=5)
        self.conv2_layer6_batch = nn.BatchNorm2d(1024, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True)

        # Part 3
        self.fc_layer1 = nn.Linear(1024, 2048)
        self.fc_layer2 = nn.Linear(2048, 4056)
        self.fc_layer3 = nn.Linear(4056, 2048)
        self.fc_layer4 = nn.Linear(2048, 1024)
        self.fc_layer5 = nn.Linear(1024, 512)
        self.fc_layer6 = nn.Linear(512, 128)
        self.fc_layer7 = nn.Linear(128, 1)


    def forward(self, x):
        BATCH_SIZE = x.shape[0]
        SEQ_LENGTH = x.shape[1]
        IMG_SIZE = x.shape[3]
        #_________|Part 1|_____________
        x = x.view(BATCH_SIZE*SEQ_LENGTH, 3, IMG_SIZE, IMG_SIZE)
        x = self.relu(self.conv_layer1_batch(self.conv_layer1(x)))
        x = self.relu(self.conv_layer2_batch(self.conv_layer2(x)))
        x = self.relu(self.conv_layer3_batch(self.conv_layer3(x)))
        x = self.relu(self.conv_layer4_batch(self.conv_layer4(x)))
        x = self.relu(self.conv_layer5_batch(self.conv_layer5(x)))
        x = self.relu(self.conv_layer6_batch(self.conv_layer6(x)))
        x = self.relu(self.conv_layer7_batch(self.conv_layer7(x)))
        x = self.relu(self.conv_layer8_batch(self.conv_layer8(x)))
        #________________________
        x = x.view(BATCH_SIZE, SEQ_LENGTH, 1, 112, 112) #TODO вычислять значения
        x = x.squeeze(2)
        #_________|Part 2|_____________
        x = self.relu(self.conv2_layer1_batch(self.conv2_layer1(x)))
        x = self.relu(self.conv2_layer2_batch(self.conv2_layer2(x)))
        x = self.relu(self.conv2_layer3_batch(self.conv2_layer3(x)))
        x = self.relu(self.conv2_layer4_batch(self.conv2_layer4(x)))
        x = self.relu(self.conv2_layer5_batch(self.conv2_layer5(x)))
        x = self.relu(self.conv2_layer6_batch(self.conv2_layer6(x)))
        #______________________________
        x = F.adaptive_avg_pool2d(x, (1, 1))
        x = x.view(x.size(0), -1)
        #_________|Part 3|_____________
        x = self.sigmoid(self.fc_layer1(x))
        x = self.sigmoid(self.fc_layer2(x))
        x = self.sigmoid(self.fc_layer3(x))
        x = self.sigmoid(self.fc_layer4(x))
        x = self.sigmoid(self.fc_layer5(x))
        x = self.sigmoid(self.fc_layer6(x))
        x = self.sigmoid(self.fc_layer7(x))
        return x
#%%
