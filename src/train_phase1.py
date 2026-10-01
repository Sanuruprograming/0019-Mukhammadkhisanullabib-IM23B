import tensorflow as tf
from tensorflow.keras.applications import EfficientNetB5
from tensorflow.keras import layers, models
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping
import os

# Import dari file preprocessing Anda
from preprocessing import load_datasets, DATASET_DIR, IMG_SIZE

def build_feature_extractor():
    IMG_SHAPE = IMG_SIZE + (3,) 
    # Menggunakan EfficientNet-B5 sesuai instruksi Anda
    base_model = EfficientNetB5(input_shape=IMG_SHAPE, include_top=False, weights='imagenet')
    
    # Membekukan seluruh bobot bawaan untuk Fase 1
    base_model.trainable = False 

    model = models.Sequential([
        base_model,
        layers.GlobalAveragePooling2D(),
        layers.Dropout(0.4), 
        layers.Dense(1, activation='sigmoid') # 1 Node untuk klasifikasi biner
    ])
    return model

if __name__ == "__main__":
    # 1. Muat dataset
    train_ds, val_ds, test_ds = load_datasets(DATASET_DIR)
    
    # 2. Optimasi pipeline data
    AUTOTUNE = tf.data.AUTOTUNE
    train_ds = train_ds.prefetch(buffer_size=AUTOTUNE)
    val_ds = val_ds.prefetch(buffer_size=AUTOTUNE)

    # 3. Bangun dan Kompilasi Model
    model = build_feature_extractor()
    model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
                  loss='binary_crossentropy',
                  metrics=['accuracy'])
    
    # 4. Siapkan direktori penyimpanan checkpoint
    if not os.path.exists('models'):
        os.makedirs('models')
        
    # Menyimpan model HANYA jika validasi akurasi membaik
    checkpoint = ModelCheckpoint(
        filepath='models/efficientnetb5_phase1.keras', 
        save_best_only=True, 
        monitor='val_accuracy', 
        mode='max',
        verbose=1
    )
    
    # Mencegah overtraining
    early_stopping = EarlyStopping(
        monitor='val_loss', 
        patience=3, 
        restore_best_weights=True
    )

    print("\n--- Memulai Pelatihan Fase 1 (Feature Extraction) ---")
    # Epoch diset ke 10 sebagai awalan
    history = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=10, 
        callbacks=[checkpoint, early_stopping]
    )
    
    print("\nFase 1 Selesai. Model Anda telah disimpan di folder 'models'.")