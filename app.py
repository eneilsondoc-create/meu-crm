import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import datetime
import os

# --- CONFIGURAÇÕES DA PÁGINA ---
st.set_page_config(page_title="Painel Financeiro", layout="wide")
st.title("📊 Painel Financeiro")

# Nome exato do seu arquivo no GitHub
ARQUIVO_EXCEL = "gestao_financeira.xlsx" 

# --- CARREGAMENTO DE DADOS ---
@st.cache_data
def carregar_dados():
    if os.path.exists(ARQUIVO_EXCEL):
        df = pd.read_excel(ARQUIVO_EXCEL)
        
        # CORREÇÃO DO ERRO DE DATA: Força o formato datetime e remove linhas vazias
        df['Data'] = pd.to_datetime(df['Data'], errors='coerce')
        df = df.dropna(subset=['Data'])
        
        # Ordena por data para o gráfico não ficar estranho
        df = df.sort_values(by='Data')
        return df
    else:
        st.error(f"Arquivo {ARQUIVO_EXCEL} não encontrado!")
        return pd.DataFrame()

df_v = carregar_dados()

if not df_v.empty:
    # --- FILTRO DE ANO ---
    anos_disponiveis = sorted(df_v['Data'].dt.year.unique(), reverse=True)
    ano_sel = st.selectbox("📅 Selecione o Ano", anos_disponiveis, index=0)

    # --- FILTRAGEM ---
    df_filtrado = df_v[df_v['Data'].dt.year == ano_sel]

    # --- GRÁFICO ---
    if not df_filtrado.empty:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_filtrado['Data'], 
            y=df_filtrado['Valor'], # Certifique-se que a coluna se chama 'Valor'
            mode='lines+markers',
            name='Evolução'
        ))
        
        fig.update_layout(template="plotly_white", height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # Mostra a tabela logo abaixo
        st.write("### Dados Detalhados", df_filtrado)
    else:
        st.warning(f"Não há dados para o ano de {ano_sel}.")
else:
    st.info("Aguardando carregamento dos dados...")
