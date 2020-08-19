#
#
#  This script is part of the solution to build a stand alone video analyser, this script includes
#  the building of the prediction model. The weights have been already tailored for the prediction wanted,
#  its name is given as input parameter.
#
#  Notes: the device for calculation is cpu
#
#   Input: names weights
#
#   Output: Model object
#
def build_model( weight_name = None )
    device = 'cpu'
    if weight_name is None:
        weight_name ='weights/yolov3-spp-ultralytics.pt'
    # Build the model we load the two classes configuration
    # Those parameters could be pushed as parameter specially the size which
    # could be assessed using benchmark
    model = Darknet('cfg/yolov3-spp_3.cfg',
                    416)
    model.load_state_dict(torch.load('weights/weight_ppe_23_05_190_2.pt', map_location='device')['model'])
    # Fuse the model
    model.fuse()
    model.to(device)
    return  model


