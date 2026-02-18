import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. Configuração da Página
st.set_page_config(page_title="Gestão Financeira VIP", layout="wide")

VENDAS_FILE = "vendas.xlsx"
DESPESAS_FILE = "despesas.xlsx"

# Função robusta para carregar dados e evitar erros de float/NaN


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


# --- BARRA LATERAL (NAVEGAÇÃO) ---
st.sidebar.title("🧭 Menu Principal")
pagina = st.sidebar.radio(
    "Ir para:", ["💰 Lançamentos", "📉 Despesas", "📊 Resumo Geral"])

# --- PÁGINA 1: LANÇAMENTOS ---
if pagina == "💰 Lançamentos":
    st.header("💵 Novo Lançamento de Venda")
    df_v = carregar_dados(VENDAS_FILE, ["Data", "Cliente", "Descrição", "Tipo",
                          "Valor", "Pagamento", "Documento", "NF", "Recebido", "Comentário"])

    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
            data_v = st.date_input("Data da Venda", datetime.now())
            cliente = st.text_input("Nome do Cliente")
            desc = st.radio(
                "Descrição:", ["Fisioterapia", "Pilates", "Outros"], horizontal=True)
            tipo = st.radio("Tipo:", ["Serviço", "Comercial"], horizontal=True)
        with col2:
            valor_v = st.number_input(
                "Valor (R$)", min_value=0.0, format="%.2f")
            forma_p = st.radio(
                "Pagamento:", ["Pix", "Dinheiro", "Crédito"], horizontal=True)
            doc = st.radio("Pessoa:", ["PF", "PJ"], horizontal=True)
            nf = st.selectbox("Nota Fiscal?", ["Não", "Sim"])
            recebido = st.selectbox("Recebido?", ["Sim", "Não"])

        coment_v = st.text_area("Comentário")

        if st.button("💾 Salvar Venda", type="primary", use_container_width=True):
            novo_v = pd.DataFrame([{
                "Data": data_v.strftime("%d/%m/%Y"), "Cliente": cliente, "Descrição": desc,
                "Tipo": tipo, "Valor": str(valor_v), "Pagamento": forma_p,
                "Documento": doc, "NF": nf, "Recebido": recebido, "Comentário": coment_v
            }])
            df_v = pd.concat([df_v, novo_v], ignore_index=True)
            df_v.to_excel(VENDAS_FILE, index=False)
            st.success("Venda registrada!")
            st.rerun()

    st.subheader("📋 Últimos Lançamentos")
    st.dataframe(df_v.tail(10), use_container_width=True)

# --- PÁGINA 2: DESPESAS ---
elif pagina == "📉 Despesas":
    st.header("💸 Registro de Despesas")
    df_d = carregar_dados(DESPESAS_FILE, [
                          "Data", "Despesa", "Valor", "Tipo", "Pagamento", "Parcelas", "NF", "Pago", "Comentário"])

    with st.container(border=True):
        c1, c2 = st.columns(2)
        with c1:
            data_d = st.date_input("Data da Despesa", datetime.now())
            nome_d = st.text_input("Descrição da Despesa")
            tipo_d = st.radio("Tipo de Despesa:", [
                              "Fixa", "Variável", "Impostos", "Pessoal"], horizontal=True)
        with c2:
            valor_d = st.number_input(
                "Valor da Despesa (R$)", min_value=0.0, format="%.2f")
            forma_d = st.radio(
                "Forma:", ["Pix", "Dinheiro", "Boleto", "Cartão"], horizontal=True)
            parcelas = st.number_input("Parcelas", min_value=1, value=1)
            nf_d = st.selectbox("Nota Fiscal?", ["Sim", "Não"], key="d_nf")
            pago = st.selectbox("Pago?", ["Sim", "Não"], key="d_pago")

        coment_d = st.text_area("Comentário Despesa")

        if st.button("💾 Salvar Despesa", type="primary", use_container_width=True):
            nova_d = pd.DataFrame([{
                "Data": data_d.strftime("%d/%m/%Y"), "Despesa": nome_d, "Valor": str(valor_d),
                "Tipo": tipo_d, "Pagamento": forma_d, "Parcelas": str(parcelas),
                "NF": nf_d, "Pago": pago, "Comentário": coment_d
            }])
            df_d = pd.concat([df_d, nova_d], ignore_index=True)
            df_d.to_excel(DESPESAS_FILE, index=False)
            st.success("Despesa registrada!")
            st.rerun()

# --- PÁGINA 3: RESUMO GERAL COM GRÁFICO DE DUAS BARRAS ---
elif pagina == "📊 Resumo Geral":
    st.header("📊 Análise Mensal Comparativa")

    df_v = carregar_dados(VENDAS_FILE, ["Data", "Valor", "Recebido"])
    df_d = carregar_dados(DESPESAS_FILE, ["Data", "Valor", "Pago"])

    if not df_v.empty or not df_d.empty:
        # Conversão de dados para cálculo
        df_v['Data'] = pd.to_datetime(
            df_v['Data'], dayfirst=True, errors='coerce')
        df_d['Data'] = pd.to_datetime(
            df_d['Data'], dayfirst=True, errors='coerce')
        df_v['Valor'] = pd.to_numeric(df_v['Valor'], errors='coerce').fillna(0)
        df_d['Valor'] = pd.to_numeric(df_d['Valor'], errors='coerce').fillna(0)

        # Filtro de Ano
        anos = sorted(list(set(df_v['Data'].dt.year.dropna()) | set(
            df_d['Data'].dt.year.dropna())), reverse=True)
        if not anos:
            anos = [datetime.now().year]
        ano_sel = st.selectbox("Selecione o Ano:", anos)

        # Filtrar o que está pago/recebido no ano escolhido
        v_ano = df_v[(df_v['Recebido'] == "Sim") &
                     (df_v['Data'].dt.year == ano_sel)]
        d_ano = df_d[(df_d['Pago'] == "Sim") & (
            df_d['Data'].dt.year == ano_sel)]

        # Agrupar por mês (1-12)
        meses_nomes = ["Jan", "Fev", "Mar", "Abr", "Mai",
                       "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
        res_v = v_ano.groupby(v_ano['Data'].dt.month)[
            'Valor'].sum().reindex(range(1, 13), fill_value=0)
        res_d = d_ano.groupby(d_ano['Data'].dt.month)[
            'Valor'].sum().reindex(range(1, 13), fill_value=0)

        # Criar DataFrame para o gráfico de 2 barras
        df_chart = pd.DataFrame({
            "Mês": meses_nomes,
            "Lançamentos Pagos": res_v.values,
            "Despesas Pagas": res_d.values
        }).set_index("Mês")

        # Exibir Métricas
        c1, c2, c3 = st.columns(3)
        c1.metric("Receita (Ano)", f"R$ {res_v.sum():,.2f}")
        c2.metric("Despesas (Ano)",
                  f"R$ {res_d.sum():,.2f}", delta_color="inverse")
        c3.metric("Saldo", f"R$ {(res_v.sum() - res_d.sum()):,.2f}")

        st.divider()
        st.subheader(f"📊 Fluxo de Caixa {ano_sel} (Lado a Lado)")
        # Gráfico com cores: Verde para Receita, Vermelho para Despesa
        st.bar_chart(df_chart, color=["#2ecc71", "#e74c3c"])
    else:
        st.info("Aguardando dados marcados como 'Sim' em Recebido/Pago.")
