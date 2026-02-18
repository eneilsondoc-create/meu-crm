import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. Configuração inicial
st.set_page_config(page_title="CRM & Agenda Master", layout="wide")

CLIENTES_FILE = "clientes.xlsx"
AGENDA_FILE = "agenda.xlsx"

# Função para carregar dados tratando erros de tipo (Float vs Str)


def carregar_dados(file, colunas):
    if os.path.exists(file):
        try:
            df = pd.read_excel(file)
            # Converte tudo para string para evitar erro de 'float' em células vazias
            df = df.astype(str).replace('nan', '')
            for col in colunas:
                if col not in df.columns:
                    df[col] = ""
            return df
        except:
            return pd.DataFrame(columns=colunas)
    return pd.DataFrame(columns=colunas)


# --- INTERFACE ---
st.title("🚀 Sistema CRM & Agenda")

aba1, aba2 = st.tabs(["👥 Gerenciar Clientes", "📅 Agenda Semanal"])

# --- ABA 1: CLIENTES ---
with aba1:
    st.subheader("📝 Cadastro de Clientes")
    
    # Em vez de colunas muito apertadas, usamos campos simples
    # No celular, o endereço aparecerá logo após o CPF
    nome = st.text_input("Nome Completo")
    cpf = st.text_input("CPF (Somente números)")
    
    # Campo de endereço com área de texto (melhor para celular)
    endereco = st.text_area("Endereço Completo", help="Rua, Número, Bairro e Cidade")
    
    telefone = st.text_input("Telefone/WhatsApp")

    # Botões grandes para facilitar o toque com o dedo
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("💾 Salvar Cliente", type="primary", use_container_width=True):
            if nome and cpf:
                agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                # Garanta que a coluna 'Endereço' está escrita EXATAMENTE igual ao Excel
                novo = pd.DataFrame([{"Nome": nome, "CPF": cpf, "Endereço": endereco, "Telefone": telefone, "Data Cadastro": agora}])
                df_c = pd.concat([df_c, novo], ignore_index=True)
                df_c.to_excel(CLIENTES_FILE, index=False)
                st.success("✅ Salvo!")
                st.rerun()
# --- ABA 2: AGENDA ---
with aba2:
    df_a = carregar_dados(AGENDA_FILE, ["Dia", "Horário", "Cliente"])
    horas = [f"{h:02d}:00" for h in range(7, 23) if h not in [12, 13]]
    dias = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"]

    col_l, col_r = st.columns([1, 3])

    with col_l:
        st.subheader("📌 Agendar/Excluir")
        d_sel = st.selectbox("Dia", dias)
        h_sel = st.selectbox("Hora", horas)

        nomes_cli = df_c['Nome'].tolist() if not df_c.empty else []
        c_sel = st.selectbox("Selecionar Cliente",
                             nomes_cli if nomes_cli else ["Vazio"])

        if st.button("🗓️ Confirmar Horário", use_container_width=True):
            lotacao = df_a[(df_a['Dia'] == d_sel) & (df_a['Horário'] == h_sel)]
            if len(lotacao) < 4:
                novo_ag = pd.DataFrame(
                    [{"Dia": d_sel, "Horário": h_sel, "Cliente": c_sel}])
                df_a = pd.concat([df_a, novo_ag], ignore_index=True)
                df_a.to_excel(AGENDA_FILE, index=False)
                st.rerun()
            else:
                st.error("Horário lotado!")

        st.divider()
        st.subheader("🗑️ Desmarcar")
        # Filtra quem está agendado no dia e hora selecionados
        agendados = df_a[(df_a['Dia'] == d_sel) & (
            df_a['Horário'] == h_sel)]['Cliente'].tolist()
        if agendados:
            remover_cli = st.selectbox("Quem remover?", agendados)
            if st.button("❌ Remover Selecionado"):
                # Remove apenas a linha correspondente
                df_a = df_a.drop(df_a[(df_a['Dia'] == d_sel) &
                                      (df_a['Horário'] == h_sel) &
                                      (df_a['Cliente'] == remover_cli)].index)
                df_a.to_excel(AGENDA_FILE, index=False)
                st.rerun()

    with col_r:
        st.subheader("🗓️ Quadro Semanal")
        grade = []
        for h in horas:
            linha = {"Horário": h}
            for d in dias:
                clientes_vaga = df_a[(df_a['Dia'] == d) & (
                    df_a['Horário'] == h)]['Cliente'].values
                # Solução para o erro de FLOAT: converte cada item para str antes do join
                linha[d] = " | ".join([str(c) for c in clientes_vaga if c])
            grade.append(linha)

        st.table(pd.DataFrame(grade))

