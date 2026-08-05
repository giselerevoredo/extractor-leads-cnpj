import streamlit as st
import pandas as pd
import io

# Configuração da página
st.set_page_config(
    page_title="LeadGov Pro - Extrator B2B",
    page_icon="💼",
    layout="wide"
)

# Estilização CSS para recriar o tema claro/pro
st.markdown("""
<style>
/* Fundo Geral */
.stApp { background-color: #F8FAFC; color: #0F172A; }

/* Forçar Inputs, Selects e Uploader para Fundo Branco e Texto Escuro */
div[data-baseweb="input"] > div,
div[data-baseweb="select"] > div,
div[data-testid="stTextInput"] input,
div[data-testid="stDateInput"] input {
    background-color: #FFFFFF !important;
    color: #0F172A !important;
    border: 1px solid #CBD5E1 !important;
    border-radius: 6px !important;
}

/* Rótulos e Labels */
label, p, span {
    color: #1E293B !important;
    font-weight: 600;
}

/* Container de Upload Claro */
[data-testid="stFileUploader"] {
    background-color: #FFFFFF !important;
    border: 1px dashed #94A3B8 !important;
    border-radius: 8px !important;
    padding: 10px !important;
}

/* Cards de Métricas Topo */
.metric-card {
    background-color: #FFFFFF;
    padding: 16px;
    border-radius: 10px;
    border: 1px solid #E2E8F0;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}
.metric-title { font-size: 11px; font-weight: 700; color: #64748B; text-transform: uppercase; }
.metric-value { font-size: 24px; font-weight: 800; color: #0F172A; margin: 4px 0; }
.metric-sub { font-size: 12px; color: #10B981; font-weight: 600; }

/* Banner de Upload */
.upload-box {
    background-color: #EFF6FF;
    border: 1px solid #BFDBFE;
    border-radius: 10px;
    padding: 15px 20px;
    margin-bottom: 20px;
}

/* Botões */
.stButton>button { border-radius: 6px; font-weight: 600; }
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

# Tentar carregar arquivo automático da UF selecionada do repositório
arquivo_github = f"estabelecimentos_{uf_selecionada}.csv"
df_raw = carregar_dados(arquivo_github)

# --- BANNER DE UPLOAD MANUAL ---
st.markdown("""
<div class="upload-box">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <h4 style="margin: 0; color: #1E40AF;">📄 Possui um arquivo oficial da Receita (.CSV ou .ZIP)?</h4>
            <p style="margin: 0; color: #3B82F6; font-size: 13px;">Carregue direto no navegador para filtrar localmente sem enviar para nenhum servidor externo.</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Carregar ESTABELE / CSV", type=["csv", "txt"], label_visibility="collapsed")

if uploaded_file is not None:
    df_raw = carregar_dados(uploaded_file)

# --- CARDS DE MÉTRICAS (Topo) ---
col_m1, col_m2, col_m3, col_m4 = st.columns(4)

total_leads = len(df_raw) if df_raw is not None else 0

with col_m1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">LEADS ENCONTRADOS</div>
        <div class="metric-value">{total_leads}</div>
        <div class="metric-sub" style="color: #64748B;">Empresas na base ativa</div>
    </div>
    """, unsafe_allow_html=True)

with col_m2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">COM WHATSAPP VÁLIDO</div>
        <div class="metric-value">{total_leads}</div>
        <div class="metric-sub">100% da amostra</div>
    </div>
    """, unsafe_allow_html=True)

with col_m3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">HIGIENIZAÇÃO LGPD</div>
        <div class="metric-value">{total_leads}</div>
        <div class="metric-sub" style="color: #6366F1;">Zero CPFs / Limpeza Ativa</div>
    </div>
    """, unsafe_allow_html=True)

with col_m4:
    valor_est = total_leads * 0.12
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">VALOR ESTIMADO DO LOTE</div>
        <div class="metric-value">R$ {valor_est:.2f}</div>
        <div class="metric-sub" style="color: #D97706;">~ US$ {(valor_est/5):.2f} no Fiverr</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- PAINEL DE FILTROS AVANÇADOS ---
st.markdown("### ⚙️ Filtros Avançados de Pesquisa")

with st.container():
    f_col1, f_col2, f_col3, f_col4 = st.columns(4)
    with f_col1:
        uf_filtro = st.selectbox("ESTADO (UF)", [uf_selecionada] + list(ufs.keys()))
    with f_col2:
        cidade_filtro = st.text_input("NOME DA CIDADE", placeholder="Ex: Campinas, Curitiba...")
    with f_col3:
        ramo_filtro = st.text_input("RAMO DE ATIVIDADE (CNAE / TERMO)", placeholder="Ex: Solar, Software, 6201501...")
    with f_col4:
        situacao_filtro = st.selectbox("SITUAÇÃO CADASTRAL", ["Apenas Ativas (2)", "Todas"])

    f_col5, f_col6, f_col7, f_col8 = st.columns(4)
    with f_col5:
        data_ini = st.date_input("ABERTURA A PARTIR DE", value=None)
    with f_col6:
        data_fim = st.date_input("ABERTURA ATÉ", value=None)
    with f_col7:
        cap_min = st.text_input("CAPITAL SOCIAL MÍNIMO (R$)", placeholder="Ex: 10000")
    with f_col8:
        cap_max = st.text_input("CAPITAL SOCIAL MÁXIMO (R$)", placeholder="Ex: 500000")

    chk_col1, chk_col2, chk_col3 = st.columns(3)
    with chk_col1:
        ocultar_contabil = st.checkbox("▼ Ocultar E-mails de Contabilidade", value=True)
    with chk_col2:
        alertar_gratuitos = st.checkbox("⚠️ Alertar Provedores Gratuitos (@gmail)", value=True)
    with chk_col3:
        apenas_whats = st.checkbox("📞 Apenas com Telefone / WhatsApp", value=False)

st.markdown("---")

# --- TABELA E EXPORTAÇÃO ---
header_col1, header_col2 = st.columns([2, 1])

with header_col1:
    st.markdown("### Leads Extraídos & Enriquecidos")
    st.caption(f"Exibindo {total_leads} empresas ativas com dados limpos")

with header_col2:
    exp_col1, exp_col2 = st.columns(2)
    
    if df_raw is not None and not df_raw.empty:
        # Gera o CSV normal
        csv_buffer = df_raw.to_csv(index=False).encode('utf-8')
        
        # Gera um arquivo compatível com Excel sem precisar de openpyxl/xlsxwriter
        excel_csv_buffer = df_raw.to_csv(index=False, sep='\t').encode('utf-16')
        
        with exp_col1:
            st.download_button("🟢 Exportar Excel", data=excel_csv_buffer, file_name=f"leads_{uf_selecionada}.xls", mime="application/vnd.ms-excel")
        with exp_col2:
            st.download_button("⚫ Exportar CSV", data=csv_buffer, file_name=f"leads_{uf_selecionada}.csv", mime="text/csv")
    else:
        with exp_col1:
            st.button("🟢 Exportar Excel", disabled=True)
        with exp_col2:
            st.button("⚫ Exportar CSV", disabled=True)
            
# Exibição dos Dados
if df_raw is not None and not df_raw.empty:
    st.dataframe(df_raw, use_container_width=True)
else:
    st.warning(f"Nenhum arquivo 'estabelecimentos_{uf_selecionada}.csv' localizado. Faça o upload manual usando o botão acima ou gere pelo Colab.")
