"use client";
import { useState, useRef } from "react";
import Link from "next/link";
import jsPDF from "jspdf";
import autoTable from "jspdf-autotable";

export default function Home() {
  const [inputMode, setInputMode] = useState<'lokal' | 'osint'>('lokal');
  const [image, setImage] = useState<File | null>(null);
  const [urlInput, setUrlInput] = useState<string>('');
  const [preview, setPreview] = useState<string | null>(null);
  const [result, setResult] = useState<any>(null); 
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  
  const fileInputRef = useRef<HTMLInputElement>(null);

  const resetForm = () => {
    setImage(null); 
    setPreview(null); 
    setResult(null); 
    setError(null); 
    setUrlInput('');
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const file = e.target.files[0];
      setImage(file);
      setPreview(URL.createObjectURL(file));
      setResult(null); 
      setError(null);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true); 
    setError(null);

    try {
      let response;
      if (inputMode === 'lokal') {
        if (!image) throw new Error("Pilih gambar terlebih dahulu!");
        const formData = new FormData(); 
        formData.append("file", image);
        response = await fetch("http://127.0.0.1:8000/predict", { method: "POST", body: formData });
      } else {
        if (!urlInput.startsWith('http')) throw new Error("URL harus diawali dengan http:// atau https://");
        response = await fetch("http://127.0.0.1:8000/predict_url", { 
          method: "POST", 
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ url: urlInput }) 
        });
      }

      const data = await response.json();
      if (data.error) throw new Error(data.error); 
      
      setResult(data);
      if (inputMode === 'osint' && data.preview_url) {
        setPreview(data.preview_url);
      }
    } catch (err: any) {
      setError(err.message || "Koneksi ke server gagal. Pastikan FastAPI berjalan.");
    } finally {
      setLoading(false);
    }
  };

  const downloadReportPDF = () => {
    if (!result) return;
    const doc = new jsPDF();
    
    doc.setFontSize(55); 
    doc.setTextColor(235, 235, 235);
    doc.text("FORENSIK DIGITAL", 30, 150, { angle: 45 });
    doc.text("DOKUMEN RAHASIA", 70, 200, { angle: 45 });

    doc.setFontSize(16); doc.setTextColor(15, 23, 42);
    doc.text("Laporan Analisis Forensik Citra & OSINT", 14, 20);
    doc.setFontSize(10); doc.setTextColor(100);
    doc.text(`Waktu Cetak: ${new Date().toLocaleString("id-ID")}`, 14, 26);
    doc.setLineWidth(0.5); doc.line(14, 30, 196, 30);

    let summaryData = [
      ["Nama Berkas", result.informasi_file.nama_file],
      ["Resolusi Fisik", `${result.informasi_file.resolusi} (${result.informasi_file.jumlah_pixel.toLocaleString('id-ID')} px)`],
    ];

    if (result.sumber === 'osint') {
      summaryData.push(["Sumber Platform", result.informasi_osint.platform]);
      summaryData.push(["Profil Terlacak", result.informasi_osint.profil_pengunggah]);
      summaryData.push(["Tautan Asli", result.informasi_osint.sumber_url]);
    } else {
      summaryData.push(["IP Address Pengunggah", result.informasi_pengunggah.ip_address]);
    }

    summaryData.push(
      ["Hasil Klasifikasi AI", result.analisis_ai.prediksi],
      ["Keyakinan Model", result.analisis_ai.keyakinan],
      ["Kesimpulan Analis", result.kesimpulan_sistem]
    );

    autoTable(doc, {
      startY: 40, head: [["Parameter Analisis", "Keterangan Identifikasi"]], body: summaryData,
      theme: "grid", 
      headStyles: { fillColor: [15, 23, 42] },
      bodyStyles: { fillColor: false }, 
      alternateRowStyles: { fillColor: false },
    });

    const finalY = (doc as any).lastAutoTable?.finalY || 100;
    
    doc.setFontSize(12); doc.setTextColor(15, 23, 42);
    doc.text("Ekstraksi Metadata EXIF", 14, finalY + 12);
    
    const exifRows = Object.entries(result.metadata_foto).map(([key, val]) => [key, String(val)]);
    autoTable(doc, {
      startY: finalY + 16, head: [["Tag EXIF", "Nilai Metadata"]],
      body: exifRows.length > 0 ? exifRows : [["Info", "Tidak ada metadata EXIF terdeteksi"]],
      theme: "grid", 
      headStyles: { fillColor: [71, 85, 105] },
      bodyStyles: { fillColor: false }, 
      alternateRowStyles: { fillColor: false },
    });
    
    doc.save(`Forensik_${result.informasi_file.nama_file}.pdf`);
  };

  return (
    <main className="min-h-screen bg-[#fafafa] text-slate-800 font-sans p-6 md:p-12">
      <div className="max-w-6xl mx-auto">
        <header className="mb-12 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <h1 className="text-3xl font-extrabold tracking-tight text-slate-900">
              Verifikasi <span className="text-blue-600">Citra AI & OSINT</span>
            </h1>
            <p className="text-slate-500 mt-1 text-sm md:text-base">Mendeteksi manipulasi visual, ekstraksi metadata, dan pelacakan profil sumber.</p>
          </div>
          <Link href="/riwayat" className="text-sm font-medium text-slate-600 hover:text-slate-900 bg-white border border-slate-200 px-5 py-2.5 rounded-full shadow-sm hover:shadow transition-all">
            Lihat Database Riwayat &rarr;
          </Link>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          <section className="lg:col-span-5 flex flex-col gap-4">
            <div className="bg-white p-6 rounded-[2rem] shadow-[0_2px_20px_rgb(0,0,0,0.03)] border border-slate-100">
              
              <div className="flex bg-slate-100 p-1 rounded-2xl mb-6">
                <button type="button" onClick={() => { setInputMode('lokal'); resetForm(); }} className={`flex-1 py-2.5 text-sm font-semibold rounded-xl transition-all ${inputMode === 'lokal' ? 'bg-white text-slate-900 shadow' : 'text-slate-500 hover:text-slate-700'}`}>
                  Berkas Lokal
                </button>
                <button type="button" onClick={() => { setInputMode('osint'); resetForm(); }} className={`flex-1 py-2.5 text-sm font-semibold rounded-xl transition-all flex justify-center items-center gap-2 ${inputMode === 'osint' ? 'bg-white text-blue-700 shadow' : 'text-slate-500 hover:text-slate-700'}`}>
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"></path></svg>
                  Tautan OSINT
                </button>
              </div>
              
              <form onSubmit={handleSubmit} className="space-y-6">
                {!preview ? (
                  <div className="flex items-center justify-center w-full">
                    {inputMode === 'lokal' ? (
                      <label className="flex flex-col items-center justify-center w-full h-72 border-2 border-dashed rounded-3xl cursor-pointer bg-slate-50/50 hover:bg-slate-50 border-slate-200 hover:border-blue-400 transition-all group">
                        <div className="flex flex-col items-center justify-center pt-5 pb-6 text-center px-4">
                          <div className="p-4 bg-white rounded-full shadow-sm mb-4 group-hover:scale-110 transition-transform"><svg className="w-6 h-6 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"></path></svg></div>
                          <p className="mb-2 text-sm text-slate-600 font-medium">Unggah dari Komputer</p>
                          <p className="text-xs text-slate-400">JPG, JPEG, PNG, WEBP</p>
                        </div>
                        <input type="file" className="hidden" accept="image/jpeg, image/png, image/webp" onChange={handleImageChange} ref={fileInputRef} />
                      </label>
                    ) : (
                      <div className="flex flex-col items-center justify-center w-full h-72 border border-slate-200 rounded-3xl bg-slate-50/50 p-6 text-center">
                         <div className="p-4 bg-blue-100 text-blue-600 rounded-full mb-4"><svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg></div>
                         <h3 className="font-bold text-slate-800 mb-2">Pelacakan Tautan Siber</h3>
                         <p className="text-xs text-slate-500 mb-6 px-4">Masukkan URL gambar atau tautan portal berita/sosmed. Sistem akan merayapi profil dan mengekstrak gambarnya.</p>
                         <input type="url" value={urlInput} onChange={(e) => setUrlInput(e.target.value)} placeholder="https://..." required className="w-full bg-white border border-slate-300 text-slate-900 text-sm rounded-xl focus:ring-blue-500 focus:border-blue-500 block p-3.5 shadow-sm" />
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="space-y-4">
                    <div className="relative w-full aspect-[4/3] rounded-3xl overflow-hidden border border-slate-100 shadow-sm group bg-slate-100">
                      <img src={preview} alt="Pratinjau" className="object-contain w-full h-full" crossOrigin="anonymous" />
                      <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center backdrop-blur-sm">
                        <button type="button" onClick={resetForm} className="bg-white/90 text-slate-900 px-5 py-2.5 rounded-full text-sm font-semibold shadow-sm hover:bg-white transition-colors">
                          Mulai Investigasi Baru
                        </button>
                      </div>
                    </div>
                  </div>
                )}

                <button 
                  type="submit" 
                  disabled={(inputMode === 'lokal' ? !image : !urlInput) || loading || !!result} 
                  className="w-full bg-slate-900 hover:bg-blue-600 text-white font-semibold py-3.5 px-4 rounded-2xl transition-all disabled:opacity-30 flex justify-center items-center gap-2"
                >
                  {loading ? (
                    <><svg className="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg> Memproses Ekstraksi...</>
                  ) : "Mulai Analisis"}
                </button>
              </form>
              {error && <div className="mt-4 p-4 text-sm text-red-600 bg-red-50 rounded-2xl">{error}</div>}
            </div>
          </section>

          <section className="lg:col-span-7 bg-white p-6 md:p-10 rounded-[2rem] shadow-[0_2px_20px_rgb(0,0,0,0.03)] border border-slate-100">
            {result ? (
              <div className="space-y-6 animate-in fade-in duration-300">
                <div className="flex flex-col sm:flex-row gap-4">
                  <div className={`flex-1 p-6 rounded-3xl ${result.analisis_ai.prediksi === 'Real' ? 'bg-emerald-50 text-emerald-900' : 'bg-rose-50 text-rose-900'}`}>
                    <p className="text-sm opacity-70 mb-1 font-medium">Klasifikasi Material</p>
                    <p className="text-3xl font-black">{result.analisis_ai.prediksi === 'Real' ? 'Citra Asli' : 'Manipulasi AI'}</p>
                  </div>
                  <div className="flex-1 p-6 rounded-3xl bg-slate-50 text-slate-900 border border-slate-100">
                    <p className="text-sm opacity-70 mb-1 font-medium">Tingkat Keyakinan (Confidence)</p>
                    <p className="text-3xl font-black">{result.analisis_ai.keyakinan}</p>
                  </div>
                </div>

                <div>
                  <h3 className="text-xs font-bold tracking-widest text-slate-400 uppercase mb-3">Diagnosis Sistem Pakar</h3>
                  <div className="p-5 bg-blue-50/50 text-blue-900 rounded-2xl font-medium text-sm leading-relaxed border border-blue-100/50">
                    {result.kesimpulan_sistem}
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                     <h3 className="text-xs font-bold tracking-widest text-slate-400 uppercase mb-3">Spesifikasi Fisik</h3>
                     <div className="space-y-3 text-sm text-slate-600 bg-slate-50 p-4 rounded-2xl border border-slate-100">
                        <div className="flex justify-between border-b border-slate-200 pb-2">
                          <span className="text-slate-400">Berkas</span>
                          <span className="font-medium truncate max-w-[120px]" title={result.informasi_file.nama_file}>{result.informasi_file.nama_file}</span>
                        </div>
                        <div className="flex justify-between border-b border-slate-200 pb-2">
                          <span className="text-slate-400">Format</span><span className="font-medium">{result.informasi_file.format_gambar}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-slate-400">Dimensi</span><span className="font-medium">{result.informasi_file.resolusi}</span>
                        </div>
                     </div>
                  </div>
                  
                  <div>
                     <h3 className="text-xs font-bold tracking-widest text-slate-400 uppercase mb-3 flex items-center gap-2">
                       <svg className="w-4 h-4 text-blue-500" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M10 1.944A11.954 11.954 0 012.166 5C2.056 5.649 2 6.319 2 7c0 5.225 3.34 9.67 8 11.317C14.66 16.67 18 12.225 18 7c0-.682-.057-1.35-.166-1.998A11.954 11.954 0 0110 1.944zM11 14a1 1 0 11-2 0 1 1 0 012 0zm0-7a1 1 0 10-2 0v3a1 1 0 102 0V7z" clipRule="evenodd"></path></svg>
                       {result.sumber === 'osint' ? 'Jejak Tautan Siber' : 'Profil Pengunggah'}
                     </h3>
                     <div className="space-y-3 text-sm text-slate-600 bg-blue-50/30 p-4 rounded-2xl border border-blue-100">
                        {result.sumber === 'osint' ? (
                          <>
                            <div className="flex justify-between border-b border-blue-100 pb-2">
                              <span className="text-slate-400">Platform/Web</span>
                              <span className="font-bold text-blue-700 truncate max-w-[120px]" title={result.informasi_osint.platform}>{result.informasi_osint.platform}</span>
                            </div>
                            <div className="flex flex-col border-b border-blue-100 py-2">
                              <span className="text-slate-400 text-xs mb-1">Tautan Asli:</span>
                              <a href={result.informasi_osint.sumber_url} target="_blank" rel="noopener noreferrer" className="font-medium text-xs text-blue-600 truncate hover:underline" title={result.informasi_osint.sumber_url}>
                                {result.informasi_osint.sumber_url}
                              </a>
                            </div>
                            <div className="flex flex-col pt-1">
                              <span className="text-slate-400 text-xs mb-1">Author / Profil Terlacak:</span>
                              <span className="font-bold text-slate-800 truncate" title={result.informasi_osint.profil_pengunggah}>{result.informasi_osint.profil_pengunggah}</span>
                            </div>
                          </>
                        ) : (
                          <>
                            <div className="flex justify-between border-b border-blue-100 pb-2">
                              <span className="text-slate-400">IP Address</span>
                              <span className="font-mono font-bold text-blue-700">{result.informasi_pengunggah.ip_address}</span>
                            </div>
                            <div className="flex flex-col pt-1">
                              <span className="text-slate-400 text-xs mb-1">Perangkat (User-Agent):</span>
                              <span className="font-medium text-xs text-slate-800 truncate" title={result.informasi_pengunggah.user_agent}>{result.informasi_pengunggah.user_agent}</span>
                            </div>
                          </>
                        )}
                     </div>
                  </div>
                </div>

                {/* PENAMBAHAN KEMBALI KOTAK TERMINAL EXIF */}
                <div>
                  <h3 className="text-xs font-bold tracking-widest text-slate-400 uppercase mb-3 flex items-center gap-2">
                    <svg className="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"></path></svg>
                    Log Ekstraksi Metadata EXIF
                  </h3>
                  <div className="bg-slate-900 rounded-2xl p-4 text-emerald-400 text-xs font-mono max-h-40 overflow-y-auto shadow-inner">
                    {!result.metadata_foto || Object.keys(result.metadata_foto).length === 0 || (Object.keys(result.metadata_foto).length === 1 && result.metadata_foto.Info) ? (
                      <div className="flex items-center gap-2 text-slate-400">
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                        <span>Tidak ada metadata fisik tersembunyi yang terdeteksi pada citra ini.</span>
                      </div>
                    ) : (
                      Object.entries(result.metadata_foto).map(([key, value]) => (
                        <div key={key} className="mb-1">
                          <span className="text-emerald-100/50">{key}:</span> {String(value)}
                        </div>
                      ))
                    )}
                  </div>
                </div>

                <div className="pt-2">
                    <button onClick={downloadReportPDF} className="w-full bg-white border border-slate-200 hover:border-slate-300 hover:bg-slate-50 text-slate-800 font-bold py-4 px-4 rounded-2xl transition-all shadow-sm flex items-center justify-center gap-2">
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
                      Cetak Laporan PDF Resmi (Watermarked)
                    </button>
                </div>

              </div>
            ) : (
              <div className="flex flex-col items-center justify-center h-full min-h-[400px] text-slate-400 text-center">
                <div className="p-4 bg-slate-50 rounded-full mb-4">
                  <svg className="w-8 h-8 text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
                </div>
                <p className="font-medium text-slate-600 mb-1 text-sm">Ruang Investigasi</p>
                <p className="text-xs max-w-[250px] mx-auto">Hasil analisis struktur piksel (AI) dan jejak pelacakan (OSINT) akan dirender di sini.</p>
              </div>
            )}
          </section>
        </div>
      </div>
    </main>
  );
}