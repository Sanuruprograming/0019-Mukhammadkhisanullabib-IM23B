import tensorflow as tf
import os

# Konfigurasi parameter model dan path
BATCH_SIZE = 8
IMG_SIZE = (456, 456)
# Berdasarkan struktur Anda, file python ada di dalam 'src', 
# sehingga path harus naik satu tingkat ('..') untuk mencapai 'dataset'
DATASET_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'dataset'))

def load_datasets(base_dir):
    train_dir = os.path.join(base_dir, 'train')
    val_dir = os.path.join(base_dir, 'validation')
    test_dir = os.path.join(base_dir, 'test')

    print("Memuat Data Training:")
    train_dataset = tf.keras.preprocessing.image_dataset_from_directory(
        train_dir,
        shuffle=True,
        batch_size=BATCH_SIZE,
        image_size=IMG_SIZE,
        label_mode='binary' 
    )

    print("\nMemuat Data Validasi:")
    val_dataset = tf.keras.preprocessing.image_dataset_from_directory(
        val_dir,
        shuffle=True,
        batch_size=BATCH_SIZE,
        image_size=IMG_SIZE,
        label_mode='binary'
    )

    print("\nMemuat Data Testing:")
    test_dataset = tf.keras.preprocessing.image_dataset_from_directory(
        test_dir,
        shuffle=False, 
        batch_size=BATCH_SIZE,
        image_size=IMG_SIZE,
        label_mode='binary'
    )

    return train_dataset, val_dataset, test_dataset

if __name__ == "__main__":
    # Eksekusi fungsi pemuatan data
    train_ds, val_ds, test_ds = load_datasets(DATASET_DIR)
    
    # Optimasi performa I/O untuk mencegah bottleneck saat training
    AUTOTUNE = tf.data.AUTOTUNE
    train_ds = train_ds.cache().prefetch(buffer_size=AUTOTUNE)
    val_ds = val_ds.cache().prefetch(buffer_size=AUTOTUNE)
    test_ds = test_ds.cache().prefetch(buffer_size=AUTOTUNE)
    
    print("\nAlur preprocessing dan penyiapan dataset berhasil diinisialisasi.")