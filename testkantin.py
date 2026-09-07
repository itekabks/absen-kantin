import base64
import os
import pandas as pd
import requests
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Absensi Kantin Eka Bekasi", 
    page_icon="📌",
    layout="centered"
)

# --- CONFIGURATION VIA STREAMLIT SECRETS ---
GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN", "")
REPO_NAME = st.secrets.get("REPO_NAME", "")
FILE_PATH = "karyawan.csv"
ADMIN_PASSWORD = st.secrets.get("ADMIN_PASSWORD", "admin123")

# --- FUNGSI BACA DATABASE KARYAWAN FROM CSV (MODE TEST) ---
@st.cache_data(ttl=10)
def load_data_karyawan():
    file_path = "karyawan.csv"
    if os.path.exists(file_path):
        df = pd.read_csv(file_path, dtype={'nik': str})
        df['nik'] = df['nik'].astype(str).str.strip()
        df['nama'] = df['nama'].astype(str).str.strip()
        return dict(zip(df['nik'], df['nama']))
    return {}

def update_karyawan_to_github(dict_karyawan, commit_message):
    """Fungsi untuk update & commit file karyawan.csv langsung ke GitHub"""
    if not GITHUB_TOKEN or not REPO_NAME:
        return False, "Token GitHub atau REPO_NAME belum dikonfigurasi di Secrets!"

    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    url = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PATH}"

    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        return False, f"Gagal mengakses GitHub: {res.json().get('message', '')}"
    
    sha = res.json()['sha']

    df_new = pd.DataFrame(list(dict_karyawan.items()), columns=['nik', 'nama'])
    csv_content = df_new.to_csv(index=False)

    content_encoded = base64.b64encode(csv_content.encode('utf-8')).decode('utf-8')

    payload = {
        "message": commit_message,
        "content": content_encoded,
        "sha": sha
    }

    put_res = requests.put(url, headers=headers, json=payload)
    if put_res.status_code == 200:
        st.cache_data.clear()
        return True, "Berhasil memperbarui data di GitHub!"
    else:
        return False, f"Gagal update GitHub: {put_res.json().get('message', '')}"

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

    /* Styling Tombol Kirim Mode Test */
    .stButton button {
        border-radius: 10px;
        background: linear-gradient(90deg, #3b82f6 0%, #1d4ed8 100%);
        color: white;
        border: none;
        font-weight: bold;
    }

    /* FIX NOTIFIKASI SUKSES (st.success) */
    [data-testid="stAlertContainer"] [data-baseweb="notification"] {
        background-color: #064e3b !important;
        border: 2px solid #10b981 !important;
        border-radius: 14px !important;
        padding: 16px !important;
        box-shadow: 0 8px 20px rgba(0,0,0,0.3) !important;
    }

    [data-testid="stAlertContainer"] * {
        color: #ffffff !important;
        font-size: 1.3rem !important;
        font-weight: 700 !important;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ==============================================================================
# HALAMAN UTAMA: ABSENSI KANTIN
# ==============================================================================
st.markdown("<h1 style='text-align: center; color: #1e293b; text-shadow: 1px 1px 2px rgba(255,255,255,0.8);'>📌 Absensi Kantin Eka Bekasi</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #475569; font-weight: 600; font-size: 1rem; text-shadow: 1px 1px 1px rgba(255,255,255,0.8); margin-bottom: 25px;'>Untuk penulisan NIK menggunakan 000NIK</p>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #475569; font-weight: 800; font-size: 1rem; text-shadow: 1px 1px 1px rgba(255,255,255,0.8); margin-bottom: 25px;'>Contoh 00003950</p>", unsafe_allow_html=True)

FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLScnTi-b9vCrBSRMr-G7k3_4buevp02nJ9J6ybkatj5SGCKKfw/formResponse"
ENTRY_NIK = "entry.952185819"
ENTRY_NAMA = "entry.444514235"

with st.form(key="form_absen_test", clear_on_submit=True):
    nik = st.text_input("Masukkan NIK Anda (lalu tekan Enter):")
    submit_button = st.form_submit_button(label="Kirim Absen", use_container_width=True)

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
    if nik_clean:
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
            st.error(f"Terjadi kesalahan koneksi: {e}")
    else:
        st.warning("NIK tidak boleh kosong!")

st.write("")
st.write("")

footer_html = '<div style="text-align: right; color: #334155; font-weight: 600; font-size: 0.85rem; text-shadow: 1px 1px 1px rgba(255,255,255,0.8);">Created by IT Eka Bekasi</div>'
st.markdown(footer_html, unsafe_allow_html=True)

# ==============================================================================
# MENU ADMIN DI BAGIAN BOLA KANAN / BAWAH
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

        tab_tambah, tab_daftar = st.tabs(["➕ Tambah Karyawan Baru", "📋 Daftar Karyawan"])

        with tab_tambah:
            with st.form("form_tambah_karyawan", clear_on_submit=True):
                new_nik = st.text_input("NIK Karyawan Baru (contoh: 00003950):").strip()
                new_nama = st.text_input("Nama Lengkap Karyawan:").strip()
                submit_add = st.form_submit_button("Simpan Karyawan ke GitHub")

            if submit_add:
                if new_nik and new_nama:
                    if new_nik in db_karyawan:
                        st.warning(f"⚠️ NIK **{new_nik}** sudah terdaftar atas nama **{db_karyawan[new_nik]}**!")
                    else:
                        db_karyawan[new_nik] = new_nama
                        
                        with st.spinner("Menyimpan ke GitHub..."):
                            success, msg = update_karyawan_to_github(
                                db_karyawan, 
                                f"Tambah karyawan baru: {new_nama} ({new_nik})"
                            )
                            if success:
                                st.success(f"✅ Berhasil menambahkan **{new_nama}** ({new_nik}) ke GitHub!")
                            else:
                                st.error(msg)
                else:
                    st.warning("Mohon isi NIK dan Nama secara lengkap!")

        with tab_daftar:
            st.write(f"Total Karyawan Terdaftar: **{len(db_karyawan)} Karyawan**")
            if db_karyawan:
                df_karyawan = pd.DataFrame(list(db_karyawan.items()), columns=["NIK", "Nama Karyawan"])
                st.dataframe(df_karyawan, use_container_width=True)
            else:
                st.info("Belum ada data karyawan.")
