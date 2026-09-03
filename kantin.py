import requests
import streamlit as st

st.title("📌 Absensi Kantin Eka Bekasi")

FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeHkJyHQClWw18bR2SLHBmpMWVuwYJpfERpBm--APFxsWGc1w/formResponse"
ENTRY_NIK = "entry.924986826"

# Form untuk mendukun tombol Enter & otomatis reset isi kolom setelah dikirim
with st.form(key="form_absen", clear_on_submit=True):
    nik = st.text_input("Masukkan NIK Anda (lalu tekan Enter):")
    submit_button = st.form_submit_button(label="Kirim Absen")

# Proses pengiriman data
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

# Penulisan st.markdown yang ringkas dan aman dari SyntaxError
footer_html = '<div style="text-align: right; color: gray; font-size: 0.8rem;">Created by IT Eka Bekasi</div>'
st.markdown(footer_html, unsafe_allow_html=True)
