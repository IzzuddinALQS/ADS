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
    df = pd.read_csv('global_ai_jobs.csv')
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("❌ File 'tech_jobs_dataset.csv' tidak ditemukan. Silakan letakkan filenya di folder yang sama dengan app.py.")
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

# ── 4. SIDEBAR FILTER ───────────────────────────────────────
st.sidebar.header("🎯 Filter Dashboard")

all_years = sorted(df['year'].unique())
selected_years = st.sidebar.multiselect("Pilih Tahun Data:", all_years, default=all_years)

all_modes = df['work_mode'].unique()
selected_modes = st.sidebar.multiselect("Pilih Mode Kerja:", all_modes, default=all_modes)

df_filtered = df[(df['year'].isin(selected_years)) & (df['work_mode'].isin(selected_modes))]

if df_filtered.empty:
    st.warning("⚠️ Tidak ada data yang cocok dengan kombinasi filter Anda.")
    st.stop()

# ── 5. HERO SECTION & KPI METRICS ───────────────────────────
st.title("💼 Tech Jobs Market Intelligence Dashboard")
st.markdown("Analisis tren gaji, pola kerja, dan distribusi peran industri teknologi secara dinamis.")
st.divider()

col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)
with col_kpi1:
    st.metric(label="Total Lowongan Teranalisis", value=f"{len(df_filtered):,}")
with col_kpi2:
    st.metric(label="Rata-Rata Gaji", value=f"${df_filtered['salary_usd'].mean():,.0f}")
with col_kpi3:
    st.metric(label="Median Gaji", value=f"${df_filtered['salary_usd'].median():,.0f}")
with col_kpi4:
    remote_pct = (df_filtered['work_mode'] == 'Remote').mean() * 100
    st.metric(label="Porsi Kerja Remote", value=f"{remote_pct:.1f}%")

st.markdown("---")

# ── 6. STRUKTUR UTAMA DASHBOARD (TABS) ──────────────────────
tabs = st.tabs([
    "🎯 Full Dashboard", 
    "1. Ringkasan Pasar & Tren", 
    "2. Analisis Gaji", 
    "3. Distribusi Geografis"
])

# ── TAB 0: ALL-IN-ONE DASHBOARD ──────────────────────────
with tabs[0]:
    st.header("All 10 Charts as One Dashboard")
    
    exp_order_present = [e for e in ['Entry', 'Mid', 'Senior', 'Lead'] if e in df_filtered['experience_level'].unique()]
    size_order = [s for s in ['Small', 'Medium', 'Large'] if s in df_filtered['company_size'].unique()]

    fig = plt.figure(figsize=(20, 36))
    fig.suptitle('Tech Jobs Dataset — Visual Summary', fontsize=18, fontweight='bold', y=1.005)

    # 1. Salary histogram
    ax1 = fig.add_subplot(5, 2, 1)
    ax1.hist(df_filtered['salary_usd'], bins=50, color='steelblue', edgecolor='white', linewidth=0.3)
    ax1.axvline(df_filtered['salary_usd'].mean(), color='tomato', linestyle='--', linewidth=1.2, label='Mean')
    ax1.axvline(df_filtered['salary_usd'].median(), color='darkorange', linestyle='--', linewidth=1.2, label='Median')
    ax1.set_title('Salary Distribution')
    ax1.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x/1000:.0f}k'))
    ax1.legend(fontsize=8)

    # 2. Salary by experience
    ax2 = fig.add_subplot(5, 2, 2)
    sns.boxplot(data=df_filtered, x='experience_level', y='salary_usd', order=exp_order_present, palette='Blues', width=0.5, flierprops=dict(marker='o', markersize=1, alpha=0.2), ax=ax2)
    ax2.set_title('Salary by Experience Level')
    ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x/1000:.0f}k'))

    # 3. Salary by work mode
    ax3 = fig.add_subplot(5, 2, 3)
    sns.boxplot(data=df_filtered, x='work_mode', y='salary_usd', palette='Set2', width=0.45, flierprops=dict(marker='o', markersize=1, alpha=0.2), ax=ax3)
    ax3.set_title('Salary by Work Mode')
    ax3.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x/1000:.0f}k'))

    # 4. Top 5 countries
    ax4 = fig.add_subplot(5, 2, 4)
    top_c = df_filtered['country'].value_counts().head(5)
    ax4.bar(top_c.index, top_c.values, color=sns.color_palette('muted', len(top_c)), edgecolor='white', linewidth=0.3)
    ax4.set_title('Top 5 Countries by Job Count')
    ax4.set_xticks(range(len(top_c.index)))
    ax4.set_xticklabels(top_c.index, rotation=45, ha='right', fontsize=7)

    # 5. Avg salary by country
    ax5 = fig.add_subplot(5, 2, 5)
    avg_sc = df_filtered.groupby('country')['salary_usd'].mean().sort_values(ascending=False).head(10)
    ax5.barh(avg_sc.index[::-1], avg_sc.values[::-1], color=sns.color_palette('Blues_r', len(avg_sc)), edgecolor='white', linewidth=0.3)
    ax5.set_title('Top 10 Countries by Avg Salary')
    ax5.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x/1000:.0f}k'))

    # 6. Job role distribution
    ax6 = fig.add_subplot(5, 2, 6)
    rc = df_filtered['job_role'].value_counts().sort_values()
    ax6.barh(rc.index, rc.values, color=sns.color_palette('viridis', len(rc)), edgecolor='white', linewidth=0.3)
    ax6.set_title('Job Role Distribution')

    # 7. Salary by company size
    ax7 = fig.add_subplot(5, 2, 7)
    sns.boxplot(data=df_filtered, x='company_size', y='salary_usd', order=size_order, palette='Purples', width=0.45, flierprops=dict(marker='o', markersize=1, alpha=0.2), ax=ax7)
    ax7.set_title('Salary by Company Size')
    ax7.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x/1000:.0f}k'))

    # 8. Hiring trends
    ax8 = fig.add_subplot(5, 2, 8)
    yearly_df = df_filtered.groupby('year').agg(job_count=('id','count'), avg_salary=('salary_usd','mean')).reset_index()
    ax8.plot(yearly_df['year'], yearly_df['job_count'], color='steelblue', marker='o', linewidth=1.8, markersize=5)
    ax8b = ax8.twinx()
    ax8b.plot(yearly_df['year'], yearly_df['avg_salary'], color='tomato', marker='s', linewidth=1.8, markersize=5, linestyle='--')
    ax8.set_title('Job Count & Avg Salary by Year')
    ax8.set_xticks(yearly_df['year'])
    ax8b.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x/1000:.0f}k'))

    # 9. Work mode donut
    ax9 = fig.add_subplot(5, 2, 9)
    wmc = df_filtered['work_mode'].value_counts()
    wedges, texts, autotexts = ax9.pie(wmc.values, labels=wmc.index, autopct='%1.1f%%', colors=sns.color_palette('Set2', len(wmc)), wedgeprops=dict(width=0.45, edgecolor='white', linewidth=1.5), startangle=90, pctdistance=0.78, labeldistance=1.12)
    for t in texts: t.set_fontsize(8)
    for at in autotexts: at.set_fontsize(7.5); at.set_color('white'); at.set_fontweight('bold')
    ax9.set_title('Work Mode Split')

    # 10. Correlation heatmap (KECILKAN ANGKA DI SINI)
    ax10 = fig.add_subplot(5, 2, 10)
    numeric_df = df_filtered.select_dtypes(include='number').drop(columns=['id','year'], errors='ignore')
    sns.heatmap(
        numeric_df.corr(), annot=True, fmt='.2f', cmap='coolwarm', center=0,
        linewidths=0.4, linecolor='white', annot_kws={'size': 5.5}, square=True, # Ukuran font diset ke 5.5
        cbar_kws={'shrink': 0.6}, ax=ax10
    )
    ax10.set_title('Correlation Heatmap', pad=12)
    ax10.set_xticklabels(ax10.get_xticklabels(), rotation=45, ha='right', fontsize=7)
    ax10.set_yticklabels(ax10.get_yticklabels(), rotation=0, fontsize=7)

    plt.tight_layout(h_pad=3.5, w_pad=2.5)
    st.pyplot(fig)

# ── TAB 1: RINGKASAN PASAR & TREN ───────────────────────────
with tabs[1]:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Distribusi Peran Pekerjaan (Job Roles)")
        role_counts = df_filtered['job_role'].value_counts().sort_values(ascending=True)
        fig, ax = plt.subplots()
        colors = sns.color_palette('viridis', len(role_counts))
        ax.barh(role_counts.index, role_counts.values, color=colors, edgecolor='white', linewidth=0.4)
        st.pyplot(fig)
        
    with col2:
        st.subheader("Tren Rekrutmen & Gaji dari Tahun ke Tahun")
        yearly_data = df_filtered.groupby('year').agg(job_count=('id', 'count'), avg_salary=('salary_usd', 'mean')).reset_index()
        fig, ax1 = plt.subplots()
        ax1.plot(yearly_data['year'], yearly_data['job_count'], color='steelblue', marker='o', linewidth=2)
        ax1.set_xticks(yearly_data['year'])
        ax2 = ax1.twinx()
        ax2.plot(yearly_data['year'], yearly_data['avg_salary'], color='tomato', marker='s', linestyle='--', linewidth=2)
        ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x/1000:.0f}k'))
        plt.tight_layout()
        st.pyplot(fig)

    st.markdown("---")
    
    col3, col4 = st.columns([1, 2])
    with col3:
        st.subheader("Komparasi Mode Kerja")
        work_mode_counts = df_filtered['work_mode'].value_counts()
        fig, ax = plt.subplots(figsize=(5, 5))
        ax.pie(work_mode_counts.values, labels=work_mode_counts.index, autopct='%1.1f%%', startangle=90, colors=sns.color_palette('Set2', len(work_mode_counts)), wedgeprops=dict(width=0.45, edgecolor='white', linewidth=2))
        st.pyplot(fig)
        
    with col4:
        st.subheader("Matriks Korelasi Fitur Numerik (KECILKAN ANGKA DI SINI)")
        numeric_df = df_filtered.select_dtypes(include='number').drop(columns=['id', 'year'], errors='ignore')
        if not numeric_df.empty and numeric_df.shape[1] > 1:
            fig, ax = plt.subplots(figsize=(6, 4.5)) # Atur ukuran gambar agar pas
            sns.heatmap(
                numeric_df.corr(), annot=True, fmt='.2f', cmap='coolwarm', center=0, 
                annot_kws={'size': 6.5}, linewidths=0.3, square=True, ax=ax # Ukuran font 6.5 + jarak garis putih 0.3
            )
            st.pyplot(fig)
        else:
            st.info("Korelasi memerlukan lebih dari satu kolom numerik.")

# ── TAB 2: ANALISIS GAJI ────────────────────────────────────
with tabs[2]:
    st.subheader("Distribusi Gaji Keseluruhan")
    fig, ax = plt.subplots(figsize=(12, 3.5))
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
        exp_order_present = [e for e in ['Entry', 'Mid', 'Senior', 'Lead'] if e in df_filtered['experience_level'].unique()]
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
with tabs[3]:
    col_geo1, col_geo2 = st.columns(2)
    with col_geo1:
        st.subheader("Top 5 Negara dengan Lowongan Terbanyak")
        top_countries = df_filtered['country'].value_counts().head(5)
        fig, ax = plt.subplots()
        ax.bar(top_countries.index, top_countries.values, color=sns.color_palette('muted', len(top_countries)))
        st.pyplot(fig)
        
    with col_geo2:
        st.subheader("Top 10 Negara dengan Rata-Rata Gaji Tertinggi (USD)")
        avg_salary_country = df_filtered.groupby('country')['salary_usd'].mean().sort_values(ascending=False).head(10)
        fig, ax = plt.subplots()
        ax.barh(avg_salary_country.index[::-1], avg_salary_country.values[::-1], color=sns.color_palette('Blues_r', 10))
        ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x/1000:.0f}k'))
        st.pyplot(fig)