import freenect
import cv2
import frame_convert
import matplotlib.pyplot as plt
import numpy as np
from screeninfo import get_monitors 
import time


def get_depth():
    return freenect.sync_get_depth()[0]

def get_video():
    return frame_convert.video_cv(freenect.sync_get_video()[0])

def find_projector_screen():
    monitors = get_monitors()
    if len(monitors) > 1:
        for monitor in monitors:
            if ((monitor.name.__contains__("HDMI"))):
                return monitor
    print("Projector screen not found. Make sure the projector is connected (using built-in display for now).")
    return monitors[0]

def show_image_on_projector(image, projector, frame_rate=60):
    window_name = 'Projector'
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.moveWindow(window_name, projector.x, projector.y)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    resized_image = cv2.resize(image, (projector.width, projector.height), interpolation = cv2.INTER_AREA) 

    cv2.imshow(window_name, resized_image)
    # Wait to match the frame rate
    cv2.waitKey(int(1/frame_rate * 1000))

if __name__ == "__main__":
    projector = find_projector_screen()
    while 1:
        if freenect.sync_get_depth() is None:
            break
        depth = get_depth()
        depth_colormap = frame_convert.apply_viridis_colormap(depth) 
        show_image_on_projector(depth_colormap, projector) 
        if cv2.waitKey(1) & 0xFF == 27:
            break