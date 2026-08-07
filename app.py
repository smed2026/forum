import streamlit as st
import re
from supabase import create_client, Client

#[supabase]
SUPABASE_URL = "https://yqlgtpwlhptrmlltvrhi.supabase.co"
SUPABASE_KEY = "sb_publishable_S3zafv2jYpXKUiyhK6XSyQ_w_0qBuYd"

@st.cache_resource
def init_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

st.set_page_config(page_title="Formulário de Inscrição", page_icon="📝")

# --- GERENCIAMENTO DE RESET E INICIALIZAÇÃO DE ESTADOS ---
if "precisa_resetar" not in st.session_state:
    st.session_state["precisa_resetar"] = False

def executar_reset():
    """Limpa os valores do session_state antes dos widgets serem desenhados na tela."""
    st.session_state["cpf_input"] = ""
    st.session_state["cpf_valido"] = False
    st.session_state["msg_cpf_erro"] = ""
    st.session_state["msg_cpf_sucesso"] = ""
    st.session_state["telefone_input"] = ""
    st.session_state["telefone_valido"] = False
    st.session_state["msg_tel_erro"] = ""
    st.session_state["msg_tel_sucesso"] = ""
    st.session_state["email_input"] = ""
    st.session_state["email_valido"] = False
    st.session_state["msg_email_erro"] = ""
    st.session_state["msg_email_sucesso"] = ""
    st.session_state["nome_input"] = ""
    st.session_state["cargo_input"] = ""

# Se a flag de reset estiver ativa, limpa os campos antes de instanciar os widgets
if st.session_state["precisa_resetar"]:
    executar_reset()
    st.session_state["precisa_resetar"] = False

# Inicialização padrão dos campos caso ainda não existam no session_state
estados_iniciais = {
    "cpf_input": "",
    "cpf_valido": False,
    "msg_cpf_erro": "",
    "msg_cpf_sucesso": "",
    "telefone_input": "",
    "telefone_valido": False,
    "msg_tel_erro": "",
    "msg_tel_sucesso": "",
    "email_input": "",
    "email_valido": False,
    "msg_email_erro": "",
    "msg_email_sucesso": "",
    "nome_input": "",
    "cargo_input": "",
    "msg_sucesso_global": ""
}

for chave, valor in estados_iniciais.items():
    if chave not in st.session_state:
        st.session_state[chave] = valor


# --- INTERFACE INICIAL ---
st.title("📝 Formulário de Inscrição")

# Exibe mensagem global de sucesso obtida da inscrição anterior (se houver)
if st.session_state["msg_sucesso_global"]:
    st.success(st.session_state["msg_sucesso_global"])
    st.session_state["msg_sucesso_global"] = ""


# --- FUNÇÃO PARA EXIBIR ALERTAS CUSTOMIZADOS EM HTML/CSS ---
def exibir_alerta(mensagem: str, tipo: str):
    """Exibe uma mensagem customizada de erro (vermelho) ou sucesso (verde) abaixo do campo."""
    if not mensagem:
        return

    if tipo == "erro":
        cor_bg = "#fde8e8"
        cor_texto = "#9b1c1c"
        cor_borda = "#f05252"
        icone = "❌"
    elif tipo == "sucesso":
        cor_bg = "#def7ec"
        cor_texto = "#03543f"
        cor_borda = "#0e9f6e"
        icone = "✅"
    else:
        return

    html_alerta = f"""
    <div style="
        background-color: {cor_bg};
        color: {cor_texto};
        border-left: 5px solid {cor_borda};
        padding: 8px 12px;
        border-radius: 4px;
        font-size: 13px;
        font-weight: 500;
        margin-top: 4px;
        margin-bottom: 8px;">
        {icone} {mensagem}
    </div>
    """
    st.markdown(html_alerta, unsafe_allow_html=True)


# --- VALIDAÇÃO MATEMÁTICA DO CPF ---
def validar_algoritmo_cpf(cpf_string: str) -> bool:
    """Valida se um CPF é matematicamente válido usando os dígitos verificadores."""
    cpf = re.sub(r"\D", "", cpf_string)

    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False

    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    resto = (soma * 10) % 11
    digito_1 = 0 if resto == 10 else resto

    if digito_1 != int(cpf[9]):
        return False

    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    resto = (soma * 10) % 11
    digito_2 = 0 if resto == 10 else resto

    return digito_2 == int(cpf[10])


# --- MÁSCARA E VALIDAÇÃO DE CPF ---
def formatar_e_validar_cpf():
    numeros = re.sub(r"\D", "", st.session_state["cpf_input"])[:11]
    cpf_formatado = ""
    if len(numeros) > 0:
        cpf_formatado = numeros[:3]
        if len(numeros) > 3:
            cpf_formatado += "." + numeros[3:6]
        if len(numeros) > 6:
            cpf_formatado += "." + numeros[6:9]
        if len(numeros) > 9:
            cpf_formatado += "-" + numeros[9:11]

    st.session_state["cpf_input"] = cpf_formatado

    if len(numeros) == 11:
        if not validar_algoritmo_cpf(numeros):
            st.session_state["cpf_valido"] = False
            st.session_state["msg_cpf_erro"] = "CPF inválido! Verifique se os 11 dígitos estão corretos."
            st.session_state["msg_cpf_sucesso"] = ""
        else:
            try:
                res = supabase.table("inscritos").select("id").eq("cpf", cpf_formatado).execute()
                if len(res.data) > 0:
                    st.session_state["cpf_valido"] = False
                    st.session_state["msg_cpf_erro"] = "Este CPF já possui uma inscrição cadastrada!"
                    st.session_state["msg_cpf_sucesso"] = ""
                else:
                    st.session_state["cpf_valido"] = True
                    st.session_state["msg_cpf_erro"] = ""
                    st.session_state["msg_cpf_sucesso"] = "CPF verificado e disponível!"
            except Exception as e:
                st.session_state["cpf_valido"] = False
                st.session_state["msg_cpf_erro"] = f"Erro ao verificar CPF no banco: {e}"
                st.session_state["msg_cpf_sucesso"] = ""
    elif len(numeros) > 0:
        st.session_state["cpf_valido"] = False
        st.session_state["msg_cpf_erro"] = "CPF incompleto! Preencha os 11 dígitos."
        st.session_state["msg_cpf_sucesso"] = ""
    else:
        st.session_state["cpf_valido"] = False
        st.session_state["msg_cpf_erro"] = ""
        st.session_state["msg_cpf_sucesso"] = ""


# --- MÁSCARA E VALIDAÇÃO DE TELEFONE ---
def formatar_e_validar_telefone():
    numeros = re.sub(r"\D", "", st.session_state["telefone_input"])[:11]
    tel_formatado = ""
    if len(numeros) > 0:
        tel_formatado = f"({numeros[:2]}"
        if len(numeros) > 2:
            if len(numeros) <= 10:
                tel_formatado += f") {numeros[2:6]}"
                if len(numeros) > 6:
                    tel_formatado += f"-{numeros[6:10]}"
            else:
                tel_formatado += f") {numeros[2:7]}"
                if len(numeros) > 7:
                    tel_formatado += f"-{numeros[7:11]}"

    st.session_state["telefone_input"] = tel_formatado

    if len(numeros) >= 10:
        st.session_state["telefone_valido"] = True
        st.session_state["msg_tel_erro"] = ""
        st.session_state["msg_tel_sucesso"] = "Telefone formatado e válido!"
    elif len(numeros) > 0:
        st.session_state["telefone_valido"] = False
        st.session_state["msg_tel_erro"] = "Telefone incompleto! Insira DDD + Número."
        st.session_state["msg_tel_sucesso"] = ""
    else:
        st.session_state["telefone_valido"] = False
        st.session_state["msg_tel_erro"] = ""
        st.session_state["msg_tel_sucesso"] = ""


# --- VALIDAÇÃO DE E-MAIL ---
def validar_email():
    email_input = st.session_state["email_input"].strip()
    padrao_email = r"^[\w\.-]+@[\w\.-]+\.\w+$"

    if len(email_input) > 0:
        if re.match(padrao_email, email_input):
            st.session_state["email_valido"] = True
            st.session_state["msg_email_erro"] = ""
            st.session_state["msg_email_sucesso"] = "Endereço de e-mail válido!"
        else:
            st.session_state["email_valido"] = False
            st.session_state["msg_email_erro"] = "E-mail inválido! Exemplo aceito: usuario@dominio.com"
            st.session_state["msg_email_sucesso"] = ""
    else:
        st.session_state["email_valido"] = False
        st.session_state["msg_email_erro"] = ""
        st.session_state["msg_email_sucesso"] = ""


# Obter lista de grupos do Supabase
def obter_grupos():
    try:
        res = supabase.table("grupos").select("nome, qtdvagas, qtdvagasusadas").execute()
        return res.data
    except Exception as e:
        st.error(f"Erro ao carregar tabela 'grupos': {e}")
        return []


grupos_dados = obter_grupos()
lista_nomes_grupos = [g["nome"] for g in grupos_dados] if grupos_dados else []

# --- 1. ETAPA DE ENTRADA DO CPF ---
st.subheader("1. Identificação")
st.text_input(
    "Digite seu CPF (Pressione Enter ou Tab ao concluir):",
    key="cpf_input",
    placeholder="000.000.000-00",
    on_change=formatar_e_validar_cpf
)

# Exibe as mensagens de validação do CPF
if st.session_state["msg_cpf_erro"]:
    exibir_alerta(st.session_state["msg_cpf_erro"], "erro")
    st.stop()  # Bloqueia a continuação caso o CPF seja inválido ou já cadastrado
elif st.session_state["msg_cpf_sucesso"]:
    exibir_alerta(st.session_state["msg_cpf_sucesso"], "sucesso")
else:
    st.info("Por favor, digite um CPF válido para liberar o formulário.")
    st.stop()

# --- 2. DEMAIS CAMPOS ---
st.divider()
st.subheader("2. Dados Pessoais e Inscrição")

col1, col2 = st.columns(2)

with col1:
    st.text_input(
        "Telefone (DDD + Número):",
        key="telefone_input",
        placeholder="(00) 00000-0000",
        on_change=formatar_e_validar_telefone
    )
    if st.session_state["msg_tel_erro"]:
        exibir_alerta(st.session_state["msg_tel_erro"], "erro")
    elif st.session_state["msg_tel_sucesso"]:
        exibir_alerta(st.session_state["msg_tel_sucesso"], "sucesso")

with col2:
    st.text_input(
        "E-mail:",
        key="email_input",
        placeholder="nome@dominio.com",
        on_change=validar_email
    )
    if st.session_state["msg_email_erro"]:
        exibir_alerta(st.session_state["msg_email_erro"], "erro")
    elif st.session_state["msg_email_sucesso"]:
        exibir_alerta(st.session_state["msg_email_sucesso"], "sucesso")

# --- FORMULÁRIO FINAL DE ENVIO ---
with st.form("form_demais_dados", clear_on_submit=False):
    nome = st.text_input("Nome Completo:", key="nome_input")

    grupo_selecionado = st.selectbox(
        "Grupo ao qual pertence:",
        options=lista_nomes_grupos if lista_nomes_grupos else ["Nenhum grupo disponível"]
    )

    cargo = st.text_input("Cargo:", key="cargo_input")
    btn_confirmar = st.form_submit_button("Confirmar Inscrição", type="primary")

# --- PROCESSAMENTO DO ENVIO ---
if btn_confirmar:
    cpf_atual = st.session_state["cpf_input"]
    telefone_atual = st.session_state["telefone_input"]
    email_atual = st.session_state["email_input"]

    # Validações sem limpar o formulário em caso de erro
    if not st.session_state["telefone_valido"]:
        exibir_alerta("Corrija o número de Telefone antes de prosseguir com o envio.", "erro")
    elif not st.session_state["email_valido"]:
        exibir_alerta("Corrija o E-mail antes de prosseguir com o envio.", "erro")
    elif not (nome and cargo and grupo_selecionado):
        exibir_alerta("Por favor, preencha todos os campos do formulário para concluir.", "erro")
    elif grupo_selecionado == "Nenhum grupo disponível":
        exibir_alerta("Selecione um grupo válido para prosseguir.", "erro")
    else:
        info_grupo = next((g for g in grupos_dados if g["nome"] == grupo_selecionado), None)

        if info_grupo and info_grupo["qtdvagasusadas"] >= info_grupo["qtdvagas"]:
            st.error("O número de vagas para este grupo está esgotado.")
        else:
            try:
                res_rpc = supabase.rpc("processar_inscricao", {
                    "p_cpf": cpf_atual,
                    "p_nome": nome,
                    "p_email": email_atual,
                    "p_telefone": telefone_atual,
                    "p_grupo_nome": grupo_selecionado,
                    "p_cargo": cargo
                }).execute()

                resultado = res_rpc.data

                if resultado == "SEM_VAGAS":
                    st.error("O número de vagas para este grupo está esgotado.")
                elif resultado == "SUCESSO":
                    # Salva mensagem de sucesso e agenda o reset para a próxima execução limpa
                    st.session_state["msg_sucesso_global"] = "✅ Inscrição realizada com sucesso!"
                    st.session_state["precisa_resetar"] = True
                    st.rerun()

            except Exception as e:
                exibir_alerta(f"Erro ao processar a inscrição no Supabase: {e}", "erro")