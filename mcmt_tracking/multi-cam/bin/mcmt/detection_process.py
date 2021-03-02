from multiprocessing import Process
import numpy as np
import cv2
import sys
import csv
import time

# local imported codes
sys.path.append('../utility/')
from object_tracking_util import Camera, scalar_to_rgb, setup_system_objects, \
                                    single_cam_detector, multi_cam_detector


class SingleCameraDetector(Process):
    """
    Process for single camera detection
    """
    def __init__(self, filename, index, queue, FPS, FRAME_WIDTH, FRAME_HEIGHT, SCALE_FACTOR):
        super().__init__()
        self.filename = filename
        self.queue = queue
        self.index = index
        self.fps = FPS
        self.frame_h = FRAME_HEIGHT
        self.frame_w = FRAME_WIDTH
        self.scale_factor = SCALE_FACTOR
        self.cap = None
        self.fgbg, self.detector = setup_system_objects(FPS, SCALE_FACTOR)
        self.video_ends_indicator = 0
        self.frame_count = 0
        self.frame = None
        self.good_tracks = None
        self.origin = np.array([0, 0])
        self.tracks = []
        self.next_id = 0

    def run(self):
        self.cap = cv2.VideoCapture(self.filename)
        self.cap.set(3, self.frame_w)
        self.cap.set(4, self.frame_h)
        self.cap.set(5, self.fps)

        # check if video capturing is successful
        ret, self.frame = self.cap.read()
        if ret:
            print(f"Video Capture {self.filename}: PASS")
        else:
            print(f"Video Capture {self.filename}: FAIL")
            self.cap.release()

        while self.cap.isOpened():
            ret, self.frame = self.cap.read()
            if ret:
                self.frame = cv2.resize(self.frame, (self.frame_w, self.frame_h))

                self.good_tracks, self.tracks, self.next_id, self.frame = single_cam_detector(
                    self.tracks, self.next_id, self.index, self.fgbg, self.detector, self.fps,
                    self.frame_w, self.frame_h, self.scale_factor, self.origin, self.frame)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            else:
                self.video_ends_indicator = 1
                break

            self.queue.put((self.good_tracks, self.frame_count, self.frame))
            self.frame_count += 1

            if self.video_ends_indicator == 1:
                break

        self.cap.release()
        cv2.destroyAllWindows()


class MultiCameraDetector(Process):
    """
    Process for multi camera detection
    """
    def __init__(self, filenames, queue, FPS, FRAME_WIDTH, FRAME_HEIGHT, SCALE_FACTOR):
        super().__init__()
        self.filenames = filenames
        self.cameras = []
        self.queue = queue
        self.fps = FPS
        self.frame_h = FRAME_HEIGHT
        self.frame_w = FRAME_WIDTH
        self.scale_factor = SCALE_FACTOR
        _, self.detector = setup_system_objects(FPS, SCALE_FACTOR)
        self.video_ends_indicator = 0
        self.frame_count = 0
        self.good_tracks = None
        self.frame = None
        self.start_timer = None
        self.end_timer = None

    def run(self):
        for filename in self.filenames:
            camera = Camera(filename, self.fps, self.frame_h, self.frame_w, self.scale_factor)
            ret, self.frame = camera.cap.read()
            if ret:
                self.cameras.append(camera)
                print(f"Video Capture {filename}: PASS")
                camera.init_fgbg()
            else:
                print(f"Video Capture {filename}: FAIL")
                camera.cap.release()

        while True:
            self.start_timer = time.time()
            sendList = []
            for index, camera in enumerate(self.cameras):
                ret, self.frame = camera.cap.read()

                if ret:
                    self.frame = cv2.resize(self.frame, (self.frame_w, self.frame_h))
                    self.good_tracks, self.frame = multi_cam_detector(camera, self.detector, self.frame)

                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        self.video_ends_indicator = 1
                        break

                else:
                    self.video_ends_indicator = 1
                    break

                sendList.append((self.good_tracks, self.frame, camera.dead_tracks))

            # sendList: [(good_tracks_0, frame_0, dead_tracks_0), (good_tracks_1, frame_1, dead_tracks_1), frame_count]
            sendList.append((self.frame_count))
            self.queue.put(sendList)
            self.frame_count += 1

            if self.video_ends_indicator == 1:
                break

            self.end_timer = time.time()
            print(f"Detection process took: {self.end_timer - self.start_timer}")

        cv2.destroyAllWindows()

        for index, camera in enumerate(self.cameras):
            camera.cap.release()
            with open(f"data_out_{index}.csv", 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                for row in camera.output_log:
                    writer.writerow(row)
