import cv2
import mediapipe as mp
import time
import numpy as np
import os
import sys
import subprocess
import argparse
import json

mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_draw = mp.solutions.drawing_utils
drawing_spec = mp_draw.DrawingSpec()
drawing_spec.color = (0, 0, 255)

def process_video(video, lm_path):
    global pose, drawing_spec, mp_pose, mp_draw
    frameLandmarks = []

    while True:
        success, img = video.read()
        if not success:
            break

        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = pose.process(imgRGB)
        landmarks = []
        if results.pose_landmarks:
            for lm in results.pose_landmarks.landmark:
                h, w, c = img.shape
                cx, cy = int(lm.x*w), int(lm.y*h)
                landmarks.append({"x": lm.x, "y": lm.y, "z": lm.z})
        frameLandmarks.append(landmarks)

    lm_file = open(lm_path, "w+")
    lm_file.write(json.dumps(frameLandmarks))
    lm_file.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('input')
    parser.add_argument('output')
    args = parser.parse_args()
    video = cv2.VideoCapture(args.input)
    process_video(video, args.output)
    video.release()

