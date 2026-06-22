import os
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import GlobalAveragePooling2D, Dense, Dropout
from tensorflow.keras.models import Model

# Konfigurasi
IMG_WIDTH, IMG_HEIGHT = 224, 224
BATCH_SIZE = 32
EPOCHS = 10
# URUTAN KELAS HARUS COCOK DENGAN CONFIG BACKEND (Mentah, Matang, Busuk)
CLASSES = ['Unripe', 'Ripe', 'Rotten'] 

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TRAIN_DIR = os.path.join(BASE_DIR, 'dataset', 'train')
VAL_DIR = os.path.join(BASE_DIR, 'dataset', 'validation')
MODEL_DIR = os.path.join(BASE_DIR, 'model')

# Pastikan folder model ada
os.makedirs(MODEL_DIR, exist_ok=True)

def create_model():
    # Base model MobileNetV2 (ringan, cocok untuk TFLite)
    base_model = MobileNetV2(
        weights='imagenet', 
        include_top=False, 
        input_shape=(IMG_HEIGHT, IMG_WIDTH, 3)
    )
    
    # Freeze base model weights
    base_model.trainable = False

    # Tambahkan layer klasifikasi
    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dropout(0.2)(x)
    predictions = Dense(len(CLASSES), activation='softmax')(x)

    model = Model(inputs=base_model.input, outputs=predictions)
    
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    return model

def main():
    print("="*50)
    print("  Memulai Proses Training MangoCheck Model AI")
    print("="*50)

    # Data Generator dengan augmentasi dasar
    train_datagen = ImageDataGenerator(
        rescale=1./255,          # Normalization_Mode: "0_1"
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2,
        horizontal_flip=True,
        fill_mode='nearest'
    )
    
    val_datagen = ImageDataGenerator(rescale=1./255)

    print("\n[1/4] Menyiapkan Dataset...")
    train_generator = train_datagen.flow_from_directory(
        TRAIN_DIR,
        target_size=(IMG_HEIGHT, IMG_WIDTH),
        batch_size=BATCH_SIZE,
        classes=CLASSES,
        class_mode='categorical'
    )

    val_generator = val_datagen.flow_from_directory(
        VAL_DIR,
        target_size=(IMG_HEIGHT, IMG_WIDTH),
        batch_size=BATCH_SIZE,
        classes=CLASSES,
        class_mode='categorical'
    )

    print(f"\nUrutan Kelas (Sangat Penting): {train_generator.class_indices}")

    print("\n[2/4] Membangun Model MobileNetV2...")
    model = create_model()

    print("\n[3/4] Melatih Model...")
    history = model.fit(
        train_generator,
        epochs=EPOCHS,
        validation_data=val_generator
    )

    print("\n[4/4] Mengonversi ke TensorFlow Lite...")
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    tflite_model = converter.convert()

    tflite_model_path = os.path.join(MODEL_DIR, 'mango_classifier.tflite')
    with open(tflite_model_path, 'wb') as f:
        f.write(tflite_model)

    print("\n" + "="*50)
    print(f"  Training Selesai!")
    print(f"  Model berhasil disimpan di: {tflite_model_path}")
    print("="*50)

if __name__ == '__main__':
    main()
