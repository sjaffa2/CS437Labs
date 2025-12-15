from pathlib import Path

import globox


def main() -> None:
  image_path = Path("/base_path/images")
  label_path = Path("/base_path/labels")
  save_file = Path("/base_path/coco_transformed.json")

  annotations = globox.AnnotationSet.from_yolo_v5(label_path, image_folder=image_path)
  annotations.save_coco(save_file, auto_ids=True)


if __name__ == "__main__":
    main()
