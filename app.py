import streamlit as st
import pandas as pd
import os
from datetime import datetime
import plotly.graph_objects as go

# 1. Configuração da Página
st.set_page_config(page_title="Gestão Financeira VIP", layout="wide")

VENDAS_FILE = "vendas.xlsx"
DESPESAS_FILE = "despesas.xlsx"

def carregar_dados(file, colunas):
    if os.path.exists(file):
        try:
            df = pd.read_excel(file)
            df = df.astype(str).replace('nan', '')
            for col in colunas:
                if col not in df.columns: df[col] = ""
            return df
        except:
            return pd.DataFrame(columns=colunas)
    return pd.DataFrame(columns=colunas)

# --- BARRA LATERAL ---
st.sidebar.title("🧭 Menu")
pagina = st.sidebar.radio("Ir para:", ["💰 Lançamentos", "📉 Despesas", "📊 Resumo Geral"])

# --- PÁGINA 1: LANÇAMENTOS ---
if pagina == "💰 Lançamentos":
    st.header("💵 Lançamentos de Vendas")
    df_v = carregar_dados(VENDAS_FILE, ["Data", "Cliente", "Descrição", "Tipo", "Valor", "Pagamento", "Documento", "NF", "Recebido", "Comentário"])

    with st.expander("➕ Novo Lançamento", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            data_v = st.date_input("Data", datetime.now())
            cliente = st.text_input("Cliente")
            desc = st.radio("Descrição", ["Fisioterapia", "Pilates", "Outros"], horizontal=True)
        with col2:
            valor_v = st.number_input("Valor (R$)", min_value=0.0, format="%.2f")
            recebido = st.selectbox("Recebido?", ["Sim", "Não"])
            forma_p = st.selectbox("Pagamento", ["Pix", "Dinheiro", "Crédito"])

        if st.button("💾 Salvar Venda", type="primary", use_container_width=True):
            novo = pd.DataFrame([{"Data": data_v.strftime("%d/%m/%Y"), "Cliente": cliente, "Descrição": desc, "Valor": str(valor_v), "Recebido": recebido, "Pagamento": forma_p}])
            df_v = pd.concat([df_v, novo], ignore_index=True)
            df_v.to_excel(VENDAS_FILE, index=False)
            st.rerun()

    st.divider()
    st.subheader("📋 Histórico e Exclusão")
    if not df_v.empty:
        # Botão de Excluir
        idx_excluir = st.number_input("Digite o ID da linha para excluir:", min_value=0, max_value=len(df_v)-1, step=1)
        if st.button("🗑️ Excluir Linha Selecionada", type="secondary"):
            df_v = df_v.drop(idx_excluir).reset_index(drop=True)
            df_v.to_excel(VENDAS_FILE, index=False)
            st.success("Registro excluído!")
            st.rerun()
        st.dataframe(df_v, use_container_width=True)

# --- PÁGINA 2: DESPESAS ---
elif pagina == "📉 Despesas":
    st.header("💸 Controle de Despesas")
    df_d = carregar_dados(DESPESAS_FILE, ["Data", "Despesa", "Valor", "Tipo", "Pagamento", "Pago"])

    with st.expander("➕ Nova Despesa", expanded=True):
        c1, c2 = st.columns(2)
        with c1:
            data_d = st.date_input("Data", datetime.now())
            nome_d = st.text_input("Descrição")
        with c2:
            valor_d = st.number_input("Valor (R$)", min_value=0.0, format="%.2f")
            pago = st.selectbox("Pago?", ["Sim", "Não"])

        if st.button("💾 Salvar Despesa", type="primary", use_container_width=True):
            novo = pd.DataFrame([{"Data": data_d.strftime("%d/%m/%Y"), "Despesa": nome_d, "Valor": str(valor_d), "Pago": pago}])
            df_d = pd.concat([df_d, novo], ignore_index=True)
            df_d.to_excel(DESPESAS_FILE, index=False)
            st.rerun()

    st.divider()
    st.subheader("📋 Histórico e Exclusão")
    if not df_d.empty:
        idx_d = st.number_input("ID da despesa para excluir:", min_value=0, max_value=len(df_d)-1, step=1)
        if st.button("🗑️ Apagar Despesa"):
            df_d = df_d.drop(idx_d).reset_index(drop=True)
            df_d.to_excel(DESPESAS_FILE, index=False)
            st.rerun()
        st.dataframe(df_d, use_container_width=True)

# --- PÁGINA 3: RESUMO GERAL ---
elif pagina == "📊 Resumo Geral":
    st.header("📊 Resultado Mensal")
    df_v = carregar_dados(VENDAS_FILE, ["Data", "Valor", "Recebido"])
    df_d = carregar_dados(DESPESAS_FILE, ["Data", "Valor", "Pago"])

    if not df_v.empty or not df_d.empty:
        # Tratamento
        df_v['Data'] = pd.to_datetime(df_v['Data'], dayfirst=True, errors='coerce')
        df_d['Data'] = pd.to_datetime(df_d['Data'], dayfirst=True, errors='coerce')
        df_v['Valor'] = pd.to_numeric(df_v['Valor'], errors='coerce').fillna(0)
        df_d['Valor'] = pd.to_numeric(df_d['Valor'], errors='coerce').fillna(0)

        anos = sorted(list(set(df_v['Data'].dt.year.dropna()) | set(df_d['Data'].dt.year.dropna())), reverse=True)
        ano_sel = st.selectbox("Ano:", anos if anos else [datetime.now().year])

        # Agrupamento
        meses = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
        res_v = df_v[(df_v['Recebido'] == "Sim") & (df_v['Data'].dt.year == ano_sel)].groupby(df_v['Data'].dt.month)['Valor'].sum().reindex(range(1,13), fill_value=0)
        res_d = df_d[(df_d['Pago'] == "Sim") & (df_d['Data'].dt.year == ano_sel)].groupby(df_d['Data'].dt.month)['Valor'].sum().reindex(range(1,13), fill_value=0)

        # GRÁFICO COM PLOTLY (PARA MOSTRAR VALORES)
        fig = go.Figure()
        fig.add_trace(go.Bar(x=meses, y=res_v, name='Recebidos', marker_color='#2ecc71', text=res_v, textposition='auto'))
        fig.add_trace(go.Bar(x=meses, y=res_d, name='Pagos', marker_color='#e74c3c', text=res_d, textposition='auto'))

        fig.update_layout(barmode='group', title=f"Fluxo de Caixa {ano_sel}", xaxis_title="Mês", yaxis_title="Reais (R$)")
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.metric("Saldo Líquido Anual", f"R$ {(res_v.sum() - res_d.sum()):,.2f}")
    else:
        st.info("Sem dados para exibir.")
