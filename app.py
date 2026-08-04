import streamlit as st
import pandas as pd

st.set_page_config(page_title="Extrator de Leads - Receita Federal", page_icon="🎯", layout="wide")

st.title("🎯 Extrator de Leads — Receita Federal")
st.markdown("Carregue o arquivo de Estabelecimentos da Receita e filtre os leads por Estado, Cidade e CNAE (código ou nome do segmento).")

# Dicionário de tradução de CNAEs
CNAE_DESCRICOES = {
    "6201500": "Desenvolvimento de programas de computador sob encomenda",
    "6202300": "Desenvolvimento e licenciamento de programas de computador customizáveis",
    "6209100": "Suporte técnico, manutenção e outros serviços em tecnologia da informação",
    "7311400": "Agências de publicidade",
    "7319002": "Promoção de vendas",
    "7319003": "Marketing direto",
    "7020400": "Atividades de consultoria em gestão empresarial",
    "8599604": "Treinamento em desenvolvimento profissional e gerencial",
    "4711301": "Hipermercados",
    "4711302": "Supermercados",
    "5611201": "Restaurantes e similares",
    "5611203": "Lanchonetes, casas de chá, de sucos e similares",
    "4771701": "Comércio varejista de produtos farmacêuticos, sem manipulação de fórmulas",
    "9602501": "Cabeleireiros, manicure e pedicure",
    "4120400": "Construção de edifícios",
    "6821801": "Corretagem na compra e venda e avaliação de imóveis",
    "8630503": "Atividade médica ambulatorial restrita a consultas",
    "6911701": "Atividades advocatícias",
    "6920601": "Atividades de contabilidade",
}

# Upload do arquivo
uploaded_file = st.file_uploader("Selecione o arquivo extraído (ex: .ESTABELE ou .csv)", type=["ESTABELE", "csv", "txt"])

if uploaded_file is not None:
    st.success("Arquivo carregado com sucesso! Configure seus filtros abaixo:")
    
    columns = [
        "CNPJ_BASICO", "CNPJ_ORDEM", "CNPJ_DV", "IDENTIFICADOR_MATRIZ_FILIAL", 
        "NOME_FANTASIA", "SITUACAO_CADASTRAL", "DATA_SITUACAO_CADASTRAL", 
        "MOTIVO_SITUACAO_CADASTRAL", "NOME_CIDADE_EXTERIOR", "PAIS", 
        "DATA_INICIO_ATIVIDADE", "CNAE_FISCAL_PRINCIPAL", "CNAE_FISCAL_SECUNDARIA", 
        "TIPO_LOGRADOURO", "LOGRADOURO", "NUMERO", "COMPLEMENTO", "BAIRRO", 
        "CEP", "UF", "MUNICIPIO", "DDD_1", "TELEFONE_1", "DDD_2", "TELEFONE_2", 
        "DDD_FAX", "FAX", "CORREIO_ELETRONICO", "SITUACAO_ESPECIAL", "DATA_SITUACAO_ESPECIAL"
    ]
    
    try:
        # Leitura em blocos para economizar memória
        df = pd.read_csv(
            uploaded_file, 
            sep=";", 
            header=None, 
            names=columns, 
            dtype=str, 
            encoding="latin1",
            on_bad_lines="skip"
        )
        
        # Filtro fixo: Apenas Empresas Ativas (02)
        df_ativa = df[df["SITUACAO_CADASTRAL"] == "02"].copy()
        
        # Adiciona a Tradução do CNAE na base antes de filtrar
        df_ativa["DESCRICAO_CNAE"] = df_ativa["CNAE_FISCAL_PRINCIPAL"].map(
            lambda x: CNAE_DESCRICOES.get(str(x), "Outros / CNAE não mapeado")
        )
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            ufs_disponiveis = sorted(df_ativa["UF"].dropna().unique().tolist())
            uf_selecionada = st.selectbox("1. Selecione o Estado (UF):", ["Todos"] + ufs_disponiveis)
            
        with col2:
            cidade_busca = st.text_input("2. Filtrar Cidade (Nome ou Código):", placeholder="Ex: Campo Grande ou código").strip()
            
        with col3:
            cnae_busca = st.text_input("3. Filtrar CNAE (Código ou Nome da Atividade):", placeholder="Ex: 6201500 ou Software / Restaurante").strip()
            
        # Aplicação dos filtros
        df_filtrado = df_ativa.copy()
        
        if uf_selecionada != "Todos":
            df_filtrado = df_filtrado[df_filtrado["UF"] == uf_selecionada]
            
        if cidade_busca:
            df_filtrado = df_filtrado[
                df_filtrado["MUNICIPIO"].astype(str).str.contains(cidade_busca, case=False, na=False)
            ]
            
        if cnae_busca:
            # Busca tanto no código quanto na descrição traduzida
            df_filtrado = df_filtrado[
                df_filtrado["CNAE_FISCAL_PRINCIPAL"].astype(str).str.contains(cnae_busca, case=False, na=False) |
                df_filtrado["DESCRICAO_CNAE"].astype(str).str.contains(cnae_busca, case=False, na=False)
            ]
            
        st.subheader(f"Resultados encontrados: {len(df_filtrado)} leads ativas")
        
        # Exibe prévia das colunas
        colunas_exibicao = [
            "CNPJ_BASICO", "NOME_FANTASIA", "UF", "MUNICIPIO", 
            "CNAE_FISCAL_PRINCIPAL", "DESCRICAO_CNAE", "DDD_1", "TELEFONE_1", "CORREIO_ELETRONICO"
        ]
        
        cols_presentes = [c for c in colunas_exibicao if c in df_filtrado.columns]
        st.dataframe(df_filtrado[cols_presentes].head(50))
        
        # Botão para baixar CSV
        csv_data = df_filtrado.to_csv(index=False, sep=";", encoding="utf-8-sig")
        st.download_button(
            label="📥 Baixar Planilha de Leads (CSV)",
            data=csv_data,
            file_name="leads_extraidos.csv",
            mime="text/csv"
        )
        
    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")
