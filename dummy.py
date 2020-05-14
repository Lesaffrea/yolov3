#
#  This script is the one to use after installation
#
#
import torchvision
import torch
#  Test that we can load  the way to install is not to use
# the anaconda install if you se tis environment
import cv2


torch.__version__
torchvision .__version__



# We try torch vison
check = torchvision.get_image_backend()

import torch.jit
import torch._utils_internal


names ='torchvision'
# Check !!
torch.ops.torchvision.nms

torchvision.ops.roi_align

torchvision.ops.nms