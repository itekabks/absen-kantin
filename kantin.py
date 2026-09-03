import datetime
import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.title("📌 Absensi Sederhana")

# Hubungkan ke Google Sheet
conn = st.connection("gsheets", type=GSheetsConnection)

# Input NIK
nik = st.text_input("Masukkan NIK Anda:")

if st.button("Kirim Absen"):
    if nik:
        # Ambil data lama & tambah data baru
        data_lama = conn.read()
        waktu = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Gabungkan data baru
        data_baru = [{"Waktu": waktu, "NIK": nik}]
        df_update = data_lama._append(data_baru, ignore_index=True)

        # Simpan kembali ke Google Sheet
        conn.update(data=df_update)
        st.success(f"✅ Berhasil absen untuk NIK: {nik}")
    else:
        st.warning("Isi NIK terlebih dahulu!")
