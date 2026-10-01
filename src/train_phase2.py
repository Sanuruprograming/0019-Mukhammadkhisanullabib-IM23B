import tensorflow as tf
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping
import os

# Import dari file preprocessing Anda
from preprocessing import load_datasets, DATASET_DIR

if __name__ == "__main__":
    # 1. Muat dataset (pastikan BATCH_SIZE di preprocessing.py tetap meringankan memori Anda)
    train_ds, val_ds, test_ds = load_datasets(DATASET_DIR)
    
    AUTOTUNE = tf.data.AUTOTUNE
    train_ds = train_ds.prefetch(buffer_size=AUTOTUNE)
    val_ds = val_ds.prefetch(buffer_size=AUTOTUNE)

    # 2. Muat model terbaik dari Fase 1
    model_path = 'models/efficientnetb5_phase1.keras'
    print(f"Memuat model dari {model_path}...")
    model = tf.keras.models.load_model(model_path)

    # 3. Buka gembok (unfreeze) base_model
    # Dalam arsitektur Sequential kita, EfficientNet-B5 berada pada indeks layer ke-0
    base_model = model.layers[0]
    base_model.trainable = True

    # Bekukan kembali semua layer kecuali 30 layer terakhir
    # EfficientNet-B5 memiliki >500 layer. Melatih hanya ujungnya mencegah overtaxing 
    # memori komputer Anda sekaligus menghindari overfitting.
    for layer in base_model.layers[:-30]:
        layer.trainable = False

    # 4. Kompilasi ulang dengan Learning Rate yang sangat kecil (1e-5)
    model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=1e-5),
                  loss='binary_crossentropy',
                  metrics=['accuracy'])
    
    # 5. Siapkan checkpoint penyimpanan baru untuk Fase 2
    checkpoint = ModelCheckpoint(
        filepath='models/efficientnetb5_phase2.keras', 
        save_best_only=True, 
        monitor='val_accuracy', 
        mode='max',
        verbose=1
    )
    
    early_stopping = EarlyStopping(
        monitor='val_loss', 
        patience=3, 
        restore_best_weights=True
    )

    print("\n--- Memulai Pelatihan Fase 2 (Fine-Tuning) ---")
    history = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=10, 
        callbacks=[checkpoint, early_stopping]
    )
    
    print("\nFase 2 Selesai. Model final Anda tersimpan di folder 'models'.")