import os
import json
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras import layers, models
from PIL import Image

'''Handles fruit image classification predictions using a pre-trained TensorFlow model.'''

# with tf.device('/CPU:0'):
#     model = tf.keras.models.load_model("fruit_model.h5")


'''
dataset_path = "C:/Users/I_NEE/Desktop/AI 3rd/Fruit Bot/fruit_FIDS30" # foldernamesascategories...

if not os.path.isdir(dataset_path):
    print("Invalid dataset path, exiting.")
    exit()


# Settings
IMAGE_SIZE = (256, 256) ##### ##### #####
BATCH_SIZE = 32
EPOCHS = 50

train_datagen = ImageDataGenerator(
    rescale=1./255,
    validation_split=0.2,
    rotation_range=20,
    zoom_range=0.2,
    horizontal_flip=True
)

train_generator = train_datagen.flow_from_directory(
    dataset_path,
    target_size=IMAGE_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='training'
)

val_generator = train_datagen.flow_from_directory(
    dataset_path,
    target_size=IMAGE_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='validation'
)

model = models.Sequential([
    layers.Conv2D(32, (3, 3), activation='relu', input_shape=(*IMAGE_SIZE, 3)),
    layers.MaxPooling2D((2, 2)),

    layers.Conv2D(64, (3, 3), activation='relu'),
    layers.MaxPooling2D((2, 2)),

    layers.Conv2D(128, (3, 3), activation='relu'),
    layers.MaxPooling2D((2, 2)),

    layers.Flatten(),
    layers.Dense(256, activation='relu'),
    layers.Dropout(0.5),
    layers.Dense(train_generator.num_classes, activation='softmax')
])

model.compile(optimizer='adam',
              loss='categorical_crossentropy',
              metrics=['accuracy'])

print("Training the model...")
history = model.fit(train_generator,
                    validation_data=val_generator,
                    epochs=EPOCHS)

loss, acc = model.evaluate(val_generator)
print(f"Validation Accuracy: {acc * 100:.2f}%")

model.save("fruit_model.h5")
print("Model saved as fruit_model.h5")

class_indices = train_generator.class_indices
inv_class_indices = {v: k for k, v in class_indices.items()}

with open("fruit_categories.json", "w") as f:
    json.dump(inv_class_indices, f)
print("Class mapping saved to fruit_categories.json")

'''

##### ##### ##### ##### ##### ##### ##### ##### ##### ##### #####

def predict_image(model, image_size, json_filepath, image_path):
    '''Predicts the fruit class from an image using the loaded model and a JSON mapping file.'''
    with open(json_filepath, "r") as f:
        inv_class_indices = json.load(f)
    
    if not image_path:
        print("No image provided for prediction.")
        return
    img = Image.open(image_path)
    img = img.resize(image_size, Image.LANCZOS)
    img_array = np.array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    
    preds = model.predict(img_array)
    best_idx = np.argmax(preds)
    confidence = preds[0][best_idx]
    best_label = inv_class_indices.get(str(best_idx), "Unknown")
    
    print(f"My best guess is {best_label} with {confidence * 100:.2f}% confidence.")

    return f"My best guess is {best_label} with {confidence * 100:.2f}% confidence."
    
# IMAGE_SIZE = (256, 256) ##### ##### #####   
# model = tf.keras.models.load_model("fruit_model.h5")
 
# predict_image(model, IMAGE_SIZE, "fruit_categories.json", '33.jpg')
