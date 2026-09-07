import base64
import os
import pandas as pd
import requests
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="[TEST] Absensi Kantin Eka Bekasi", 
    page_icon="🧪",
    layout="centered"
)

# --- FUNGSI BACA DATABASE KARYAWAN FROM CSV (MODE TEST) ---
@st.cache_data(ttl=10) # Cache diperbarui tiap 10 detik agar responsif saat edit CSV
def load_data_karyawan():
    file_path = "karyawan.csv"
    if os.path.exists(file_path):
        # Membaca NIK sebagai string/teks agar nol di depan tidak hilang
        df = pd.read_csv(file_path, dtype={'nik': str})
        df['nik'] = df['nik'].astype(str).str.strip()
        df['nama'] = df['nama'].astype(str).str.strip()
        return dict(zip(df['nik'], df['nama']))
    return {}

db_karyawan = load_data_karyawan()

# --- BACKGROUND & CUSTOM CSS ---
def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

img_base64 = get_base64_image("nasi.JPG")

if img_base64:
    bg_css = f"""
    <style>
        .stApp {{
            background-image: linear-gradient(rgba(245, 247, 250, 0.75), rgba(195, 207, 226, 0.75)), url("data:image/jpeg;base64,{img_base64}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
    </style>
    """
    st.markdown(bg_css, unsafe_allow_html=True)

custom_css = """
<style>
    /* Styling Form Glassmorphism */
    [data-testid="stForm"] {
        background: rgba(255, 255, 255, 0.88) !important;
        backdrop-filter: blur(8px);
        border-radius: 20px;
        padding: 30px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.15);
        border: 1px solid rgba(255,255,255,0.4);
    }

    /* Styling Tombol Kirim Mode Test (Biru) */
    .stButton button {
        border-radius: 10px;
        background: linear-gradient(90deg, #3b82f6 0%, #1d4ed8 100%);
        color: white;
        border: none;
        font-weight: bold;
    }

    /* Custom Notifikasi Sukses (st.success) - Warna Jelas & Font Besar */
    div[data-testid="stNotification"] {
        border-radius: 12px !important;
        padding: 16px !important;
    }

    div[data-testid="stNotification"][data-test-script-type="success"] {
        background-color: #059669 !important; /* Hijau Emerald Solid */
        border: 1px solid #10b981 !important;
        box-shadow: 0 6px 15px rgba(0,0,0,0.2) !important;
    }

    /* Memperbesar Font Teks di Dalam Notifikasi Sukses */
    div[data-testid="stNotification"][data-test-script-type="success"] p,
    div[data-testid="stNotification"][data-test-script-type="success"] span,
    div[data-testid="stNotification"][data-test-script-type="success"] div {
        color: #ffffff !important;
        font-size: 1.3rem !important; /* Ukuran font diperbesar */
        font-weight: 700 !important;   /* Cetak tebal */
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# Header Mode Test
st.markdown("<h1 style='text-align: center; color: #1e293b; text-shadow: 1px 1px 2px rgba(255,255,255,0.8);'>🧪 [TESTING] Absensi Kantin Eka Bekasi</h1>", unsafe_allow_html=True)

# URL & Entry Google Form versi TEST
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLScnTi-b9vCrBSRMr-G7k3_4buevp02nJ9J6ybkatj5SGCKKfw/formResponse"
ENTRY_NIK = "entry.952185819"

# Form Input Absen
with st.form(key="form_absen_test", clear_on_submit=True):
    nik = st.text_input("Masukkan NIK Anda (lalu tekan Enter):")
    submit_button = st.form_submit_button(label="Kirim Absen (TEST)", use_container_width=True)

# Auto-Focus Javascript
components.html(
    """
    <script>
        const focusInput = () => {
            const inputs = window.parent.document.querySelectorAll('input[type="text"]');
            if (inputs.length > 0) {
                inputs[0].focus();
            }
        };
        setTimeout(focusInput, 300);
    </script>
    """,
    height=0,
    width=0
)

# --- PROSES KIRIM ABSEN & CEK DATABASE ---
if submit_button:
    nik_clean = nik.strip()
    if nik_clean:
        # Cek apakah NIK ada di database CSV
        nama_karyawan = db_karyawan.get(nik_clean)

        payload = {ENTRY_NIK: nik_clean}
        try:
            response = requests.post(FORM_URL, data=payload)
            if response.status_code == 200:
                if nama_karyawan:
                    # Menampilkan Nama Karyawan jika terdaftar
                    st.success(f"✅ Berhasil Absen: **{nama_karyawan.title()}** (NIK: {nik_clean})")
                else:
                    # Jika NIK belum terdaftar di database CSV
                    st.warning(f"⚠️ Berhasil Absen NIK: **{nik_clean}** *(Nama belum terdaftar di database)*")
            else:
                st.error(f"❌ Gagal mengirim data. Response Code: {response.status_code}")
        except Exception as e:
            st.error(f"Terjadi kesalahan koneksi: {e}")
    else:
        st.warning("NIK tidak boleh kosong!")

st.write("")
st.write("")

# Footer Mode Test
footer_html = '<div style="text-align: right; color: #334155; font-weight: 600; font-size: 0.85rem; text-shadow: 1px 1px 1px rgba(255,255,255,0.8);">[TEST ENVIRONMENT] IT Eka Bekasi</div>'
st.markdown(footer_html, unsafe_allow_html=True)
