from tflite_support import metadata


displayer = metadata.MetadataDisplayer.with_model_file(
    "/content/best_float32_with_metadata.tflite"
)

print(displayer.get_metadata_json())
print(displayer.get_packed_associated_file_list())
