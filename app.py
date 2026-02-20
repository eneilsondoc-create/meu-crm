import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import datetime
import os

# --- CONFIGURAÇÕES DA PÁGINA ---
st.set_page_config(page_title="Painel Financeiro", layout="wide")

# --- ESTILO CSS PARA MELHORAR O VISUAL ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

ARQUIVO_EXCEL = "gestao_financeira.xlsx"

# --- CARREGAMENTO DE DADOS ---
@st.cache_data
def carregar_dados():
    if os.path.exists(ARQUIVO_EXCEL):
        df = pd.read_excel(ARQUIVO_EXCEL)
        # Converte e limpa datas
        df['Data'] = pd.to_datetime(df['Data'], errors='coerce')
        df = df.dropna(subset=['Data'])
        # IMPORTANTE: Ordenar por data para o gráfico não ficar "vai e vem"
        df = df.sort_values('Data')
        return df
    return pd.DataFrame()

df_v = carregar_dados()

if not df_v.empty:
    # --- BARRA LATERAL (SIDEBAR) ---
    st.sidebar.image("https://cdn-icons-png.flaticon.com/512/5542/5542146.png", width=100)
    st.sidebar.title("Filtros do Painel")
    
    anos_disponiveis = sorted(df_v['Data'].dt.year.unique(), reverse=True)
    ano_sel = st.sidebar.selectbox("📅 Selecione o Ano", anos_disponiveis)
    
    # Filtro de mês opcional
    meses_nome = {1:'Jan', 2:'Fev', 3:'Mar', 4:'Abr', 5:'Mai', 6:'Jun', 
                  7:'Jul', 8:'Ago', 9:'Set', 10:'Out', 11:'Nov', 12:'Dez'}
    mes_sel = st.sidebar.multiselect("📆 Filtrar Meses", 
                                    options=list(meses_nome.keys()), 
                                    format_func=lambda x: meses_nome[x],
                                    default=list(meses_nome.keys()))

    # --- FILTRAGEM ---
    df_filtrado = df_v[(df_v['Data'].dt.year == ano_sel) & (df_v['Data'].dt.month.isin(mes_sel))]

    # --- CORPO PRINCIPAL ---
    st.title("📊 Painel Financeiro")
    
    # Métricas de Resumo
    col1, col2, col3 = st.columns(3)
    total_valor = df_filtrado['Valor'].sum() if 'Valor' in df_filtrado.columns else 0
    qtd_transacoes = len(df_filtrado)
    
    col1.metric("Total no Período", f"R$ {total_valor:,.2f}")
    col2.metric("Transações", qtd_transacoes)
    col3.metric("Ano Selecionado", ano_sel)

    # --- GRÁFICO ---
    st.subheader("📈 Evolução Financeira")
    
    if not df_filtrado.empty:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_filtrado['Data'], 
            y=df_filtrado['Valor'],
            mode='lines+markers',
            line=dict(color='#0083B8', width=3),
            marker=dict(size=8),
            hovertemplate="Data: %{x}<br>Valor: R$ %{y:.2f}<extra></extra>"
        ))
        
        fig.update_layout(
            margin=dict(l=20, r=20, t=20, b=20),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=True, gridcolor='LightGray'),
            yaxis=dict(showgrid=True, gridcolor='LightGray'),
            height=450
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Tabela de dados
        with st.expander("📄 Ver dados detalhados"):
            st.dataframe(df_filtrado, use_container_width=True)
    else:
        st.warning("Nenhum dado encontrado para os filtros selecionados.")
else:
    st.error("Não foi possível carregar os dados. Verifique o arquivo Excel.")
