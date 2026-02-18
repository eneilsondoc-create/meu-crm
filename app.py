import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. Configuração da página
st.set_page_config(page_title="CRM Master", layout="wide")

CLIENTES_FILE = "clientes.xlsx"
AGENDA_FILE = "agenda.xlsx"

# Função para carregar dados tratando erros de tipo (Float vs Str)
def carregar_dados(file, colunas):
    if os.path.exists(file):
        try:
            df = pd.read_excel(file)
            # CURA PARA O ERRO DA IMAGEM 1: Transforma tudo em texto
            df = df.astype(str).replace('nan', '')
            for col in colunas:
                if col not in df.columns: df[col] = ""
            return df
        except:
            return pd.DataFrame(columns=colunas)
    return pd.DataFrame(columns=colunas)

# --- INTERFACE ---
st.title("🚀 Meu CRM Profissional")

aba1, aba2 = st.tabs(["👥 Clientes", "📅 Agenda"])

# --- ABA 1: CLIENTES (Ajustada para Celular) ---
with aba1:
    df_c = carregar_dados(CLIENTES_FILE, ["Nome", "CPF", "Endereço", "Telefone", "Data Cadastro"])
    
    st.subheader("📝 Novo Cadastro")
    nome = st.text_input("Nome Completo")
    cpf = st.text_input("CPF")
    
    # Campo de Endereço grande para não sumir no celular
    endereco = st.text_area("Endereço Completo")
    tel = st.text_input("Telefone")
    
    if st.button("💾 Salvar Cliente", type="primary", use_container_width=True):
        if nome and cpf:
            agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            # CURA PARA O ERRO DA IMAGEM 4: Criando o novo registro corretamente
            novo = pd.DataFrame([{"Nome": nome, "CPF": cpf, "Endereço": endereco, "Telefone": tel, "Data Cadastro": agora}])
            df_c = pd.concat([df_c, novo], ignore_index=True)
            df_c.to_excel(CLIENTES_FILE, index=False)
            st.success("✅ Cadastrado!")
            st.rerun()
        else:
            st.warning("⚠️ Preencha Nome e CPF!")

    st.divider()
    st.subheader("📋 Lista de Clientes")
    st.dataframe(df_c, use_container_width=True, hide_index=True)

# --- ABA 2: AGENDA ---
with aba2:
    df_a = carregar_dados(AGENDA_FILE, ["Dia", "Horário", "Cliente"])
    horas = [f"{h:02d}:00" for h in range(7, 23) if h not in [12, 13]]
    dias = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"]

    # Menu de agendamento
    with st.expander("➕ Agendar Novo Horário"):
        d_sel = st.selectbox("Dia", dias)
        h_sel = st.selectbox("Hora", horas)
        n_lista = df_c['Nome'].tolist() if not df_c.empty else []
        c_sel = st.selectbox("Cliente", n_lista if n_lista else ["Nenhum cadastrado"])
        
        if st.button("Confirmar Agendamento", use_container_width=True):
            lotacao = df_a[(df_a['Dia'] == d_sel) & (df_a['Horário'] == h_sel)]
            if len(lotacao) < 4:
                novo_ag = pd.DataFrame([{"Dia": d_sel, "Horário": h_sel, "Cliente": c_sel}])
                df_a = pd.concat([df_a, novo_ag], ignore_index=True)
                df_a.to_excel(AGENDA_FILE, index=False)
                st.rerun()

    # Grade visual
    st.subheader("🗓️ Quadro Semanal")
    grade = []
    for h in horas:
        linha = {"Horário": h}
        for d in dias:
            # Filtra os clientes
            clientes_vaga = df_a[(df_a['Dia'] == d) & (df_a['Horário'] == h)]['Cliente'].tolist()
            # O .join agora funciona porque garantimos que tudo é string
            linha[d] = " | ".join([str(c) for c in clientes_vaga if c])
        grade.append(linha)
    
    st.dataframe(pd.DataFrame(grade), use_container_width=True, hide_index=True)
