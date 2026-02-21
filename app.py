import streamlit as st
import google.generativeai as genai
from docx import Document
from io import BytesIO

# ==========================================
# 1. KONFIGURASI HALAMAN (FRONTEND UI)
# ==========================================
st.set_page_config(page_title="LexFilsafat AI", page_icon="⚖️", layout="centered")

st.title("⚖️ LexFilsafat AI")
st.markdown("**Asisten Analisis Hukum Positif, Filsafat & Pembuat Dokumen**")
st.write("Masukkan kronologi perkara. AI akan menganalisis kasusnya dan membuatkan draft dokumen yang bisa diunduh.")

# ==========================================
# 2. SETUP API KEY (BACKEND LOGIC)
# ==========================================
# GANTI TEKS DI BAWAH DENGAN API KEY GOOGLE GEMINI ANDA
API_KEY = "AIzaSyAbvauLRB7JUW1akFB36e90B-NdFeTKZtA" 
genai.configure(api_key=API_KEY)

# ==========================================
# 3. FUNGSI PEMBUAT FILE WORD (.docx)
# ==========================================
def create_word_docx(teks_analisis, judul_perkara):
    doc = Document()
    doc.add_heading(f'Hasil Analisis & Draft Hukum: {judul_perkara}', 0)
    
    doc.add_paragraph('Dokumen ini digenerate secara otomatis oleh LexFilsafat AI.')
    doc.add_paragraph('Disclaimer: Ini adalah draft awal/analisis edukatif dan bukan nasihat hukum yang mengikat. Harap sesuaikan kembali syarat formilnya.\n')
    
    # Memasukkan hasil AI ke dalam file Word
    doc.add_paragraph(teks_analisis)
    
    # Menyimpan file ke memory (agar bisa didownload via web)
    bio = BytesIO()
    doc.save(bio)
    return bio.getvalue()

# ==========================================
# 4. SYSTEM PROMPT
# ==========================================
system_prompt = """
Kamu adalah seorang Ahli Hukum Positif Indonesia, Filsuf Hukum, dan Drafter Dokumen Hukum. 
Tugasmu adalah menganalisis perkara dari pengguna dan membuatkan draft awal dokumen (seperti Somasi/Teguran) jika diperlukan.
WAJIB gunakan format ini:
1. ⚖️ Kualifikasi Perkara & Delik Hukum
2. 📖 Pasal & Dasar Hukum (Fokus Indonesia, sertakan KUHP UU 1/2023 atau Lex Specialis)
3. 🧠 Analisis Filsafat Hukum
4. 📚 Rujukan Ilmiah & Yurisprudensi Global
5. 📝 Draft Surat Hukum (Buatkan draft kasar surat somasi/teguran/perjanjian terkait kasus ini dengan format profesional).
"""

# ==========================================
# 5. INTERAKSI PENGGUNA (FRONTEND + BACKEND)
# ==========================================
# Input pengguna
judul_kasus = st.text_input("Judul Kasus / Perkara (Opsional):", placeholder="Contoh: Kasus Hutang Piutang Pinjol")
user_input = st.text_area("Deskripsikan kronologi perkara di sini:", height=150, 
                          placeholder="Contoh: Teman saya pinjam uang 10 juta pakai materai, janji bayar bulan lalu tapi sekarang nomor saya diblokir...")

# Tombol untuk memproses
if st.button("Analisis & Buat Dokumen 🚀"):
    if user_input.strip() == "":
        st.warning("Silakan masukkan deskripsi perkara terlebih dahulu.")
    else:
        with st.spinner('Menganalisis hukum, meracik filsafat, dan menyusun draft dokumen...'):
            try:
                # Memanggil model AI (Menggunakan gemini-2.5-flash)
                model = genai.GenerativeModel('gemini-2.5-flash')
                
                full_prompt = f"{system_prompt}\n\nPerkara Pengguna:\n{user_input}"
                response = model.generate_content(full_prompt)
                
                teks_hasil = response.text
                
                # Menampilkan hasil di layar web
                st.success("Analisis & Draft Dokumen Selesai!")
                st.markdown("---")
                st.markdown(teks_hasil)
                
                # Menyiapkan file Word untuk diunduh
                judul_file = judul_kasus if judul_kasus else "Perkara_Hukum"
                docx_file = create_word_docx(teks_hasil, judul_file)
                
                st.markdown("---")
                st.subheader("📥 Unduh Hasil")
                st.write("Klik tombol di bawah ini untuk mengunduh hasil analisis dan draft surat dalam format Microsoft Word.")
                
                # Tombol Download Streamlit
                st.download_button(
                    label="📄 Unduh Dokumen (.docx)",
                    data=docx_file,
                    file_name=f"{judul_file.replace(' ', '_')}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
                
            except Exception as e:
                st.error(f"Terjadi kesalahan saat menghubungi AI: {e}")

# Footer
st.markdown("---")
st.caption("Dikembangkan oleh LexFilsafat AI")