import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Tenta importar o Plotly para o gráfico com valores
try:
    import plotly.graph_objects as go
except ModuleNotFoundError:
    st.error("Erro: A biblioteca 'plotly' não está instalada. Rode 'pip install plotly' no seu terminal.")
    st.stop()

# Configuração da Página
st.set_page_config(page_title="Gestão Financeira", layout="wide")

VENDAS_FILE = "vendas.xlsx"
DESPESAS_FILE = "despesas.xlsx"


def carregar_dados(file, colunas):
    if os.path.exists(file):
        try:
            df = pd.read_excel(file)
            df = df.astype(str).replace('nan', '')
            for col in colunas:
                if col not in df.columns:
                    df[col] = ""
            return df
        except:
            return pd.DataFrame(columns=colunas)
    return pd.DataFrame(columns=colunas)


# --- NAVEGAÇÃO LATERAL ---
st.sidebar.title("🧭 Menu Principal")
pagina = st.sidebar.radio(
    "Ir para:", ["💰 Lançamentos", "📉 Despesas", "📊 Resumo Geral"])

# --- PÁGINA 1: LANÇAMENTOS ---
if pagina == "💰 Lançamentos":
    st.header("💵 Lançamentos de Vendas")
    df_v = carregar_dados(
        VENDAS_FILE, ["Data", "Cliente", "Descrição", "Valor", "Recebido"])

    with st.expander("➕ Nova Venda", expanded=True):
        c1, c2 = st.columns(2)
        with c1:
            data_v = st.date_input("Data", datetime.now())
            cli_v = st.text_input("Cliente")
        with c2:
            val_v = st.number_input("Valor (R$)", min_value=0.0, format="%.2f")
            rec_v = st.selectbox("Recebido?", ["Sim", "Não"])

        if st.button("💾 Salvar Venda", type="primary", use_container_width=True):
            novo = pd.DataFrame([{"Data": data_v.strftime(
                "%d/%m/%Y"), "Cliente": cli_v, "Valor": str(val_v), "Recebido": rec_v}])
            df_v = pd.concat([df_v, novo], ignore_index=True)
            df_v.to_excel(VENDAS_FILE, index=False)
            st.success("Venda salva!")
            st.rerun()

    st.divider()
    if not df_v.empty:
        st.subheader("🗑️ Excluir Registro")
        idx_v = st.number_input("ID da linha para apagar:", min_value=0, max_value=len(
            df_v)-1, step=1, key="del_v")
        if st.button("❌ Apagar Selecionado", key="btn_v"):
            df_v = df_v.drop(idx_v).reset_index(drop=True)
            df_v.to_excel(VENDAS_FILE, index=False)
            st.rerun()
        st.dataframe(df_v, use_container_width=True)

# --- PÁGINA 2: DESPESAS ---
elif pagina == "📉 Despesas":
    st.header("💸 Controle de Despesas")
    df_d = carregar_dados(DESPESAS_FILE, ["Data", "Despesa", "Valor", "Pago"])

    with st.expander("➕ Nova Despesa", expanded=True):
        c1, c2 = st.columns(2)
        with c1:
            data_d = st.date_input("Data", datetime.now(), key="dt_d")
            nome_d = st.text_input("Descrição")
        with c2:
            val_d = st.number_input(
                "Valor (R$)", min_value=0.0, format="%.2f", key="v_d")
            pago_d = st.selectbox("Pago?", ["Sim", "Não"], key="p_d")

    if st.button("💾 Salvar Despesa", type="primary", use_container_width=True):
        novo_d = pd.DataFrame([{"Data": data_d.strftime(
            "%d/%m/%Y"), "Despesa": nome_d, "Valor": str(val_d), "Pago": pago_d}])
        df_d = pd.concat([df_d, novo_d], ignore_index=True)
        df_d.to_excel(DESPESAS_FILE, index=False)
        st.success("Despesa salva!")
        st.rerun()

    st.divider()
    if not df_d.empty:
        st.subheader("🗑️ Excluir Despesa")
        idx_d = st.number_input("ID da linha para apagar:", min_value=0, max_value=len(
            df_d)-1, step=1, key="del_d")
        if st.button("❌ Apagar Selecionada", key="btn_d"):
            df_d = df_d.drop(idx_d).reset_index(drop=True)
            df_d.to_excel(DESPESAS_FILE, index=False)
            st.rerun()
        st.dataframe(df_d, use_container_width=True)

# --- PÁGINA 3: RESUMO GERAL ---
elif pagina == "📊 Resumo Geral":
    st.header("📊 Resumo Financeiro")
    df_v = carregar_dados(VENDAS_FILE, ["Data", "Valor", "Recebido"])
    df_d = carregar_dados(DESPESAS_FILE, ["Data", "Valor", "Pago"])

    if not df_v.empty or not df_d.empty:
        df_v['Data'] = pd.to_datetime(
            df_v['Data'], dayfirst=True, errors='coerce')
        df_d['Data'] = pd.to_datetime(
            df_d['Data'], dayfirst=True, errors='coerce')
        df_v['Valor'] = pd.to_numeric(df_v['Valor'], errors='coerce').fillna(0)
        df_d['Valor'] = pd.to_numeric(df_d['Valor'], errors='coerce').fillna(0)

        anos = sorted(list(set(df_v['Data'].dt.year.dropna()) | set(
            df_d['Data'].dt.year.dropna())), reverse=True)
        ano_sel = st.selectbox("Ano:", anos if anos else [datetime.now().year])

        meses = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
                 "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
        res_v = df_v[(df_v['Recebido'] == "Sim") & (df_v['Data'].dt.year == ano_sel)].groupby(
            df_v['Data'].dt.month)['Valor'].sum().reindex(range(1, 13), fill_value=0)
        res_d = df_d[(df_d['Pago'] == "Sim") & (df_d['Data'].dt.year == ano_sel)].groupby(
            df_d['Data'].dt.month)['Valor'].sum().reindex(range(1, 13), fill_value=0)

        # Gráfico de duas barras com valores visíveis
        fig = go.Figure()
        fig.add_trace(go.Bar(x=meses, y=res_v, name='Recebido',
                      marker_color='#2ecc71', text=res_v, textposition='auto'))
        fig.add_trace(go.Bar(x=meses, y=res_d, name='Pago',
                      marker_color='#e74c3c', text=res_d, textposition='auto'))
        fig.update_layout(barmode='group', title=f"Desempenho {ano_sel}")
        st.plotly_chart(fig, use_container_width=True)

        st.metric("Saldo Anual", f"R$ {(res_v.sum() - res_d.sum()):,.2f}")
    else:
        st.info("Lance dados e marque como 'Sim' para gerar o resumo.")
