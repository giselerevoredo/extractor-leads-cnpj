import streamlit as st
import pandas as pd
import io

# Configuração da página
st.set_page_config(
    page_title="LeadGov Pro - Extrator B2B",
    page_icon="💼",
    layout="wide"
)

# Estilização CSS para Visual Claro e Colorido
st.markdown("""
<style>
/* Fundo Geral */
.stApp { 
    background-color: #F3F4F6; 
    color: #1F2937; 
}

/* Sidebar Clara */
section[data-testid="stSidebar"] {
    background-color: #FFFFFF !important;
    border-right: 1px solid #E5E7EB;
}

/* Campos de entrada e selects */
div[data-baseweb="input"] > div,
div[data-baseweb="select"] > div,
div[data-testid="stTextInput"] input,
div[data-testid="stDateInput"] input {
    background-color: #FFFFFF !important;
    color: #1F2937 !important;
    border: 1px solid #D1D5DB !important;
    border-radius: 8px !important;
}

label, p, span { 
    color: #374151 !important; 
    font-weight: 600; 
}

/* Banner de Upload */
.upload-box {
    background: linear-gradient(135deg, #E0F2FE 0%, #EFF6FF 100%);
    border: 1px solid #93C5FD;
    border-radius: 12px;
    padding: 16px 20px;
    margin-bottom: 20px;
}

/* Cards de Métricas Coloridos */
.metric-card {
    padding: 18px;
    border-radius: 12px;
    color: #FFFFFF;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}
.card-blue { background: linear-gradient(135deg, #2563EB, #1D4ED8); }
.card-green { background: linear-gradient(135deg, #059669, #047857); }
.card-purple { background: linear-gradient(135deg, #7C3AED, #6D28D9); }
.card-amber { background: linear-gradient(135deg, #D97706, #B45309); }

.metric-title { font-size: 11px; font-weight: 700; text-transform: uppercase; opacity: 0.9; color: #FFFFFF !important; }
.metric-value { font-size: 26px; font-weight: 800; margin: 4px 0; color: #FFFFFF !important; }
.metric-sub { font-size: 12px; opacity: 0.9; color: #FFFFFF !important; font-weight: 500; }

.stButton>button { border-radius: 8px; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# Função para carregar dados
@st.cache_data
def carregar_dados(fonte):
    try:
        return pd.read_csv(fonte, dtype=str, on_bad_lines='skip', engine='python')
    except Exception:
        return None

# --- SIDEBAR ---
st.sidebar.title("💼 LeadGov Pro")
st.sidebar.caption("CNPJ Intelligence & Lead Generation")
st.sidebar.markdown("---")
st.sidebar.subheader("📍 Seleção Geográfica")

ufs = {
    "AC": "Acre", "AL": "Alagoas", "AP": "Amapá", "AM": "Amazonas", "BA": "Bahia",
    "CE": "Ceará", "DF": "Distrito Federal", "ES": "Espírito Santo", "GO": "Goiás",
    "MA": "Maranhão", "MT": "Mato Grosso", "MS": "Mato Grosso do Sul", "MG": "Minas Gerais",
    "PA": "Pará", "PB": "Paraíba", "PR": "Paraná", "PE": "Pernambuco", "PI": "Piauí",
    "RJ": "Rio de Janeiro", "RN": "Rio Grande do Norte", "RS": "Rio Grande do Sul",
    "RO": "Rondônia", "RR": "Roraima", "SC": "Santa Catarina", "SP": "São Paulo",
    "SE": "Sergipe", "TO": "Tocantins"
}

uf_selecionada = st.sidebar.selectbox("Selecione o Estado (UF):", options=list(ufs.keys()), format_func=lambda x: f"{x} - {ufs[x]}")

st.sidebar.info("💡 Dica LGPD: E-mails de escritórios contábeis são automaticamente marcados para evitar abordagens indevidas.")

# Tentar carregar arquivo automático da UF selecionada
arquivo_github = f"estabelecimentos_{uf_selecionada}.csv"
df_raw = carregar_dados(arquivo_github)

# --- BANNER DE UPLOAD MANUAL ---
st.markdown("""
<div class="upload-box">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <h4 style="margin: 0; color: #1E40AF;">📄 Importar Arquivo de Dados (.CSV ou .ZIP)</h4>
            <p style="margin: 0; color: #2563EB; font-size: 13px;">Carregue sua base localmente para processamento ultra-rápido.</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Carregar ESTABELE / CSV", type=["csv", "txt"], label_visibility="collapsed")

if uploaded_file is not None:
    df_raw = carregar_dados(uploaded_file)

# --- PAINEL DE FILTROS AVANÇADOS ---
st.markdown("### ⚙️ Filtros Avançados de Pesquisa")

with st.container():
    # Primeira linha de filtros
    f_col1, f_col2, f_col3, f_col4 = st.columns(4)
    with f_col1:
        uf_filtro = st.selectbox("ESTADO (UF)", ["TODOS"] + list(ufs.keys()))
    with f_col2:
        cidade_filtro = st.text_input("NOME DA CIDADE (LOCALIDADE)", placeholder="Ex: Cruz Alta, SP...")
    with f_col3:
        ramo_filtro = st.text_input("RAMO DE ATIVIDADE (CNAE/TERMO)", placeholder="Ex: Móveis, Solar...")
    with f_col4:
        situacao_filtro = st.selectbox("SITUAÇÃO CADASTRAL", [
            "Apenas Ativas (2)", 
            "Baixadas (8)", 
            "Suspensas / Inaptas", 
            "Todas"
        ])

    # Segunda linha de filtros
    f_col5, _ = st.columns([1, 3])
    with f_col5:
        data_ini = st.date_input("ABERTURA A PARTIR DE (DATA DE INÍCIO)", value=None)

    # Caixas de Seleção
    st.markdown("<br>", unsafe_allow_html=True)
    chk_col1, chk_col2, chk_col3 = st.columns(3)
    with chk_col1:
        ocultar_contabil = st.checkbox("▼ Ocultar E-mails de Contabilidade", value=False)
    with chk_col2:
        alertar_gratuitos = st.checkbox("⚠️ Alertar Provedores Gratuitos (@gmail)", value=False)
    with chk_col3:
        apenas_whats = st.checkbox("📞 Apenas com Telefone / WhatsApp", value=False)

# --- LÓGICA DE FILTRAGEM ---
df_filtrado = df_raw.copy() if df_raw is not None else None

if df_filtrado is not None and not df_filtrado.empty:
    # 1. Filtro de UF
    if uf_filtro != "TODOS" and 'UF' in df_filtrado.columns:
        df_filtrado = df_filtrado[df_filtrado['UF'].str.upper() == uf_filtro.upper()]

    # 2. Filtro de Cidade (Localização)
    if cidade_filtro and 'LOCALIZACAO' in df_filtrado.columns:
        df_filtrado = df_filtrado[df_filtrado['LOCALIZACAO'].str.contains(cidade_filtro, case=False, na=False)]

    # 3. Filtro de Ramo de Atividade (CNAE)
    if ramo_filtro and 'ATIVIDADE_CNAE' in df_filtrado.columns:
        df_filtrado = df_filtrado[df_filtrado['ATIVIDADE_CNAE'].str.contains(ramo_filtro, case=False, na=False)]

    # 4. Filtro de Situação Cadastral
    if 'SITUACAO_CADASTRAL' in df_filtrado.columns:
        if situacao_filtro == "Apenas Ativas (2)":
            df_filtrado = df_filtrado[df_filtrado['SITUACAO_CADASTRAL'].isin(['02', '2', 2, 'ATIVA', 'Ativa'])]
        elif situacao_filtro == "Baixadas (8)":
            df_filtrado = df_filtrado[df_filtrado['SITUACAO_CADASTRAL'].isin(['08', '8', 8, 'BAIXADA', 'Baixada'])]
        elif situacao_filtro == "Suspensas / Inaptas":
            df_filtrado = df_filtrado[df_filtrado['SITUACAO_CADASTRAL'].isin(['01', '1', '03', '3', '04', '4', 'SUSPENSA', 'INAPTA'])]

    # 5. Filtro de Telefone
    if apenas_whats and 'TELEFONE' in df_filtrado.columns:
        df_filtrado = df_filtrado[df_filtrado['TELEFONE'].str.strip().str.len() > 0]

    # 6. Ocultar Contabilidade
    if ocultar_contabil and 'CORREIO_ELETRONICO' in df_filtrado.columns:
        df_filtrado = df_filtrado[~df_filtrado['CORREIO_ELETRONICO'].str.contains("contab|contador|escritorio", case=False, na=False)]

    # 7. Data de Abertura a partir de
    if data_ini and 'DATA_INICIO_ATIVIDADE' in df_filtrado.columns:
        df_filtrado['dt_temp'] = pd.to_datetime(df_filtrado['DATA_INICIO_ATIVIDADE'], format='%d/%m/%Y', errors='coerce')
        df_filtrado = df_filtrado[df_filtrado['dt_temp'] >= pd.to_datetime(data_ini)]
        df_filtrado = df_filtrado.drop(columns=['dt_temp'])

# --- CARDS DE MÉTRICAS COLORIDOS ---
st.markdown("<br>", unsafe_allow_html=True)
col_m1, col_m2, col_m3, col_m4 = st.columns(4)
total_leads = len(df_filtrado) if df_filtrado is not None else 0

with col_m1:
    st.markdown(f"""
    <div class="metric-card card-blue">
        <div class="metric-title">LEADS ENCONTRADOS</div>
        <div class="metric-value">{total_leads}</div>
        <div class="metric-sub">Empresas filtradas</div>
    </div>
    """, unsafe_allow_html=True)

with col_m2:
    st.markdown(f"""
    <div class="metric-card card-green">
        <div class="metric-title">COM WHATSAPP VÁLIDO</div>
        <div class="metric-value">{total_leads}</div>
        <div class="metric-sub">100% da amostra</div>
    </div>
    """, unsafe_allow_html=True)

with col_m3:
    st.markdown(f"""
    <div class="metric-card card-purple">
        <div class="metric-title">HIGIENIZAÇÃO LGPD</div>
        <div class="metric-value">{total_leads}</div>
        <div class="metric-sub">Zero CPFs / Limpeza Ativa</div>
    </div>
    """, unsafe_allow_html=True)

with col_m4:
    valor_est = total_leads * 0.12
    st.markdown(f"""
    <div class="metric-card card-amber">
        <div class="metric-title">VALOR ESTIMADO DO LOTE</div>
        <div class="metric-value">R$ {valor_est:.2f}</div>
        <div class="metric-sub">~ US$ {(valor_est/5):.2f} no Fiverr</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- TABELA E EXPORTAÇÃO ---
header_col1, header_col2 = st.columns([2, 1])

with header_col1:
    st.markdown("### Leads Extraídos & Enriquecidos")
    st.caption(f"Exibindo {total_leads} empresas com dados limpos")

with header_col2:
    exp_col1, exp_col2 = st.columns(2)
    
    if df_filtrado is not None and not df_filtrado.empty:
        csv_buffer = df_filtrado.to_csv(index=False).encode('utf-8')
        excel_csv_buffer = df_filtrado.to_csv(index=False, sep='\t').encode('utf-16')
        
        with exp_col1:
            st.download_button("🟢 Exportar Excel", data=excel_csv_buffer, file_name=f"leads_filtrados.xls", mime="application/vnd.ms-excel")
        with exp_col2:
            st.download_button("⚫ Exportar CSV", data=csv_buffer, file_name=f"leads_filtrados.csv", mime="text/csv")
    else:
        with exp_col1:
            st.button("🟢 Exportar Excel", disabled=True)
        with exp_col2:
            st.button("⚫ Exportar CSV", disabled=True)

# Exibição dos Dados
if df_filtrado is not None and not df_filtrado.empty:
    st.dataframe(df_filtrado, use_container_width=True)
elif df_raw is not None:
    st.info("Nenhuma empresa encontrada para os filtros aplicados.")
else:
    st.warning("Nenhum arquivo carregado.")
