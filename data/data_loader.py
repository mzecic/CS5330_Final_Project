from mediapipe_model_maker.python.vision import gesture_recognizer

# Set up data preprocessing parameters (adjust confidence thresholds as needed)
hand_params = gesture_recognizer.HandDataPreprocessingParams(min_detection_confidence=0.5)

# Specify the path to your dataset folder
dataset_path = "data"

# Load the dataset; MediaPipe will process the images to extract hand landmarks
data = gesture_recognizer.Dataset.from_folder(dataset_path, hand_params)

# Print labels inferred from subfolder names
print("Labels:", data.labels_names)

# Split the dataset into training, validation, and testing sets (e.g., 80-10-10 split)
train_data, rest_data = data.split(0.8)
validation_data, test_data = rest_data.split(0.5)

# Set up training hyperparameters (adjust epochs, batch size, learning rate as needed)
hparams_train = gesture_recognizer.HParams(
    export_dir="exported_model",
    epochs=10,
    batch_size=32,
    learning_rate=0.001
)
options = gesture_recognizer.GestureRecognizerOptions(hparams=hparams_train)

# Fine-tune the gesture recognizer on your custom dataset
model = gesture_recognizer.GestureRecognizer.create(
    train_data=train_data,
    validation_data=validation_data,
    options=options
)

model.export_model()
