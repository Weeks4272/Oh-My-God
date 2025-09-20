// Universal AI Assistant - Simplified Implementation
let universalAI;
let currentMode = 'coding';

class UniversalAI {
    constructor() {
        this.conversationHistory = [];
    }

    async generateResponse(userInput, mode = 'coding') {
        try {
            const response = await fetch('http://localhost:8000/api/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    prompt: userInput,
                    language: mode,
                    context: '',
                    max_tokens: 1000,
                    temperature: 0.7,
                }),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();

            if (data.success && data.data.code) {
                this.updateConversationHistory(userInput, data.data.code);
                return {
                    type: 'ai',
                    content: data.data.code,
                };
            } else {
                throw new Error(data.error || 'Failed to get a valid response from the AI.');
            }

        } catch (error) {
            console.error('Error generating response:', error);
            return {
                type: 'error',
                content: "I apologize, but I encountered an error processing your request. Please try again later.",
            };
        }
    }

    updateConversationHistory(userInput, aiResponse) {
        const entry = {
            timestamp: new Date().toISOString(),
            user: userInput,
            ai: aiResponse
        };
        this.conversationHistory.push(entry);
        if (this.conversationHistory.length > 50) {
            this.conversationHistory = this.conversationHistory.slice(-50);
        }
    }
}

function formatAIResponse(content) {
    let formatted = content
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/```([\s\S]*?)```/g, '<pre style="background: #0d1117; padding: 12px; border-radius: 6px; overflow-x: auto; margin: 8px 0; border: 1px solid #30363d; color: #c9d1d9;"><code>$1</code></pre>')
        .replace(/`(.*?)`/g, '<code style="background: #0d1117; padding: 2px 6px; border-radius: 3px; font-size: 13px; color: #c9d1d9;">$1</code>')
        .replace(/\n/g, '<br>');
    return formatted;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function addMessageToChat(type, content, containerId) {
    const chatMessages = document.getElementById(containerId);
    if (!chatMessages) {
        console.error('Chat messages container not found:', containerId);
        return;
    }

    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    const timestamp = new Date().toLocaleTimeString();

    if (type === 'user') {
        messageDiv.innerHTML = `
            <div class="message-content">${escapeHtml(content)}</div>
            <div class="message-time" style="font-size: 12px; color: #8b949e; margin-top: 4px;">${timestamp}</div>
        `;
    } else {
        messageDiv.innerHTML = `
            <div class="message-content">${formatAIResponse(content)}</div>
            <div class="message-time" style="font-size: 12px; color: #8b949e; margin-top: 4px;">${timestamp}</div>
        `;
    }

    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function showTypingIndicator(containerId) {
    const chatMessages = document.getElementById(containerId);
    if (!chatMessages) return;

    const typingDiv = document.createElement('div');
    typingDiv.className = 'message ai typing-indicator';
    typingDiv.id = 'typingIndicator';
    typingDiv.innerHTML = `
        <div class="message-content">
            <em>Thinking...</em>
        </div>
    `;
    chatMessages.appendChild(typingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function hideTypingIndicator() {
    const typingIndicator = document.getElementById('typingIndicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

async function sendMessage() {
    const chatInput = document.getElementById('mainChatInput');
    const message = chatInput.value.trim();
    if (!message) return;

    chatInput.value = '';
    addMessageToChat('user', message, 'mainChatMessages');
    showTypingIndicator('mainChatMessages');

    try {
        const response = await universalAI.generateResponse(message, currentMode);
        hideTypingIndicator();
        addMessageToChat(response.type, response.content, 'mainChatMessages');
    } catch (error) {
        console.error('Error generating response:', error);
        hideTypingIndicator();
        addMessageToChat('error', 'Sorry, I encountered an error processing your request.', 'mainChatMessages');
    }
}

document.addEventListener('DOMContentLoaded', function() {
    universalAI = new UniversalAI();

    const sendButton = document.getElementById('mainSendMessage');
    const chatInput = document.getElementById('mainChatInput');

    if (sendButton && chatInput) {
        sendButton.addEventListener('click', sendMessage);
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
    }

    document.querySelectorAll('.mode-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.mode-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            currentMode = this.dataset.mode;
        });
    });
});