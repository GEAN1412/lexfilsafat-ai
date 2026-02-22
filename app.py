import streamlit as st
import google.generativeai as genai
from docx import Document
from io import BytesIO
import pandas as pd
import os
from datetime import datetime
import json
from PIL import Image, ImageDraw, ImageFont
import textwrap

# ==========================================
# 1. KONFIGURASI HALAMAN
# ==========================================
st.set_page_config(page_title="LexFilsafat AI - Super App", page_icon="⚖️", layout="wide")

# KONFIGURASI DESAIN INSTAGRAM
FONT_HEADLINE_PATH = "Roboto-Bold.ttf"  # Pastikan file ini ada di GitHub
FONT_BODY_PATH = "Roboto-Regular.ttf"   # Pastikan file ini ada di GitHub
BG_COLOR = "#1E1E1E"    # Latar Belakang Gelap (Dark Mode)
TEXT_COLOR = "#FFFFFF"  # Teks Putih
ACCENT_COLOR = "#FFD700" # Emas (Khas Hukum/Elegan)

# ==========================================
# 2. SETUP API KEY (AMAN DARI LEAK)
# ==========================================
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except:
    API_KEY = ""

if API_KEY == "":
    st.error("🚨 Sistem Terkunci: API Key Gemini belum dikonfigurasi di Secrets.")
    st.stop()

genai.configure(api_key=API_KEY)

# ==========================================
# FUNGSI BANTUAN (Word & Database)
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
# FUNGSI BARU: GENERATOR GAMBAR (PILLOW)
# ==========================================
def create_instagram_slide(headline, body, slide_num):
    # 1. Buat Kanvas 1080x1080
    img = Image.new('RGB', (1080, 1080), color=BG_COLOR)
    draw = ImageDraw.Draw(img)

    # 2. Load Font (Dengan Fallback ke Default jika file ttf tidak ada)
    try:
        font_h = ImageFont.truetype(FONT_HEADLINE_PATH, 80) # Ukuran Headline
        font_b = ImageFont.truetype(FONT_BODY_PATH, 45)     # Ukuran Body
        font_s = ImageFont.truetype(FONT_BODY_PATH, 30)     # Ukuran Footer
    except:
        # Jika user lupa upload font, pakai default (jelek tapi jalan)
        font_h = ImageFont.load_default()
        font_b = ImageFont.load_default()
        font_s = ImageFont.load_default()

    # 3. Setup Margin & Text Wrapping
    margin = 80
    max_width_h = 20 # Karakter per baris untuk Headline
    max_width_b = 35 # Karakter per baris untuk Body

    # 4. Gambar Headline (Warna Emas)
    wrapped_h = textwrap.fill(headline, width=max_width_h)
    draw.text((margin, 150), wrapped_h, font=font_h, fill=ACCENT_COLOR)

    # Hitung tinggi headline agar body text tidak bertabrakan
    bbox = draw.textbbox((margin, 150), wrapped_h, font=font_h)
    h_height = bbox[3] 
    
    # 5. Gambar Body Text (Warna Putih) di bawah Headline
    wrapped_b = textwrap.fill(body, width=max_width_b)
    draw.text((margin, h_height + 60), wrapped_b, font=font_b, fill=TEXT_COLOR)

    # 6. Gambar Footer & Elemen Grafis
    # Garis aksen di bawah
    draw.rectangle([(margin, 980), (1080-margin, 990)], fill=ACCENT_COLOR)
    # Watermark
    draw.text((margin, 1000), f"Slide {slide_num} • LexFilsafat AI", font=font_s, fill=TEXT_COLOR)

    return img

# ==========================================
# 3. SIDEBAR NAVIGASI
# ==========================================
st.sidebar.title("⚖️ LexFilsafat Menu")
menu = st.sidebar.radio("Pilih Layanan:", 
    ["Analisis Umum", "Klinik Bisnis & Pajak", "Kalkulator Hukum", "Dashboard Admin 🔒"]
)

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
            st.warning("⚠️ Isi dulu kronologi perkaranya.")
        else:
            with st.spinner("Menganalisis..."):
                try:
                    prompt = f"Sebagai Ahli Hukum. Analisis: {user_input}. Berikan Kualifikasi, Pasal, Filsafat, Rujukan."
                    hasil = model.generate_content(prompt).text
                    st.success("Selesai!")
                    st.markdown(hasil)
                    
                    if user_nama and user_email:
                        simpan_ke_database(user_nama, user_email, user_input)
                        prompt_draft = f"Buatkan draft surat hukum formal untuk: {user_input}"
                        draft = model.generate_content(prompt_draft).text
                        docx_file = create_word_docx(draft, "Draft_Hukum")
                        st.download_button("📥 Unduh Draft (.docx)", data=docx_file, file_name="Draft_Premium.docx")
                except Exception as e:
                    st.error(f"Error AI: {e}")

# ==========================================
# MENU 2 & 3 (Placeholder)
# ==========================================
elif menu == "Klinik Bisnis & Pajak":
    st.title("🏢 Klinik Legal Bisnis & Pajak")
    st.info("Fitur sedang dalam maintenance untuk upgrade sistem.")

elif menu == "Kalkulator Hukum":
    st.title("🧮 Kalkulator Pesangon")
    st.info("Fitur sedang dalam maintenance untuk upgrade sistem.")

# ==========================================
# MENU 4: DASHBOARD ADMIN (PASSWORD PROTECTED)
# ==========================================
elif menu == "Dashboard Admin 🔒":
    st.title("🔒 Area Khusus Admin")
    password = st.text_input("Password:", type="password")
    
    if password == "lexai1234":
        st.success("Akses Admin Diterima.")
        st.markdown("---")
        
        tab1, tab2 = st.tabs(["🎥 Generator Konten (Auto-Image)", "📊 Database Leads"])
        
        # TAB 1: GENERATOR KONTEN
        with tab1:
            st.subheader("Dapur Konten Otomatis")
            ide_konten = st.text_input("Topik Konten:", placeholder="Contoh: Utang Pinjol vs Utang Teman")
            platform = st.selectbox("Format:", [
                "Instagram Feed (Auto-Generate Gambar)",
                "YouTube Shorts / Veo (Naskah Video)"
            ])
            
            if st.button("Generate Konten 🚀"):
                if not ide_konten.strip():
                    st.warning("Masukkan topik dulu!")
                else:
                    # --- LOGIKA INSTAGRAM (AUTO GAMBAR) ---
                    if "Instagram" in platform:
                        with st.spinner("Meracik naskah & Menggambar slide..."):
                            try:
                                # Prompt JSON Strict
                                prompt_ig = f"""
                                Kamu adalah Social Media Manager. Buat konten Instagram 5 slide tentang: "{ide_konten}".
                                Target: Gen-Z. Bahasa: Santai, Edukatif, Nendang.
                                
                                PENTING: Output HANYA boleh format JSON murni. Jangan ada teks lain.
                                Struktur JSON:
                                {{
                                  "caption": "Caption instagram lengkap dengan hashtag...",
                                  "slides": [
                                    {{"headline": "Judul Slide 1 (Max 5 Kata)", "body": "Penjelasan ringkas slide 1..."}},
                                    {{"headline": "Judul Slide 2", "body": "Penjelasan slide 2..."}},
                                    {{"headline": "Judul Slide 3", "body": "Penjelasan slide 3..."}},
                                    {{"headline": "Judul Slide 4", "body": "Penjelasan slide 4..."}},
                                    {{"headline": "Judul Slide 5 (Kesimpulan)", "body": "Call to action..."}}
                                  ]
                                }}
                                """
                                response = model.generate_content(prompt_ig)
                                # Bersihkan Markdown JSON
                                json_str = response.text.replace("```json", "").replace("```", "").strip()
                                data = json.loads(json_str)
                                
                                # Tampilkan Caption
                                st.subheader("1. Caption (Copy Paste)")
                                st.code(data['caption'], language='text')
                                
                                # Tampilkan Gambar
                                st.subheader("2. Slide Gambar (Klik Kanan -> Save Image)")
                                cols = st.columns(5)
                                for i, slide in enumerate(data['slides']):
                                    img = create_instagram_slide(slide['headline'], slide['body'], i+1)
                                    with cols[i]:
                                        st.image(img, caption=f"Slide {i+1}", use_column_width=True)

                            except Exception as e:
                                st.error(f"Gagal generate gambar. Coba lagi. Error: {e}")
                    
                    # --- LOGIKA VIDEO VEO (MARKDOWN TABLE) ---
                    else:
                        with st.spinner("Menulis naskah video..."):
                            prompt_video = f"""
                            Buatkan naskah video Shorts tentang: "{ide_konten}".
                            Format Markdown Table:
                            | No | Naskah Voiceover | Visual Prompt (English for Veo) |
                            |---|---|---|
                            | 1 | ... | `cinematic shot...` |
                            """
                            st.markdown(model.generate_content(prompt_video).text)

        # TAB 2: DATABASE
        with tab2:
            st.subheader("Data Leads")
            if os.path.exists('database_perkara.csv'):
                df = pd.read_csv('database_perkara.csv')
                st.dataframe(df)
            else:
                st.info("Belum ada data.")

    elif password != "":
        st.error("Password Salah!")
