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
st.set_page_config(page_title="LexFilsafat AI - Super App", page_icon="⚖️", layout="wide")

# ==========================================
# 2. SETUP API KEY (DENGAN PENANGANAN ERROR)
# ==========================================
# Mengambil API Key dari Secrets Streamlit Cloud
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except:
    # Jika gagal membaca rahasia, gunakan variabel lokal (Ganti saat tes di laptop)
    API_KEY = "MASUKKAN_API_KEY_ANDA_DISINI" 

# Pengecekan agar web tidak crash jika API Key belum diisi
if API_KEY == "MASUKKAN_API_KEY_ANDA_DISINI" or API_KEY == "":
    st.error("🚨 **Sistem Terkunci:** API Key Gemini belum dikonfigurasi dengan benar. Silakan cek menu 'Secrets' di pengaturan Streamlit Cloud Anda.")
    st.stop() # Menghentikan kode ke bawah agar tidak muncul error merah panjang

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
    file_path = 'database_perkara.csv'
    data_baru = pd.DataFrame({'Tanggal': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")], 'Nama': [nama], 'Email': [email], 'Kasus': [kasus]})
    if os.path.exists(file_path):
        data_lama = pd.read_csv(file_path)
        data_final = pd.concat([data_lama, data_baru], ignore_index=True)
    else:
        data_final = data_baru
    data_final.to_csv(file_path, index=False)

# ==========================================
# 3. SIDEBAR NAVIGASI
# ==========================================
st.sidebar.title("⚖️ LexFilsafat Menu")
menu = st.sidebar.radio("Pilih Layanan:", 
    ["Analisis Umum", "Klinik Bisnis & Pajak", "Kalkulator Hukum", "Mode Kreator (Admin)", "Database Leads"]
)

# Inisialisasi Model AI
model = genai.GenerativeModel('gemini-2.5-flash')

# ==========================================
# MENU 1: ANALISIS UMUM
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
        # VALIDASI: Cek apakah user sudah mengisi kasusnya
        if not user_input.strip():
            st.warning("⚠️ Hei! Anda belum mengisi deskripsi perkara. Silakan ketik kronologinya terlebih dahulu.")
        else:
            with st.spinner("Menganalisis..."):
                try:
                    prompt = f"Sebagai Ahli Hukum & Filsafat. Analisis kasus ini: {user_input}. Berikan Kualifikasi Perkara, Pasal, Filsafat, dan Rujukan."
                    hasil = model.generate_content(prompt).text
                    st.success("Analisis berhasil!")
                    st.markdown(hasil)
                    
                    if user_nama and user_email:
                        simpan_ke_database(user_nama, user_email, user_input)
                        prompt_draft = f"Buatkan draft surat hukum formal (misal somasi/gugatan) untuk kasus: {user_input}"
                        draft = model.generate_content(prompt_draft).text
                        docx_file = create_word_docx(draft, "Draft_Hukum")
                        st.download_button("📥 Unduh Draft Spesifik (.docx)", data=docx_file, file_name="Draft_Premium.docx")
                    else:
                        st.warning("⚠️ Masukkan Nama dan Email di atas untuk membuka tombol Unduh Draft Surat Hukum.")
                except Exception as e:
                    st.error(f"Terjadi masalah pada server AI: {e}")

# ==========================================
# MENU 2: KLINIK BISNIS & PAJAK
# ==========================================
elif menu == "Klinik Bisnis & Pajak":
    st.title("🏢 Klinik Legal Bisnis & Pajak UMKM")
    kasus_bisnis = st.text_area("Apa kendala bisnis Anda?", height=150)
    
    if st.button("Konsultasi Bisnis"):
        if not kasus_bisnis.strip():
            st.warning("⚠️ Silakan jelaskan dulu kendala bisnis atau pajak Anda.")
        else:
            with st.spinner("Menyusun opini legal bisnis..."):
                try:
                    prompt_bisnis = f"Sebagai Corporate Lawyer dan Konsultan Pajak Indonesia. Berikan opini legal, regulasi pajak/Cipta Kerja terbaru, dan mitigasi risiko terkait bisnis ini: {kasus_bisnis}"
                    st.markdown(model.generate_content(prompt_bisnis).text)
                except Exception as e:
                    st.error(f"Terjadi masalah pada server AI: {e}")

# ==========================================
# MENU 3: KALKULATOR HUKUM
# ==========================================
elif menu == "Kalkulator Hukum":
    st.title("🧮 Kalkulator Pesangon PHK")
    gaji = st.number_input("Masukkan Gaji Pokok (Rp):", min_value=0, step=1000000)
    masa_kerja = st.number_input("Lama Bekerja (Tahun):", min_value=0, step=1)
    
    if st.button("Hitung Estimasi"):
        uang_pesangon = min(masa_kerja, 9) * gaji
        uang_penghargaan = max(0, ((masa_kerja - 3) // 3) * gaji)
        total = uang_pesangon + uang_penghargaan
        st.success(f"**Estimasi Hak Pesangon & Penghargaan Masa Kerja:** Rp {total:,.2f}")

# ==========================================
# MENU 4: MODE KREATOR (ADMIN ONLY)
# ==========================================
elif menu == "Mode Kreator (Admin)":
    st.title("🎥 Generator Script Konten Hukum & Ekonomi")
    ide_konten = st.text_input("Topik hari ini:", placeholder="Contoh: Logika hukum pinjol ilegal.")
    platform = st.selectbox("Pilih Platform:", ["YouTube Shorts (60 detik)", "Instagram Carousel (5 Slide)", "Video YouTube Panjang"])
    
    if st.button("Buat Naskah Konten"):
        if not ide_konten.strip():
            st.warning("⚠️ Silakan masukkan topik kontennya terlebih dahulu!")
        else:
            with st.spinner("Sedang meracik hook dan storytelling..."):
                try:
                    prompt_kreator = f"Kamu adalah Scriptwriter. Buatkan naskah untuk {platform} dengan topik: {ide_konten}. Target audiens: Gen-Z/Milenial. Berikan format visual/teks layar dan audio yang detail."
                    st.markdown(model.generate_content(prompt_kreator).text)
                except Exception as e:
                    st.error(f"Terjadi masalah pada server AI: {e}")

# ==========================================
# MENU 5: DATABASE LEADS
# ==========================================
elif menu == "Database Leads":
    st.title("📊 Database Klien / Leads")
    if os.path.exists('database_perkara.csv'):
        df = pd.read_csv('database_perkara.csv')
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Belum ada data masuk.")
