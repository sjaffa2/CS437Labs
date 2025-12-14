from tflite_support.metadata_writers import object_detector
from tflite_support.metadata_writers import writer_utils

ObjectDetectorWriter = object_detector.MetadataWriter
_MODEL_PATH = "best_float32.tflite"
_LABEL_FILE = "labels.txt"
_SAVE_TO_PATH = "best_float32_with_metadata.tflite"
_INPUT_NORM_MEAN = 0
_INPUT_NORM_STD = 255

writer = ObjectDetectorWriter.create_for_inference(
    writer_utils.load_file(_MODEL_PATH), [_INPUT_NORM_MEAN], [_INPUT_NORM_STD],
    [_LABEL_FILE])

print(writer.get_metadata_json())

writer_utils.save_file(writer.populate(), _SAVE_TO_PATH)