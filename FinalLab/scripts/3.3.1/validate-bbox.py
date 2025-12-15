import os

def check_boxes(b):
    xmin, ymin, xmax, ymax = b
    if xmin < 0 or ymin < 0 or xmax < 0 or ymax < 0:
        print("Negative coordinate:", b)
    if xmax <= xmin or ymax <= ymin:
        print("Invalid box:", b)

def check_labels(label_dir):
    for filename in os.listdir(label_dir):

        infile = os.path.join(label_dir, filename)
        with open(infile, "r") as f:
            lines = f.readlines()
        
        for line in lines:
            coords = line.split(' ')
            cls_type = int(coords[0])
            check_boxes((float(coords[1]), float(coords[2]), float(coords[3]), float(coords[4])))

check_labels(
    label_dir="/base_path/labels"
)