import streamlit as st
#from st_supabase_connection import SupabaseConnection
import pandas as pd
from supabase import create_client, Client
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
import io

# 1. Conexão com o Banco de Dados (Substitua pelas suas credenciais do Supabase)
#supabase = st.connection("supabase", type=SupabaseConnection)
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Sistema Comercial", page_icon="📊", layout="wide")

st.title("🚀 Sistema de controle - Clinica Dr. Jair")
st.markdown("---")

st.header("Bem-vindo ao Dashboard de Gestão - Clinica Dr. Jair")

resultado_paciente = supabase.table("pacientes").select("*").execute()
qtd_paciente = resultado_paciente.count

#resultado_medico = supabase.table("medicos").select("*").execute()
#qtd_medico = resultado_medico.count

col1, col2, col3 = st.columns(3)

col1.metric("Pacientes Cadastrados", qtd_paciente, "+5")
col2.metric("Medicos Cadastrados", "01", "12")
col3.metric("Especialidades", "R$ 15.000", "+12%")

# 1. Configura o relógio (autorefresh): força a página a recarregar a cada 1000 milissegundos (1 segundo)
st_autorefresh(interval=1000, key="relogio_atualizado")

# 2. Obtém a data e hora atual do sistema
agora = datetime.now()
data_formatada = agora.strftime("%d/%m/%Y")
hora_formatada = agora.strftime("%H:%M:%S")

# 3. Exibe o relógio na Barra Lateral (Sidebar)
#with st.sidebar:
st.markdown("### 🕒 Horário do Sistema")
#st.metric(label="Data", value=data_formatada)
#$st.metric(label="Hora Atual", value=hora_formatada)

col1, col2, = st.columns([5, 5])

# 2. Usar 'with' para adicionar widgets nas colunas
with col1:
    st.metric(label="Data", value=data_formatada)

with col2:
    st.metric(label="Hora Atual", value=hora_formatada)

#st.markdown("""
#("""
### Como utilizar
#Use o menu lateral para navegar entre as telas de **Cadastro** e **Relatórios**.
#- **Cadastro Clientes**: Adicionar ou editar clientes.
#- **Cadastro Produtos**: Adicionar ou editar produtos.
#- **Relatório Vendas**: Visualizar vendas consolidadas.
#""")