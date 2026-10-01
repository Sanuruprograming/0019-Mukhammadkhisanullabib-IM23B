import sqlite3
import os

def setup_database():
<<<<<<< HEAD
    # Menentukan lokasi file database
    db_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'database'))
    
    # Pastikan folder database ada
=======
    db_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'database'))
>>>>>>> 808c2c1d (Initial commit)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
        
    db_path = os.path.join(db_dir, 'verifikasi_citra.db')
<<<<<<< HEAD
    
    # Membuka koneksi (akan otomatis membuat file jika belum ada)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Membuat tabel untuk menyimpan riwayat verifikasi
=======
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
>>>>>>> 808c2c1d (Initial commit)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS riwayat_verifikasi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            waktu_pengecekan TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            nama_file TEXT NOT NULL,
<<<<<<< HEAD
=======
            format_gambar TEXT,
            resolusi TEXT,
            jumlah_pixel INTEGER,
>>>>>>> 808c2c1d (Initial commit)
            path_gambar TEXT NOT NULL,
            prediksi_ai TEXT NOT NULL,
            confidence_score TEXT NOT NULL,
            metadata_summary TEXT,
<<<<<<< HEAD
            kesimpulan_sistem TEXT NOT NULL
=======
            kesimpulan_sistem TEXT NOT NULL,
            sumber_url TEXT,
            platform TEXT,
            profil_pengunggah TEXT
>>>>>>> 808c2c1d (Initial commit)
        )
    ''')
    
    conn.commit()
    conn.close()
<<<<<<< HEAD
    
    print(f"Database berhasil diinisialisasi pada: {db_path}")
    print("Tabel 'riwayat_verifikasi' sudah siap digunakan.")
=======
    print("Database siap dengan fitur OSINT (URL, Platform, Profil)!")
>>>>>>> 808c2c1d (Initial commit)

if __name__ == "__main__":
    setup_database()