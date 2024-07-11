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


MIN_DEPTH = 400
MAX_DEPTH = 550
AVERAGE_DEPTH = MAX_DEPTH - MIN_DEPTH

def apply_custom_colormap(depth, min_depth=400, max_depth=550):
    depth = np.clip(depth.astype(np.float32), min_depth, max_depth)
    depth = ((depth - min_depth) / (max_depth - min_depth) * 255).astype(np.uint8)
    find_max_min_value(depth)
    colormap = np.colormap((256, 1, 3), dtype=np.uint8)

    # for i in range(256):
    #     if i < 128:
    #         colormap[i, 0, 0] = 255 - 2 * i  # Red decreases
    #         colormap[i, 0, 1] = 2 * i        # Green increases
    #         colormap[i, 0, 2] = 255          # Blue stays at max
    #     else:
    #         colormap[i, 0, 0] = 255          # Red stays at max
    #         colormap[i, 0, 1] = 255 - 2 * (i - 128)  # Green decreases
    #         colormap[i, 0, 2] = 2 * (i - 128)        # Blue increases
    

    colormap[:, 0, 0] = 255 - np.linspace(0, 255, 256)  # Red decreases from 255 to 0
    colormap[:, 0, 1] = np.linspace(0, 255, 256)  # Green increases from 0 to 255
    colormap[:128, 0, 2] = 255  # Blue stays at 255 for the first half
    colormap[128:, 0, 2] = np.linspace(255, 0, 128)  # Blue decreases from 255 to 0 for the second half
    
    depth_colormap = cv2.applyColorMap(depth, colormap)
    return depth_colormap

def apply_custom_colormap(depth, min_depth=400, max_depth=550):

    colormap = np.colormap((256, 1, 3), dtype=np.uint8)
    colormap[:, 0, 0] = 255 - np.linspace(0, 255, 256)  # Red decreases from 255 to 0
    colormap[:, 0, 1] = np.linspace(0, 255, 256)  # Green increases from 0 to 255
    colormap[:128, 0, 2] = 255  # Blue stays at 255 for the first half
    colormap[128:, 0, 2] = np.linspace(255, 0, 128)  # Blue decreases from 255 to 0 for the second half
    
    depth_colormap = cv2.applyColorMap(depth, colormap)
    return depth_colormap

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
    depth_colormap = depth_colormap[:, :, [0, 1, 2]]
    return depth_colormap

if __name__ == "__main__":
    projector = find_projector_screen()
    while 1:
        if freenect.sync_get_depth() is None:
            break
        # print('message')
        depth = get_depth()
        vmin = np.min(depth)

        #find_max_min_value(depth)
        #depth_colormap = frame_convert.apply_viridis_colormap(depth)
        depth_colormap = apply_colormap(depth)
        # find_max_min_value(depth_colormap)
        show_image_on_projector(depth_colormap, projector)
        if cv2.waitKey(1) & 0xFF == 27:
            break