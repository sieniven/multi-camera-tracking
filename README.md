# **Multi-camera surveillance system for multiple target tracking capabilities**

## Information

Hello! This project is to develop software capabilities for a real-time multi-camera surveillance system monitoring a specific areas. Some use cases include traffic junctions, security of a demarcated area, etc. 

This project aims to develop a multiple target tracking system using these cameras to track and localize small and fast moving targets using motion-based features. Using appearance-based features in this case is difficult, as these targets often appear as small black "dots/blobs" in video frames. The aim of the project is to be able to continuously track, re-identify these targets between the cameras, and montor their 3-dimensional coordinates when they are in the monitored space. 

## Capabilities

The current software is able to track multiple targets in each camera frame. The software implements computer vision techniques such as blob detection, background subtractions, etc. 

It also implements the DeepSort algorithm to continuously track and localize these targets. Filtering techiques such as Kalman filtering (KF), Extended KF, Kernelized Correlation filter, Discriminative Correlation filter and Particle filter are also implemented as state estimation techniques. As these targets move at fast and erratic speeds, it is important to implement state estimation to predict their positions for continuous tracking.

In addition, the software has re-identification capabilities between targets. This would mean that every camera will be able to know that they are tracking the same target. We use cross-correlation of their kinematic-based feature signals to match these targets. I am currently working on improving the accuracy of this capability, by developing a binary classification model to re-identify targets between cameras.

## Running the software

Running the software:
``` bash
cd ./mcmt_tracking/multi-cam/bin/
python mcmt_tracker.py
```

* To configure the tracker to run in real-time, change to cameras = [ 0, 1] in main body.

* To configure the tracking to run on video files, change cameras list to input the respective video filenames.