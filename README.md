# Documentação Chatbot: Virtual Bank

## 1. Introdução

Este material serve como a **documentação** para o projeto de um chatbot de atendimento ao cliente, desenvolvido como uma atividade de um processo de seleção. O chatbot é projetado para um banco, visando otimizar a interação com o cliente, reduzir a carga sobre os canais tradicionais e fornecer suporte eficiente e seguro. A solução abrange desde a concepção conceitual até a implementação técnica em Python com interface web, além de um plano de testes e validação.

## 2. Apresentação Conceitual do Modelo de Chatbot

### 2.1. Contexto e Objetivos

O cenário bancário atual exige soluções para atender às demandas dos clientes por agilidade e conveniência. Este chatbot surge como uma ferramenta estratégica para aprimorar a experiência do cliente, oferecendo um canal de comunicação digital **intuitivo e acessível**. Seus principais objetivos são:

*   **Responder a Perguntas Frequentes (FAQs):** Fornecer informações rápidas sobre produtos e serviços bancários.
*   **Auxiliar em Tarefas Transacionais Básicas:** Permitir consultas de saldo e extrato de forma segura.
*   **Direcionar Clientes:** Encaminhar usuários para atendimento humano em situações complexas.
*   **Personalizar a Experiência:** Utilizar dados para oferecer interações mais relevantes.

### 2.2. Funcionalidades Propostas

As funcionalidades do chatbot foram desenhadas para cobrir as necessidades mais comuns dos clientes bancários, conforme detalhado na tabela abaixo:

| Categoria         | Funcionalidade Principal              | Descrição Detalhada                                                                                                                                                                                                        |
| :---------------- | :------------------------------------ | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Informações**   | Consulta de Saldo                     | O cliente poderá solicitar e visualizar o saldo de suas contas (corrente, poupança, investimentos) de forma segura, após autenticação.                                                                             |
|                   | Extrato de Conta                      | Geração de extrato simplificado ou detalhado para um período específico, com opção de envio por e-mail ou visualização direta na interface.                                                                   |
|                   | Informações sobre Produtos e Serviços | Fornecimento de detalhes sobre cartões de crédito, empréstimos, financiamentos, investimentos, seguros, taxas e tarifas, horários de agências, etc.                                                               |
| **Transações**    | Pagamento de Contas                   | Iniciação de pagamentos de boletos ou contas de consumo (água, luz, telefone) via código de barras ou digitação manual, com confirmação de dados.                                                              |
|                   | Transferências Bancárias              | Realização de transferências entre contas do mesmo titular, para outros bancos (TED/DOC/Pix), com validação de dados do beneficiário e confirmação.                                                               |
| **Suporte**       | Perguntas Frequentes (FAQ)            | Respostas automáticas para dúvidas comuns sobre o uso de aplicativos, segurança, procedimentos bancários, etc.                                                                                                |
|                   | Direcionamento para Atendente Humano  | Em casos de complexidade ou insatisfação, o chatbot oferecerá a opção de transferir o atendimento para um agente humano, fornecendo o histórico da conversa.                                                    |
|                   | Notificações Personalizadas           | Envio de alertas sobre vencimento de contas, movimentações financeiras, ofertas personalizadas (mediante consentimento do cliente).                                                                               |

### 2.3. Arquitetura Conceitual

A arquitetura do chatbot é modular e escalável, fundamentada em Python para o backend e tecnologias web para a interface, garantindo flexibilidade e compatibilidade. Os componentes chave incluem:

*   **Interface do Usuário (Frontend):** Responsável pela interação visual, desenvolvida com HTML, CSS e JavaScript para uma experiência intuitiva.
    *   **Processamento de Linguagem Natural (NLP) e Agente de IA:** Módulo central que utiliza **LangChain** e **Google GenAI (modelo Gemini)** para interpretar a intenção do usuário, extrair informações relevantes e orquestrar o uso de ferramentas específicas para responder às solicitações. Substitui a lógica baseada em palavras-chave por um agente de IA mais robusto e conversacional.
*   **Gerenciamento de Diálogo:** Controla o fluxo da conversa, mantendo o contexto e fornecendo respostas coerentes.
*   **Integração com Sistemas Bancários (Backend):** Conexão segura (simulada neste case) com APIs internas do banco para acesso a dados e transações.
*   **Base de Conhecimento:** Armazena FAQs e informações de produtos para respostas rápidas.
*   **Módulo de Autenticação:** Garante a segurança das operações sensíveis através de um processo de autenticação de usuário.

## 3. Implementação Técnica (Python com Interface Web)

### 3.1. Visão Geral da Tecnologia

O chatbot é implementado utilizando **Python** com o framework **Flask** para o backend, proporcionando uma estrutura leve e flexível para o desenvolvimento web. A interface do usuário é construída com **HTML, CSS e JavaScript**, garantindo uma experiência interativa e responsiva diretamente no navegador.

### 3.2. Estrutura do Projeto

O projeto está organizado na seguinte estrutura de diretórios:

```
chatbot-banco/
├── app.py
├── requirements.txt
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── script.js
├── templates/
│   └── index.html
└── data/
    ├── users.csv
    ├── accounts.csv
    └── transactions.csv
```

*   `app.py`: Contém a lógica do backend Flask, o motor do chatbot e as rotas da API. Inclui a funcionalidade de carregamento de dados a partir de arquivos CSV.
*   `requirements.txt`: Lista as dependências Python do projeto, incluindo `Flask` e `pandas`.
*   `static/`: Armazena arquivos estáticos (CSS, JavaScript).
*   `templates/`: Contém os templates HTML.

### 3.3. Detalhes do Backend (`app.py`)

O arquivo `app.py` é o coração do backend, implementando as seguintes funcionalidades:

*   **Servidor Flask:** Inicializa a aplicação web e define as rotas.
*   **Carregamento de Dados:** Os dados de usuários, contas e transações são carregados dinamicamente de arquivos CSV (`users.csv`, `accounts.csv`, `transactions.csv`) localizados no diretório `data/`. Isso permite uma gestão mais flexível e escalável dos dados, substituindo os dicionários embutidos no código. A função `load_data_from_csv()` é responsável por popular a estrutura `USUARIOS` a partir desses arquivos.
*   **FAQ e Produtos:** `FAQ_DATABASE` e `PRODUTOS` continuam como dicionários embutidos para informações estáticas.
*   **Integração com LangChain e Google GenAI:** O chatbot agora utiliza o framework LangChain para criar um agente de IA. Este agente é configurado com o modelo `gemini-pro` do Google GenAI e um conjunto de ferramentas (`tools`) para interagir com os dados bancários simulados e responder a perguntas. As ferramentas incluem `get_account_balance`, `get_account_statement`, `get_product_info`, `get_faq_answer`, `simulate_transfer_guidance` e `simulate_payment_guidance`.
*   **`ChatbotEngine`:** Esta classe encapsula a lógica de processamento de mensagens, que agora delega a maior parte do raciocínio e da interação ao agente LangChain:
    *   `processar_mensagem(mensagem, cpf)`: Método principal que recebe a mensagem do usuário e o CPF (se autenticado). Ele adiciona a mensagem ao histórico de chat e invoca o agente LangChain para gerar uma resposta, que pode incluir a utilização das ferramentas definidas.
    *   O fluxo de autenticação (CPF e senha) é mantido separado do agente por questões de segurança.
*   **Rotas da API:**
    *   `/`: Renderiza a interface HTML do chatbot (`index.html`).
    *   `/api/chat` (POST): Recebe as mensagens do usuário, gerencia o fluxo de autenticação e, após a autenticação, processa as mensagens através do `ChatbotEngine` (que agora utiliza o agente LangChain) e retorna a resposta do chatbot.
    *   `/api/logout` (POST): Limpa a sessão do usuário e o histórico do chat, efetivando o logout.

### 3.4. Detalhes do Frontend (HTML, CSS, JavaScript)

*   **`index.html`:** A página principal que carrega a interface do chatbot. Inclui a estrutura básica, o cabeçalho, a área de mensagens e o campo de entrada.
*   **`static/css/style.css`:** Define a estilização visual do chatbot, garantindo um design moderno, responsivo e alinhado com a identidade de um banco. Inclui estilos para mensagens, cabeçalho, campo de entrada e animações.
*   **`static/js/script.js`:** Gerencia a interatividade do chatbot:
    *   **`Reconhecimento de Voz`:** Integra a Web Speech API para permitir que o usuário interaja por voz. Um novo botão de microfone (`#voiceBtn`) inicia e para a gravação. A fala do usuário é transcrita para texto e preenche o campo de mensagem (`#messageInput`). **Ao finalizar a transcrição, a mensagem é enviada automaticamente** para o chatbot, otimizando a fluidez da interação por voz. 
    *   **`sendMessage()`:** Captura a mensagem do usuário, envia para o backend via API (`/api/chat`), exibe a mensagem do usuário e a resposta do bot na interface.
    *   **`addMessage(text, sender)`:** Adiciona uma nova bolha de mensagem ao chat, formatando o texto e a hora.
    *   **`showTypingIndicator()` / `removeTypingIndicator()`:** Exibe e remove um indicador visual quando o bot está "digitando".
    *   **`logout()`:** Envia uma requisição para o backend para limpar a sessão e reseta a interface para o estado inicial de boas-vindas.
    *   **`scrollToBottom()`:** Garante que a área de chat sempre role para a mensagem mais recente.
    *   Gerencia o estado de autenticação do usuário e a exibição do botão de logout.

## 4. Plano de Testes e Validação

Para garantir a qualidade, segurança e eficácia do chatbot, será adotada uma abordagem multifacetada de testes e validação, envolvendo usuários, time técnico e time de negócio.

### 4.1. Testes com Usuários (UAT - User Acceptance Testing)

*   **Objetivo:** Avaliar a usabilidade, a clareza das interações e a capacidade do chatbot de atender às expectativas dos clientes.
*   **Metodologia:** Sessões com clientes reais ou simulados, utilizando cenários predefinidos e interação livre. Coleta de feedback qualitativo via questionários e entrevistas.
*   **Métricas de Sucesso:** Taxa de Sucesso na Conclusão de Tarefas (>85%), Tempo Médio por Interação (<2 min), Net Promoter Score (NPS > 50), Taxa de Escalonamento para Atendente Humano (<15%), Taxa de Compreensão de Intenção (>90%).

### 4.2. Validação pelo Time Técnico

*   **Objetivo:** Garantir a robustez, escalabilidade, segurança e desempenho da solução técnica.
*   **Metodologia:** Testes de unidade, integração, carga e segurança. Revisão de código e monitoramento de performance.
*   **Métricas de Sucesso:** Tempo de Resposta do Chatbot (<2 segundos), Taxa de Erros (<1%), Utilização de Recursos (CPU < 70%, Memória < 80% em picos), Cobertura de Testes (>80%), 0 Vulnerabilidades críticas/altas.

### 4.3. Validação pelo Time de Negócio

*   **Objetivo:** Assegurar que o chatbot esteja alinhado com os objetivos estratégicos do banco, gerando valor e otimizando os processos de negócio.
*   **Metodologia:** Análise de KPIs de negócio, avaliação do impacto na redução de custos e satisfação do cliente, reuniões de feedback com stakeholders.
*   **Métricas de Sucesso:** Redução de Custos Operacionais (10% em 6 meses), Aumento da Satisfação do Cliente (5 pontos no NPS), Otimização do Tempo dos Atendentes Humanos (redução de 20% no volume de chamadas de baixo valor), Taxa de Resolução no Primeiro Contato (>70%), ROI positivo em 12 meses.

## 5. Desenvolvimento Contínuo

O chatbot será um produto em constante evolução. A análise contínua de logs de conversas, feedbacks de usuários e métricas de desempenho será crucial para identificar oportunidades de aprimoramento, refinar funcionalidades e desenvolver novas capacidades, garantindo a relevância e eficácia do chatbot a longo prazo.

## 6. Considerações

Este projeto demonstra a capacidade de conceber, desenvolver e validar um chatbot de atendimento ao cliente robusto e eficiente para o setor bancário. A combinação de uma arquitetura bem definida, implementação técnica sólida em Python e uma estratégia abrangente de testes e validação assegura um produto de alta qualidade, capaz de entregar valor significativo tanto para o banco quanto para seus clientes.
