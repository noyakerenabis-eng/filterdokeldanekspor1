import streamlit as st
import pandas as pd
import os
from io import StringIO

st.set_page_config(page_title="Pencarian Komoditas Domestik & Ekspor", layout="wide")

st.title("🌿 Sistem Pencarian Komoditas Domestik & Ekspor")
st.write("Gunakan tab di bawah ini untuk melihat data **domestik keluar**, **ekspor**, **domestik masuk**, dan **impor**.")

# === Lokasi file ===
file_domestik = "ujidokel.txt"   # Domestik keluar
file_ekspor = "bahanekspor.txt" # Ekspor
file_domas = "domas.txt"        # Domestik masuk
file_impor = "impor.txt"        # Impor (baru ditambahkan)

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
tab1, tab2, tab3, tab4 = st.tabs(["🏠 Domestik Keluar", "🚢 Ekspor", "📥 Domestik Masuk", "📦 Impor"])

# ==========================================================
# 🏠 TAB 1 - DOMESTIK KELUAR
# (kode kamu tetap – tidak diubah)
# ==========================================================
# ... (kode TAB 1 tetap seperti yang kamu kirim)

# ==========================================================
# 🚢 TAB 2 - EKSPOR
# (kode kamu tetap – tidak diubah)
# ==========================================================
# ... (kode TAB 2 tetap seperti yang kamu kirim)

# ==========================================================
# 📥 TAB 3 - DOMESTIK MASUK
# (kode kamu tetap – tidak diubah)
# ==========================================================
# ... (kode TAB 3 tetap seperti yang kamu kirim)

# ==========================================================
# 📦 TAB 4 - IMPOR (BARU)
# ==========================================================
with tab4:
    st.subheader("📦 Pencarian Komoditas Impor")

    if not os.path.exists(file_impor):
        st.warning(f"📁 File '{file_impor}' tidak ditemukan.")
    else:
        df, enc = robust_read_tabfile(file_impor)
        if df is None:
            st.error("❌ Gagal membaca file impor.txt.")
        else:
            df.columns = df.columns.str.strip()

            # Kolom wajib impor
            cols_needed = ['Komoditas', 'Satpel', 'Negara Asal', 'Pelabuhan Masuk', 'Pemohon']
            if not all(c in df.columns for c in cols_needed):
                st.error(f"Kolom wajib tidak lengkap di file impor. Harus ada: {', '.join(cols_needed)}")
                st.stop()

            # Bersihkan
            for c in cols_needed:
                df[c] = df[c].astype(str).str.strip().str.upper()

            # Filter
            col1, col2 = st.columns(2)
            with col1:
                satpel_list = sorted(df['Satpel'].dropna().unique())
                satpel_input = st.selectbox("🏢 Pilih Satpel (Impor):", ["SEMUA"] + satpel_list)
            with col2:
                if satpel_input != "SEMUA":
                    komoditas_list = sorted(df[df['Satpel'] == satpel_input]['Komoditas'].dropna().unique())
                else:
                    komoditas_list = sorted(df['Komoditas'].dropna().unique())
                komoditas_input = st.selectbox("🌾 Pilih Komoditas (Impor):", ["SEMUA"] + komoditas_list)

            df_filtered = df.copy()
            if satpel_input != "SEMUA":
                df_filtered = df_filtered[df_filtered['Satpel'] == satpel_input]
            if komoditas_input != "SEMUA":
                df_filtered = df_filtered[df_filtered['Komoditas'] == komoditas_input]

            if df_filtered.empty:
                st.warning("⚠️ Tidak ada data impor yang cocok.")
            else:
                st.success(f"✅ Ditemukan {len(df_filtered)} data impor")

                freq_asal = df_filtered['Negara Asal'].value_counts().reset_index()
                freq_asal.columns = ['Negara Asal', 'Frekuensi']

                freq_pelabuhan = df_filtered['Pelabuhan Masuk'].value_counts().reset_index()
                freq_pelabuhan.columns = ['Pelabuhan Masuk', 'Frekuensi']

                freq_pemohon = df_filtered['Pemohon'].value_counts().reset_index()
                freq_pemohon.columns = ['Pemohon', 'Frekuensi']

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown("### 🌍 Negara Asal")
                    st.dataframe(freq_asal, use_container_width=True)
                with col2:
                    st.markdown("### ⚓ Pelabuhan Masuk")
                    st.dataframe(freq_pelabuhan, use_container_width=True)
                with col3:
                    st.markdown("### 👤 Pemohon")
                    st.dataframe(freq_pemohon, use_container_width=True)
