import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import streamlit as st

# ── 1. PAGE CONFIGURATION ───────────────────────────────────
st.set_page_config(
    page_title="Tech Jobs Executive Dashboard",
    page_icon="💼",
    layout="wide"
)

# ── 2. CACHED DATA LOADING ──────────────────────────────────
@st.cache_data
def load_data():
    # Menggunakan file lokal agar loading super cepat dan aman
    df = pd.read_csv('global_ai_jobs.csv')
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("❌ File 'tech_jobs_dataset.csv' tidak ditemukan di folder yang sama dengan app.py. Silakan unduh dan letakkan filenya terlebih dahulu.")
    st.stop()

# ── 3. GLOBAL PLOT STYLE ────────────────────────────────────
sns.set_theme(style='whitegrid', palette='muted')
plt.rcParams.update({
    'figure.figsize'     : (10, 4),
    'figure.dpi'         : 100,
    'axes.titlesize'     : 12,
    'axes.titlepad'      : 10,
    'axes.labelsize'     : 10,
    'xtick.labelsize'    : 8,
    'ytick.labelsize'    : 8,
})

# ── 4. SIDEBAR FILTER (INTERAKTIF) ──────────────────────────
st.sidebar.header("🎯 Filter Dashboard")

# Filter Tahun
all_years = sorted(df['year'].unique())
selected_years = st.sidebar.multiselect("Pilih Tahun Data:", all_years, default=all_years)

# Filter Work Mode
all_modes = df['work_mode'].unique()
selected_modes = st.sidebar.multiselect("Pilih Mode Kerja:", all_modes, default=all_modes)

# Proses Filtering Data secara Real-Time
df_filtered = df[(df['year'].isin(selected_years)) & (df['work_mode'].isin(selected_modes))]

# Validasi jika data hasil filter kosong
if df_filtered.empty:
    st.warning("⚠️ Tidak ada data yang cocok dengan kombinasi filter Anda. Silakan ubah filter di sidebar.")
    st.stop()

# ── 5. HERO SECTION & KPI METRICS ───────────────────────────
st.title("💼 Tech Jobs Market Intelligence Dashboard")
st.markdown("Analisis tren gaji, pola kerja, dan distribusi peran industri teknologi secara dinamis.")
st.divider()

# Baris Kartu Informasi Utama (KPIs)
col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)

with col_kpi1:
    st.metric(label="Total Lowongan Teranalisis", value=f"{len(df_filtered):,}")
with col_kpi2:
    avg_salary_filtered = df_filtered['salary_usd'].mean()
    st.metric(label="Rata-Rata Gaji", value=f"${avg_salary_filtered:,.0f}")
with col_kpi3:
    med_salary_filtered = df_filtered['salary_usd'].median()
    st.metric(label="Median Gaji", value=f"${med_salary_filtered:,.0f}")
with col_kpi4:
    remote_pct = (df_filtered['work_mode'] == 'Remote').mean() * 100
    st.metric(label="Porsi Kerja Remote", value=f"{remote_pct:.1f}%")

st.markdown("---")

# ── 6. STRUKTUR UTAMA DASHBOARD (TABS) ──────────────────────
tab_summary, tab_salary, tab_geography = st.tabs([
    "📈 Ringkasan Pasar & Tren", 
    "💰 Analisis Gaji & Faktor Penentu", 
    "🌍 Distribusi Geografis"
])

# ── TAB 1: RINGKASAN PASAR & TREN ───────────────────────────
with tab_summary:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Distribusi Peran Pekerjaan (Job Roles)")
        role_counts = df_filtered['job_role'].value_counts().sort_values(ascending=True)
        fig, ax = plt.subplots()
        colors = sns.color_palette('viridis', len(role_counts))
        ax.barh(role_counts.index, role_counts.values, color=colors, edgecolor='white', linewidth=0.4)
        ax.set_xlabel('Jumlah Lowongan')
        st.pyplot(fig)
        
    with col2:
        st.subheader("Tren Rekrutmen & Gaji dari Tahun ke Tahun")
        yearly_data = df_filtered.groupby('year').agg(job_count=('id', 'count'), avg_salary=('salary_usd', 'mean')).reset_index()
        fig, ax1 = plt.subplots()
        
        ax1.plot(yearly_data['year'], yearly_data['job_count'], color='steelblue', marker='o', linewidth=2, label='Jumlah Lowongan')
        ax1.set_xlabel('Tahun')
        ax1.set_ylabel('Jumlah Lowongan', color='steelblue')
        ax1.tick_params(axis='y', labelcolor='steelblue')
        ax1.set_xticks(yearly_data['year'])
        
        ax2 = ax1.twinx()
        ax2.plot(yearly_data['year'], yearly_data['avg_salary'], color='tomato', marker='s', linestyle='--', linewidth=2, label='Rerata Gaji')
        ax2.set_ylabel('Rerata Gaji (USD)', color='tomato')
        ax2.tick_params(axis='y', labelcolor='tomato')
        ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x/1000:.0f}k'))
        
        plt.tight_layout()
        st.pyplot(fig)

    st.markdown("---")
    
    col3, col4 = st.columns([1, 2])
    with col3:
        st.subheader("Komparasi Mode Kerja")
        work_mode_counts = df_filtered['work_mode'].value_counts()
        fig, ax = plt.subplots(figsize=(5, 5))
        ax.pie(work_mode_counts.values, labels=work_mode_counts.index, autopct='%1.1f%%', 
               startangle=90, colors=sns.color_palette('Set2', len(work_mode_counts)),
               wedgeprops=dict(width=0.45, edgecolor='white', linewidth=2))
        st.pyplot(fig)
        
    with col4:
        st.subheader("Matriks Korelasi Fitur Numerik")
        numeric_df = df_filtered.select_dtypes(include='number').drop(columns=['id', 'year'], errors='ignore')
        if not numeric_df.empty and numeric_df.shape[1] > 1:
            fig, ax = plt.subplots()
            sns.heatmap(numeric_df.corr(), annot=True, fmt='.2f', cmap='coolwarm', center=0, ax=ax)
            st.pyplot(fig)
        else:
            st.info("Korelasi memerlukan lebih dari satu kolom numerik.")

# ── TAB 2: ANALISIS GAJI ────────────────────────────────────
with tab_salary:
    st.subheader("Distribusi Gaji Keseluruhan")
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.hist(df_filtered['salary_usd'], bins=40, color='steelblue', edgecolor='white', linewidth=0.4)
    ax.axvline(df_filtered['salary_usd'].mean(), color='tomato', linestyle='--', label=f"Mean: ${df_filtered['salary_usd'].mean():,.0f}")
    ax.axvline(df_filtered['salary_usd'].median(), color='darkorange', linestyle='--', label=f"Median: ${df_filtered['salary_usd'].median():,.0f}")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x/1000:.0f}k'))
    ax.legend()
    st.pyplot(fig)
    
    st.markdown("---")
    
    col_sal1, col_sal2, col_sal3 = st.columns(3)
    
    with col_sal1:
        st.subheader("Gaji berdasarkan Pengalaman")
        EXP_ORDER = ['Entry', 'Mid', 'Senior', 'Lead']
        exp_order_present = [e for e in EXP_ORDER if e in df_filtered['experience_level'].unique()]
        fig, ax = plt.subplots()
        sns.boxplot(data=df_filtered, x='experience_level', y='salary_usd', order=exp_order_present, palette='Blues', ax=ax)
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x/1000:.0f}k'))
        st.pyplot(fig)
        
    with col_sal2:
        st.subheader("Gaji berdasarkan Mode Kerja")
        fig, ax = plt.subplots()
        sns.boxplot(data=df_filtered, x='work_mode', y='salary_usd', palette='Set2', ax=ax)
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x/1000:.0f}k'))
        st.pyplot(fig)
        
    with col_sal3:
        st.subheader("Gaji berdasarkan Ukuran Perusahaan")
        size_order = [s for s in ['Small', 'Medium', 'Large'] if s in df_filtered['company_size'].unique()]
        fig, ax = plt.subplots()
        sns.boxplot(data=df_filtered, x='company_size', y='salary_usd', order=size_order, palette='Purples', ax=ax)
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x/1000:.0f}k'))
        st.pyplot(fig)

# ── TAB 3: DISTRIBUSI GEOGRAFIS ─────────────────────────────
with tab_geography:
    col_geo1, col_geo2 = st.columns(2)
    
    with col_geo1:
        st.subheader("Top 5 Negara dengan Lowongan Terbanyak")
        top_countries = df_filtered['country'].value_counts().head(5)
        fig, ax = plt.subplots()
        bars = ax.bar(top_countries.index, top_countries.values, color=sns.color_palette('muted', len(top_countries)))
        ax.set_ylabel('Jumlah Lowongan')
        st.pyplot(fig)
        
    with col_geo2:
        st.subheader("Top 10 Negara dengan Rata-Rata Gaji Tertinggi (USD)")
        avg_salary_country = df_filtered.groupby('country')['salary_usd'].mean().sort_values(ascending=False).head(10)
        fig, ax = plt.subplots()
        ax.barh(avg_salary_country.index[::-1], avg_salary_country.values[::-1], color=sns.color_palette('Blues_r', 10))
        ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x/1000:.0f}k'))
        st.pyplot(fig)