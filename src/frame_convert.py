import numpy as np
import cv2


def apply_viridis_colormap(depth, min_depth=400, max_depth=550):
    """
    Apply the Viridis colormap to the depth data.
    The minimum detection distance of the Xbox360 Kinect is around 400mm.
    The maximum detection distance of the Xbox360 Kinect is around 5000mm.
    """
    depth = np.clip(depth, min_depth, max_depth)
    depth = ((depth - min_depth) / (max_depth - min_depth) * 255).astype(np.uint8)
    depth_colormap = cv2.applyColorMap(depth, cv2.COLORMAP_VIRIDIS) 
    return depth_colormap


def video_cv(video):
    """Converts video into a BGR format for opencv

    This is abstracted out to allow for experimentation

    Args:
        video: A numpy array with 1 byte per pixel, 3 channels RGB

    Returns:
        An opencv image who's datatype is 1 byte, 3 channel BGR
    """
    video = video[:, :, ::-1]  # RGB -> BGR
    return video