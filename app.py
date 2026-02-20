import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import datetime
import os

# --- CONFIGURAÇÕES DA PÁGINA ---
st.set_page_config(page_title="Painel Financeiro", layout="wide")

# Nome do arquivo no seu GitHub
ARQUIVO_EXCEL = "gestao_financeira.xlsx"

# --- FUNÇÃO DE CARREGAMENTO ---
@st.cache_data
def carregar_dados():
    if os.path.exists(ARQUIVO_EXCEL):
        df = pd.read_excel(ARQUIVO_EXCEL)
        # 1. Converte coluna Data e remove erros (NaT)
        df['Data'] = pd.to_datetime(df['Data'], errors='coerce')
        df = df.dropna(subset=['Data'])
        # 2. ORDENAÇÃO: Crucial para o gráfico não ficar estranho
        df = df.sort_values(by='Data')
        return df
    return pd.DataFrame()

df_v = carregar_dados()

if not df_v.empty:
    # --- BARRA LATERAL (FILTROS) ---
    st.sidebar.header("📌 Filtros")
    
    # Seleção de Ano
    anos = sorted(df_v['Data'].dt.year.unique(), reverse=True)
    ano_sel = st.sidebar.selectbox("Selecione o Ano", anos)
    
    # Seleção de Mês
    meses_disponiveis = sorted(df_v[df_v['Data'].dt.year == ano_sel]['Data'].dt.month.unique())
    meses_nome = {1:'Jan', 2:'Fev', 3:'Mar', 4:'Abr', 5:'Mai', 6:'Jun', 
                  7:'Jul', 8:'Ago', 9:'Set', 10:'Out', 11:'Nov', 12:'Dez'}
    
    mes_sel = st.sidebar.multiselect(
        "Selecione os Meses", 
        options=meses_disponiveis,
        format_func=lambda x: meses_nome[x],
        default=meses_disponiveis
    )

    # --- FILTRAGEM DOS DADOS ---
    df_filtrado = df_v[(df_v['Data'].dt.year == ano_sel) & (df_v['Data'].dt.month.isin(mes_sel))]

    # --- CORPO DO PAINEL ---
    st.title("📊 Painel Financeiro")
    
    # Métricas principais em colunas
    m1, m2, m3 = st.columns(3)
    total_periodo = df_filtrado['Valor'].sum() if 'Valor' in df_filtrado.columns else 0
    m1.metric("Receita Total", f"R$ {total_periodo:,.2f}")
    m2.metric("Qtd. Registros", len(df_filtrado))
    m3.metric("Ano", ano_sel)

    # --- GRÁFICO DE EVOLUÇÃO ---
    st.subheader("📈 Evolução Financeira")
    if not df_filtrado.empty:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_filtrado['Data'], 
            y=df_filtrado['Valor'],
            mode='lines+markers',
            line=dict(color='#00d4ff', width=3),
            marker=dict(size=7),
            name="Valor"
        ))
        fig.update_layout(
            template="plotly_dark",
            xaxis_title="Data",
            yaxis_title="Valor (R$)",
            height=400,
            margin=dict(l=20, r=20, t=20, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Nenhum dado para os filtros aplicados.")

    # --- ÁREA DE EDIÇÃO (CORREÇÃO DO SUBMIT BUTTON) ---
    st.divider()
    st.subheader("📝 Gerenciar Registros")
    
    with st.expander("Ver Tabela e Editar"):
        # Mostra a tabela
        st.dataframe(df_filtrado, use_container_width=True)
        
        # Exemplo de formulário corrigido (Evita o erro de "Missing Submit Button")
        with st.form("form_edicao"):
            st.write("Para editar um registro, use o formulário abaixo:")
            # Adicione aqui seus inputs de edição (ex: st.text_input...)
            
            # TODO O FORMULÁRIO PRECISA DE UM BOTÃO DE SUBMIT
            submit = st.form_submit_button("Salvar Alterações")
            if submit:
                st.info("Funcionalidade de salvamento em desenvolvimento.")

else:
    st.error("O arquivo 'gestao_financeira.xlsx' não foi carregado corretamente.")
  
