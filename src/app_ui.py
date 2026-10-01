import streamlit as st
import requests
from PIL import Image
import io

# 1. Konfigurasi Halaman & UI
st.set_page_config(page_title="Verifikasi Citra AI", page_icon="🔍", layout="wide")

# URL API Backend Anda (FastAPI)
API_URL = "http://127.0.0.1:8000"

# 2. Desain Sidebar Navigasi
st.sidebar.title("Navigasi Sistem")
menu = st.sidebar.radio("Pilih Menu:", ["Verifikasi Gambar", "Riwayat Pelaporan"])

# 3. Halaman Utama: Verifikasi Gambar
if menu == "Verifikasi Gambar":
    st.title("🔍 Sistem Verifikasi Citra Digital")
    st.write("Unggah gambar untuk menganalisis jejak manipulasi visual dan memeriksa metadata forensik.")

    # Komponen pengunggah file
    uploaded_file = st.file_uploader("Pilih gambar format JPG/PNG...", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        # Menampilkan pratinjau gambar di UI
        image = Image.open(uploaded_file)
        st.image(image, caption="Pratinjau Gambar", width=400)

        # Tombol eksekusi
        if st.button("Mulai Analisis AI", type="primary"):
            with st.spinner("Memproses ekstraksi piksel dan membaca metadata..."):
                # Membungkus file untuk dikirim ke API
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                
                try:
                    # Menembak endpoint POST /predict di FastAPI
                    response = requests.post(f"{API_URL}/predict", files=files)
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        if "error" in data:
                            st.error(data["error"])
                        else:
                            st.success("Verifikasi Selesai!")
                            
                            # Mengatur tata letak hasil menggunakan kolom
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.subheader("🧠 Hasil Klasifikasi AI")
                                st.metric(label="Prediksi Kelas", value=data["analisis_ai"]["prediksi"])
                                st.metric(label="Tingkat Keyakinan", value=data["analisis_ai"]["keyakinan"])
                                
                                st.subheader("📋 Kesimpulan Pakar")
                                st.info(data["kesimpulan_sistem"])
                                
                            with col2:
                                st.subheader("ℹ️ Informasi Ekstraksi")
                                st.write(f"**Nama File:** {data['informasi_file']['nama_file']}")
                                st.write(f"**Resolusi Input:** {data['informasi_file']['resolusi']}")
                                
                                st.subheader("📷 Metadata EXIF")
                                # Menampilkan JSON metadata dalam kotak yang rapi dan bisa di-scroll
                                st.json(data["metadata_foto"])
                    else:
                        st.error(f"Error {response.status_code}: Gagal memproses gambar pada server.")
                except requests.exceptions.ConnectionError:
                    st.error("KONEKSI GAGAL: Pastikan server FastAPI (api_backend.py) sedang berjalan di terminal lain!")

# 4. Halaman Kedua: Riwayat Pelaporan Database
elif menu == "Riwayat Pelaporan":
    st.title("📂 Database Riwayat Verifikasi")
    st.write("Daftar seluruh rekam jejak gambar yang telah diproses oleh sistem.")
    
    with st.spinner("Memuat data dari SQLite..."):
        try:
            # Menembak endpoint GET /history di FastAPI
            response = requests.get(f"{API_URL}/history")
            
            if response.status_code == 200:
                history_data = response.json()
                if history_data:
                    # Menampilkan data dalam bentuk tabel interaktif
                    st.dataframe(history_data, use_container_width=True)
                else:
                    st.info("Belum ada riwayat gambar yang diproses.")
            else:
                st.error("Gagal mengambil data dari server.")
        except requests.exceptions.ConnectionError:
            st.error("KONEKSI GAGAL: Pastikan server FastAPI (api_backend.py) sedang berjalan di terminal lain!")