from datetime import datetime
import base64
import os
import time
import pandas as pd
import requests
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Absensi Kantin Eka Bekasi (Server Test)", 
    page_icon="📌",
    layout="wide"
)

# --- CONFIGURATION VIA STREAMLIT SECRETS & CONSTANTS (SERVER TEST) ---
ADMIN_PASSWORD = "Eka1234!"

# Link Rekap Responses Google Form Server Test
RESPONSES_URL = "https://docs.google.com/forms/d/1yXnImWhn058mHP4DZ8l6F03AxaGljZGos-wZpJcyPVY/edit#responses"

# 1. ID & Link Google Sheet DATABASE KARYAWAN TEST
KARYAWAN_SPREADSHEET_ID = "1mdIv5YXs7IHS0DQO4uNhsqrVeDT6aTgQk2EbGI_10nk"
KARYAWAN_SPREADSHEET_URL = f"https://docs.google.com/spreadsheets/d/{KARYAWAN_SPREADSHEET_ID}/edit"

# 2. ID Google Sheet REKAP HASIL ABSENSI TEST
RESPONSES_SPREADSHEET_ID = "MASUKKAN_ID_SPREADSHEET_GOOGLE_FORM_DI_SINI"


# --- FUNGSI BACA DATABASE KARYAWAN DARI GOOGLE SPREADSHEET TEST ---
@st.cache_data(ttl=10)
def load_data_karyawan():
    if not KARYAWAN_SPREADSHEET_ID:
        return {}
        
    csv_url = f"https://docs.google.com/spreadsheets/d/{KARYAWAN_SPREADSHEET_ID}/gviz/tq?tqx=out:csv&nocache={int(time.time())}"
    
    try:
        df = pd.read_csv(csv_url, dtype=str)
        
        if df.empty:
            return {}
            
        col_nik = [c for c in df.columns if 'nik' in c.strip().lower()][0]
        col_nama = [c for c in df.columns if 'nama' in c.strip().lower()][0]
        
        df['nik_clean'] = df[col_nik].astype(str).str.strip().str.replace(".0", "", regex=False).str.zfill(8)
        df['nama_clean'] = df[col_nama].astype(str).str.strip()
        
        return dict(zip(df['nik_clean'], df['nama_clean']))
    except Exception:
        return {}


# --- FUNGSI CEK ABSEN DUPLIKAT HARI INI ---
def is_already_absent_today(nik):
    if RESPONSES_SPREADSHEET_ID == "MASUKKAN_ID_SPREADSHEET_GOOGLE_FORM_DI_SINI":
        return False
        
    csv_url = f"https://docs.google.com/spreadsheets/d/{RESPONSES_SPREADSHEET_ID}/gviz/tq?tqx=out:csv&nocache={int(time.time())}"
    
    try:
        df_responses = pd.read_csv(csv_url)
        
        if df_responses.empty:
            return False
            
        df_responses.iloc[:, 0] = pd.to_datetime(df_responses.iloc[:, 0], errors='coerce')
        today_date = datetime.now().date()
        
        nik_input = str(nik).strip()
        nik_in_sheet = df_responses.iloc[:, 1].astype(str).str.strip().str.replace(".0", "", regex=False).str.zfill(8)
        
        already_exists = df_responses[
            (nik_in_sheet == nik_input) & 
            (df_responses.iloc[:, 0].dt.date == today_date)
        ]
        
        return not already_exists.empty
    except Exception:
        return False


db_karyawan = load_data_karyawan()

# --- BACKGROUND & CUSTOM CSS (SUPER JUMBO VERSION) ---
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
            background-image: linear-gradient(rgba(245, 247, 250, 0.70), rgba(195, 207, 226, 0.70)), url("data:image/jpeg;base64,{img_base64}");
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
    /* Container styling diperlebar maksimal untuk tampilan TV/Monitor */
    .stMainBlockContainer {
        max-width: 1100px !important;
        padding-top: 2rem !important;
    }

    /* Input Field Styling - EKSTRA JUMBO */
    div[data-testid="stTextInput"] input {
        background-color: #ffffff !important; 
        color: #0f172a !important;            
        font-size: 5.5rem !important;         /* Angka NIK Super Besar */
        font-weight: 900 !important;          
        height: 120px !important;             /* Kotak Input Ekstra Tinggi */
        text-align: center !important;        
        letter-spacing: 12px !important;      /* Jarak antar angka diperlebar */
        border-radius: 20px !important;
        border: 5px solid #2563eb !important; 
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2) !important;
    }

    /* Efek Focus Input */
    div[data-testid="stTextInput"] input:focus {
        border-color: #1d4ed8 !important;
        box-shadow: 0 0 0 8px rgba(37, 99, 235, 0.4) !important;
    }

    /* Sembunyikan Helper Text Bawaan & Label standar */
    div[data-testid="stTextInput"] small,
    div[data-testid="stTextInput"] div[data-aria-live="polite"] {
        display: none !important;
    }

    /* HEADER EXPANDER ADMIN */
    div[data-testid="stExpander"] summary {
        background-color: rgba(255, 255, 255, 0.95) !important;
        border-radius: 12px !important;
        border: 2px solid #cbd5e1 !important;
        padding: 12px 20px !important;
    }
    div[data-testid="stExpander"] summary * {
        color: #0f172a !important;
        font-weight: 800 !important;
        font-size: 1.3rem !important;
    }

    /* TEKS PANEL ADMIN */
    div[data-testid="stExpander"] p, 
    div[data-testid="stExpander"] span:not(button span) {
        color: #0f172a !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
    }

    /* TOMBOL LOGOUT */
    div[data-testid="stExpander"] button[kind="secondary"] {
        background-color: #dc2626 !important;
        border: none !important;
        border-radius: 10px !important;
    }
    div[data-testid="stExpander"] button[kind="secondary"] * {
        color: #ffffff !important;
        font-weight: 800 !important;
    }

    /* TOMBOL EDIT DATA */
    div[data-testid="stExpander"] a[data-testid="stLinkButton"] {
        background-color: #2563eb !important;
        border: none !important;
        border-radius: 10px !important;
    }
    div[data-testid="stExpander"] a[data-testid="stLinkButton"] * {
        color: #ffffff !important;
        font-weight: 800 !important;
    }

    /* TAB HEADER */
    button[data-baseweb="tab"] * {
        color: #0f172a !important;
        font-weight: 800 !important;
        font-size: 1.2rem !important;
    }

    /* NOTIFIKASI HASIL ABSEN (SUPER JELAS) */
    div[data-testid="stAlert"]:not(:has(svg[data-testid="stIconInfo"])) {
        border-radius: 20px !important;
        padding: 30px !important;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.3) !important;
    }
    div[data-testid="stAlert"]:not(:has(svg[data-testid="stIconInfo"])) *,
    div[data-testid="stAlert"]:not(:has(svg[data-testid="stIconInfo"])) p {
        color: #ffffff !important;
        font-size: 2.8rem !important;          
        font-weight: 900 !important;
        line-height: 1.3 !important;
        text-shadow: 2px 2px 6px rgba(0, 0, 0, 0.6) !important;
    }
    div[data-testid="stAlert"]:has(svg[data-testid="stIconSuccess"]) {
        background-color: #047857 !important; 
        border: none !important;
    }
    div[data-testid="stAlert"]:has(svg[data-testid="stIconError"]) {
        background-color: #b91c1c !important; 
        border: none !important;
    }
    div[data-testid="stAlert"]:has(svg[data-testid="stIconWarning"]) {
        background-color: #b45309 !important; 
        border: none !important;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ==============================================================================
# HALAMAN UTAMA: ABSENSI KANTIN
# ==============================================================================
st.markdown("<h1 style='text-align: center; color: #0f172a; font-weight: 900; font-size: 3.8rem; text-shadow: 2px 2px 4px rgba(255,255,255,0.9); margin-bottom: 10px;'>📌 Absensi Kantin Eka Bekasi</h1>", unsafe_allow_html=True)

st.markdown("<p style='text-align: center; color: #1e293b; font-weight: 900; font-size: 2.4rem; text-shadow: 1px 2px 3px rgba(255,255,255,0.9); margin-bottom: 20px; letter-spacing: 2px;'>CONTOH PENULISAN NIK 00003950</p>", unsafe_allow_html=True)

st.markdown("<p style='text-align: center; color: #0f172a; font-weight: 800; font-size: 2.2rem; margin-bottom: 15px;'>Silakan Ketik NIK Anda (Lalu tekan Enter):</p>", unsafe_allow_html=True)

# Link Endpoint & Entry Google Form SERVER TEST
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLScnTi-b9vCrBSRMr-G7k3_4buevp02nJ9J6ybkatj5SGCKKfw/formResponse"
ENTRY_NIK = "entry.952185819"
ENTRY_NAMA = "entry.444514235"

def handle_nik_submit():
    input_val = st.session_state.nik_input_key.strip()
    if input_val:
        st.session_state.last_submitted_nik = input_val
    st.session_state.nik_input_key = ""

if "last_submitted_nik" not in st.session_state:
    st.session_state.last_submitted_nik = ""

st.text_input(
    label="nik_label_hidden",
    label_visibility="collapsed",
    max_chars=8, 
    placeholder="00000000",
    key="nik_input_key",
    on_change=handle_nik_submit
)

# Auto Focus Javascript
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

# Eksekusi Proses Absen dengan Validasi 8 Digit
if st.session_state.last_submitted_nik:
    input_nik = st.session_state.last_submitted_nik
    st.session_state.last_submitted_nik = ""
    
    # 1. Validasi hanya angka
    if not input_nik.isdigit():
        st.error("⚠️ NIK hanya boleh berisi angka!")
    # 2. Validasi wajib tepat 8 digit
    elif len(input_nik) != 8:
        st.error(f"❌ NIK harus berjumlah tepat 8 digit angka! (Anda mengetik {len(input_nik)} digit)")
    else:
        nik_clean = input_nik
        if is_already_absent_today(nik_clean):
            st.error(f"❌ NIK {nik_clean} SUDAH ABSEN HARI INI!")
        else:
            nama_karyawan = db_karyawan.get(nik_clean, "Nama Tidak Ditemukan")
            payload = {
                ENTRY_NIK: nik_clean,
                ENTRY_NAMA: nama_karyawan
            }
            try:
                response = requests.post(FORM_URL, data=payload)
                if response.status_code == 200:
                    if nama_karyawan != "Nama Tidak Ditemukan":
                        st.success(f"✅ Berhasil Absen: **{nama_karyawan.title()}** (NIK: {nik_clean})")
                    else:
                        st.warning(f"⚠️ Berhasil Absen NIK: **{nik_clean}** *(Nama tidak di database)*")
                else:
                    st.error(f"❌ Gagal mengirim data. Code: {response.status_code}")
            except Exception as e:
                st.error(f"❌ Terjadi kesalahan koneksi: {e}")

st.write("")

footer_html = '<div style="text-align: right; color: #0f172a; font-weight: 800; font-size: 1.3rem; text-shadow: 1px 1px 2px rgba(255,255,255,0.9); margin-top: 15px;">Created by IT Eka Bekasi</div>'
st.markdown(footer_html, unsafe_allow_html=True)

# ==============================================================================
# PANEL INFORMASI & DAFTAR KARYAWAN (KHUSUS ADMIN TEST)
# ==============================================================================
st.divider()

if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

if "login_error" not in st.session_state:
    st.session_state.login_error = False

def handle_login():
    pwd = st.session_state.pass_input_key
    if pwd == ADMIN_PASSWORD:
        st.session_state.admin_logged_in = True
        st.session_state.login_error = False
    else:
        st.session_state.admin_logged_in = False
        st.session_state.login_error = True
    st.session_state.pass_input_key = ""

with st.expander("🔒 Panel Login Admin (Klik di sini)"):
    if not st.session_state.admin_logged_in:
        st.subheader("🔑 Masukkan Password Admin")
        st.text_input(
            "Masukkan Password lalu tekan Enter", 
            type="password", 
            key="pass_input_key",
            on_change=handle_login
        )
        if st.session_state.login_error:
            st.error("❌ Password salah!")
    else:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"Total Karyawan Terdaftar di Google Sheet: **{len(db_karyawan)} Karyawan**")
        with col2:
            if st.button("🔒 Logout"):
                st.session_state.admin_logged_in = False
                st.session_state.login_error = False
                st.rerun()

        st.link_button("✏️ Edit / Update Data Karyawan (Google Spreadsheet)", KARYAWAN_SPREADSHEET_URL, use_container_width=True)
        st.write("")

        tab_daftar, tab_respon = st.tabs([
            "📋 Daftar Karyawan", 
            "📊 Data Absensi (Google Form Test)"
        ])

        with tab_daftar:
            if db_karyawan:
                df_karyawan = pd.DataFrame(list(db_karyawan.items()), columns=["NIK", "Nama Karyawan"])
                st.dataframe(df_karyawan, use_container_width=True)
                if st.button("🔄 Refresh Data Karyawan"):
                    st.cache_data.clear()
                    st.rerun()
            else:
                st.info("Belum ada data karyawan atau Google Sheet belum di-set Publik.")

        with tab_respon:
            st.write("### 📥 Tarik / Lihat Data Hasil Absensi")
            st.info("Klik tombol di bawah ini untuk membuka halaman Respon / Rekap Absensi Kantin di Google Forms Test.")
            st.link_button("🔗 Buka Google Form Responses", RESPONSES_URL, use_container_width=True)
