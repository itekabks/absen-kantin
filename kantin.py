import requests
import streamlit as st

st.set_page_config(
    page_title="Absensi Kantin Eka Bekasi", 
    page_icon="📌",
    layout="centered"
)

# --- CUSTOM CSS UNTUK EFEK BACKGROUND & TAMPILAN ---
custom_css = """
<style>
    /* 1. Background Halaman Gradasi Soft */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }

    /* 2. Efek Card Glassmorphism untuk Form */
    [data-testid="stForm"] {
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 30px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        border: 1px solid rgba(255,255,255,0.3);
    }

    /* 3. Menghaluskan Sudut Gambar */
    [data-testid="stImage"] img {
        border-radius: 20px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.15);
    }

    /* 4. Efek Tombol Animasi saat Hover */
    .stButton button {
        border-radius: 10px;
        background: linear-gradient(90deg, #ff7e5f 0%, #feb47b 100%);
        color: white;
        border: none;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(255, 126, 95, 0.4);
        color: white;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# --- TAMPILAN APLIKASI ---

# Gambar Header
st.image("nasi.JPG", use_container_width=True)

# Judul Utama
st.markdown("<h1 style='text-align: center; color: #2c3e50;'>📌 Absensi Kantin Eka Bekasi</h1>", unsafe_allow_html=True)

FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeHkJyHQClWw18bR2SLHBmpMWVuwYJpfERpBm--APFxsWGc1w/formResponse"
ENTRY_NIK = "entry.924986826"

# Form Input Absen
with st.form(key="form_absen", clear_on_submit=True):
    nik = st.text_input("Masukkan NIK Anda (lalu tekan Enter):")
    submit_button = st.form_submit_button(label="Kirim Absen", use_container_width=True)

# Proses Kirim
if submit_button:
    if nik.strip():
        payload = {ENTRY_NIK: nik}
        try:
            response = requests.post(FORM_URL, data=payload)
            if response.status_code == 200:
                st.success(f"✅ Berhasil absen untuk NIK: {nik}")
            else:
                st.error("Gagal mengirim data. Periksa kembali pengaturan Form Anda.")
        except Exception as e:
            st.error(f"Terjadi kesalahan koneksi: {e}")
    else:
        st.warning("NIK tidak boleh kosong!")

st.write("")
st.write("")

# Footer
footer_html = '<div style="text-align: right; color: #7f8c8d; font-weight: 500; font-size: 0.85rem;">Created by IT Eka Bekasi</div>'
st.markdown(footer_html, unsafe_allow_html=True)
