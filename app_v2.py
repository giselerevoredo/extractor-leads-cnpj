import base64
import os
import re
import pandas as pd
import requests
import streamlit as st

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="LeadGov B2B Pro - Extrator Receita Federal",
    page_icon="🏢",
    layout="wide",
)

# --- ESTILIZAÇÃO CSS CUSTOMIZADA (LAYOUT TIPO PAINEL GOV B2B) ---
st.markdown(
    """
    <style>
    .main { background-color: #f8fafc; }
    .kpi-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 18px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .kpi-title { font-size: 0.75rem; font-weight: 700; color: #64748b; text-transform: uppercase; }
    .kpi-value { font-size: 1.8rem; font-weight: 900; color: #0f172a; margin-top: 4px; }
    .kpi-sub { font-size: 0.75rem; color: #10b981; font-weight: 600; margin-top: 2px; }
    .badge-lgpd {
        background-color: #dbeafe; color: #1e40af; padding: 2px 8px;
        border-radius: 4px; font-size: 11px; font-weight: bold;
    }
    .badge-mei {
        background-color: #e0e7ff; color: #3730a3; padding: 2px 8px;
        border-radius: 4px; font-size: 11px; font-weight: bold;
    }
    .badge-warn {
        background-color: #fef3c7; color: #92400e; padding: 2px 8px;
        border-radius: 4px; font-size: 11px; font-weight: bold;
    }
    </style>
""",
    unsafe_allow_html=True,
)


# --- BUSCA NOMES DAS CIDADES VIA API DO IBGE ---
@st.cache_data
def carregar_municipios_ibge():
    try:
        url = "https://servicodados.ibge.gov.br/api/v1/localidades/municipios"
        res = requests.get(url, timeout=10).json()
        return {str(m["id"])[:6]: m["nome"].upper() for m in res}
    except:
        return {}


# Mapeamento auxiliar TOM/Receita para garantir capitais/cidades chave
CODIGOS_TOM_GERAL = {
    "9027": "CAMPO GRANDE",
    "9051": "CORUMBÁ",
    "9073": "DOURADOS",
    "9809": "AQUIDAUANA",
    "7535": "CURITIBA",
    "7560": "LONDRINA",
    "7595": "MARINGÁ",
    "7438": "CASCAVEL",
    "7805": "PONTA GROSSA",
    "7633": "FOZ DO IGUACU",
}


@st.cache_data
def carregar_dados_estado(sigla_uf):
    arquivo = f"estabelecimentos_{sigla_uf}.csv"

    if not os.path.exists(arquivo):
        if sigla_uf == "MS" and os.path.exists(
            "estabelecimentos_filtrados.csv"
        ):
            arquivo = "estabelecimentos_filtrados.csv"
        else:
            return None

    colunas = [
        "CNPJ_BASICO",
        "CNPJ_ORDEM",
        "CNPJ_DV",
        "IDENTIFICADOR",
        "NOME_FANTASIA",
        "SITUACAO_CADASTRAL",
        "DATA_SITUACAO",
        "MOTIVO_SITUACAO",
        "NOME_CIDADE_EXTERIOR",
        "PAIS",
        "DATA_INICIO_ATIVIDADE",
        "CNAE_PRINCIPAL",
        "CNAE_SECUNDARIO",
        "TIPO_LOGRADOURO",
        "LOGRADOURO",
        "NUMERO",
        "COMPLEMENTO",
        "BAIRRO",
        "CEP",
        "UF",
        "MUNICIPIO_CODIGO",
        "DDD1",
        "TELEFONE1",
        "DDD2",
        "TELEFONE2",
        "DDD_FAX",
        "FAX",
        "CORREIO_ELETRONICO",
        "SITUACAO_ESPECIAL",
        "DATA_SITUACAO_ESPECIAL",
    ]

    df = pd.read_csv(
        arquivo,
        sep=";",
        names=colunas,
        dtype=str,
        encoding="latin-1",
        on_bad_lines="skip",
    )

    dic_ibge = carregar_municipios_ibge()

    def traduzir_cidade(cod):
        cod_str = str(cod).strip()
        if cod_str in dic_ibge:
            return dic_ibge[cod_str]
        elif cod_str in CODIGOS_TOM_GERAL:
            return CODIGOS_TOM_GERAL[cod_str]
        return f"CIDADE CÓD. {cod_str}"

    df["NOME_MUNICIPIO"] = df["MUNICIPIO_CODIGO"].apply(traduzir_cidade)

    # CNPJ Completo Formatado
    df["CNPJ_COMPLETO"] = df.apply(
        lambda r: f"{str(r['CNPJ_BASICO']).zfill(8)}/{str(r['CNPJ_ORDEM']).zfill(4)}-{str(r['CNPJ_DV']).zfill(2)}"
        if pd.notna(r["CNPJ_BASICO"])
        else "",
        axis=1,
    )

    # Formatação Telefone / WhatsApp
    def formatar_tel(row):
        ddd = str(row["DDD1"]).strip() if pd.notna(row["DDD1"]) else ""
        tel = str(row["TELEFONE1"]).strip() if pd.notna(row["TELEFONE1"]) else ""
        if ddd and tel:
            return f"({ddd}) {tel}"
        return ""

    df["TELEFONE_COMPLETO"] = df.apply(formatar_tel, axis=1)

    # Link direto WhatsApp
    def link_wa(row):
        ddd = re.sub(r"\D", "", str(row["DDD1"])) if pd.notna(row["DDD1"]) else ""
        tel = (
            re.sub(r"\D", "", str(row["TELEFONE1"]))
            if pd.notna(row["TELEFONE1"])
            else ""
        )
        if ddd and tel and len(tel) >= 8:
            return f"https://wa.me/55{ddd}{tel}"
        return ""

    df["WHATSAPP_URL"] = df.apply(link_wa, axis=1)

    mapa_situacao = {
        "01": "NULA",
        "02": "ATIVA",
        "03": "SUSPENSA",
        "04": "INAPTÂ",
        "08": "BAIXADA",
    }
    df["SITUACAO_TEXTO"] = (
        df["SITUACAO_CADASTRAL"].map(mapa_situacao).fillna("OUTRA")
    )

    return df


# --- NAVEGAÇÃO SUPERIOR (ABAS IGUAIS AO HTML) ---
st.title("🏢 LeadGov B2B Pro")
st.caption("Extrator & Enriquecedor de Leads - Receita Federal | Dados 2026")

aba1, aba2, aba3, aba4 = st.tabs(
    [
        "🔍 Mineração Live",
        "🐍 Gerador Colab Python",
        "💼 Calculadora & Vendas",
        "🛡️ Blindagem LGPD",
    ]
)

# ==============================================================================
# ABA 1: MINERAÇÃO LIVE
# ==============================================================================
with aba1:
    st.sidebar.header("📍 1. Estado & Base")
    uf_list = ["MS", "PR", "SP", "RJ", "SC", "RS", "MG", "GO", "BA", "PE"]
    uf_sel = st.sidebar.selectbox("Estado (UF):", uf_list)

    df = carregar_dados_estado(uf_sel)

    if df is None:
        st.error(
            f"⚠️ O arquivo `estabelecimentos_{uf_sel}.csv` ainda não foi encontrado na pasta do projeto!"
        )
        st.info(
            f"Gere o lote do estado {uf_sel} no Colab e envie para o repositório GitHub."
        )
    else:
        st.sidebar.header("🔍 2. Filtros Avançados")

        # Filtros laterais
        cidades = ["Todas"] + sorted([c for c in df["NOME_MUNICIPIO"].unique() if c])
        cidade_sel = st.sidebar.selectbox("Cidade:", cidades)

        filtro_cnae = st.sidebar.text_input(
            "CNAE (Código ou Termo):", placeholder="Ex: Solar, Software, 6201501"
        )
        filtro_nome = st.sidebar.text_input("Nome Fantasia:").upper()
        filtro_bairro = st.sidebar.text_input("Bairro:").upper()

        situacao_sel = st.sidebar.selectbox(
            "Situação Cadastral:",
            ["ATIVA", "BAIXADA", "SUSPENSA", "INAPTÂ", "Todas"],
            index=0,
        )

        st.sidebar.subheader("🛡️ Higienização LGPD & Contato")
        remover_contabilidade = st.sidebar.checkbox(
            "Ocultar E-mails de Contabilidade", value=True
        )
        alertar_gmail = st.sidebar.checkbox(
            "Alertar Provedores Gratuitos (@gmail)", value=True
        )
        apenas_com_tel = st.sidebar.checkbox(
            "Apenas com Telefone / WhatsApp", value=False
        )

        # Aplicando Filtros
        df_f = df.copy()

        if cidade_sel != "Todas":
            df_f = df_f[df_f["NOME_MUNICIPIO"] == cidade_sel]
        if filtro_cnae:
            df_f = df_f[
                df_f["CNAE_PRINCIPAL"].str.contains(filtro_cnae, na=False)
            ]
        if filtro_nome:
            df_f = df_f[
                df_f["NOME_FANTASIA"].str.contains(filtro_nome, na=False)
            ]
        if filtro_bairro:
            df_f = df_f[
                df_f["BAIRRO"].str.contains(filtro_bairro, na=False)
            ]
        if situacao_sel != "Todas":
            df_f = df_f[df_f["SITUACAO_TEXTO"] == situacao_sel]
        if apenas_com_tel:
            df_f = df_f[df_f["TELEFONE1"].notna() & (df_f["TELEFONE1"] != "")]
        if remover_contabilidade:
            df_f = df_f[
                ~df_f["CORREIO_ELETRONICO"]
                .str.lower()
                .str.contains("contab|contabil|escritorio", na=False)
            ]

        # CALCULANDO MÉTRICAS / KPIS (ESTILO HTML)
        total_leads = len(df_f)
        total_wa = len(df_f[df_f["WHATSAPP_URL"] != ""])
        pct_wa = int((total_wa / total_leads * 100)) if total_leads > 0 else 0
        valor_est = total_leads * 0.12

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Leads Encontrados", f"{total_leads:,}")
        col2.metric(
            "Com WhatsApp Válido",
            f"{total_wa:,}",
            delta=f"{pct_wa}% da amostra",
        )
        col3.metric("Higienização LGPD", f"{total_leads:,}", delta="Ativa")
        col4.metric(
            "Valor Estimado do Lote",
            f"R$ {valor_est:,.2f}",
            delta=f"~ US$ {(valor_est/5.5):,.2f}",
        )

        st.markdown("---")

        # EXPORTAÇÃO E TRADUÇÃO DE CABEÇALHOS
        c_exp1, c_exp2 = st.columns([2, 1])
        with c_exp1:
            st.subheader(f"📋 Resultados do Lote ({uf_sel})")
        with c_exp2:
            lang_export = st.radio(
                "Idioma Cabeçalho Exportação:",
                ["PT-BR", "EN (Fiverr/Upwork)"],
                horizontal=True,
            )

        cols_pt = [
            "CNPJ_COMPLETO",
            "NOME_FANTASIA",
            "NOME_MUNICIPIO",
            "BAIRRO",
            "CNAE_PRINCIPAL",
            "TELEFONE_COMPLETO",
            "CORREIO_ELETRONICO",
            "SITUACAO_TEXTO",
        ]
        df_exibir = df_f[cols_pt].copy()

        # Renomeia se o idioma for EN
        if lang_export == "EN (Fiverr/Upwork)":
            df_exibir.columns = [
                "TAX_ID_CNPJ",
                "COMPANY_NAME",
                "CITY",
                "NEIGHBORHOOD",
                "CNAE_CODE",
                "PHONE",
                "EMAIL",
                "STATUS",
            ]

        st.dataframe(df_exibir, use_container_width=True)

        # Botão Download
        csv_download = df_exibir.to_csv(index=False, sep=";").encode("latin-1")
        st.download_button(
            label=f"📥 Baixar Lote de Leads em CSV ({lang_export})",
            data=csv_download,
            file_name=f"leads_{uf_sel.lower()}_{cidade_sel.lower()}.csv",
            mime="text/csv",
        )

# ==============================================================================
# ABA 2: GERADOR DE SCRIPT PYTHON COLAB
# ==============================================================================
with aba2:
    st.subheader("🐍 Gerador de Script para Google Colab")
    st.write(
        "Gere automaticamente o código Python otimizado para rodar no Google Colab e filtrar gigabytes sem travar a memória RAM."
    )

    uf_colab = st.selectbox(
        "Selecione o Estado para o Script do Colab:",
        ["PR", "MS", "SP", "RJ", "MG", "SC", "RS", "BA", "PE", "GO"],
    )

    script_codigo = f"""import pandas as pd

# --- PIPELINE DE EXTRAÇÃO AUTOMÁTICA RECEITA FEDERAL ---
arquivo_origem = "K3241.K03200Y8.D60711.ESTABELE"
uf_desejada = "{uf_colab}"
arquivo_destino = f"estabelecimentos_{{uf_desejada}}.csv"

chunksize = 100000
primeiro_bloco = True

print(f"Iniciando filtragem da Receita Federal para UF: {{uf_desejada}}...")

for chunk in pd.read_csv(
    arquivo_origem, 
    sep=";", 
    encoding="latin-1", 
    header=None, 
    dtype=str, 
    chunksize=chunksize, 
    on_bad_lines="skip"
):
    # Coluna 19 é a UF no padrão da Receita Federal
    chunk_filtrado = chunk[chunk[19] == uf_desejada]
    
    if primeiro_bloco:
        chunk_filtrado.to_csv(arquivo_destino, mode='w', index=False, header=False, sep=';')
        primeiro_bloco = False
    else:
        chunk_filtrado.to_csv(arquivo_destino, mode='a', index=False, header=False, sep=';')

print(f"✅ Concluído! Arquivo gerado com sucesso: {{arquivo_destino}}")
"""
    st.code(script_codigo, language="python")

# ==============================================================================
# ABA 3: CALCULADORA DE PRECIFICAÇÃO & FREELANCE
# ==============================================================================
with aba3:
    st.subheader("💼 Calculadora Comercial & Anúncios Prontos")

    col_calc1, col_calc2 = st.columns([1, 2])

    with col_calc1:
        st.markdown("### 🧮 Precificação")
        qtd_leads = st.number_input(
            "Volume do Lote (Qtd. Leads):",
            value=5000,
            step=500,
        )

        preco_br = qtd_leads * 0.03
        if preco_br < 49.0:
            preco_br = 49.0

        preco_usd = (qtd_leads * 0.02) / 5.5
        if preco_usd < 10.0:
            preco_usd = 10.0

        st.info(f"**Preço BR Sugerido:** R$ {preco_br:.2f}")
        st.success(f"**Preço Exterior Sugerido:** US$ {preco_usd:.2f}")

    with col_calc2:
        st.markdown("### 📝 Modelo de Anúncio Copiável (Workana / Fiverr)")
        opcao_template = st.radio(
            "Idioma Modelo:", ["Português (BR)", "Inglês (Global)"]
        )

        if opcao_template == "Português (BR)":
            st.text_area(
                "Título & Descrição:",
                value="""[TITULO]: Extração de Lista de Empresas e Leads B2B da Receita Federal por Estado e Cidade

[DESCRIÇÃO]:
Forneço listas atualizadas e higienizadas de empresas (B2B) direto da base oficial da Receita Federal.

O que está incluído no arquivo:
- CNPJ e Razão Social / Nome Fantasia
- Cidade, Bairro e Endereço
- Telefone / WhatsApp Formatado
- E-mail Institucional (Higienizado contra e-mails de contabilidade)
- Código CNAE e Ramo de Atuação
- Situação Cadastral Ativa

Dados 100% adequados à LGPD (apenas dados públicos de Pessoas Jurídicas). Entrega rápida em formato Excel (.XLSX) ou CSV.""",
                height=220,
            )
        else:
            st.text_area(
                "Gig Title & Description:",
                value="""[TITLE]: I will extract targeted Brazil B2B leads and business lists from official government data

[DESCRIPTION]:
Get verified and up-to-date B2B business leads from Brazil customized by State, City, or Industry (CNAE Code).

Data Fields Included:
- CNPJ (Tax ID) & Company Legal Name
- City, State, Address & ZIP Code
- Clean Email & Formatted Phone / WhatsApp
- Main Activity (CNAE Code & Description)
- Registration Status (Active Companies)

Delivered in clean Excel (.XLSX) or CSV format ready for CRM import.""",
                height=220,
            )

# ==============================================================================
# ABA 4: BLINDAGEM LGPD
# ==============================================================================
with aba4:
    st.subheader("🛡️ Guia de Conformidade LGPD para Prospecção B2B")
    st.markdown(
        """
    - **Dados Públicos de PJ:** Informações cadastrais de Pessoas Jurídicas (CNPJ, endereço comercial, e-mail institucional e telefone da empresa) são de domínio público na Receita Federal e seu uso comerciais B2B é legítimo (**Legítimo Interesse - Art. 7º, IX da LGPD**).
    - **Atenção aos MEIs:** Empresas individuais (MEI) podem conter e-mails pessoais ou nomes civis no cadastro. O app sinaliza esses casos para garantir abordagem ética.
    - **Filtro de Contabilidade:** O app remove automaticamente e-mails genéricos de escritórios contábeis para evitar *spam* não solicitado a terceiros.
    """
    )
