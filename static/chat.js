// Chat Interface JavaScript
class ChatInterface {
    constructor() {
        this.messages = [];
        this.agents = {
            spacex: {
                name: 'SpaceX Agent',
                status: 'online',
                icon: '🚀',
                description: 'Handles SpaceX launch data and mission information'
            },
            weather: {
                name: 'Weather Agent',
                status: 'online',
                icon: '🌍',
                description: 'Provides weather data and forecasts'
            },
            summary: {
                name: 'Summary Agent',
                status: 'online',
                icon: '📝',
                description: 'Creates intelligent summaries and analysis'
            },
            google_adk: {
                name: 'Google ADK',
                status: 'online',
                icon: '🧠',
                description: 'AI-powered coordination and validation'
            },
            system: {
                name: 'System',
                status: 'online',
                icon: '⚙️',
                description: 'System messages and coordination'
            }
        };
        this.currentAgent = null;
        this.isTyping = false;        this.autoScroll = true;
        
        this.init();
        this.startUptime();
    }

    startUptime() {
        this.startTime = Date.now();
        setInterval(() => {
            const uptimeElement = document.getElementById('uptime');
            if (uptimeElement) {
                const elapsed = Date.now() - this.startTime;
                const hours = Math.floor(elapsed / 3600000);
                const minutes = Math.floor((elapsed % 3600000) / 60000);
                const seconds = Math.floor((elapsed % 60000) / 1000);
                uptimeElement.textContent = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
            }
        }, 1000);
    }

    init() {
        this.setupEventListeners();
        this.renderAgents();
        this.addSystemMessage('Welcome to the Multi-Agent AI System! Ask me anything about SpaceX launches, weather, or let me coordinate multiple agents for complex tasks.');
        this.setupQuickActions();
    }

    setupEventListeners() {
        // Send button click
        document.getElementById('send-button').addEventListener('click', () => {
            this.sendMessage();
        });

        // Enter key to send
        document.getElementById('chat-input').addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });        // Auto-resize textarea
        document.getElementById('chat-input').addEventListener('input', (e) => {
            this.autoResizeTextarea(e.target);
        });
    }

    autoResizeTextarea(textarea) {
        textarea.style.height = 'auto';
        textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
    }    renderAgents() {
        const agentList = document.getElementById('agent-list');
        agentList.innerHTML = '';

        Object.entries(this.agents).forEach(([key, agent]) => {
            const agentCard = document.createElement('div');
            agentCard.className = 'agent-card';
            agentCard.innerHTML = `
                <div class="agent-header">
                    <div class="agent-name">
                        <span class="agent-status ${agent.status}"></span>
                        <span>${agent.name}</span>
                    </div>
                    <span class="agent-icon">${agent.icon}</span>
                </div>
                <p class="agent-description">${agent.description}</p>
            `;
            
            agentCard.addEventListener('click', () => {
                this.selectAgent(key, agentCard);
            });
            
            agentList.appendChild(agentCard);
        });
    }

    selectAgent(agentKey, cardElement) {
        // Remove active class from all cards
        document.querySelectorAll('.agent-card').forEach(card => {
            card.classList.remove('active');
        });
        
        // Add active class to selected card
        cardElement.classList.add('active');
        
        this.currentAgent = agentKey;
        this.addSystemMessage(`🎯 Now focusing on ${this.agents[agentKey].name}. Ask specific questions about ${agentKey === 'spacex' ? 'SpaceX missions and launches' : agentKey === 'weather' ? 'weather conditions and forecasts' : agentKey === 'summary' ? 'summaries and analysis' : 'AI coordination and validation'}.`);
    }

    setupQuickActions() {
        const quickActions = [
            { text: '🚀 Find next SpaceX launch', icon: 'fas fa-rocket' },
            { text: '🌤️ Check weather conditions', icon: 'fas fa-cloud-sun' },
            { text: '📊 Analyze launch readiness', icon: 'fas fa-chart-line' },
            { text: '📝 Get mission summary', icon: 'fas fa-file-alt' },
            { text: '💾 Show raw data', icon: 'fas fa-database' }
        ];

        const quickActionsContainer = document.getElementById('quick-actions');
        
        // Keep the auto-scroll button
        const autoScrollBtn = document.getElementById('auto-scroll-btn');
        
        quickActions.forEach(action => {
            const button = document.createElement('button');
            button.className = 'quick-action';
            button.innerHTML = `<i class="${action.icon}"></i> ${action.text}`;
            button.addEventListener('click', () => {
                document.getElementById('chat-input').value = action.text.replace(/[🚀🌤️📊📝💾]\s/, '');
                this.sendMessage();
            });
            quickActionsContainer.appendChild(button);
        });
    }

    async sendMessage() {
        const input = document.getElementById('chat-input');
        const message = input.value.trim();
        
        if (!message) return;

        // Add user message
        this.addMessage(message, 'user');
        input.value = '';
        input.style.height = 'auto';

        // Show typing indicator
        this.showTyping();

        try {
            // Send to backend
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    agent: this.currentAgent
                })
            });

            const data = await response.json();
            
            // Hide typing indicator
            this.hideTyping();

            if (data.success) {
                this.processAgentResponse(data);
            } else {
                this.addMessage(`Error: ${data.error}`, 'system');
            }
        } catch (error) {
            this.hideTyping();
            this.addMessage(`Network error: ${error.message}`, 'system');
        }
   }

    sendQuickMessage(message) {
        document.getElementById('chat-input').value = message;
        this.sendMessage();
    }

    processAgentResponse(data) {
        // Add agent responses based on the workflow
        if (data.workflow_logs) {
            data.workflow_logs.forEach(log => {
                if (log.agent && this.agents[log.agent]) {
                    this.updateAgentStatus(log.agent, 'busy');
                    this.addMessage(log.message, 'agent', log.agent);
                    setTimeout(() => {
                        this.updateAgentStatus(log.agent, 'online');
                    }, 1000);
                } else {
                    this.addMessage(log.message, 'system');
                }
            });
        }

        // Add final result
        if (data.result) {
            this.addMessage(data.result.summary || 'Task completed successfully!', 'agent', 'summary');
            
            // Add raw data if available
            if (data.result.raw_data) {
                this.addJsonMessage(data.result.raw_data, 'Raw API Data');
            }
        }
    }

    addMessage(content, type = 'system', agent = null) {
        const message = {
            id: Date.now() + Math.random(),
            content,
            type,
            agent,
            timestamp: new Date()
        };

        this.messages.push(message);
        this.renderMessage(message);
        this.scrollToBottom();
    }

    addSystemMessage(content) {
        this.addMessage(content, 'system');
    }    addJsonMessage(data, title = 'JSON Data') {
        const jsonContent = `
            <div class="json-viewer">
                <div class="json-header">
                    <strong>${title}</strong>
                    <button onclick="copyToClipboard('${JSON.stringify(data).replace(/'/g, "\\'")}', this)" class="message-action">
                        <i class="fas fa-copy"></i> Copy JSON
                    </button>
                </div>
                <pre>${JSON.stringify(data, null, 2)}</pre>
            </div>
        `;
        this.addMessage(jsonContent, 'system');
    }renderMessage(message) {
        const messagesContainer = document.getElementById('chat-messages');
        const messageElement = document.createElement('div');
        messageElement.className = `message ${message.type}`;
        messageElement.setAttribute('data-message-id', message.id);

        const agent = message.agent ? this.agents[message.agent] : null;
        const avatar = agent ? agent.icon : (message.type === 'user' ? '👤' : '⚙️');
        const senderName = agent ? agent.name : (message.type === 'user' ? 'You' : 'System');

        messageElement.innerHTML = `
            <div class="message-avatar">
                ${avatar}
            </div>
            <div class="message-content">
                <div class="message-bubble">
                    <div class="message-text">${message.content}</div>
                </div>
                <div class="message-meta">
                    <span>${senderName}</span>
                    <span>•</span>
                    <span>${this.formatTime(message.timestamp)}</span>
                </div>
                <div class="message-actions">
                    <button class="message-action" onclick="copyMessage('${message.id}')">
                        <i class="fas fa-copy"></i> Copy
                    </button>
                    ${message.type !== 'user' ? `
                        <button class="message-action" onclick="regenerateResponse('${message.id}')">
                            <i class="fas fa-redo"></i> Retry
                        </button>
                    ` : ''}
                </div>
            </div>
        `;

        messagesContainer.appendChild(messageElement);
        
        // Animate message appearance
        setTimeout(() => {
            messageElement.style.opacity = '1';
        }, 50);
    }

    showTyping() {
        if (this.isTyping) return;
        
        this.isTyping = true;
        const typingIndicator = document.getElementById('typing-indicator');
        typingIndicator.classList.add('show');
        this.scrollToBottom();
    }

    hideTyping() {
        this.isTyping = false;
        const typingIndicator = document.getElementById('typing-indicator');
        typingIndicator.classList.remove('show');
    }

    updateAgentStatus(agentKey, status) {
        if (this.agents[agentKey]) {
            this.agents[agentKey].status = status;
            this.renderAgents();
        }
    }

    scrollToBottom() {
        if (!this.autoScroll) return;
        
        const messagesContainer = document.getElementById('chat-messages');
        setTimeout(() => {
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }, 100);
    }

    formatTime(date) {
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }

    clearMessages() {
        this.messages = [];
        document.getElementById('chat-messages').innerHTML = '';
        this.addSystemMessage('Chat cleared. How can I help you?');
    }

    // Export chat as JSON
    exportChat() {
        const chatData = {
            messages: this.messages,
            timestamp: new Date().toISOString(),
            agents: this.agents
        };

        const blob = new Blob([JSON.stringify(chatData, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `chat-export-${new Date().toISOString().slice(0, 10)}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }
}

// Global functions for message actions
function copyMessage(messageId) {
    const message = chatInterface.messages.find(m => m.id == messageId);
    if (message) {
        navigator.clipboard.writeText(message.content.replace(/<[^>]*>/g, ''));
        showToast('Message copied to clipboard');
    }
}

function copyToClipboard(text, button) {
    navigator.clipboard.writeText(text);
    const originalText = button.innerHTML;
    button.innerHTML = '<i class="fas fa-check"></i> Copied!';
    setTimeout(() => {
        button.innerHTML = originalText;
    }, 2000);
}

function regenerateResponse(messageId) {
    // Find the user message before this response
    const messageIndex = chatInterface.messages.findIndex(m => m.id == messageId);
    if (messageIndex > 0) {
        const userMessage = chatInterface.messages[messageIndex - 1];
        if (userMessage.type === 'user') {
            // Resend the user message
            document.getElementById('chat-input').value = userMessage.content;
            chatInterface.sendMessage();
        }
    }
}

function showToast(message) {
    // Simple toast notification
    const toast = document.createElement('div');
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: rgba(0, 0, 0, 0.8);
        color: white;
        padding: 12px 20px;
        border-radius: 8px;
        z-index: 10000;
        font-size: 14px;
    `;
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        document.body.removeChild(toast);
    }, 3000);
}

// Initialize chat interface when DOM is loaded
let chatInterface;
document.addEventListener('DOMContentLoaded', () => {
    chatInterface = new ChatInterface();
});

// Auto-scroll toggle
function toggleAutoScroll() {
    chatInterface.autoScroll = !chatInterface.autoScroll;
    const button = document.getElementById('auto-scroll-btn');
    
    if (chatInterface.autoScroll) {
        button.innerHTML = '<i class="fas fa-arrows-alt-v"></i><span>Auto-scroll</span>';
        button.classList.add('active');
    } else {
        button.innerHTML = '<i class="fas fa-hand-paper"></i><span>Manual scroll</span>';
        button.classList.remove('active');
    }
}
