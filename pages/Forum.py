import streamlit as st
from supabase import create_client, Client

# Configuração do Supabase
SUPABASE_URL = "SUA_URL_DO_SUPABASE"
SUPABASE_KEY = "SUA_CHAVE_ANON_SUPABASE"


@st.cache_resource
def init_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)


supabase = init_supabase()

st.set_page_config(page_title="Formulário de Inscrição", page_icon="📝")
st.title("📝 Formulario de Inscrição")


# Função para buscar a lista de grupos para a caixa de pesquisa
def obter_grupos():
    try:
        res = supabase.table("grupos").select("nome, qtdvagas, qtdvagasusadas").execute()
        return res.data
    except Exception as e:
        st.error(f"Erro ao carregar os grupos: {e}")
        return []


grupos_dados = obter_grupos()
lista_nomes_grupos = [g["nome"] for g in grupos_dados] if grupos_dados else []

# Instancia o formulário (O uso do st.form facilita o reset automático dos campos ao submeter)
with st.form("form_inscricao", clear_on_submit=True):
    cpf = st.text_input("CPF:", placeholder="000.000.000-00")
    nome = st.text_input("Nome Completo:")
    email = st.text_input("E-mail:")
    telefone = st.text_input("Telefone:")

    # Campo de pesquisa e seleção do grupo mostrando apenas o nome
    grupo_selecionado = st.selectbox(
        "Grupo ao qual pertence:",
        options=lista_nomes_grupos if lista_nomes_grupos else ["Nenhum grupo cadastrado"]
    )

    cargo = st.text_input("Cargo:")

    btn_confirmar = st.form_submit_button("Confirmar Inscrição", type="primary")

if btn_confirmar:
    # 1. Validação de preenchimento dos campos
    if not (cpf and nome and email and telefone and cargo and grupo_selecionado):
        st.warning("Por favor, preencha todos os campos do formulário!")
    elif grupo_selecionado == "Nenhum grupo cadastrado":
        st.error("Selecione um grupo válido!")
    else:
        # Encontra os dados do grupo selecionado
        info_grupo = next((g for g in grupos_dados if g["nome"] == grupo_selecionado), None)

        # 2. Checagem prévia de limite de vagas
        if info_grupo and info_grupo["qtdvagasusadas"] >= info_grupo["qtdvagas"]:
            st.error("O número de vagas para esse grupo que pertence esta esgotadas as vagas")
        else:
            # 3. Verificação de CPF único
            res_cpf = supabase.table("inscritos").select("id").eq("cpf", cpf).execute()

            if len(res_cpf.data) > 0:
                st.error("Erro: Este CPF já possui um cadastro efetuado!")
            else:
                # 4. Processamento da inscrição via Função RPC no Supabase
                try:
                    res_rpc = supabase.rpc("processar_inscricao", {
                        "p_cpf": cpf,
                        "p_nome": nome,
                        "p_email": email,
                        "p_telefone": telefone,
                        "p_grupo_nome": grupo_selecionado,
                        "p_cargo": cargo
                    }).execute()

                    resultado = res_rpc.data

                    if resultado == "SEM_VAGAS":
                        st.error("O número de vagas para esse grupo que pertence esta esgotadas as vagas")
                    elif resultado == "SUCESSO":
                        st.success("Inscrição realizada com sucesso!")
                        # Força a atualização do cache da página para recarregar a lista de grupos se necessário
                        st.rerun()

                except Exception as e:
                    st.error(f"Ocorreu um erro ao processar a inscrição: {e}")