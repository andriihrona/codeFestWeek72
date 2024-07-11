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

def find_max_min_value(heightmap):
    max_value = np.max(heightmap)
    min_value = np.min(heightmap)
    print(f"Max value: {max_value}, Min value: {min_value}")

# def apply_colormap(depth, min_depth=0, max_depth=255, mean=100):
#     depth = np.clip(depth.astype(np.uint8), min_depth, max_depth)
#     depth = ((depth - min_depth) / (max_depth - min_depth) * 255).astype(np.uint8)

#     blue_threshold = int(mean + min_depth / 3)
#     green_threshold = int(mean + max_depth / 2)

#     colormap = np.zeros((256, 1, 3), dtype=np.uint8)
#     colormap[:blue_threshold, 0, 2] = 255 #Bleu
#     colormap[blue_threshold:green_threshold, 0, 1] = 255 #Vert
#     colormap[green_threshold:, 0, 0] = 255 #Rouge

#     depth_colormap = cv2.applyColorMap(depth, colormap)
#     #RGB 012
#     #
#     depth_colormap = depth_colormap[:,:, [2, 0, 1]]
#     return depth_colormap 
# # 
def apply_colormap(depth, min_depth=0, max_depth=255):
    depth = np.clip(depth.astype(np.uint8), min_depth, max_depth)
    # depth = ((depth - min_depth) / (max_depth - min_depth) * 255).astype(np.uint8)

  #  blue_threshold = int(mean + min_depth / 3)
  #  green_threshold = int(mean + max_depth / 2)

   # colormap = np.zeros((256, 1, 3), dtype=np.uint8)
   # colormap[:blue_threshold, 0, 0] = 255 #Bleu
  #  colormap[blue_threshold:green_threshold, 0, 1] = 255 #Vert
 #   colormap[green_threshold:, 0, 2] = 255 #Rouge

    depth_colormap = cv2.applyColorMap(depth, cv2.COLORMAP_TURBO)
    depth_colormap = depth_colormap[:, :, [0, 2, 1]]
    return depth_colormap

def normalise_depth(depth_map):
    print('shape', depth_map.shape)
    c = depth_map[:, :]
    c[(c >= 0) & (c <= 85)] = 0
    c[(c >= 86) & (c <= 145)] = 1
    c[c > 145] = 2
    depth_map[:, :] = c
    return depth_map

if __name__ == "__main__":
    projector = find_projector_screen()
    while 1:
        if freenect.sync_get_depth() is None:
            break
        depth = get_depth()
        depth_colormap = apply_colormap(depth)
        find_max_min_value(depth_colormap)
        show_image_on_projector(depth_colormap, projector)
        if cv2.waitKey(1) & 0xFF == 27:
            break