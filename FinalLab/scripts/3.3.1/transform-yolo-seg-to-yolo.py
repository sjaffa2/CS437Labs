import os

def convert_yolo_seg_to_det(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    for filename in os.listdir(input_dir):
        if not filename.endswith(".txt"):
            continue

        infile = os.path.join(input_dir, filename)
        outfile = os.path.join(output_dir, filename)

        with open(infile, "r") as f:
            lines = f.readlines()

        new_lines = []
        for line in lines:
            parts = list(map(float, line.strip().split()))
            if len(parts) < 3:
                continue

            class_id = int(parts[0])
            coords = parts[1:]
            xs = coords[0::2]
            ys = coords[1::2]

            x_min, x_max = min(xs), max(xs)
            y_min, y_max = min(ys), max(ys)

            x_center = (x_min + x_max) / 2
            y_center = (y_min + y_max) / 2
            width = x_max - x_min
            height = y_max - y_min

            new_line = f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n"
            new_lines.append(new_line)

        with open(outfile, "w") as f:
            f.writelines(new_lines)

    print(f"Converted {len(os.listdir(input_dir))} label files to detection format in: {output_dir}")

# Example usage
convert_yolo_seg_to_det(
    input_dir="/base_path/labels/train",
    output_dir="/base_path/labels2"
)
