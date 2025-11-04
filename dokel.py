import streamlit as st
import pandas as pd
import os
from io import StringIO

st.set_page_config(page_title="Pencarian Komoditas Domestik & Ekspor", layout="wide")

st.title("🌿 Sistem Pencarian Komoditas Domestik & Ekspor")
st.write("Gunakan tab di bawah ini untuk melihat data **domestik keluar**, **ekspor**, dan **domestik masuk**.")

# === Lokasi file ===
file_domestik = "ujidokel.txt"
file_ekspor = "bahanekspor.txt"
file_domas = "domas.txt"

# === Fungsi membaca file robust ===
def robust_read_tabfile(path):
    encodings = ['utf-8', 'utf-8-sig', 'cp1252', 'latin1', 'iso-8859-1']
    for enc in encodings:
        try:
            df = pd.read_csv(path, sep="\t", dtype=str, encoding=enc, engine='python')
            return df, enc
        except:
            continue
    return None, None

# === Tab utama ===
tab1, tab2, tab3 = st.tabs(["🏠 Domestik Keluar", "🚢 Ekspor", "📥 Domestik Masuk"])

# ==========================================================
# 🏠 TAB 1 - DOMESTIK KELUAR (sudah lengkap)
# ==========================================================
with tab1:
    st.subheader("📦 Pencarian Daerah Tujuan Berdasarkan Komoditas")
    if os.path.exists(file_domestik):
        try:
            df = pd.read_csv(file_domestik, sep="\t")
            df.columns = df.columns.str.strip()
            required_cols = ['Daerah Tujuan', 'Komoditas', 'Provinsi', 'Pulau', 'Satpel']
            if not all(col in df.columns for col in required_cols):
                st.error(f"❌ Kolom wajib tidak ditemukan: {', '.join(required_cols)}")
                st.stop()

            for c in required_cols:
                df[c] = df[c].astype(str).str.strip().str.upper()

            satpel_list = sorted(df['Satpel'].unique())
            satpel_input = st.selectbox("🏢 Pilih Satpel:", ["SEMUA"] + satpel_list)

            if satpel_input == "SEMUA":
                komoditas_list = sorted(df['Komoditas'].unique())
            else:
                komoditas_list = sorted(df[df['Satpel'] == satpel_input]['Komoditas'].unique())

            pilih_cara = st.radio("Cara Input Komoditas:", ["Ketik manual", "Pilih dari daftar"])
            if pilih_cara == "Ketik manual":
                komoditas_input = st.text_input("📝 Tulis komoditas").strip().upper()
            else:
                komoditas_input = st.selectbox("📋 Pilih komoditas:", komoditas_list)

            if komoditas_input:
                if satpel_input == "SEMUA":
                    df_filtered = df[df['Komoditas'].str.contains(komoditas_input, na=False)]
                else:
                    df_filtered = df[(df['Komoditas'].str.contains(komoditas_input, na=False)) & (df['Satpel'] == satpel_input)]

                if df_filtered.empty:
                    st.warning("⚠️ Tidak ada data ditemukan.")
                else:
                    # Frekuensi dan klasifikasi
                    freq_tujuan = df_filtered['Daerah Tujuan'].value_counts().reset_index()
                    freq_tujuan.columns = ['Daerah Tujuan', 'Frekuensi']

                    st.markdown("### 🧾 Data Klasifikasi Komoditas")
                    tambahan_cols = ['Klasifikasi', 'Nama Tercetak', 'Kode HS']
                    for col in tambahan_cols:
                        if col not in df_filtered.columns:
                            df_filtered[col] = "-"

                    kolom_tampil = ['Komoditas'] + tambahan_cols
                    st.dataframe(df_filtered[kolom_tampil].drop_duplicates())

        except Exception as e:
            st.error(f"⚠️ Error membaca file domestik keluar: {e}")

# ==========================================================
# 🚢 TAB 2 - EKSPOR (DITAMBAHKAN KLASIFIKASI)
# ==========================================================
with tab2:
    st.subheader("🚢 Pencarian Komoditas Ekspor")
    if not os.path.exists(file_ekspor):
        st.warning(f"📁 File '{file_ekspor}' tidak ditemukan.")
    else:
        df, _ = robust_read_tabfile(file_ekspor)
        cols_needed = ['Komoditas', 'Satpel', 'Tujuan', 'Daerah Asal', 'Pemohon']
        for col in cols_needed:
            df[col] = df[col].astype(str).str.upper()

        satpel = st.selectbox("🏢 Pilih Satpel:", ["SEMUA"] + sorted(df['Satpel'].unique()))
        kom_list = sorted(df[df['Satpel'] == satpel]['Komoditas'].unique()) if satpel != "SEMUA" else sorted(df['Komoditas'].unique())
        kom_input = st.selectbox("🌾 Pilih Komoditas:", ["SEMUA"] + kom_list)

        df_filtered = df.copy()
        if satpel != "SEMUA":
            df_filtered = df_filtered[df_filtered['Satpel'] == satpel]
        if kom_input != "SEMUA":
            df_filtered = df_filtered[df_filtered['Komoditas'] == kom_input]

        if not df_filtered.empty:
            st.success(f"✅ {len(df_filtered)} data ditemukan")

            st.markdown("### 🧾 Data Klasifikasi Komoditas")
            for col in ['Klasifikasi', 'Nama Tercetak', 'Kode HS']:
                if col not in df_filtered.columns:
                    df_filtered[col] = "-"
            st.dataframe(df_filtered[['Komoditas', 'Klasifikasi', 'Nama Tercetak', 'Kode HS']].drop_duplicates())

# ==========================================================
# 📥 TAB 3 - DOMESTIK MASUK (DITAMBAHKAN KLASIFIKASI)
# ==========================================================
with tab3:
    st.subheader("📥 Pencarian Komoditas Domestik Masuk")
    if not os.path.exists(file_domas):
        st.warning("📁 File domas.txt tidak ditemukan.")
    else:
        df, _ = robust_read_tabfile(file_domas)
        for col in ['Komoditas', 'Satpel', 'Daerah Asal', 'Daerah Tujuan', 'Pemohon']:
            df[col] = df[col].astype(str).str.upper()

        satpel = st.selectbox("🏢 Pilih Satpel (Masuk):", ["SEMUA"] + sorted(df['Satpel'].unique()))
        kom_list = sorted(df[df['Satpel'] == satpel]['Komoditas'].unique()) if satpel != "SEMUA" else sorted(df['Komoditas'].unique())
        kom_input = st.selectbox("🌾 Pilih Komoditas (Masuk):", ["SEMUA"] + kom_list)

        df_filtered = df.copy()
        if satpel != "SEMUA":
            df_filtered = df_filtered[df_filtered['Satpel'] == satpel]
        if kom_input != "SEMUA":
            df_filtered = df_filtered[df_filtered['Komoditas'] == kom_input]

        if not df_filtered.empty:
            st.success(f"✅ {len(df_filtered)} data ditemukan")

            st.markdown("### 🧾 Data Klasifikasi Komoditas")
            for col in ['Klasifikasi', 'Nama Tercetak', 'Kode HS']:
                if col not in df_filtered.columns:
                    df_filtered[col] = "-"
            st.dataframe(df_filtered[['Komoditas', 'Klasifikasi', 'Nama Tercetak', 'Kode HS']].drop_duplicates())
