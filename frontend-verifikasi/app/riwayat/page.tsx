"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import jsPDF from "jspdf";

export default function RiwayatPage() {
  const [history, setHistory] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/history")
      .then((res) => res.json())
      .then((data) => {
        if (!data.error) setHistory(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Gagal memuat riwayat:", err);
        setLoading(false);
      });
  }, []);

  const exportHistoryPDF = () => {
    if (history.length === 0) return;
    try {
      const doc = new jsPDF("landscape");
      
      // 1. Watermark Latar Belakang Terang
      doc.setFontSize(60); 
      doc.setTextColor(235, 235, 235);
      doc.text("FORENSIK DIGITAL", 45, 130, { angle: 30 });
      doc.text("DATABASE RAHASIA", 90, 170, { angle: 30 });

      // 2. Judul Laporan
      doc.setFontSize(14); 
      doc.setTextColor(30, 58, 138);
      doc.text("REKAPITULASI RIWAYAT VERIFIKASI CITRA & OSINT - DATABASE SQLITE", 14, 20);
      
      doc.setFontSize(9);
      doc.setTextColor(100, 100, 100);
      doc.text(`Waktu Cetak: ${new Date().toLocaleString("id-ID")}`, 14, 26);

      // 3. Header Tabel Manual
      let startY = 35;
      doc.setFillColor(30, 58, 138);
      doc.rect(14, startY, 268, 8, "F");
      
      doc.setFontSize(8);
      doc.setTextColor(255, 255, 255);
      doc.text("ID", 18, startY + 5);
      doc.text("Waktu", 32, startY + 5);
      doc.text("Berkas / URL", 80, startY + 5);
      doc.text("Format", 145, startY + 5);
      doc.text("Resolusi", 170, startY + 5);
      doc.text("Prediksi AI", 205, startY + 5);
      doc.text("Keyakinan", 235, startY + 5);
      doc.text("Sumber", 258, startY + 5);

      // 4. Baris Data Manual
      startY += 8;
      doc.setFontSize(8);
      doc.setTextColor(50, 50, 50);

      history.forEach((item, index) => {
        // Jika baris hampir tembus ke bawah halaman, buat halaman baru
        if (startY > 180) {
          doc.addPage();
          startY = 20;
        }

        const idText = `#${item.id || "-"}`;
        const waktuText = item.waktu_pengecekan ? new Date(item.waktu_pengecekan).toLocaleDateString("id-ID") : "-";
        const namaText = (item.nama_file || "Unknown").substring(0, 35);
        const formatText = item.format_gambar || "-";
        const resolusiText = item.resolusi || "-";
        const prediksiText = item.prediksi_ai === 'Real' ? 'Asli' : 'AI Generated';
        const keyakinanText = item.confidence_score || "-";
        const sumberText = (item.platform || "Lokal").substring(0, 12);

        doc.text(idText, 18, startY + 6);
        doc.text(waktuText, 32, startY + 6);
        doc.text(namaText, 80, startY + 6);
        doc.text(formatText, 145, startY + 6);
        doc.text(resolusiText, 170, startY + 6);
        doc.text(prediksiText, 205, startY + 6);
        doc.text(keyakinanText, 235, startY + 6);
        doc.text(sumberText, 258, startY + 6);

        // Garis pemisah tipis antar baris
        doc.setLineWidth(0.1);
        doc.setLineCap("butt");
        doc.setDrawColor(220, 225, 230);
        doc.line(14, startY + 9, 282, startY + 9);

        startY += 9;
      });
      
      doc.save(`Rekap_Database_Forensik_${Date.now()}.pdf`);
    } catch (err) {
      console.error("Gagal mencetak PDF:", err);
      alert("Terjadi kesalahan saat mencetak PDF rekap.");
    }
  };

  return (
    <main className="min-h-screen bg-[#fafafa] text-slate-800 font-sans p-6 md:p-12">
      <div className="max-w-7xl mx-auto">
        <header className="mb-8 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <h1 className="text-3xl font-extrabold tracking-tight text-slate-900">
              Database <span className="text-blue-600">Riwayat Investigasi</span>
            </h1>
            <p className="text-slate-500 mt-1 text-sm">Arsip log forensik digital, analisis piksel AI, dan rekam jejak OSINT.</p>
          </div>
          <div className="flex gap-3">
            <button onClick={exportHistoryPDF} disabled={history.length === 0} className="bg-slate-900 hover:bg-blue-600 text-white text-sm font-semibold px-5 py-2.5 rounded-full shadow transition-all disabled:opacity-30">
              Cetak Rekap PDF (Watermarked)
            </button>
            <Link href="/" className="text-sm font-medium text-slate-700 bg-white border border-slate-200 px-5 py-2.5 rounded-full shadow-sm hover:bg-slate-50 transition-all">
              &larr; Kembali ke Beranda
            </Link>
          </div>
        </header>

        <div className="bg-white rounded-[2rem] shadow-[0_2px_20px_rgb(0,0,0,0.03)] border border-slate-100 overflow-hidden">
          {loading ? (
            <div className="p-12 text-center text-slate-400">Memuat data dari database SQLite...</div>
          ) : history.length === 0 ? (
            <div className="p-12 text-center text-slate-400">Belum ada riwayat verifikasi yang tersimpan di database.</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse text-sm">
                <thead>
                  <tr className="bg-slate-900 text-white">
                    <th className="p-4 font-semibold">ID</th>
                    <th className="p-4 font-semibold">Waktu</th>
                    <th className="p-4 font-semibold">Berkas / URL</th>
                    <th className="p-4 font-semibold">Format</th>
                    <th className="p-4 font-semibold">Resolusi</th>
                    <th className="p-4 font-semibold">Prediksi AI</th>
                    <th className="p-4 font-semibold">Keyakinan</th>
                    <th className="p-4 font-semibold">Platform/Sumber</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {history.map((item) => (
                    <tr key={item.id} className="hover:bg-slate-50/80 transition-colors">
                      <td className="p-4 font-mono text-slate-400">#{item.id}</td>
                      <td className="p-4 text-slate-500 text-xs">{new Date(item.waktu_pengecekan).toLocaleString("id-ID")}</td>
                      <td className="p-4 font-medium text-slate-800 max-w-[200px] truncate" title={item.nama_file}>{item.nama_file}</td>
                      <td className="p-4 text-slate-600">{item.format_gambar || "-"}</td>
                      <td className="p-4 text-slate-600 text-xs font-mono">{item.resolusi || "-"}</td>
                      <td className="p-4">
                        <span className={`px-3 py-1 rounded-full text-xs font-bold ${item.prediksi_ai === 'Real' ? 'bg-emerald-50 text-emerald-700' : 'bg-rose-50 text-rose-700'}`}>
                          {item.prediksi_ai === 'Real' ? 'Asli' : 'AI Generated'}
                        </span>
                      </td>
                      <td className="p-4 font-bold text-slate-700">{item.confidence_score}</td>
                      <td className="p-4 text-blue-600 font-medium">{item.platform || "Lokal"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </main>
  );
}