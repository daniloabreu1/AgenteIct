const chatContainer = document.getElementById('chatContainer');
const messageInput = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');
const logoutBtn = document.getElementById('logoutBtn');

let isAuthenticated = false;
let isWaitingResponse = false;
let isWaitingPassword = false;

document.addEventListener('DOMContentLoaded', () => {
    messageInput.focus();

    sendBtn.addEventListener('click', sendMessage);
    messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    logoutBtn.addEventListener('click', logout);
});

async function sendMessage() {
    const message = messageInput.value.trim();

    if (!message || isWaitingResponse) return;

    const isPasswordAttempt = isWaitingPassword;

    const displayMessage = isPasswordAttempt ? '********' : message;

    addMessage(displayMessage, 'user');
    messageInput.value = '';

    if (isPasswordAttempt) {
        messageInput.type = 'text';
        isWaitingPassword = false;
    }

    showTypingIndicator();
    isWaitingResponse = true;
    sendBtn.disabled = true;

    if (isWaitingPassword) {
        messageInput.type = 'text';
        isWaitingPassword = false;
    }

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ mensagem: message })
        });

        const data = await response.json();

        removeTypingIndicator();

        setTimeout(() => {
            addMessage(data.resposta, 'bot');

            if (data.tipo === 'sucesso') {
                isAuthenticated = true;
                logoutBtn.style.display = 'block';
                removeWelcomeMessage();
            } else if (data.tipo === 'autenticacao') {
                isWaitingPassword = true;
                messageInput.type = 'password';

            } else if (data.tipo === 'logout') {
                isWaitingResponse = true;
                sendBtn.disabled = true;

                setTimeout(() => {
                    logout();
                }, 3000);
                messageInput.type = 'text';
                return;

            } else if (data.tipo === 'erro') {
                if (isWaitingPassword) {
                     isWaitingPassword = false;
                     messageInput.type = 'text';
                }
            }

            isWaitingResponse = false;
            sendBtn.disabled = false;
            messageInput.focus();
        }, 500);

    } catch (error) {
        console.error('Erro ao enviar mensagem:', error);
        removeTypingIndicator();
        addMessage('Desculpe, ocorreu um erro. Por favor, tente novamente.', 'bot');
        isWaitingResponse = false;
        sendBtn.disabled = false;
    }
}

function addMessage(text, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;

    const now = new Date();
    const timeString = now.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });

    messageDiv.innerHTML = `
        <div class="message-content">
            ${formatMessage(text)}
            <div class="message-time">${timeString}</div>
        </div>
    `;

    chatContainer.appendChild(messageDiv);
    scrollToBottom();
}

function formatMessage(text) {
    return text.replace(/\n/g, '<br>');
}

function showTypingIndicator() {
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message bot';
    typingDiv.id = 'typingIndicator';

    typingDiv.innerHTML = `
        <div class="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
        </div>
    `;

    chatContainer.appendChild(typingDiv);
    scrollToBottom();
}

function removeTypingIndicator() {
    const typingIndicator = document.getElementById('typingIndicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

function removeWelcomeMessage() {
    const welcomeMessage = document.querySelector('.welcome-message');
    if (welcomeMessage) {
        welcomeMessage.style.animation = 'fadeOut 0.3s ease-out';
        setTimeout(() => {
            welcomeMessage.remove();
        }, 300);
    }
}

async function logout() {
    try {
        await fetch('/api/logout', {
            method: 'POST'
        });

        chatContainer.innerHTML = `
            <div class="welcome-message">
                <div class="bot-avatar">
                    <svg width="50" height="50" viewBox="0 0 50 50" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <circle cx="25" cy="25" r="25" fill="#E3F2FD"/>
                        <path d="M25 15C19.48 15 15 19.48 15 25C15 30.52 19.48 35 25 35C30.52 35 35 30.52 35 25C35 19.48 30.52 15 25 15ZM25 20C26.66 20 28 21.34 28 23C28 24.66 26.66 26 25 26C23.34 26 22 24.66 22 23C22 21.34 23.34 20 25 20ZM25 32.2C22.5 32.2 20.29 30.92 19 29C19.03 26.99 23 25.9 25 25.9C26.99 25.9 30.97 26.99 31 29C29.71 30.92 27.5 32.2 25 32.2Z" fill="#0066CC"/>
                    </svg>
                </div>
                <h2>Olá! Bem-vindo ao Atendimento Virtual</h2>
                <p>Sou seu assistente virtual e estou aqui para ajudar com:</p>
                <ul class="features-list">
                    <li>💰 Consulta de saldo e extrato</li>
                    <li>💳 Informações sobre produtos e serviços</li>
                    <li>🔄 Orientações sobre transferências e pagamentos</li>
                    <li>❓ Respostas para suas dúvidas frequentes</li>
                </ul>
                <p class="start-message">Para começar, por favor informe seu <strong>CPF</strong> (apenas números):</p>
            </div>
        `;

        isAuthenticated = false;
        isWaitingPassword = false;
        isWaitingResponse = false;

        logoutBtn.style.display = 'none';
        sendBtn.disabled = false;

        messageInput.value = '';
        messageInput.type = 'text';
        messageInput.focus();

    } catch (error) {
        console.error('Erro ao fazer logout:', error);
    }
}

function scrollToBottom() {
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

const style = document.createElement('style');
style.textContent = `
    @keyframes fadeOut {
        from {
            opacity: 1;
            transform: translateY(0);
        }
        to {
            opacity: 0;
            transform: translateY(-20px);
        }
    }
`;
document.head.appendChild(style);

