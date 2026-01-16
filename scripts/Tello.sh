#!/bin/bash

IMG_SAVE_PATH=./src/Tello/FOV

/home/sadman/miniconda/envs/llamauav/bin/python -u ./src/drone_controller.py \
    --img_save_path $IMG_SAVE_PATH