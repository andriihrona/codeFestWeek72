import freenect
import cv2
import numpy as np
from screeninfo import get_monitors 

def get_depth():
    return freenect.sync_get_depth()[0]

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

def raw_depth_to_centimeters(raw_depth):
  if raw_depth < 2047:
   metres = 1.0 / (raw_depth * -0.0030711016 + 3.3309495161)
   return int(metres * 100)
  return 0

def raw_depth_from_centimeters(centimeters):
    metres = centimeters / 100.0
    if metres > 0:
        raw_depth = (1.0 / metres - 3.3309495161) / -0.0030711016
        return int(raw_depth)
    return 2047

def normalize(depth, max_cm=45):
    min_depth_ctm = raw_depth_to_centimeters(np.min(depth))
    seuil_depth = raw_depth_from_centimeters(min_depth_ctm + max_cm)
    d_min = np.min(depth)

    normalized_depth = np.where(depth < d_min, d_min, depth)
    print(normalized_depth)
    normalized_depth = np.where(normalized_depth > seuil_depth, seuil_depth, normalized_depth)

    max_v = np.max(normalized_depth)
    min_v = np.min(normalized_depth)
    normalized_depth = (normalized_depth - min_v / max_v - min_v) * 255
    normalized_depth = normalized_depth.astype(np.uint8)
    return normalized_depth

def apply_colormap(depth, min_depth=0, max_depth=255):
    depth = np.clip(depth.astype(np.uint8), min_depth, max_depth)
    # depth = normalize(depth)
    depth_colormap = cv2.applyColorMap(depth, cv2.COLORMAP_TURBO)
    depth_colormap = depth_colormap[:, :, [0, 2, 1]]
    return depth_colormap

def normalise_depth(depth_map):
    # depth_map = normalize(depth_map)

    c = depth_map[:, :]

    THRESHOLD = 1

    THRESHOLD_WATER = int(85 * THRESHOLD)
    THRESHOLD_MOUNTAIN = int(171 * THRESHOLD)

    c[(c >= 0) & (c <= THRESHOLD_WATER)] = 0
    c[(c > THRESHOLD_WATER) & (c <= THRESHOLD_MOUNTAIN)] = 1
    c[c > THRESHOLD_MOUNTAIN] = 2
    depth_map[:, :] = c
    return depth_map

if __name__ == "__main__":
    projector = find_projector_screen()
    while 1:
        if freenect.sync_get_depth() is None:
            break
        depth = get_depth()
        depth_colormap = apply_colormap(depth)
        show_image_on_projector(depth_colormap, projector)
        if cv2.waitKey(1) & 0xFF == 27:
            break