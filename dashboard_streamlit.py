import pandas as pd
import streamlit as st
import plotly.express as px

# 📌 Insira o ID do seu arquivo no Google Drive
GOOGLE_DRIVE_FILE_ID = "SEU_ID_AQUI"

# 📌 Construir URL direta para download do arquivo
CSV_URL = f"https://drive.google.com/uc?id={GOOGLE_DRIVE_FILE_ID}"

# 📌 Tentar carregar o CSV do Google Drive com tratamento de erros
try:
    df = pd.read_csv(CSV_URL, sep=";", on_bad_lines="skip", encoding="utf-8")
    st.success("✅ Arquivo CSV carregado com sucesso!")
except Exception as e:
    st.error(f"❌ Erro ao carregar o arquivo: {e}")
    st.stop()

# Configuração da Página
st.set_page_config(page_title="Dashboard de Análise", layout="wide")

# Criar Navegação
pagina_selecionada = st.sidebar.radio("📌 Selecione a Página", ["📊 Análise Atual", "📈 Comparação Histórica"])

# 📌 Criar Filtros Interativos
if pagina_selecionada in ["📊 Análise Atual", "📈 Comparação Histórica"]:
    st.sidebar.header("📌 Filtros")
    ano_selecionado = st.sidebar.selectbox("📅 Selecione o Ano", sorted(df["ANO"].unique()))
    mes_selecionado = st.sidebar.multiselect("📆 Selecione o(s) Mês(es)", sorted(df["mês"].unique()), default=df["mês"].unique())
    convenio_selecionado = st.sidebar.multiselect("🏥 Selecione o(s) Convênio(s)", sorted(df["CONVENIOS"].unique()), default=df["CONVENIOS"].unique())
    medico_selecionado = st.sidebar.multiselect("👨‍⚕️ Selecione o(s) Médico(s)", sorted(df["MEDICO"].unique()), default=df["MEDICO"].unique())

    # Aplicar Filtros
    df_filtrado = df[
        (df["ANO"] == ano_selecionado) &
        (df["mês"].isin(mes_selecionado)) &
        (df["CONVENIOS"].isin(convenio_selecionado)) &
        (df["MEDICO"].isin(medico_selecionado))
    ]

# 📌 Página "📊 Análise Atual"
if pagina_selecionada == "📊 Análise Atual":
    st.title("📊 Análise de Faturamento e Atendimentos")

    col1, col2 = st.columns(2)

    with col1:
        fig_fat_med = px.bar(df_filtrado.groupby("MEDICO")["valor"].sum().reset_index(), 
                             x="valor", y="MEDICO", orientation="h", 
                             title="Faturamento por Médico", text_auto=True)
        st.plotly_chart(fig_fat_med, use_container_width=True)

        fig_fat_conv = px.bar(df_filtrado.groupby("CONVENIOS")["valor"].sum().reset_index(), 
                              x="valor", y="CONVENIOS", orientation="h", 
                              title="Faturamento por Convênio", text_auto=True)
        st.plotly_chart(fig_fat_conv, use_container_width=True)

    with col2:
        fig_qtde_med = px.bar(df_filtrado.groupby("MEDICO")["qTDE"].sum().reset_index(), 
                              x="qTDE", y="MEDICO", orientation="h", 
                              title="Atendimentos por Médico", text_auto=True)
        st.plotly_chart(fig_qtde_med, use_container_width=True)

        fig_qtde_conv = px.bar(df_filtrado.groupby("CONVENIOS")["qTDE"].sum().reset_index(), 
                               x="qTDE", y="CONVENIOS", orientation="h", 
                               title="Atendimentos por Convênio", text_auto=True)
        st.plotly_chart(fig_qtde_conv, use_container_width=True)

# 📌 Página "📈 Comparação Histórica"
elif pagina_selecionada == "📈 Comparação Histórica":
    st.title("📈 Comparação Histórica de Faturamento, Atendimentos e Conversão")

    df_historico = df.groupby("ANO")["valor"].sum().reset_index()
    fig_historico = px.bar(df_historico, x="ANO", y="valor", text_auto=True, title="Faturamento Anual")
    st.plotly_chart(fig_historico, use_container_width=True)

    df_qtde_historico = df.groupby("ANO")["qTDE"].sum().reset_index()
    fig_qtde_historico = px.line(df_qtde_historico, x="ANO", y="qTDE", markers=True, title="Volume de Atendimentos Anual")
    st.plotly_chart(fig_qtde_historico, use_container_width=True)

    # 📌 Cálculo das Taxas de Conversão
    df_cirurgias = df[df["PROCEDIMENTO_GRUPO"] == "Cirurgia"].groupby("ANO")["qTDE"].sum()
    df_procedimentos = df[df["PROCEDIMENTO_GRUPO"] == "Procedimento"].groupby("ANO")["qTDE"].sum()
    df_exames = df[df["PROCEDIMENTO_GRUPO"] == "Exame"].groupby("ANO")["qTDE"].sum()
    df_consultas = df[df["PROCEDIMENTO_GRUPO"] == "Consulta"].groupby("ANO")["qTDE"].sum()

    df_conversao = pd.DataFrame(index=df["ANO"].unique())  
    df_conversao["Cirurgias"] = df_cirurgias
    df_conversao["Procedimentos"] = df_procedimentos
    df_conversao["Exames"] = df_exames
    df_conversao["Consultas"] = df_consultas
    df_conversao.fillna(0, inplace=True)

    df_conversao["Conversão de Cirurgias (%)"] = (df_conversao["Cirurgias"] / df_conversao["Consultas"]) * 100
    df_conversao["Conversão de Procedimentos (%)"] = (df_conversao["Procedimentos"] / df_conversao["Consultas"]) * 100
    df_conversao["Conversão de Exames (%)"] = (df_conversao["Exames"] / df_conversao["Consultas"]) * 100

    df_conversao.replace([float('inf'), float('-inf')], 0, inplace=True)
    df_conversao.reset_index(inplace=True)
    df_conversao.rename(columns={"index": "ANO"}, inplace=True)

    fig_conversao = px.line(df_conversao, x="ANO", 
                            y=["Conversão de Cirurgias (%)", "Conversão de Procedimentos (%)", "Conversão de Exames (%)"], 
                            markers=True, title="Taxa de Conversão Anual (%)")
    fig_conversao.update_layout(yaxis_tickformat=".2f")  
    st.plotly_chart(fig_conversao, use_container_width=True)
