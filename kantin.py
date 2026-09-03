import requests
import streamlit as st

st.title("📌 Absensi Kantin Eka Bekasi")

# Link Form yang sudah disesuaikan
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeHkJyHQClWw18bR2SLHBmpMWVuwYJpfERpBm--APFxsWGc1w/formResponse"

# GANTI ANGKA DI BAWAH SESUAI HASIL INSPECT (misal: "entry.123456789")
ENTRY_NIK = "entry.924986826"

nik = st.text_input("Masukkan NIK Anda:")

if st.button("Kirim Absen"):
    if nik:
        payload = {ENTRY_NIK: nik}
        try:
            response = requests.post(FORM_URL, data=payload)
            if response.status_code == 200:
                st.success(f"✅ Berhasil absen untuk NIK: {nik}")
            else:
                st.error("Gagal mengirim data. Periksa kembali Entry ID Anda.")
        except Exception as e:
            st.error(f"Terjadi kesalahan koneksi: {e}")
    else:
        st.warning("Isi NIK terlebih dahulu!")
