from datetime import datetime
import base64
import os
import time
import pandas as pd
import requests
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Absensi Kantin Eka Bekasi", 
    page_icon="📌",
    layout="centered"
)

# --- CONFIGURATION VIA STREAMLIT SECRETS & CONSTANTS ---
GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN", "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")
REPO_NAME = st.secrets.get("REPO_NAME", "itekabks/absen-kantin")
FILE_PATH = "karyawan.csv"
ADMIN_PASSWORD = st.secrets.get("ADMIN_PASSWORD", "admin123")
RESPONSES_URL = "https://docs.google.com/forms/d/1kKLUDGAQb5UfedMVCedWBExvuOl2bsa3649CIrjEccw/edit?pli=1#responses"

# ⚠️ MASUKKAN ID GOOGLE SHEET REKAP FORM ANDA DI SINI ⚠️
SPREADSHEET_ID = "MASUKKAN_ID_SPREADSHEET_GOOGLE_FORM_DI_SINI"

# --- FUNGSI CEK ABSEN DUPLIKAT HARI INI (REAL-TIME NO-CACHE) ---
def is_already_absent_today(nik):
    """Mengecek apakah NIK sudah pernah absen pada tanggal hari ini dari Google Sheet"""
    if SPREADSHEET_ID == "MASUKKAN_ID_SPREADSHEET_GOOGLE_FORM_DI_SINI":
        return False
        
    # Parameter &nocache= digunakan untuk memaksa fetching data paling segar
    csv_url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&nocache={int(time.time())}"
    
    try:
        df_responses = pd.read_csv(csv_url)
        
        if df_responses.empty:
            return False
            
        # Format tanggal & penyesuaian string NIK
        df_responses.iloc[:, 0] = pd.to_datetime(df_responses.iloc[:, 0], errors='coerce')
        today_date = datetime.now().date()
        
        nik_input = str(nik).strip()
        nik_in_sheet = df_responses.iloc[:, 1].astype(str).str.strip().str.replace(".0", "", regex=False)
        
        already_exists = df_responses[
            (nik_in_sheet == nik_input) & 
            (df_responses.iloc[:, 0].dt.date == today_date)
        ]
        
        return not already_exists.empty
    except Exception as e:
        return False

# --- FUNGSI BACA DATABASE KARYAWAN FROM CSV ---
@st.cache_data(ttl=10)
def load_data_karyawan():
    file_path = "karyawan.csv"
    if os.path.exists(file_path):
        df = pd.read_csv(file_path, sep=';', dtype={'nik': str})
        df['nik'] = df['nik'].astype(str).str.strip()
        df['nama'] = df['nama'].astype(str).str.strip()
        return dict(zip(df['nik'], df['nama']))
    return {}

def update_karyawan_to_github(dict_karyawan, commit_message):
    token = GITHUB_TOKEN.strip().replace('"', '').replace("'", "")
    repo = REPO_NAME.strip().replace('"', '').replace("'", "")
    
    if not token or not repo:
        return False, "Token GitHub atau REPO_NAME belum dikonfigurasi di Secrets!"

    if token.startswith("github_pat_") or token.startswith("ghp_"):
        auth_header = f"token {token}"
    else:
        auth_header = f"Bearer {token}"

    headers = {
        "Authorization": auth_header,
        "Accept": "application/vnd.github.v3+json"
    }
    url = f"https://api.github.com/repos/{repo}/contents/{FILE_PATH}"

    df_new = pd.DataFrame(list(dict_karyawan.items()), columns=['nik', 'nama'])
    csv_content = df_new.to_csv(index=False, sep=';')
    content_encoded = base64.b64encode(csv_content.encode('utf-8')).decode('utf-8')

    res = requests.get(url, headers=headers)
    
    if res.status_code == 401:
        return False, "Gagal mengakses GitHub: Bad credentials"

    payload = {
        "message": commit_message,
        "content": content_encoded
    }

    if res.status_code == 200:
        payload["sha"] = res.json()['sha']
    elif res.status_code != 404:
        return False, f"Gagal mengakses GitHub: {res.json().get('message', '')}"

    put_res = requests.put(url, headers=headers, json=payload)
    if put_res.status_code in [200, 201]:
        st.cache_data.clear()
        return True, "Berhasil memperbarui data di GitHub!"
    else:
        return False, f"Gagal update GitHub ({put_res.status_code}): {put_res.json().get('message', '')}"

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
        background: rgba(255, 255, 255, 0.92) !important;
        backdrop-filter: blur(8px);
        border-radius: 20px;
        padding: 35px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.15);
        border: 1px solid rgba(255,255,255,0.4);
    }

    /* FIX TEKS LABEL INPUT DARI SEMUA FORM */
    [data-testid="stForm"] label, 
    [data-testid="stForm"] label p {
        color: #0f172a !important;
        font-weight: 800 !important;
        font-size: 1.25rem !important;
    }

    /* 🔍 MEMBESARKAN KOTAK INPUT & TEKS ANGKA NIK */
    div[data-testid="stTextInput"] input {
        font-size: 2.2rem !important;      /* Angka yang diketik berukuran SANGAT BESAR */
        font-weight: 900 !important;     /* Angka tebal/bold */
        height: 70px !important;         /* Kotak input lebih tinggi */
        text-align: center !important;   /* Posisi angka tepat di tengah */
        letter-spacing: 4px !important;  /* Spasi antar angka lebih renggang */
        color: #0f172a !important;       /* Warna teks sangat kontras/gelap */
        border-radius: 12px !important;
        border: 2px solid #3b82f6 !important;
    }

    /* MEMBESARKAN TOMBOL ABSEN */
    .stButton button {
        border-radius: 12px;
        background: linear-gradient(90deg, #3b82f6 0%, #1d4ed8 100%);
        color: white;
        border: none;
        font-weight: bold;
        height: 60px !important;          /* Tombol lebih tinggi */
        font-size: 1.3rem !important;     /* Teks tombol diperbesar */
    }

    /* STYLING NOTIFIKASI UMUM (SUKSES, ERROR, WARNING) */
    div[data-testid="stAlert"] {
        border-radius: 16px !important;
        padding: 20px !important;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.4) !important;
    }

    div[data-testid="stAlert"] [data-baseweb="notification"] {
        background-color: transparent !important;
    }

    div[data-testid="stAlert"] * {
        color: #ffffff !important;
        font-size: 1.5rem !important;    /* Teks notifikasi diperbesar agar terlihat dari jauh */
        font-weight: 800 !important;
        line-height: 1.5 !important;
    }

    div[data-testid="stAlert"] svg {
        width: 36px !important;
        height: 36px !important;
    }

    /* 1. STYLING NOTIFIKASI SUKSES (st.success) -> Hijau Tua Solid */
    div[data-testid="stAlert"]:has(div[class*="st-emotion-cache"]:contains("✅")),
    div[data-testid="stAlert"][aria-label*="success"],
    div[data-testid="stAlert"]:has(svg[data-testid="stIconSuccess"]) {
        background-color: #064e3b !important;
        border: 2px solid #10b981 !important;
    }
    div[data-testid="stAlert"]:has(svg[data-testid="stIconSuccess"]) svg {
        fill: #34d399 !important;
    }

    /* 2. STYLING NOTIFIKASI GAGAL (st.error) -> Merah Tua Solid */
    div[data-testid="stAlert"]:has(div[class*="st-emotion-cache"]:contains("⚠️")),
    div[data-testid="stAlert"]:has(div[class*="st-emotion-cache"]:contains("❌")),
    div[data-testid="stAlert"][aria-label*="error"],
    div[data-testid="stAlert"]:has(svg[data-testid="stIconError"]) {
        background-color: #7f1d1d !important;
        border: 2px solid #f87171 !important;
    }
    div[data-testid="stAlert"]:has(svg[data-testid="stIconError"]) svg {
        fill: #fca5a5 !important;
    }

    /* 3. STYLING NOTIFIKASI PERINGATAN (st.warning) -> Cokelat/Kuning Tua Solid */
    div[data-testid="stAlert"][aria-label*="warning"],
    div[data-testid="stAlert"]:has(svg[data-testid="stIconWarning"]) {
        background-color: #78350f !important;
        border: 2px solid #fbbf24 !important;
    }
    div[data-testid="stAlert"]:has(svg[data-testid="stIconWarning"]) svg {
        fill: #fde047 !important;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ==============================================================================
# HALAMAN UTAMA: ABSENSI KANTIN
# ==============================================================================
st.markdown("<h1 style='text-align: center; color: #1e293b; text-shadow: 1px 1px 2px rgba(255,255,255,0.8);'>📌 Absensi Kantin Eka Bekasi</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #475569; font-weight: 600; font-size: 1rem; text-shadow: 1px 1px 1px rgba(255,255,255,0.8); margin-bottom: 25px;'>Untuk penulisan NIK menggunakan 8 digit angka</p>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #475569; font-weight: 800; font-size: 2rem; text-shadow: 1px 1px 1px rgba(255,255,255,0.8); margin-bottom: 25px;'>Contoh 00003950</p>", unsafe_allow_html=True)

FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeHkJyHQClWw18bR2SLHBmpMWVuwYJpfERpBm--APFxsWGc1w/formResponse"
ENTRY_NIK = "entry.924986826"
ENTRY_NAMA = "entry.827733304"

with st.form(key="form_absen_test", clear_on_submit=True):
    nik = st.text_input("Masukkan NIK Anda (lalu tekan Enter):", max_chars=8)
    submit_button = st.form_submit_button(label="ABSEN", use_container_width=True)

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

if submit_button:
    nik_clean = nik.strip()
    if not nik_clean:
        st.warning("⚠️ NIK tidak boleh kosong!")
    elif not nik_clean.isdigit():
        st.error("⚠️ NIK hanya boleh berisi angka! (Tidak boleh ada huruf atau simbol)")
    elif len(nik_clean) != 8:
        st.error(f"⚠️ NIK harus terdiri dari 8 karakter/digit! (Anda memasukkan {len(nik_clean)} digit)")
    else:
        # CEK VALIDASI ABSEN DOUBLE DI HARI YANG SAMA
        if is_already_absent_today(nik_clean):
            st.error(f"❌ NIK {nik_clean} SUDAH ABSEN HARI INI! (Tidak dapat absen 2 kali)")
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
                        st.warning(f"⚠️ Berhasil Absen NIK: **{nik_clean}** *(Nama tidak ditemukan di database)*")
                else:
                    st.error(f"❌ Gagal mengirim data. Response Code: {response.status_code}")
            except Exception as e:
                st.error(f"❌ Terjadi kesalahan koneksi: {e}")

st.write("")
st.write("")

footer_html = '<div style="text-align: right; color: #334155; font-weight: 600; font-size: 0.85rem; text-shadow: 1px 1px 1px rgba(255,255,255,0.8);">Created by IT Eka Bekasi</div>'
st.markdown(footer_html, unsafe_allow_html=True)

# ==============================================================================
# MENU ADMIN
# ==============================================================================
st.divider()

with st.expander("⚙️ Panel Login Admin (Klik di sini)"):
    if "admin_logged_in" not in st.session_state:
        st.session_state.admin_logged_in = False

    if not st.session_state.admin_logged_in:
        with st.form("form_login_admin"):
            password_input = st.text_input("Masukkan Password Admin:", type="password")
            login_btn = st.form_submit_button("Login Admin")

            if login_btn:
                if password_input == ADMIN_PASSWORD:
                    st.session_state.admin_logged_in = True
                    st.success("Login Berhasil!")
                    st.rerun()
                else:
                    st.error("Password salah!")
    else:
        st.write("### 🔑 Portal Admin Karyawan")
        if st.button("🔒 Logout Admin"):
            st.session_state.admin_logged_in = False
            st.rerun()

        tab_tambah, tab_daftar, tab_respon = st.tabs([
            "➕ Tambah Karyawan Baru", 
            "📋 Daftar Karyawan", 
            "📊 Data Absensi (Google Form)"
        ])

        with tab_tambah:
            with st.form("form_tambah_karyawan", clear_on_submit=True):
                new_nik = st.text_input("NIK Karyawan Baru (contoh: 00003950):", max_chars=8).strip()
                new_nama = st.text_input("Nama Lengkap Karyawan:").strip()
                submit_add = st.form_submit_button("Simpan Karyawan ke GitHub")

            if submit_add:
                if not new_nik or not new_nama:
                    st.warning("Mohon isi NIK dan Nama secara lengkap!")
                elif not new_nik.isdigit():
                    st.error("⚠️ NIK Karyawan Baru hanya boleh berupa angka!")
                elif len(new_nik) != 8:
                    st.error(f"⚠️ NIK Karyawan Baru harus tepat 8 digit! (Anda memasukkan {len(new_nik)} digit)")
                else:
                    if new_nik in db_karyawan:
                        st.warning(f"⚠️ NIK {new_nik} sudah terdaftar atas nama {db_karyawan[new_nik]}!")
                    else:
                        db_karyawan[new_nik] = new_nama
                        
                        with st.spinner("Menyimpan ke GitHub..."):
                            success, msg = update_karyawan_to_github(
                                db_karyawan, 
                                f"Tambah karyawan baru: {new_nama} ({new_nik})"
                            )
                            if success:
                                st.success(f"✅ Berhasil menambahkan {new_nama} ({new_nik}) ke GitHub!")
                            else:
                                st.error(msg)

        with tab_daftar:
            st.write(f"Total Karyawan Terdaftar: **{len(db_karyawan)} Karyawan**")
            if db_karyawan:
                df_karyawan = pd.DataFrame(list(db_karyawan.items()), columns=["NIK", "Nama Karyawan"])
                st.dataframe(df_karyawan, use_container_width=True)
            else:
                st.info("Belum ada data karyawan.")

        with tab_respon:
            st.write("### 📥 Tarik / Lihat Data Hasil Absensi")
            st.info("Klik tombol di bawah ini untuk membuka halaman Respon / Rekap Absensi Kantin langsung dari Google Forms.")
            st.link_button("🔗 Buka Google Form Responses", RESPONSES_URL, use_container_width=True)
