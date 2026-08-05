import streamlit as st
import pandas as pd
import re

# ==========================================
# CONFIGURAÇÃO DA PÁGINA
# ==========================================
st.set_page_config(
    page_title="LeadGov B2B Pro | CNPJ Intelligence",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS personalizada (Tema Escuro/Pro)
st.markdown("""
<style>
    .main { background-color: #0E1117; }
    .stMetric { background-color: #1E232A; padding: 15px; border-radius: 8px; border: 1px solid #2D3748; }
    div[data-testid="stSidebar"] { background-color: #161B22; border-right: 1px solid #2D3748; }
    .stButton>button { background-color: #0066CC; color: white; border-radius: 6px; font-weight: 600; border: none; }
    .stButton>button:hover { background-color: #0052A3; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# CONSTANTES & LISTA COMPLETA DE ESTADOS
# ==========================================
ESTADOS_BR = [
    "AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO", "MA", 
    "MG", "MS", "MT", "PA", "PB", "PE", "PI", "PR", "RJ", "RN", 
    "RO", "RR", "RS", "SC", "SE", "SP", "TO"
]

UF_NOMES = {
    "AC": "Acre", "AL": "Alagoas", "AM": "Amazonas", "AP": "Amapá",
    "BA": "Bahia", "CE": "Ceará", "DF": "Distrito Federal", "ES": "Espírito Santo",
    "GO": "Goiás", "MA": "Maranhão", "MG": "Minas Gerais", "MS": "Mato Grosso do Sul",
    "MT": "Mato Grosso", "PA": "Pará", "PB": "Paraíba", "PE": "Pernambuco",
    "PI": "Piauí", "PR": "Paraná", "RJ": "Rio de Janeiro", "RN": "Rio Grande do Norte",
    "RO": "Rondônia", "RR": "Roraima", "RS": "Rio Grande do Sul", "SC": "Santa Catarina",
    "SE": "Sergipe", "SP": "São Paulo", "TO": "Tocantins"
}

# ==========================================
# MÓDULO DE TRATAMENTO LGPD E DADOS
# ==========================================
def sanitizar_contatos(df):
    """Aplica regras de higienização e filtro LGPD"""
    df = df.copy()
    
    # Mascarar e filtrar e-mails contábeis/genéricos
    padroes_contabil = r'(contabil|contabilidade|escritorio|fiscal|tax|auditoria|assessor)'
    if 'email' in df.columns:
        df['is_contabilidade'] = df['email'].astype(str).str.contains(padroes_contabil, case=False, na=False)
        df['email_limpo'] = df.apply(
            lambda r: "[FILTRADO LGPD - CONTABILIDADE]" if r['is_contabilidade'] else r['email'], axis=1
        )
    
    # Validação Básica de Formato de Telefone
    if 'telefone' in df.columns:
        df['telefone_formatado'] = df['telefone'].astype(str).apply(
            lambda x: re.sub(r'\D', '', x) if pd.notnull(x) else ""
        )
    return df

@st.cache_data
def carregar_dados_uf(uf_selecionada):
    """Carrega o arquivo CSV correspondente ao estado selecionado"""
    caminho_arquivo = f"estabelecimentos_{uf_selecionada}.csv"
    try:
        df = pd.read_csv(caminho_arquivo, dtype=str)
        return sanitizar_contatos(df), None
    except FileNotFoundError:
        return None, f"Arquivo '{caminho_arquivo}' não encontrado no repositório. Gere-o via Colab."
    except Exception as e:
        return None, f"Erro ao carregar o arquivo: {str(e)}"

# ==========================================
# BARRA LATERAL (PAINEL DE NAVEGAÇÃO)
# ==========================================
st.sidebar.title("💼 LeadGov Pro")
st.sidebar.caption("CNPJ Intelligence & Lead Generation")
st.sidebar.divider()

st.sidebar.subheader("📍 Seleção Geográfica")
uf_ativa = st.sidebar.selectbox(
    "Selecione o Estado (UF):",
    options=ESTADOS_BR,
    format_func=lambda x: f"{x} - {UF_NOMES[x]}",
    index=11 # Padrão em MS
)

st.sidebar.divider()
st.sidebar.info("💡 **Dica LGPD:** E-mails de escritórios contábeis são automaticamente marcados para evitar abordagens indevidas.")

# ==========================================
# PAINEL PRINCIPAL / NAVEGAÇÃO
# ==========================================
st.title(f" Painel Pro - Extrator B2B ({uf_ativa})")

aba1, aba2, aba3, aba4 = st.tabs([
    "🔍 Filtragem de Leads", 
    "📊 Dashboards & Insights", 
    "⚡ Gerador Colab Python", 
    "🛡️ Shield LGPD"
])

# ------------------------------------------
# ABA 1: FILTRAGEM DE LEADS
# ------------------------------------------
with aba1:
    df, erro = carregar_dados_uf(uf_ativa)
    
    if erro:
        st.warning(erro)
        st.info("Utilize a aba **⚡ Gerador Colab Python** para criar o arquivo referente a este estado.")
    else:
        st.subheader("Filtros Avançados")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            municipio = st.text_input("Filtrar por Município:")
        with col2:
            cnae = st.text_input("Filtrar por CNAE / Atividade:")
        with col3:
            ocultar_contábeis = st.checkbox("Ocultar E-mails Contábeis", value=True)
            
        # Aplicação dos Filtros
        df_filtrado = df.copy()
        if municipio and 'municipio' in df_filtrado.columns:
            df_filtrado = df_filtrado[df_filtrado['municipio'].str.contains(municipio, case=False, na=False)]
        if cnae and 'cnae' in df_filtrado.columns:
            df_filtrado = df_filtrado[df_filtrado['cnae'].str.contains(cnae, case=False, na=False)]
        if ocultar_contábeis and 'is_contabilidade' in df_filtrado.columns:
            df_filtrado = df_filtrado[~df_filtrado['is_contabilidade']]

        # Métricas
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Registros", len(df))
        m2.metric("Filtrados", len(df_filtrado))
        m3.metric("Taxa de Aproveitamento", f"{(len(df_filtrado)/len(df)*100):.1f}%" if len(df) > 0 else "0%")

        st.divider()
        st.dataframe(df_filtrado, use_container_width=True)

        # Exportação
        csv_download = df_filtrado.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Baixar Base Filtrada (CSV)",
            data=csv_download,
            file_name=f"leads_{uf_ativa}_filtrado.csv",
            mime="text/csv"
        )

# ------------------------------------------
# ABA 2: DASHBOARDS
# ------------------------------------------
with aba2:
    st.subheader("Análise Qualitativa da Base")
    if 'df_filtrado' in locals() and df_filtrado is not None and not df_filtrado.empty:
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            if 'municipio' in df_filtrado.columns:
                st.write("**Top 10 Municípios com mais Leads**")
                top_mun = df_filtrado['municipio'].value_counts().head(10)
                st.bar_chart(top_mun)
                
        with col_chart2:
            if 'is_contabilidade' in df_filtrado.columns:
                st.write("**Proporção de E-mails Direct x Contábeis**")
                dist_emails = df_filtrado['is_contabilidade'].value_counts().rename(index={True: 'Contábil', False: 'Direto'})
                st.bar_chart(dist_emails)
    else:
        st.info("Carregue uma base válida na primeira aba para visualizar os gráficos.")

# ------------------------------------------
# ABA 3: GERADOR COLAB PYTHON
# ------------------------------------------
with aba3:
    st.subheader("Script Automatizado para Processamento na Nuvem")
    st.markdown("""
    Copie o código Python abaixo para rodar no seu **Google Colab**. 
    Ele irá extrair os dados diretamente do arquivo `.ESTABELE` da Receita Federal para a UF selecionada:
    """)
    
    script_colab = f"""# ========================================================
# SCRIPT DE EXTRAÇÃO DE LEADS CNPJ ({uf_ativa})
# Executar no Google Colab
# ========================================================
import pandas as pd

# 1. Definição dos Arquivos
arquivo_origem = "K3241014.D40810.ESTABELE"  # <--- Altere para o nome do seu arquivo baixado
uf_desejada = "{uf_ativa}"
arquivo_destino = f"estabelecimentos_{{uf_desejada}}.csv"

# Código do Estado no IBGE para filtragem rápida
codigos_uf = {{
    "RO": "11", "AC": "12", "AM": "13", "RR": "14", "PA": "15", "AP": "16", "TO": "17",
    "MA": "21", "PI": "22", "CE": "23", "RN": "24", "PB": "25", "PE": "26", "AL": "27",
    "SE": "28", "BA": "29", "MG": "31", "ES": "32", "RJ": "33", "SP": "35", "PR": "41",
    "SC": "42", "RS": "43", "MS": "50", "MT": "51", "GO": "52", "DF": "53"
}}

print(f"Iniciando extração para a UF: {{uf_desejada}}...")
# Adicione a lógica de leitura e filtro em chunks aqui
print("Fim do processo!")
"""
    st.code(script_colab, language="python")

# ------------------------------------------
# ABA 4: SHIELD LGPD
# ------------------------------------------
with aba4:
    st.subheader("🛡️ Guia de Conformidade LGPD")
    st.markdown("""
    - **Dados Públicos de PJ:** Informações cadastrais de Pessoas Jurídicas são de domínio público na Receita Federal e seu uso comercial B2B é legítimo.
    - **Atenção aos MEIs:** Empresas individuais podem conter e-mails ou nomes civis no cadastro.
    - **Filtro de Contabilidade:** O app sinaliza automaticamente e-mails contábeis para evitar spam não solicitado a terceiros.
    """)
