import numpy as np
input_size = 416
XYSCALE = [1.2, 1.1, 1.05]
def get_anchors(anchors_path, tiny=False):
    '''loads the anchors from a file'''
    with open(anchors_path) as f:
        anchors = f.readline()
    anchors = np.array(anchors.split(','), dtype=np.float32)
    return anchors.reshape(3, 3, 2)
ANCHORS = get_anchors("ml_model/yolov4_anchors.txt")
STRIDES = np.array([8, 16, 32])


classes = {}
with open("ml_model/coco.names", 'r') as data:
    for ID, name in enumerate(data):
        classes[ID] = name.strip('\n')




