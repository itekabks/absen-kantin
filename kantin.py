import requests
import streamlit as st

st.set_page_config(
    page_title="Absensi Kantin Eka Bekasi", 
    page_icon="📌",
    layout="centered"
)

# --- CUSTOM CSS UNTUK JADIKAN GAMBAR SEBAGAI BACKGROUND ---
custom_css = """
<style>
    /* 1. Gambar dijadikan background halaman penuh */
    .stApp {
        background-image: linear-gradient(rgba(245, 247, 250, 0.75), rgba(195, 207, 226, 0.75)), url("app/static/nasi.JPG");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }

    /* Jika di Streamlit Cloud path lokal tidak terbaca, gunakan fallback ini */
    .stApp[data-test-script-path] {
        background-image: linear-gradient(rgba(255, 255, 255, 0.8), rgba(255, 255, 255, 0.8)), url("./app/static/nasi.JPG");
    }

    /* 2. Kartu Form dibuat kontras agar tulisan tetap jelas terbaca */
    [data-testid="stForm"] {
        background: rgba(255, 255, 255, 0.9) !important;
        backdrop-filter: blur(8px);
        border-radius: 20px;
        padding: 30px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        border: 1px solid rgba(255,255,255,0.5);
    }

    /* 3. Styling Tombol Kirim */
    .stButton button {
        border-radius: 10px;
        background: linear-gradient(90deg, #ff7e5f 0%, #feb47b 100%);
        color: white;
        border: none;
        font-weight: bold;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# --- TAMPILAN APLIKASI ---

# Judul Utama (Tanpa st.image lagi)
st.markdown("<h1 style='text-align: center; color: #1e293b; text-shadow: 1px 1px 2px rgba(255,255,255,0.8);'>📌 Absensi Kantin Eka Bekasi</h1>", unsafe_allow_html=True)

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
footer_html = '<div style="text-align: right; color: #334155; font-weight: 600; font-size: 0.85rem; text-shadow: 1px 1px 1px rgba(255,255,255,0.8);">Created by IT Eka Bekasi</div>'
st.markdown(footer_html, unsafe_allow_html=True)
