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
# 2. SETUP API KEY (AMAN DARI LEAK)
# ==========================================
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except:
    API_KEY = "" # Kosongkan agar aman jika bocor

if API_KEY == "":
    st.error("🚨 Sistem Terkunci: API Key Gemini belum dikonfigurasi di Secrets.")
    st.stop()

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
    ["Analisis Umum", "Klinik Bisnis & Pajak", "Kalkulator Hukum", "Dashboard Admin 🔒"]
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
# MENU 4: DASHBOARD ADMIN (PASSWORD PROTECTED)
# ==========================================
elif menu == "Dashboard Admin 🔒":
    st.title("🔒 Area Khusus Admin")
    st.write("Silakan masukkan password untuk mengakses Dapur Kreator dan Database.")
    
    # Input Password (huruf akan disamarkan menjadi bintang/titik)
    password = st.text_input("Password:", type="password")
    
    if password == "lexai1234":
        st.success("Akses Diterima. Selamat datang, Admin!")
        st.markdown("---")
        
        # Membuat TAB untuk memisahkan menu
        tab1, tab2 = st.tabs(["🎥 Generator Script Konten", "📊 Database Leads"])
        
        # ISI TAB 1 (Generator Naskah)
        with tab1:
            st.subheader("Buat Naskah Konten Cepat")
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
        
        # ISI TAB 2 (Database Leads)
        with tab2:
            st.subheader("Data Pengguna Premium")
            if os.path.exists('database_perkara.csv'):
                df = pd.read_csv('database_perkara.csv')
                # Menampilkan tabel data
                st.dataframe(df, use_container_width=True)
                
                # Tambahan: Tombol untuk download database ke Excel/CSV
                csv_data = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Unduh Database (CSV)",
                    data=csv_data,
                    file_name='Backup_Database_Leads.csv',
                    mime='text/csv',
                )
            else:
                st.info("Belum ada data masuk dari pengguna.")
                
    elif password != "":
        st.error("❌ Password salah! Anda tidak memiliki izin untuk mengakses halaman ini.")

# Footer Global
st.sidebar.markdown("---")
st.sidebar.caption("Dikembangkan oleh Gean Pratama Adiaksa SH with LexFilsafat AI")

