import streamlit as st
import google.generativeai as genai
from docx import Document
from io import BytesIO
import pandas as pd
import os
from datetime import datetime

# ==========================================
# 1. KONFIGURASI HALAMAN
# ==========================================
st.set_page_config(page_title="LexFilsafat AI - Super App By Gean Pratama Adiaksa SH", page_icon="⚖️", layout="wide")

# Setup API Key (Gunakan st.secrets saat deploy di Streamlit Cloud)
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except:
    API_KEY = "MASUKKAN_API_KEY_ANDA_DISINI" # Untuk tes lokal
genai.configure(api_key=API_KEY)

# ==========================================
# FUNGSI BANTUAN
# ==========================================
def create_word_docx(teks_analisis, judul_perkara):
    doc = Document()
    doc.add_heading(f'Dokumen Hukum: {judul_perkara}', 0)
    doc.add_paragraph(teks_analisis)
    bio = BytesIO()
    doc.save(bio)
    return bio.getvalue()

def simpan_ke_database(nama, email, kasus):
    # Menyimpan data user ke file CSV lokal (sebagai pondasi database)
    file_path = 'database_perkara.csv'
    data_baru = pd.DataFrame({'Tanggal': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")], 'Nama': [nama], 'Email': [email], 'Kasus': [kasus]})
    if os.path.exists(file_path):
        data_lama = pd.read_csv(file_path)
        data_final = pd.concat([data_lama, data_baru], ignore_index=True)
    else:
        data_final = data_baru
    data_final.to_csv(file_path, index=False)

# ==========================================
# 2. SIDEBAR NAVIGASI
# ==========================================
st.sidebar.title("⚖️ LexFilsafat Menu")
menu = st.sidebar.radio("Pilih Layanan:", 
    ["Analisis Umum", "Klinik Bisnis & Pajak", "Kalkulator Hukum", "Mode Kreator (Admin)", "Database Leads"]
)

# Inisialisasi Model AI
model = genai.GenerativeModel('gemini-2.5-flash')

# ==========================================
# MENU 1: ANALISIS UMUM (Dengan Fitur Freemium/Lead Gen)
# ==========================================
if menu == "Analisis Umum":
    st.title("⚖️ Analisis Perkara Umum")
    user_input = st.text_area("Deskripsikan kronologi perkara:", height=150)
    
    st.info("💡 **Fitur Premium:** Masukkan nama dan email/WhatsApp Anda untuk mengunduh Draft Dokumen Hukum yang mendetail.")
    col1, col2 = st.columns(2)
    with col1:
        user_nama = st.text_input("Nama Anda (Opsional):")
    with col2:
        user_email = st.text_input("Email / WhatsApp (Opsional):")

    if st.button("Analisis Kasus"):
        with st.spinner("Menganalisis..."):
            prompt = f"Sebagai Ahli Hukum & Filsafat. Analisis kasus ini: {user_input}. Berikan Kualifikasi Perkara, Pasal, Filsafat, dan Rujukan."
            hasil = model.generate_content(prompt).text
            st.markdown(hasil)
            
            if user_nama and user_email:
                simpan_ke_database(user_nama, user_email, user_input)
                prompt_draft = f"Buatkan draft surat hukum formal (misal somasi/gugatan) untuk kasus: {user_input}"
                draft = model.generate_content(prompt_draft).text
                docx_file = create_word_docx(draft, "Draft_Hukum")
                st.download_button("📥 Unduh Draft Spesifik (.docx)", data=docx_file, file_name="Draft_Premium.docx")
            else:
                st.warning("⚠️ Masukkan Nama dan Email di atas untuk membuka tombol Unduh Draft Surat Hukum.")

# ==========================================
# MENU 2: KLINIK BISNIS & PAJAK
# ==========================================
elif menu == "Klinik Bisnis & Pajak":
    st.title("🏢 Klinik Legal Bisnis & Pajak UMKM")
    st.write("Konsultasi legalitas usaha, kontrak kemitraan, hingga kepatuhan pajak.")
    
    kasus_bisnis = st.text_area("Apa kendala bisnis Anda?", height=150, 
                                placeholder="Contoh 1: Kendala sinkronisasi pelaporan Coretax untuk Wajib Pajak OP dengan omzet di bawah 4,8 Miliar.\nContoh 2: Mau buat perjanjian kemitraan cabang Dina Laundry.\nContoh 3: Sengketa resep dengan mantan karyawan bakery.")
    
    if st.button("Konsultasi Bisnis"):
        with st.spinner("Menyusun opini legal bisnis..."):
            prompt_bisnis = f"Sebagai Corporate Lawyer dan Konsultan Pajak Indonesia. Berikan opini legal, regulasi pajak/Cipta Kerja terbaru, dan mitigasi risiko terkait bisnis ini: {kasus_bisnis}"
            st.markdown(model.generate_content(prompt_bisnis).text)

# ==========================================
# MENU 3: KALKULATOR HUKUM
# ==========================================
elif menu == "Kalkulator Hukum":
    st.title("🧮 Kalkulator Pesangon PHK (UU Cipta Kerja)")
    gaji = st.number_input("Masukkan Gaji Pokok (Rp):", min_value=0, step=1000000)
    masa_kerja = st.number_input("Lama Bekerja (Tahun):", min_value=0, step=1)
    
    if st.button("Hitung Estimasi"):
        # Logika sederhana UU Ciptaker (Bisa diperdalam lagi)
        uang_pesangon = min(masa_kerja, 9) * gaji
        uang_penghargaan = max(0, ((masa_kerja - 3) // 3) * gaji) # Contoh penyederhanaan
        total = uang_pesangon + uang_penghargaan
        st.success(f"**Estimasi Hak Pesangon & Penghargaan Masa Kerja:** Rp {total:,.2f}")
        st.caption("Catatan: Ini adalah estimasi kasar. Angka pasti bergantung pada alasan PHK (efisiensi, pailit, dll).")

# ==========================================
# MENU 4: MODE KREATOR (ADMIN ONLY)
# ==========================================
elif menu == "Mode Kreator (Admin)":
    st.title("🎥 Generator Script Konten Hukum & Ekonomi")
    st.write("Ubah ide kasar menjadi script siap rekam untuk YouTube atau TikTok.")
    
    ide_konten = st.text_input("Topik hari ini:", placeholder="Contoh: Logika hukum di balik pinjol ilegal vs utang bank.")
    platform = st.selectbox("Pilih Platform:", ["YouTube Shorts (60 detik)", "Instagram Carousel (5 Slide)", "Video YouTube Panjang"])
    
    if st.button("Buat Naskah Konten"):
        with st.spinner("Sedang meracik hook dan storytelling..."):
            prompt_kreator = f"Kamu adalah Scriptwriter. Buatkan naskah untuk {platform} dengan topik: {ide_konten}. Target audiens: Gen-Z/Milenial yang tertarik isu hukum dan ekonomi. Berikan format visual/teks layar dan audio yang detail. Gunakan gaya bahasa 'deep but digestible'."
            st.markdown(model.generate_content(prompt_kreator).text)

# ==========================================
# MENU 5: DATABASE LEADS
# ==========================================
elif menu == "Database Leads":
    st.title("📊 Database Klien / Leads")
    st.write("Kumpulan kontak user yang menggunakan fitur premium aplikasi Anda.")
    
    if os.path.exists('database_perkara.csv'):
        df = pd.read_csv('database_perkara.csv')
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Belum ada data masuk.")
