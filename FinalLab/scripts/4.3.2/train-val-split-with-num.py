Split between train and val folders
from pathlib import Path
import random
import os
import sys
import shutil
import argparse

data_path = "custom_data"
num_distinct_images = 110
num_augmentation = 3
train_percent = 0.9


if not os.path.isdir(data_path):
    print('Directory specified by --datapath not found. Verify the path is correct (and uses double back slashes if on Windows) and try again.')
    sys.exit(0)
if train_percent < .01 or train_percent > 0.99:
    print('Invalid entry for train_pct. Please enter a number between .01 and .99.')
    sys.exit(0)
val_percent = 1 - train_percent

input_image_path = os.path.join(data_path,'images')
input_label_path = os.path.join(data_path,'labels')

cwd = os.getcwd()
train_img_path = os.path.join(cwd,'data/train/images')
train_txt_path = os.path.join(cwd,'data/train/labels')
val_img_path = os.path.join(cwd,'data/validation/images')
val_txt_path = os.path.join(cwd,'data/validation/labels')

for dir_path in [train_img_path, train_txt_path, val_img_path, val_txt_path]:
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
        print(f'Created folder at {dir_path}.')

train_num = int(num_distinct_images*train_percent)
val_num = num_distinct_images - train_num
print('Images moving to train: %d' % train_num)
print('Images moving to validation: %d' % val_num)

def move_to_val(img_fn, txt_fn):
    if os.path.exists(os.path.join(input_image_path, img_fn)):
        shutil.copy(os.path.join(input_image_path, img_fn), os.path.join(val_img_path, img_fn))
    if os.path.exists(os.path.join(input_label_path, txt_fn)):
        shutil.copy(os.path.join(input_label_path, txt_fn), os.path.join(val_txt_path, txt_fn))

def move_to_train(img_fn, txt_fn):
    if os.path.exists(os.path.join(input_image_path, img_fn)):
        shutil.copy(os.path.join(input_image_path, img_fn), os.path.join(train_img_path, img_fn))
    if os.path.exists(os.path.join(input_label_path, txt_fn)):
        shutil.copy(os.path.join(input_label_path, txt_fn), os.path.join(train_txt_path, txt_fn))

img_nums = [i for i in range(num_distinct_images)]
while train_num > 0:
    selected_num = random.choice(img_nums)
    img_num = str(selected_num+1)
    img_fn = img_num + '.jpg'
    txt_fn = img_num + '.txt'
    move_to_train(img_fn, txt_fn)

    for i in range(1, num_augmentation+1):
        img_fn = img_num + f"_aug_{i}.jpg"
        txt_fn = img_num + f"_aug_{i}.txt"
        move_to_train(img_fn, txt_fn)
    img_nums.remove(selected_num)
    train_num -= 1

print("val: ", img_nums)
for img_num in img_nums:
    img_num = str(img_num+1)

    img_fn = img_num + '.jpg'
    txt_fn = img_num + '.txt'
    move_to_val(img_fn, txt_fn)

  for i in range(1, num_augmentation+1):
    img_fn = img_num + f"_aug_{i}.jpg"
    txt_fn = img_num + f"_aug_{i}.txt"
    move_to_val(img_fn, txt_fn)