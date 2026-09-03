import requests
import streamlit as st

st.title("📌 Absensi Sederhana")

# GANTI LINK DI BAWAH SESUAI LINK GOOGLE FORM ANDA
# (Ganti '/viewform' di akhir link menjadi '/formResponse')
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSc.../formResponse"

# GANTI ENTRY ID SESUAI DENGAN ENTRY ID NIK ANDA
ENTRY_NIK = "entry.924986826"

nik = st.text_input("Masukkan NIK Anda:")

if st.button("Kirim Absen"):
    if nik:
        # Mengirim data NIK langsung ke Google Form (otomatis masuk ke Google Sheet)
        payload = {ENTRY_NIK: nik}
        response = requests.post(FORM_URL, data=payload)

        if response.status_code == 200:
            st.success(f"✅ Berhasil absen untuk NIK: {nik}")
        else:
            st.error("Gagal mengirim data. Periksa kembali Link Form Anda.")
    else:
        st.warning("Isi NIK terlebih dahulu!")
