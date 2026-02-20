import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import datetime
import time
import os

# --- CONFIGURAÇÕES ---
st.set_page_config(page_title="Gestão Financeira Completa", layout="wide")
ARQUIVO_EXCEL = "gestao_financeira.xlsx"

# --- DEFINIÇÃO DAS COLUNAS (O PADRÃO DO SEU SISTEMA) ---
COLUNAS_VENDAS = ["ID", "Data", "Cliente Nome", "CPF_CNPJ", "Descrição", "Valor",
                  "Categoria", "Pagamento", "Tipo Cliente", "NF", "Status", "Comentário"]
COLUNAS_DESPESAS = ["ID", "Data", "Descrição", "Valor",
                    "Tipo Despesa", "Pagamento", "NF", "Status", "Comentário"]

# --- FUNÇÕES DE DADOS ---


def carregar_dados():
    if os.path.exists(ARQUIVO_EXCEL):
        try:
            v = pd.read_excel(ARQUIVO_EXCEL, sheet_name="Vendas")
            d = pd.read_excel(ARQUIVO_EXCEL, sheet_name="Despesas")

            # Garante que as colunas que podem estar faltando no Excel sejam criadas
            for col in COLUNAS_VENDAS:
                if col not in v.columns:
                    v[col] = ""
            for col in COLUNAS_DESPESAS:
                if col not in d.columns:
                    d[col] = ""

            # Reorganiza na ordem correta
            v = v[COLUNAS_VENDAS]
            d = d[COLUNAS_DESPESAS]

            # Conversões de segurança
            v['Data'] = pd.to_datetime(v['Data'], errors='coerce')
            d['Data'] = pd.to_datetime(d['Data'], errors='coerce')
            v['Valor'] = pd.to_numeric(v['Valor'], errors='coerce').fillna(0)
            d['Valor'] = pd.to_numeric(d['Valor'], errors='coerce').fillna(0)
            v['ID'] = v['ID'].astype(str)
            d['ID'] = d['ID'].astype(str)

            return v, d
        except Exception as e:
            st.error(f"Erro ao ler colunas: {e}")
            return criar_vazio()
    return criar_vazio()


def criar_vazio():
    v = pd.DataFrame(columns=COLUNAS_VENDAS)
    d = pd.DataFrame(columns=COLUNAS_DESPESAS)
    return v, d


def salvar_para_excel():
    with pd.ExcelWriter(ARQUIVO_EXCEL) as writer:
        st.session_state.vendas.to_excel(
            writer, sheet_name="Vendas", index=False)
        st.session_state.despesas.to_excel(
            writer, sheet_name="Despesas", index=False)


def formatar_data_br(df):
    df_copy = df.copy()
    if not df_copy.empty:
        df_copy['Data'] = df_copy['Data'].dt.strftime('%d/%m/%Y')
    return df_copy


# --- INICIALIZAÇÃO ---
if 'vendas' not in st.session_state:
    v, d = carregar_dados()
    st.session_state.vendas = v
    st.session_state.despesas = d

# --- MENU LATERAL ---
st.sidebar.title("📌 Menu")
menu = st.sidebar.radio(
    "Navegação", ["📊 Visão Geral", "💰 Vendas", "💸 Despesas"])

if st.sidebar.button("🔄 Sincronizar Excel"):
    v, d = carregar_dados()
    st.session_state.vendas = v
    st.session_state.despesas = d
    st.rerun()

# --- 1. VISÃO GERAL ---
if menu == "📊 Visão Geral":
    st.title("📊 Painel Financeiro")
    ano_atual = datetime.datetime.now().year
    anos = [2024, 2025, 2026]
    ano_sel = st.selectbox("📅 Selecione o Ano", anos, index=anos.index(
        ano_atual) if ano_atual in anos else 0)

    df_v = st.session_state.vendas.copy()
    df_d = st.session_state.despesas.copy()
    df_v = df_v[df_v['Data'].dt.year == ano_sel]
    df_d = df_d[df_d['Data'].dt.year == ano_sel]

    meses_br = ["Jan", "Fev", "Mar", "Abr", "Mai",
                "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
    resumo = pd.DataFrame({"M_Num": range(1, 13), "Mês": meses_br})
    resumo["Vendas"] = resumo["M_Num"].map(df_v.groupby(
        df_v['Data'].dt.month)['Valor'].sum()).fillna(0)
    resumo["Despesas"] = resumo["M_Num"].map(df_d.groupby(
        df_d['Data'].dt.month)['Valor'].sum()).fillna(0)

    fig = go.Figure()
    fig.add_trace(go.Bar(x=resumo["Mês"], y=resumo["Vendas"],
                  name='Faturamento', marker_color='#2ecc71'))
    fig.add_trace(go.Bar(
        x=resumo["Mês"], y=resumo["Despesas"], name='Gastos', marker_color='#e74c3c'))
    st.plotly_chart(fig, use_container_width=True)

# --- 2. VENDAS (TODAS AS COLUNAS) ---
elif menu == "💰 Vendas":
    st.title("💰 Gestão de Vendas")
    st.dataframe(formatar_data_br(st.session_state.vendas),
                 use_container_width=True)

    with st.expander("➕ Novo Lançamento Completo"):
        with st.form("f_v_full", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                dt = st.date_input("Data", format="DD/MM/YYYY", key="nv_dt")
                nm = st.text_input("Cliente Nome")
                cp = st.text_input("CPF/CNPJ")
                ds = st.text_input("Descrição")
                vl = st.number_input("Valor", min_value=0.0)
            with c2:
                ct = st.selectbox(
                    "Categoria", ["Serviço", "Comércio"], key="nv_cat")
                pg = st.selectbox(
                    "Pagamento", ["PIX", "Dinheiro", "Crédito", "Débito"], key="nv_pag")
                tp = st.selectbox("Tipo Cliente", ["PF", "PJ"], key="nv_tip")
                nf = st.selectbox("NF", ["Sim", "Não"], key="nv_nf")
                stt = st.selectbox("Status", ["Pago", "Pendente"], key="nv_st")
            ob = st.text_area("Comentário")
            if st.form_submit_button("Salvar Registro"):
                nova = {"ID": str(int(time.time())), "Data": pd.to_datetime(dt), "Cliente Nome": nm, "CPF_CNPJ": cp, "Descrição": ds,
                        "Valor": vl, "Categoria": ct, "Pagamento": pg, "Tipo Cliente": tp, "NF": nf, "Status": stt, "Comentário": ob}
                st.session_state.vendas = pd.concat(
                    [st.session_state.vendas, pd.DataFrame([nova])], ignore_index=True)
                salvar_para_excel()
                st.rerun()

    st.divider()
    id_v = st.text_input("ID para EDITAR TUDO ou EXCLUIR")
    if id_v:
        idx = st.session_state.vendas.index[st.session_state.vendas['ID'] == id_v].tolist(
        )
        if idx:
            i = idx[0]
            r = st.session_state.vendas.iloc[i]
            with st.form("ed_v_full"):
                st.warning(f"Editando Registro: {id_v}")
                c1, c2 = st.columns(2)
                with c1:
                    e_dt = st.date_input("Data", value=pd.to_datetime(
                        r['Data']), format="DD/MM/YYYY")
                    e_nm = st.text_input(
                        "Cliente Nome", value=r['Cliente Nome'])
                    e_cp = st.text_input("CPF/CNPJ", value=r['CPF_CNPJ'])
                    e_ds = st.text_input("Descrição", value=r['Descrição'])
                    e_vl = st.number_input("Valor", value=float(r['Valor']))
                with c2:
                    e_ct = st.selectbox("Categoria", [
                                        "Serviço", "Comércio"], index=0 if r['Categoria'] == "Serviço" else 1)
                    e_pg = st.selectbox(
                        "Pagamento", ["PIX", "Dinheiro", "Crédito", "Débito"], index=0)
                    e_tp = st.selectbox(
                        "Tipo Cliente", ["PF", "PJ"], index=0 if r['Tipo Cliente'] == "PF" else 1)
                    e_nf = st.selectbox(
                        "NF", ["Sim", "Não"], index=0 if r['NF'] == "Sim" else 1)
                    e_st = st.selectbox(
                        "Status", ["Pago", "Pendente"], index=0 if r['Status'] == "Pago" else 1)
                e_ob = st.text_area("Comentário", value=str(r['Comentário']))

                b1, b2 = st.columns(2)
                if b1.form_submit_button("✅ Atualizar"):
                    st.session_state.vendas.iloc[i] = [id_v, pd.to_datetime(
                        e_dt), e_nm, e_cp, e_ds, e_vl, e_ct, e_pg, e_tp, e_nf, e_st, e_ob]
                    salvar_para_excel()
                    st.success("Venda atualizada!")
                    st.rerun()
                if b2.form_submit_button("🗑️ Excluir"):
                    st.session_state.vendas = st.session_state.vendas.drop(
                        i).reset_index(drop=True)
                    salvar_para_excel()
                    st.rerun()

# --- 3. DESPESAS (TODAS AS COLUNAS) ---
elif menu == "💸 Despesas":
    st.title("💸 Gestão de Despesas")
    st.dataframe(formatar_data_br(st.session_state.despesas),
                 use_container_width=True)

    with st.expander("➕ Nova Despesa"):
        with st.form("f_d_full", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                dt_d = st.date_input("Data", format="DD/MM/YYYY")
                ds_d = st.text_input("Descrição")
                vl_d = st.number_input("Valor", min_value=0.0)
            with c2:
                tp_d = st.selectbox("Tipo Despesa", ["Fixa", "Variável"])
                pg_d = st.selectbox("Pagamento", ["PIX", "Boleto", "Cartão"])
                nf_d = st.selectbox("NF", ["Sim", "Não"])
                st_d = st.selectbox("Status", ["Pago", "A Pagar"])
            ob_d = st.text_area("Comentário")
            if st.form_submit_button("Salvar Despesa"):
                nova_d = {"ID": str(int(time.time())), "Data": pd.to_datetime(dt_d), "Descrição": ds_d, "Valor": vl_d,
                          "Tipo Despesa": tp_d, "Pagamento": pg_d, "NF": nf_d, "Status": st_d, "Comentário": ob_d}
                st.session_state.despesas = pd.concat(
                    [st.session_state.despesas, pd.DataFrame([nova_d])], ignore_index=True)
                salvar_para_excel()
                st.rerun()

    st.divider()
    id_d = st.text_input("ID para EDITAR/EXCLUIR Despesa")
    if id_d:
        idx_d = st.session_state.despesas.index[st.session_state.despesas['ID'] == id_d].tolist(
        )
        if idx_d:
            i_d = idx_d[0]
            r_d = st.session_state.despesas.iloc[i_d]
            with st.form("ed_d_full"):
                st.warning(f"Editando Despesa: {id_d}")
                c1, c2 = st.columns(2)
                with c1:
                    e_dt = st.date_input("Data", value=pd.to_datetime(
                        r_d['Data']), format="DD/MM/YYYY")
                    e_ds = st.text_input("Descrição", value=r_d['Descrição'])
                    e_vl = st.number_input("Valor", value=float(r_d['Valor']))
                with c2:
                    e_tp = st.selectbox(
                        "Tipo", ["Fixa", "Variável"], index=0 if r_d['Tipo Despesa'] == "Fixa" else 1)
                    e_pg = st.selectbox(
                        "Pagamento", ["PIX", "Boleto", "Cartão"], index=0)
                    e_nf = st.selectbox(
                        "NF", ["Sim", "Não"], index=0 if r_d['NF'] == "Sim" else 1)
                    e_st = st.selectbox(
                        "Status", ["Pago", "A Pagar"], index=0 if r_d['Status'] == "Pago" else 1)
                e_ob = st.text_area("Comentário", value=str(r_d['Comentário']))

                cb1, cb2 = st.columns(2)
                if cb1.form_submit_button("✅ Atualizar"):
                    st.session_state.despesas.iloc[i_d] = [id_d, pd.to_datetime(
                        e_dt), e_ds, e_vl, e_tp, e_pg, e_nf, e_st, e_ob]
                    salvar_para_excel()
                    st.success("Atualizado!")
                    st.rerun()
                if cb2.form_submit_button("🗑️ Excluir"):
                    st.session_state.despesas = st.session_state.despesas.drop(
                        i_d).reset_index(drop=True)
                    salvar_para_excel()
                    st.rerun()
