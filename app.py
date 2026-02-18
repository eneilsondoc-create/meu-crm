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

# --- ABA 1: CLIENTES (Com Botões de Editar e Excluir) ---
with aba1:
    df_c = carregar_dados(CLIENTES_FILE, ["Nome", "CPF", "Endereço", "Telefone", "Data Cadastro"])
    
    st.subheader("📝 Gerenciar Cliente")
    
    # Campos de entrada
    nome = st.text_input("Nome Completo")
    cpf_input = st.text_input("CPF (ID Único para buscar/editar/excluir)")
    endereco = st.text_area("Endereço")
    tel = st.text_input("Telefone")
    
    # Organização dos botões para Celular (Um ao lado do outro ou empilhados)
    col_b1, col_b2, col_b3 = st.columns(3)
    
    with col_b1:
        if st.button("💾 Salvar", use_container_width=True, type="primary"):
            if nome and cpf_input:
                agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                novo = pd.DataFrame([{"Nome": nome, "CPF": cpf_input, "Endereço": endereco, "Telefone": tel, "Data Cadastro": agora}])
                df_c = pd.concat([df_c, novo], ignore_index=True)
                df_c.to_excel(CLIENTES_FILE, index=False)
                st.success("Salvo!")
                st.rerun()
    
    with col_b2:
        if st.button("🔄 Editar", use_container_width=True):
            if cpf_input in df_c['CPF'].values:
                df_c.loc[df_c['CPF'] == cpf_input, ["Nome", "Endereço", "Telefone"]] = [nome, endereco, tel]
                df_c.to_excel(CLIENTES_FILE, index=False)
                st.success("Atualizado!")
                st.rerun()
            else:
                st.error("CPF não encontrado!")

    with col_b3:
        if st.button("🗑️ Excluir", use_container_width=True):
            if cpf_input in df_c['CPF'].values:
                df_c = df_c[df_c['CPF'] != cpf_input]
                df_c.to_excel(CLIENTES_FILE, index=False)
                st.warning("Removido!")
                st.rerun()
            else:
                st.error("CPF não encontrado!")

    st.divider()
    st.subheader("📋 Lista de Clientes")
    st.dataframe(df_c, use_container_width=True, hide_index=True)

# --- ABA 2: AGENDA (Com opção de excluir agendamento) ---
with aba2:
    df_a = carregar_dados(AGENDA_FILE, ["Dia", "Horário", "Cliente"])
    horas = [f"{h:02d}:00" for h in range(7, 23) if h not in [12, 13]]
    dias = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"]

    # Seção para ADICIONAR ou EXCLUIR
    col_ag1, col_ag2 = st.columns([1, 2])

    with col_ag1:
        st.subheader("📌 Agendamento")
        d_sel = st.selectbox("Escolha o Dia", dias)
        h_sel = st.selectbox("Escolha a Hora", horas)
        
        # Parte de Adicionar
        n_lista = df_c['Nome'].tolist() if not df_c.empty else []
        c_sel = st.selectbox("Selecionar Cliente para Agendar", n_lista if n_lista else ["Vazio"])
        
        if st.button("🗓️ Confirmar Horário", use_container_width=True, type="primary"):
            lotacao = df_a[(df_a['Dia'] == d_sel) & (df_a['Horário'] == h_sel)]
            if len(lotacao) < 4:
                novo_ag = pd.DataFrame([{"Dia": d_sel, "Horário": h_sel, "Cliente": c_sel}])
                df_a = pd.concat([df_a, novo_ag], ignore_index=True)
                df_a.to_excel(AGENDA_FILE, index=False)
                st.success("Agendado!")
                st.rerun()
            else:
                st.error("Lotado!")

        st.divider()
        # PARTE DE EXCLUIR AGENDAMENTO
        st.subheader("🗑️ Cancelar Horário")
        # Filtra quem está agendado no dia e hora selecionados acima
        quem_esta_agendado = df_a[(df_a['Dia'] == d_sel) & (df_a['Horário'] == h_sel)]['Cliente'].tolist()
        
        if quem_esta_agendado:
            cliente_remover = st.selectbox("Quem deseja remover?", quem_esta_agendado)
            if st.button("❌ Remover Agendamento", use_container_width=True):
                # Remove a linha específica
                df_a = df_a.drop(df_a[(df_a['Dia'] == d_sel) & 
                                      (df_a['Horário'] == h_sel) & 
                                      (df_a['Cliente'] == cliente_remover)].index)
                df_a.to_excel(AGENDA_FILE, index=False)
                st.warning("Cancelado!")
                st.rerun()
        else:
            st.info("Ninguém agendado neste horário.")

    with col_ag2:
        st.subheader("🗓️ Quadro Semanal")
        grade = []
        for h in horas:
            linha = {"Horário": h}
            for d in dias:
                clientes_vaga = df_a[(df_a['Dia'] == d) & (df_a['Horário'] == h)]['Cliente'].tolist()
                linha[d] = " | ".join([str(c) for c in clientes_vaga if c])
            grade.append(linha)
        
        st.dataframe(pd.DataFrame(grade), use_container_width=True, hide_index=True)
