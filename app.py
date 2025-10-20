from flask import Flask, render_template, request, jsonify, session

import os
import secrets
import csv
import re

from langchain_classic.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.messages import HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

USUARIOS = {}
FAQ_DATABASE = {}
PRODUTOS = {}


def load_data_from_csv():
    global USUARIOS
    USUARIOS = {}

    with open(os.path.join(DATA_DIR, 'users.csv'), mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            cpf = row['cpf']
            USUARIOS[cpf] = {
                'nome': row['name'],
                'senha': row['password'],
                'contas': {}
            }

    with open(os.path.join(DATA_DIR, 'accounts.csv'), mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            cpf = row['cpf']
            if cpf in USUARIOS:
                account_type = row['account_type']
                USUARIOS[cpf]['contas'][account_type] = {
                    'numero': row['account_number'],
                    'saldo': float(row['balance']),
                    'extrato': []
                }

    with open(os.path.join(DATA_DIR, 'transactions.csv'), mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            cpf = row['cpf']
            account_number = row['account_number']

            if cpf in USUARIOS:
                for acc_type, acc_data in USUARIOS[cpf]['contas'].items():
                    if acc_data['numero'] == account_number:
                        USUARIOS[cpf]['contas'][acc_type]['extrato'].append({
                            'data': row['date'],
                            'descricao': row['description'],
                            'valor': float(row['value']),
                            'tipo': row['type']
                        })
                        break


load_data_from_csv()

FAQ_DATABASE = {
    "horario": "Nossas agências funcionam de segunda a sexta-feira, das 10h às 16h. O atendimento digital está disponível 24 horas por dia, 7 dias por semana.",
    "cartao": "Oferecemos diversos tipos de cartões de crédito: Básico (sem anuidade), Gold (benefícios intermediários) e Platinum (benefícios premium). Para solicitar, acesse o menu 'Produtos' no aplicativo.",
    "emprestimo": "Temos linhas de empréstimo pessoal com taxas a partir de 1,5% ao mês. O valor e as condições dependem da sua análise de crédito. Posso transferir você para um especialista?",
    "investimento": "Oferecemos CDB, LCI, LCA, Tesouro Direto, Fundos de Investimento e Previdência Privada. Cada opção tem características específicas de rentabilidade e liquidez.",
    "pix": "O Pix é um meio de pagamento instantâneo disponível 24/7. Você pode fazer transferências usando CPF, e-mail, telefone ou chave aleatória.",
    "seguranca": "Nunca compartilhe sua senha, token ou dados do cartão. O banco nunca solicita essas informações por telefone, e-mail ou SMS. Em caso de suspeita de fraude, bloqueie seu cartão imediatamente pelo app.",
    "taxas": "Consulte nossa tabela completa de tarifas em nosso site. Contas digitais têm isenção de várias tarifas. Posso enviar o link por e-mail?"
}

PRODUTOS = {
    "cartao_credito": {
        "nome": "Cartões de Crédito",
        "tipos": ["Básico (sem anuidade)", "Gold (R$ 20/mês)", "Platinum (R$ 50/mês)"],
        "beneficios": "Programa de pontos, seguros, descontos em parceiros"
    },
    "emprestimo": {
        "nome": "Empréstimo Pessoal",
        "taxa": "A partir de 1,5% ao mês",
        "prazo": "Até 60 meses"
    },
    "investimentos": {
        "nome": "Investimentos",
        "opcoes": ["CDB", "LCI/LCA", "Tesouro Direto", "Fundos de Investimento", "Previdência Privada"]
    }
}

@tool
def get_account_balance(cpf: str, account_type: str = "corrente") -> str:
    """Obtém o saldo de uma conta específica do usuário.
    Use quando o usuário perguntar sobre saldo.
    Parâmetros: cpf (CPF do usuário autenticado), account_type (tipo de conta, ex: 'corrente' ou 'poupanca').
    """
    if cpf not in USUARIOS:
        return "Usuário não encontrado."

    usuario = USUARIOS[cpf]

    if account_type not in usuario['contas']:
        return f"Você não possui conta {account_type} cadastrada."

    conta = usuario['contas'][account_type]
    return f"💰 Saldo da Conta {account_type.capitalize()} (Conta {conta['numero']}): R$ {conta['saldo']:.2f}" + "\n\n"


@tool
def get_account_statement(cpf: str, account_type: str = "corrente") -> str:
    """Obtém as últimas 5 transações e o saldo atual de uma conta específica do usuário.
    Use quando o usuário perguntar sobre extrato, movimentações ou transações.
    Parâmetros: cpf (CPF do usuário autenticado), account_type (tipo de conta, ex: 'corrente' ou 'poupanca').
    """
    if cpf not in USUARIOS:
        return "Usuário não encontrado."

    usuario = USUARIOS[cpf]

    if account_type not in usuario['contas']:
        return f"Você não possui conta {account_type} cadastrada."

    conta = usuario['contas'][account_type]
    extrato = conta['extrato']

    if not extrato:
        return f"Não há transações recentes para a conta {account_type.capitalize()} (Conta {conta['numero']}). Saldo atual: R$ {conta['saldo']:.2f}"

    mensagem_extrato = f"📋 Extrato da Conta {account_type.capitalize()} (Conta {conta['numero']}):\n\n"
    for transacao in extrato[-5:]:  # Últimas 5 transações
        simbolo = "+" if transacao["tipo"] == "credito" else "-"
        mensagem_extrato += f"{transacao['data']} | {transacao['descricao']}: {simbolo}R$ {abs(transacao['valor']):.2f}\n"

    mensagem_extrato += f"\n💰 Saldo atual: R$ {conta['saldo']:.2f}"
    return mensagem_extrato

@tool
def get_product_info(product_category: str) -> str:
    """Fornece informações sobre produtos bancários como cartões, empréstimos ou investimentos.
    Use quando o usuário perguntar sobre produtos ou serviços.
    Parâmetros: product_category (categoria do produto, ex: 'cartao', 'emprestimo', 'investimento').
    """
    if product_category == "cartao":
        produto = PRODUTOS["cartao_credito"]
        return f"💳 {produto['nome']}:\n\nTipos disponíveis:\n" + "\n".join(
            [f"• {t}" for t in produto['tipos']]) + f"\n\nBenefícios: {produto['beneficios']}"
    elif product_category == "emprestimo":
        produto = PRODUTOS["emprestimo"]
        return f"💰 {produto['nome']}:\n\nTaxa: {produto['taxa']}\nPrazo: {produto['prazo']}\n\nGostaria de simular um empréstimo?"
    elif product_category == "investimento":
        produto = PRODUTOS["investimentos"]
        return f"📈 {produto['nome']}:\n\nOpções disponíveis:\n" + "\n".join(
            [f"• {o}" for o in produto['opcoes']]) + "\n\nGostaria de falar com um especialista?"
    else:
        return "Oferecemos diversos produtos: Cartões de Crédito, Empréstimos e Investimentos. Sobre qual você gostaria de saber mais?"

@tool
def get_faq_answer(query: str) -> str:
    """Busca respostas para perguntas frequentes do banco.
    Use quando o usuário tiver dúvidas gerais ou perguntar sobre 'horário', 'agência', 'taxa', 'tarifa', 'segurança', 'pix'.
    Parâmetros: query (a palavra-chave ou tópico da pergunta do usuário).
    """
    for chave, resposta in FAQ_DATABASE.items():
        if chave in query.lower():
            return resposta
    return "Desculpe, não encontrei uma resposta para sua pergunta nas Perguntas Frequentes. Posso ajudar com dúvidas sobre: horários de atendimento, cartões, empréstimos, investimentos, PIX, segurança e taxas."

@tool
def simulate_transfer_guidance() -> str:
    """Fornece orientações sobre como realizar uma transferência bancária.
    Use quando o usuário perguntar sobre 'transferência', 'transferir', 'enviar dinheiro', 'pix'.
    """
    return "🔄 Para realizar uma transferência, você precisa informar:\n1. Tipo (PIX, TED ou DOC)\n2. Valor\n3. Dados do beneficiário\n\nPor questões de segurança, transferências devem ser realizadas no aplicativo oficial do banco."

@tool
def simulate_payment_guidance() -> str:
    """Fornece orientações sobre como realizar um pagamento de conta.
    Use quando o usuário perguntar sobre 'pagamento', 'pagar', 'boleto', 'conta'.
    """
    return "💳 Para realizar um pagamento, você pode:\n1. Escanear o código de barras do boleto\n2. Digitar o código manualmente\n\nPor questões de segurança, pagamentos devem ser realizadas no aplicativo oficial do banco."

tools = [
    get_account_balance,
    get_account_statement,
    get_product_info,
    get_faq_answer,
    simulate_transfer_guidance,
    simulate_payment_guidance
]

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY não configurada. Por favor, defina a variável de ambiente.")

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0, google_api_key=GOOGLE_API_KEY)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system",
         "Você é um assistente bancário útil e amigável, seu nome é **BankBot**. Você deve responder às perguntas do usuário **priorizando o uso das ferramentas disponíveis (tools)** para buscar informações bancárias, como 'saldo' e 'extrato', ou para dar orientações. **Sua função é manter a conversa fluida**. Sempre que fornecer uma informação (como saldo ou extrato), pergunte ao usuário o que mais ele precisa. **O CPF do usuário autenticado é {cpf}**."),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)

agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

class ChatbotEngine:
    """Motor de processamento de linguagem natural do chatbot com LangChain"""

    def __init__(self):
        self.context = {}
        self.chat_history = []

    def processar_mensagem(self, mensagem, cpf=None):
        """Processa a mensagem do usuário e retorna uma resposta apropriada"""
        mensagem.lower().strip()

        if not cpf:
            cpf_match = re.search(r'\d{11}', mensagem)
            if cpf_match:
                return {
                    "tipo": "autenticacao",
                    "mensagem": "CPF identificado. Por favor, digite sua senha para continuar:"
                }
            else:
                return {
                    "tipo": "info",
                    "mensagem": "Para começar, por favor informe seu CPF (apenas números):"
                }

        try:
            self.chat_history.append(HumanMessage(content=mensagem))
            response = agent_executor.invoke(
                {"input": mensagem, "chat_history": self.chat_history, "cpf": cpf}
            )

            ai_response_content = response.get("output", "Desculpe, não consegui processar sua solicitação no momento.")
            self.chat_history.append(AIMessage(content=ai_response_content))

            return {
                "tipo": "info",
                "mensagem": ai_response_content
            }
        except Exception as e:
            print("----------------------------------------------------------------")
            print(f"ERRO NO AGENTE LANGCHAIN (Conversa): {e}")
            print("----------------------------------------------------------------")

            return {
                "tipo": "info",
                "mensagem": "Desculpe, tive um problema ao processar sua solicitação.\nPor favor, tente novamente mais tarde."
            }

    def _detectar_cpf(self, mensagem):
        """Detecta se a mensagem contém um CPF válido"""
        cpf_pattern = r'\d{11}'
        match = re.search(cpf_pattern, mensagem)
        return match is not None

chatbot = ChatbotEngine()

@app.route('/')
def index():
    """Página inicial do chatbot"""
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Endpoint para processar mensagens do chat"""
    data = request.json
    mensagem = data.get('mensagem', '')

    cpf = session.get('cpf')

    if mensagem.lower().strip() == 'sair':
        session.clear()
        chatbot.chat_history = []

        return jsonify({
            "resposta": "Sessão encerrada com sucesso.\n",
            "tipo": "logout"
        })

    if not cpf:
        cpf_match = re.search(r'\d{11}', mensagem)
        if cpf_match:
            cpf_candidato = cpf_match.group()
            if cpf_candidato in USUARIOS:
                session['cpf_temp'] = cpf_candidato
                return jsonify({
                    "resposta": "CPF identificado. Por favor, digite sua senha:",
                    "tipo": "autenticacao"
                })
            else:
                return jsonify({
                    "resposta": "CPF não encontrado em nossa base de dados. Por favor, verifique e tente novamente.",
                    "tipo": "erro"
                })

    if 'cpf_temp' in session and not cpf:
        cpf_temp = session['cpf_temp']
        senha = mensagem.strip()
        if USUARIOS[cpf_temp]['senha'] == senha:
            session['cpf'] = cpf_temp
            session.pop('cpf_temp')
            cpf = session['cpf']
            chatbot.chat_history = []
            return jsonify({
                "resposta": f"Bem-vindo(a), {USUARIOS[cpf]['nome']}! 🎉\n\nComo posso ajudar você hoje?",
                "tipo": "sucesso"
            })
        else:
            session.pop('cpf_temp')
            return jsonify({
                "resposta": "Senha incorreta.\nPor favor, informe seu CPF novamente para tentar.",
                "tipo": "erro"
            })
    resposta = chatbot.processar_mensagem(mensagem, cpf)

    return jsonify({
        "resposta": resposta["mensagem"],
        "tipo": resposta["tipo"]
    })

@app.route('/api/logout', methods=['POST'])
def logout():
    """Endpoint para fazer logout"""
    session.clear()
    chatbot.chat_history = []  # Limpar histórico do chat ao fazer logout
    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
