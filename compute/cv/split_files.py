import os
import shutil
import random

# paths
BASE_DIR = "cv\\dataset"
IMG_DIR = os.path.join(BASE_DIR, "images")
LBL_DIR = os.path.join(BASE_DIR, "labels")
DATASET_DIR = 'cv\\bed'

TRAIN_RATIO = 0.8
SEED = 42

random.seed(SEED)

# create output dirs
for split in ["train", "val"]:
    os.makedirs(os.path.join(IMG_DIR, split), exist_ok=True)
    os.makedirs(os.path.join(LBL_DIR, split), exist_ok=True)

# get all images
images = [f for f in os.listdir(DATASET_DIR) if f.endswith((".jpg", ".png", ".jpeg"))]

random.shuffle(images)

split_idx = int(len(images) * TRAIN_RATIO)
train_imgs = images[:split_idx]
val_imgs = images[split_idx:]

def move_files(file_list, split):
    for img in file_list:
        label = os.path.splitext(img)[0] + ".txt"

        src_img = os.path.join(DATASET_DIR, img)
        src_lbl = os.path.join(DATASET_DIR, 'labels', label)
        
        print(src_img)
        print(src_lbl)

        dst_img = os.path.join(IMG_DIR, split, img)
        dst_lbl = os.path.join(LBL_DIR, split, label)
        
        print(dst_img)
        print(dst_lbl)

        # safety check
        if not os.path.exists(src_lbl):
            print(f"⚠️ Missing label for {img}, skipping")
            continue

        shutil.move(src_img, dst_img)
        shutil.move(src_lbl, dst_lbl)

move_files(train_imgs, "train")
move_files(val_imgs, "val")

print(f"✅ Done: {len(train_imgs)} train, {len(val_imgs)} val")

import os

LABEL_DIR = "cv/dataset/labels"

def remap_label_file(path):
    with open(path, "r") as f:
        lines = f.readlines()

    new_lines = []
    for line in lines:
        parts = line.strip().split()
        if not parts:
            continue

        # force class 8 -> 0
        parts[0] = "0"
        new_lines.append(" ".join(parts) + "\n")

    with open(path, "w") as f:
        f.writelines(new_lines)

for root, _, files in os.walk(LABEL_DIR):
    for file in files:
        if file.endswith(".txt"):
            remap_label_file(os.path.join(root, file))

print("✅ Remapped class 8 → 0 in all label files")

