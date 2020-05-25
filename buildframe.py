#
#
#  Read the video and build images
#
#  Note: we have one issue with video one as it has a water mark
#
from PIL import Image
import matplotlib.pyplot as plt
from utils.read_video import *

#
#  Save array to image
#
def save_image( image_array, name ):
    tmp_image = Image.fromarray(image_array)
    tmp_image.save(name)

#
#  Simple small function
#
video1 = "./video/video_1.mp4"
video2 = "./video/video_2.mp4"
# Use cv2 to get 5 images out of video
fewframes = get_frames(video1, n_frames=5)
# Get image and display
image_1 = fewframes[0][0]
plt.imshow(image_1)
# save the array as image to image 1
# We build 3 images
save_image(image_1, "./video/video_1_1.jpg")
save_image(fewframes[0][3], "./video/video_1_2.jpg")
save_image(fewframes[0][5], "./video/video_1_3.jpg")




