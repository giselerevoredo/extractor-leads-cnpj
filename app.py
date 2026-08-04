import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Extrator de Leads - CNPJ", page_icon="🎯", layout="centered"
)

st.title("🎯 Extrator de Leads — Receita Federal")
st.write(
    "Carregue o arquivo de Estabelecimentos da Receita e filtre os leads facilmente."
)

# Lista completa de todos os estados do Brasil + Distrito Federal
TODAS_UFS = [
    "TODOS (BR)",
    "AC",
    "AL",
    "AM",
    "AP",
    "BA",
    "CE",
    "DF",
    "ES",
    "GO",
    "MA",
    "MG",
    "MS",
    "MT",
    "PA",
    "PB",
    "PE",
    "PI",
    "PR",
    "RJ",
    "RN",
    "RO",
    "RR",
    "RS",
    "SC",
    "SE",
    "SP",
    "TO",
]

# Dicionário com lista de segmentos comuns
SEGMENTOS = {
    "imobiliarias": ["6821801", "6821802"],
    "agencias_marketing": ["7311400", "7312200"],
    "clinicas_odontologicas": ["8630504"],
    "clinicas_medicas": ["8630501", "8630502", "8630503"],
    "academias": ["9313100"],
    "restaurantes": ["5611201", "5611203"],
    "saloes_beleza": ["9602501", "9602502"],
    "contabilidade": ["6920601"],
    "advocacia": ["6911701"],
    "escolas": ["8513900", "8520100"],
    "farmacias": ["4771701"],
    "autoescolas": ["8599601"],
    "petshops": ["9609208", "4789004"],
    "energia_solar": ["4321500", "7112000"],
    "Outro (Digitar código CNAE)": ["OUTRO"],
}

uploaded_file = st.file_uploader(
    "Selecione o arquivo extraído (ex: .ESTABELE ou .csv)",
    type=["ESTABELE", "csv", "txt"],
)

if uploaded_file is not None:
    st.success("Arquivo carregado com sucesso!")

    col1, col2 = st.columns(2)

    with col1:
        uf_selecionada = st.selectbox("Selecione o Estado (UF):", TODAS_UFS)

    with col2:
        segmento_selecionado = st.selectbox(
            "Selecione o Segmento:", list(SEGMENTOS.keys())
        )

    # Campo extra que aparece apenas se escolher "Outro"
    cnae_customizado = ""
    if segmento_selecionado == "Outro (Digitar código CNAE)":
        cnae_customizado = st.text_input(
            "Digite o CNAE desejado (apenas números, ex: 4711301):"
        )

    if st.button("🚀 Extrair Leads", type="primary"):
        # Define quais CNAEs serão usados
        if segmento_selecionado == "Outro (Digitar código CNAE)":
            cnae_limpo = (
                cnae_customizado.replace(".", "")
                .replace("-", "")
                .replace("/", "")
                .strip()
            )
            if not cnae_limpo:
                st.error("Por favor, digite um código CNAE válido.")
                st.stop()
            cnaes_alvo = [cnae_limpo]
        else:
            cnaes_alvo = SEGMENTOS[segmento_selecionado]

        with st.spinner("Processando e filtrando os dados... Aguarde."):
            colunas = [
                "cnpj_basico",
                "cnpj_ordem",
                "cnpj_dv",
                "identificador",
                "nome_fantasia",
                "situacao_cadastral",
                "data_situacao",
                "motivo",
                "nm_cidade_exterior",
                "pais",
                "dt_inicio_atividade",
                "cnae_fiscal_principal",
                "cnae_fiscal_secundaria",
                "tipo_logradouro",
                "logradouro",
                "numero",
                "complemento",
                "bairro",
                "cep",
                "uf",
                "municipio",
                "ddd_1",
                "telefone_1",
                "ddd_2",
                "telefone_2",
                "ddd_fax",
                "fax",
                "email",
                "situacao_especial",
                "data_situacao_especial",
            ]

            chunks = []
            for chunk in pd.read_csv(
                uploaded_file,
                sep=";",
                header=None,
                names=colunas,
                dtype=str,
                encoding="latin1",
                chunksize=50000,
            ):

                # Filtrar apenas empresas ATIVAS (situação 02)
                chunk = chunk[chunk["situacao_cadastral"] == "02"]

                # Filtrar pelo CNAE desejado
                chunk = chunk[chunk["cnae_fiscal_principal"].isin(cnaes_alvo)]

                # Filtrar pelo Estado selecionado (se não for BR inteiro)
                if uf_selecionada != "TODOS (BR)":
                    chunk = chunk[chunk["uf"] == uf_selecionada]

                chunks.append(chunk)

            if chunks:
                df_final = pd.concat(chunks, ignore_index=True)

                if not df_final.empty:
                    st.balloons()
                    st.success(
                        f"Encontrados **{len(df_final)}** leads ativos!"
                    )

                    # Exibir prévia na tela
                    st.dataframe(
                        df_final[
                            [
                                "cnpj_basico",
                                "nome_fantasia",
                                "uf",
                                "email",
                                "telefone_1",
                            ]
                        ].head(10)
                    )

                    # Botão para baixar planilha pronta
                    csv = df_final.to_csv(index=False, sep=";").encode(
                        "utf-8-sig"
                    )
                    st.download_button(
                        label="📥 Baixar Planilha de Leads (CSV)",
                        data=csv,
                        file_name=f"leads_{segmento_selecionado}_{uf_selecionada}.csv",
                        mime="text/csv",
                    )
                else:
                    st.warning(
                        "Nenhum lead encontrado com os filtros selecionados."
                    )
            else:
                st.warning(
                    "Nenhum resultado retornado. Verifique o arquivo enviado."
                )