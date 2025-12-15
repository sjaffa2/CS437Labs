import json

with open("./all_images.json", "r") as file:
    data = json.load(file)

IMAGES = 'images'
ANNOTATIONS = 'annotations'
CATEGORIES = 'categories'
ID = 'id'
FILENAME = 'file_name'
IMAGE_ID = 'image_id'
TRAIN = 0
VAL = 1
TEST = 2

train_json = {}
train_json[CATEGORIES] = data[CATEGORIES]
train_json[IMAGES] = []
train_json[ANNOTATIONS] = []

val_json = {}
val_json[CATEGORIES] = data[CATEGORIES]
val_json[IMAGES] = []
val_json[ANNOTATIONS] = []

test_json = {}
test_json[CATEGORIES] = data[CATEGORIES]
test_json[IMAGES] = []
test_json[ANNOTATIONS] = []

id_map = {}
for image in data[IMAGES]:
    if FILENAME not in image:
        print("image has no filename: ", image)
        continue
    number = int(image[FILENAME].split('.')[0].split('_')[0])
    if number <= 100:
        train_json[IMAGES].append(image)
        id_map[image[ID]] = TRAIN
    elif number <= 105:
        val_json[IMAGES].append(image)
        id_map[image[ID]] = VAL
    else:
        test_json[IMAGES].append(image)
        id_map[image[ID]] = TEST

for annotation in data[ANNOTATIONS]:
    image_type = id_map[annotation[IMAGE_ID]]
    if image_type == TRAIN:
        train_json[ANNOTATIONS].append(annotation)
    elif image_type == VAL:
        val_json[ANNOTATIONS].append(annotation)
    if image_type == TEST:
        test_json[ANNOTATIONS].append(annotation)

with open("./train/_annotations.coco.json", "w") as f:
    json.dump(train_json, f, indent=4)

with open("./valid/_annotations.coco.json", "w") as f:
    json.dump(val_json, f, indent=4)

with open("./test/_annotations.coco.json", "w") as f:
    json.dump(test_json, f, indent=4)