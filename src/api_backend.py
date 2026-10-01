<<<<<<< HEAD
from fastapi import FastAPI, UploadFile, File
=======
from fastapi import FastAPI, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
>>>>>>> 808c2c1d (Initial commit)
import tensorflow as tf
import numpy as np
from PIL import Image, ExifTags
import io
import uvicorn
import os
import sqlite3
import json
import time
<<<<<<< HEAD

# Inisialisasi aplikasi FastAPI
app = FastAPI(
    title="API Verifikasi Citra Digital (Real vs AI)",
    description="Backend terintegrasi dengan AI, Ekstraksi EXIF, dan Database SQLite",
    version="1.3.0"
)

model = None
# Menentukan path absolut untuk folder-folder yang dibutuhkan
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DB_PATH = os.path.join(BASE_DIR, 'database', 'verifikasi_citra.db')
UPLOAD_DIR = os.path.join(BASE_DIR, 'uploaded_images')

def get_db_connection():
    """Fungsi helper untuk membuka koneksi ke SQLite"""
=======
import requests
from bs4 import BeautifulSoup
import yt_dlp
from datetime import datetime
from urllib.parse import urlparse

app = FastAPI(title="API Verifikasi Citra Digital (OSINT Ready)", version="3.1.0")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DB_PATH = os.path.join(BASE_DIR, 'database', 'verifikasi_citra.db')
UPLOAD_DIR = os.path.join(BASE_DIR, 'uploaded_images')
model = None

class URLPayload(BaseModel):
    url: str

def get_db_connection():
>>>>>>> 808c2c1d (Initial commit)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.on_event("startup")
async def load_model():
<<<<<<< HEAD
    """Memuat model dan memastikan folder upload tersedia"""
    global model
    model_path = os.path.join(BASE_DIR, 'models', 'efficientnetb5_phase2.keras')
    
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)
        
    if os.path.exists(model_path):
        model = tf.keras.models.load_model(model_path)
        print("Model berhasil dimuat dan siap menerima request!")
    else:
        print("GAGAL: File model tidak ditemukan.")

@app.post("/predict")
async def predict_image(file: UploadFile = File(...)):
    if model is None:
        return {"error": "Model belum siap."}

    try:
        # 1. Membaca gambar
        contents = await file.read()
        
        # 2. Menyimpan Salinan Gambar Fisik ke Server
        timestamp = int(time.time())
        safe_filename = f"{timestamp}_{file.filename.replace(' ', '_')}"
        saved_image_path = os.path.join(UPLOAD_DIR, safe_filename)
        
        with open(saved_image_path, "wb") as f:
            f.write(contents)

        # 3. Ekstraksi dan Prediksi (Logika tetap sama)
        image = Image.open(io.BytesIO(contents))
        img_format = image.format or file.filename.split('.')[-1].upper()
        width, height = image.size
        
        exif_data = {}
        raw_exif = image.getexif()
        if raw_exif:
            for tag_id, value in raw_exif.items():
                tag_name = ExifTags.TAGS.get(tag_id, tag_id)
                if isinstance(value, bytes):
                    continue
                exif_data[tag_name] = str(value)
        if not exif_data:
            exif_data = {"Info": "Tidak ada metadata EXIF."}
            
        if image.mode != "RGB":
            image = image.convert("RGB")
            
        image_resized = image.resize((456, 456))
        img_array = np.array(image_resized)
        img_array = np.expand_dims(img_array, axis=0)

        prediction = model.predict(img_array)
        prob = float(prediction[0][0]) 

        if prob > 0.5:
            label = "AI Generated"
            confidence = prob * 100
        else:
            label = "Real"
            confidence = (1.0 - prob) * 100

        kamera_fisik_terdeteksi = "Make" in exif_data or "Model" in exif_data
        
        if label == "AI Generated" and kamera_fisik_terdeteksi:
            kesimpulan = "PERINGATAN: Gambar memiliki metadata dari kamera asli, namun AI mendeteksi jejak manipulasi visual."
        elif label == "AI Generated" and not kamera_fisik_terdeteksi:
            kesimpulan = "SINTETIS: Gambar kemungkinan besar sepenuhnya dibuat oleh AI."
        elif label == "Real" and kamera_fisik_terdeteksi:
            kesimpulan = "OTENTIK: Gambar direkam menggunakan perangkat kamera fisik."
        else:
            kesimpulan = "TIDAK TERIDENTIFIKASI: Gambar asli secara visual, tanpa metadata kamera."

        conf_str = f"{round(confidence, 2)}%"

        # 4. Menyimpan Hasil ke Database SQLite
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO riwayat_verifikasi 
            (nama_file, path_gambar, prediksi_ai, confidence_score, metadata_summary, kesimpulan_sistem)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (file.filename, saved_image_path, label, conf_str, json.dumps(exif_data), kesimpulan))
        conn.commit()
        conn.close()

        # 5. Mengembalikan Respons
        # 5. Mengembalikan Respons
        return {
            "status": "Sukses",
            "informasi_file": {
                "nama_file": file.filename, 
                "format_gambar": img_format,
                "resolusi": f"{width} x {height}"
            },
            "metadata_foto": exif_data,
            "analisis_ai": {
                "prediksi": label, 
                "keyakinan": conf_str
            },
            "kesimpulan_sistem": kesimpulan
        }

    except Exception as e:
        return {"error": f"Terjadi kesalahan: {str(e)}"}

@app.get("/history")
async def get_history():
    """Endpoint baru untuk melihat riwayat pelaporan database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, waktu_pengecekan, nama_file, prediksi_ai, confidence_score FROM riwayat_verifikasi ORDER BY waktu_pengecekan DESC")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    except Exception as e:
        return {"error": str(e)}
=======
    global model
    model_path = os.path.join(BASE_DIR, 'models', 'efficientnetb5_phase2.keras')
    if not os.path.exists(UPLOAD_DIR): os.makedirs(UPLOAD_DIR)
    if os.path.exists(model_path):
        model = tf.keras.models.load_model(model_path)
        print("Model EfficientNet-B5 berhasil dimuat!")

@app.post("/predict")
async def predict_image(request: Request, file: UploadFile = File(...)):
    if model is None: return {"error": "Model belum siap."}
    try:
        client_ip = request.client.host
        user_agent = request.headers.get("user-agent", "Tidak diketahui")
        contents = await file.read()
        safe_filename = f"{int(time.time())}_{file.filename.replace(' ', '_')}"
        saved_image_path = os.path.join(UPLOAD_DIR, safe_filename)
        with open(saved_image_path, "wb") as f: f.write(contents)
        image = Image.open(io.BytesIO(contents))
        img_format = image.format or file.filename.split('.')[-1].upper()
        width, height = image.size
        total_pixels = width * height
        exif_data = {}
        if image.getexif():
            for tag_id, value in image.getexif().items():
                tag_name = ExifTags.TAGS.get(tag_id, tag_id)
                if not isinstance(value, bytes): exif_data[tag_name] = str(value)
        if not exif_data: exif_data = {"Info": "Tidak ada metadata EXIF."}
        if image.mode != "RGB": image = image.convert("RGB")
        img_array = np.expand_dims(np.array(image.resize((456, 456))), axis=0)
        prob = float(model.predict(img_array)[0][0]) 
        label = "AI Generated" if prob > 0.5 else "Real"
        confidence = prob * 100 if prob > 0.5 else (1.0 - prob) * 100
        conf_str = f"{round(confidence, 2)}%"
        kesimpulan = f"Analisis Berkas Lokal: Gambar diidentifikasi sebagai {label} dengan keyakinan {conf_str}."
        gabungan_metadata = {"exif_kamera": exif_data, "jejak_jaringan": {"ip_address": client_ip, "user_agent": user_agent}}
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO riwayat_verifikasi (nama_file, format_gambar, resolusi, jumlah_pixel, path_gambar, prediksi_ai, confidence_score, metadata_summary, kesimpulan_sistem, sumber_url, platform, profil_pengunggah) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (file.filename, img_format, f"{width} x {height}", total_pixels, saved_image_path, label, conf_str, json.dumps(gabungan_metadata), kesimpulan, "Berkas Lokal", "-", "-"))
        conn.commit()
        conn.close()
        return {"sumber": "lokal", "informasi_file": {"nama_file": file.filename, "format_gambar": img_format, "resolusi": f"{width} x {height}", "jumlah_pixel": total_pixels}, "informasi_pengunggah": {"ip_address": client_ip, "user_agent": user_agent}, "metadata_foto": exif_data, "analisis_ai": {"prediksi": label, "keyakinan": conf_str}, "kesimpulan_sistem": kesimpulan}
    except Exception as e: return {"error": str(e)}

@app.post("/predict_url")
async def predict_from_url(payload: URLPayload, request: Request):
    if model is None: return {"error": "Model belum siap."}
    url = payload.url
    try:
        domain = urlparse(url).netloc
        img_url = url
        platform_name = domain if domain else "Situs Web Biasa"
        profil_name = "Anonim"
        waktu_upload = "Tidak Terlacak"
        
        # DETEKSI INTELLIGENCE: Apakah ini tautan CDN/Server Raw?
        is_cdn = any(cdn in domain for cdn in ['fbcdn.net', 'cdninstagram', 'twimg', 'akamaihd'])
        
        if is_cdn:
            platform_name = f"Server Distribusi (CDN: {domain})"
            profil_name = "Terhapus (Tautan Langsung CDN)"
            waktu_upload = "Dihapus oleh Server"
        else:
            ydl_opts = {'quiet': True, 'skip_download': True, 'extract_flat': False, 'no_warnings': True}
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    if info:
                        if info.get('thumbnails'): img_url = info['thumbnails'][-1]['url']
                        elif info.get('thumbnail'): img_url = info['thumbnail']
                        
                        platform_name = info.get('extractor_key', platform_name)
                        extracted_author = info.get('uploader') or info.get('channel') or info.get('creator')
                        if extracted_author: profil_name = extracted_author
                        else: profil_name = "Dilindungi Privasi Platform"
                        
                        raw_date = info.get('upload_date')
                        if raw_date: waktu_upload = f"{raw_date[6:8]}/{raw_date[4:6]}/{raw_date[0:4]}"
            except Exception:
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
                res = requests.get(url, headers=headers, timeout=10)
                if 'text/html' in res.headers.get('Content-Type', ''):
                    soup = BeautifulSoup(res.text, 'html.parser')
                    og_img = soup.find('meta', property='og:image')
                    if og_img: img_url = og_img.get('content')
                    og_site = soup.find('meta', property='og:site_name')
                    if og_site: platform_name = og_site.get('content')
                    author = soup.find('meta', attrs={'name': 'author'}) 
                    if author: profil_name = author.get('content')

        img_res = requests.get(img_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        if 'image' not in img_res.headers.get('Content-Type', ''):
            return {"error": "Gagal mengekstrak. Tautan tidak valid atau diblokir oleh platform."}

        contents = img_res.content
        safe_filename = f"osint_{int(time.time())}.jpg"
        saved_image_path = os.path.join(UPLOAD_DIR, safe_filename)
        with open(saved_image_path, "wb") as f: f.write(contents)
        
        image = Image.open(io.BytesIO(contents))
        img_format = image.format or "JPEG"
        width, height = image.size
        total_pixels = width * height
        
        exif_data = {}
        if image.getexif():
            for tag_id, value in image.getexif().items():
                tag_name = ExifTags.TAGS.get(tag_id, tag_id)
                if not isinstance(value, bytes): exif_data[tag_name] = str(value)
        if not exif_data: exif_data = {"Info": "Meta fisik dihapus oleh server platform (Standar Kompresi Web)."}
            
        if image.mode != "RGB": image = image.convert("RGB")
        img_array = np.expand_dims(np.array(image.resize((456, 456))), axis=0)

        prob = float(model.predict(img_array)[0][0]) 
        label = "AI Generated" if prob > 0.5 else "Real"
        confidence = prob * 100 if prob > 0.5 else (1.0 - prob) * 100
        conf_str = f"{round(confidence, 2)}%"
        
        kesimpulan = f"ANALISIS OSINT: Citra dari platform '{platform_name}' (Profil: {profil_name}) teridentifikasi sebagai {label}."
        gabungan_metadata = {"exif_kamera": exif_data, "osint_data": {"url_sumber": url, "waktu_upload": waktu_upload}}

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO riwayat_verifikasi (nama_file, format_gambar, resolusi, jumlah_pixel, path_gambar, prediksi_ai, confidence_score, metadata_summary, kesimpulan_sistem, sumber_url, platform, profil_pengunggah) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (safe_filename, img_format, f"{width} x {height}", total_pixels, saved_image_path, label, conf_str, json.dumps(gabungan_metadata), kesimpulan, url, platform_name, profil_name))
        conn.commit()
        conn.close()

        return {
            "sumber": "osint", "informasi_file": {"nama_file": safe_filename, "format_gambar": img_format, "resolusi": f"{width} x {height}", "jumlah_pixel": total_pixels},
            "informasi_osint": {"sumber_url": url, "platform": platform_name, "profil_pengunggah": profil_name, "waktu_upload": waktu_upload},
            "metadata_foto": exif_data, "analisis_ai": {"prediksi": label, "keyakinan": conf_str}, "kesimpulan_sistem": kesimpulan, "preview_url": img_url
        }
    except Exception as e: return {"error": f"Gagal mengekstrak data dari URL: {str(e)}"}

@app.get("/history")
async def get_history():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM riwayat_verifikasi ORDER BY waktu_pengecekan DESC")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    except Exception as e: return {"error": str(e)}
>>>>>>> 808c2c1d (Initial commit)

if __name__ == "__main__":
    uvicorn.run("api_backend:app", host="127.0.0.1", port=8000, reload=True)