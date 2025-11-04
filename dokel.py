import streamlit as st
import pandas as pd
import os
from io import StringIO

st.set_page_config(page_title="Pencarian Komoditas Domestik & Ekspor", layout="wide")

st.title("🌿 Sistem Pencarian Komoditas Domestik & Ekspor")
st.write("Gunakan tab di bawah ini untuk melihat data **domestik keluar**, **ekspor**, dan **domestik masuk**.")

# === Lokasi file ===
file_domestik = "ujidokel.txt"   # Domestik keluar
file_ekspor = "bahanekspor.txt" # Ekspor
file_domas = "domas.txt"        # Domestik masuk

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
# 🏠 TAB 1 - DOMESTIK KELUAR
# ==========================================================
with tab1:
    st.subheader("📦 Pencarian Daerah Tujuan Berdasarkan Komoditas")
    st.write("""
    Masukkan atau pilih **komoditas** untuk melihat daftar **daerah tujuan**, **provinsi**, dan **pulau**
    tanpa duplikasi, beserta **frekuensi kemunculannya**.  
    Gunakan filter **Satpel** untuk membatasi data.
    """)

    if os.path.exists(file_domestik):
        try:
            df = pd.read_csv(file_domestik, sep="\t")
            df.columns = df.columns.str.strip()

            required_cols = ['Daerah Tujuan', 'Komoditas', 'Provinsi', 'Pulau', 'Satpel']
            if not all(col in df.columns for col in required_cols):
                st.error(f"❌ Kolom wajib tidak ditemukan. Pastikan ada: {', '.join(required_cols)}")
                st.stop()

            for c in required_cols:
                df[c] = df[c].astype(str).str.strip().str.upper()

            satpel_list = sorted(df['Satpel'].unique())
            satpel_input = st.selectbox("🏢 Pilih Satpel (opsional):", ["SEMUA"] + satpel_list)

            if satpel_input == "SEMUA":
                komoditas_list = sorted(df['Komoditas'].unique())
            else:
                komoditas_list = sorted(df[df['Satpel'] == satpel_input]['Komoditas'].unique())

            pilih_cara = st.radio("Pilih cara input komoditas:", ["Ketik manual", "Pilih dari daftar"])
            if pilih_cara == "Ketik manual":
                komoditas_input = st.text_input("📝 Tulis nama komoditas (contoh: BUAH DURIAN)").strip().upper()
            else:
                komoditas_input = st.selectbox("📋 Pilih komoditas:", komoditas_list)

            if komoditas_input:
                if satpel_input == "SEMUA":
                    df_filtered = df[df['Komoditas'].str.contains(komoditas_input, case=False, na=False)]
                else:
                    df_filtered = df[
                        (df['Komoditas'].str.contains(komoditas_input, case=False, na=False)) &
                        (df['Satpel'] == satpel_input)
                    ]

                if df_filtered.empty:
                    st.warning("⚠️ Tidak ada data yang cocok dengan filter tersebut.")
                else:
                    # Frekuensi
                    freq_tujuan = df_filtered['Daerah Tujuan'].value_counts().reset_index()
                    freq_tujuan.columns = ['Daerah Tujuan', 'Frekuensi']

                    freq_prov = df_filtered['Provinsi'].value_counts().reset_index()
                    freq_prov.columns = ['Provinsi', 'Frekuensi']

                    freq_pulau = df_filtered['Pulau'].value_counts().reset_index()
                    freq_pulau.columns = ['Pulau', 'Frekuensi']

                    st.subheader(f"📊 Hasil untuk Komoditas: **{komoditas_input}** | Satpel: **{satpel_input}**")

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.markdown("### 🏙️ Daerah Tujuan")
                        st.dataframe(freq_tujuan, use_container_width=True)
                    with col2:
                        st.markdown("### 🗺️ Provinsi")
                        st.dataframe(freq_prov, use_container_width=True)
                    with col3:
                        st.markdown("### 🌴 Pulau")
                        st.dataframe(freq_pulau, use_container_width=True)

                    # Tampilkan klasifikasi tambahan
                    st.markdown("### 🧾 Data Klasifikasi Komoditas")
                    tambahan_cols = ['Klasifikasi', 'Nama Tercetak', 'Kode HS']
                    for col in tambahan_cols:
                        if col not in df_filtered.columns:
                            df_filtered[col] = "-"

                    kolom_tampil = ['Komoditas'] + tambahan_cols
                    st.dataframe(df_filtered[kolom_tampil].drop_duplicates().reset_index(drop=True),
                                 use_container_width=True)

        except Exception as e:
            st.error(f"⚠️ Terjadi kesalahan saat membaca file domestik: {e}")
    else:
        st.warning(f"📁 File '{file_domestik}' belum ditemukan.")

# ==========================================================
# 🚢 TAB 2 - EKSPOR
# ==========================================================
with tab2:
    st.subheader("🚢 Pencarian Komoditas Ekspor")

    if not os.path.exists(file_ekspor):
        st.warning(f"📁 File '{file_ekspor}' tidak ditemukan.")
    else:
        df, enc = robust_read_tabfile(file_ekspor)
        if df is None:
            st.error("❌ Gagal membaca file ekspor.")
        else:
            df.columns = df.columns.str.strip()
            tujuan_col = 'Tujuan' if 'Tujuan' in df.columns else 'Daerah Tujuan'
            cols_needed = ['Komoditas', 'Satpel', tujuan_col, 'Daerah Asal', 'Pemohon']

            if not all(c in df.columns for c in cols_needed):
                st.error(f"Kolom wajib tidak lengkap di file ekspor. Harus ada: {', '.join(cols_needed)}")
                st.stop()

            for c in cols_needed:
                df[c] = df[c].astype(str).str.strip().str.upper()

            col1, col2 = st.columns(2)
            with col1:
                satpel_list = sorted(df['Satpel'].dropna().unique())
                satpel_input = st.selectbox("🏢 Pilih Satpel (Ekspor):", ["SEMUA"] + satpel_list)
            with col2:
                if satpel_input != "SEMUA":
                    komoditas_list = sorted(df[df['Satpel'] == satpel_input]['Komoditas'].dropna().unique())
                else:
                    komoditas_list = sorted(df['Komoditas'].dropna().unique())
                komoditas_input = st.selectbox("🌾 Pilih Komoditas (Ekspor):", ["SEMUA"] + komoditas_list)

            df_filtered = df.copy()
            if satpel_input != "SEMUA":
                df_filtered = df_filtered[df_filtered['Satpel'] == satpel_input]
            if komoditas_input != "SEMUA":
                df_filtered = df_filtered[df_filtered['Komoditas'] == komoditas_input]

            if df_filtered.empty:
                st.warning("⚠️ Tidak ada data ekspor yang cocok.")
            else:
                st.success(f"✅ Ditemukan {len(df_filtered)} data ekspor")

                freq_tujuan = df_filtered[tujuan_col].value_counts().reset_index()
                freq_tujuan.columns = [tujuan_col, 'Frekuensi']

                freq_asal = df_filtered['Daerah Asal'].value_counts().reset_index()
                freq_asal.columns = ['Daerah Asal', 'Frekuensi']

                freq_pemohon = df_filtered['Pemohon'].value_counts().reset_index()
                freq_pemohon.columns = ['Pemohon', 'Frekuensi']

                freq_satpel = df_filtered['Satpel'].value_counts().reset_index()
                freq_satpel.columns = ['Satpel', 'Frekuensi']

                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.markdown(f"### 🌍 {tujuan_col}")
                    st.dataframe(freq_tujuan, use_container_width=True)
                with col2:
                    st.markdown("### 🏠 Daerah Asal")
                    st.dataframe(freq_asal, use_container_width=True)
                with col3:
                    st.markdown("### 👤 Pemohon")
                    st.dataframe(freq_pemohon, use_container_width=True)
                with col4:
                    st.markdown("### 🏢 Satpel")
                    st.dataframe(freq_satpel, use_container_width=True)

# ==========================================================
# 📥 TAB 3 - DOMESTIK MASUK
# ==========================================================
with tab3:
    st.subheader("📥 Pencarian Komoditas Domestik Masuk")

    if not os.path.exists(file_domas):
        st.warning(f"📁 File '{file_domas}' tidak ditemukan.")
    else:
        df, enc = robust_read_tabfile(file_domas)
        if df is None:
            st.error("❌ Gagal membaca file domas.txt.")
        else:
            df.columns = df.columns.str.strip()
            cols_needed = ['Komoditas', 'Satpel', 'Daerah Asal', 'Daerah Tujuan', 'Pemohon']

            if not all(c in df.columns for c in cols_needed):
                st.error(f"Kolom wajib tidak lengkap di file domas. Harus ada: {', '.join(cols_needed)}")
                st.stop()

            for c in cols_needed:
                df[c] = df[c].astype(str).str.strip().str.upper()

            col1, col2 = st.columns(2)
            with col1:
                satpel_list = sorted(df['Satpel'].dropna().unique())
                satpel_input = st.selectbox("🏢 Pilih Satpel (Masuk):", ["SEMUA"] + satpel_list)
            with col2:
                if satpel_input != "SEMUA":
                    komoditas_list = sorted(df[df['Satpel'] == satpel_input]['Komoditas'].dropna().unique())
                else:
                    komoditas_list = sorted(df['Komoditas'].dropna().unique())
                komoditas_input = st.selectbox("🌾 Pilih Komoditas (Masuk):", ["SEMUA"] + komoditas_list)

            df_filtered = df.copy()
            if satpel_input != "SEMUA":
                df_filtered = df_filtered[df_filtered['Satpel'] == satpel_input]
            if komoditas_input != "SEMUA":
                df_filtered = df_filtered[df_filtered['Komoditas'] == komoditas_input]

            if df_filtered.empty:
                st.warning("⚠️ Tidak ada data domestik masuk yang cocok.")
            else:
                st.success(f"✅ Ditemukan {len(df_filtered)} data domestik masuk")

                freq_asal = df_filtered['Daerah Asal'].value_counts().reset_index()
                freq_asal.columns = ['Daerah Asal', 'Frekuensi']

                freq_tujuan = df_filtered['Daerah Tujuan'].value_counts().reset_index()
                freq_tujuan.columns = ['Daerah Tujuan', 'Frekuensi']

                freq_pemohon = df_filtered['Pemohon'].value_counts().reset_index()
                freq_pemohon.columns = ['Pemohon', 'Frekuensi']

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown("### 🏠 Daerah Asal")
                    st.dataframe(freq_asal, use_container_width=True)
                with col2:
                    st.markdown("### 🎯 Daerah Tujuan")
                    st.dataframe(freq_tujuan, use_container_width=True)
                with col3:
                    st.markdown("### 👤 Pemohon")
                    st.dataframe(freq_pemohon, use_container_width=True)
