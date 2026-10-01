import tensorflow as tf
import numpy as np
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Import dari file preprocessing Anda
from preprocessing import load_datasets, DATASET_DIR

if __name__ == "__main__":
    print("--- Memulai Evaluasi Model ---")
    
    # 1. Hanya memuat data testing (train dan val akan diabaikan)
    _, _, test_ds = load_datasets(DATASET_DIR)
    
    # 2. Muat model final terbaik dari Fase 2
    model_path = 'models/efficientnetb5_phase2.keras'
    print(f"\nMemuat model dari: {model_path}")
    model = tf.keras.models.load_model(model_path)
    
    # 3. Kumpulkan label asli dan prediksi model
    print("Mengekstraksi prediksi dari dataset testing... (Ini mungkin memakan waktu beberapa menit)")
    y_true = []
    y_pred_probs = []
    
    for images, labels in test_ds:
        y_true.extend(labels.numpy())
        # Melakukan prediksi batch per batch
        preds = model.predict(images, verbose=0)
        y_pred_probs.extend(preds)
        
    y_true = np.array(y_true).flatten()
    y_pred_probs = np.array(y_pred_probs).flatten()
    
    # Karena ini klasifikasi biner, probabilitas > 0.5 dianggap kelas 1 (Generated AI)
    y_pred = (y_pred_probs > 0.5).astype(int)
    
    # 4. Cetak Classification Report (Akurasi, Precision, Recall, F1-Score)
    print("\n" + "="*50)
    print("LAPORAN KLASIFIKASI (CLASSIFICATION REPORT)")
    print("="*50)
    target_names = ['Real (0)', 'AI Generated (1)']
    print(classification_report(y_true, y_pred, target_names=target_names))
    
    # 5. Buat dan Simpan Confusion Matrix
    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=target_names, yticklabels=target_names)
    plt.title('Confusion Matrix - Deteksi Citra AI')
    plt.ylabel('Label Asli (True Label)')
    plt.xlabel('Tebakan Model (Predicted Label)')
    
    # Simpan gambar ke dalam folder
    output_image = 'confusion_matrix.png'
    plt.savefig(output_image)
    print(f"\nVisualisasi Confusion Matrix telah disimpan sebagai '{output_image}' di dalam folder src.")