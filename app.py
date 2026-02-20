import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import datetime
import time
import os

# --- CONFIGURAÇÕES DA PÁGINA ---
st.set_page_config(page_title="Painel Financeiro", layout="wide")
st.title("📊 Painel Financeiro")

# Nome do seu arquivo Excel (certifique-se de que ele esteja no GitHub)
ARQUIVO_EXCEL = "gestao_financeira.xlsx" 

# --- CARREGAMENTO DE DADOS ---
@st.cache_data
def carregar_dados():
    if os.path.exists(ARQUIVO_EXCEL):
        df = pd.read_excel(ARQUIVO_EXCEL)
        
        # CORREÇÃO DO ERRO: Força a coluna 'Data' a ser do tipo datetime
        # O 'errors=coerce' transforma datas inválidas em "Nat" (vazio) para não travar o app
        df['Data'] = pd.to_datetime(df['Data'], errors='coerce')
        
        # Remove linhas onde a data ficou vazia (opcional, mas recomendado)
        df = df.dropna(subset=['Data'])
        return df
    else:
        st.error(f"Arquivo {ARQUIVO_EXCEL} não encontrado no repositório!")
        return pd.DataFrame()

df_v = carregar_dados()

if not df_v.empty:
    # --- FILTRO DE ANO ---
    anos_disponiveis = sorted(df_v['Data'].dt.year.unique(), reverse=True)
    
    # Se a lista de anos estiver vazia, define o ano atual
    ano_padrao = anos_disponiveis[0] if anos_disponiveis else datetime.datetime.now().year
    
    ano_sel = st.selectbox("📅 Selecione o Ano", anos_disponiveis, index=0)

    # --- FILTRAGEM DOS DADOS (Onde dava o erro) ---
    df_v_filtrado = df_v[df_v['Data'].dt.year == ano_sel]

    # --- EXEMPLO DE GRÁFICO (PLOTLY) ---
    # Substitua 'Valor' e 'Data' pelos nomes reais das suas colunas
    if not df_v_filtrado.empty:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_v_filtrado['Data'], 
            y=df_v_filtrado['Valor'] if 'Valor' in df_v_filtrado.columns else [0],
            mode='lines+markers',
            name='Vendas'
        ))
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning(f"Não há dados para o ano de {ano_sel}.")
else:
    st.info("Aguardando carregamento dos dados...")

