// Chat Interface JavaScript
class ChatInterface {
    constructor() {
        this.messages = [];
        this.agents = {
            spacex: {
                name: 'SpaceX Agent',
                status: 'online',
                icon: this.getSVGIcon('rocket'),
                description: 'Handles SpaceX launch data and mission information'
            },
            weather: {
                name: 'Weather Agent',
                status: 'online',
                icon: this.getSVGIcon('weather'),
                description: 'Provides weather data and forecasts'
            },
            summary: {
                name: 'Summary Agent',
                status: 'online',
                icon: this.getSVGIcon('document'),
                description: 'Creates intelligent summaries and analysis'
            },
            satellite_data: {
                name: 'Satellite Data Agent',
                status: 'online',
                icon: this.getSVGIcon('satellite'),
                description: 'Fetches satellite tracking and orbital data'
            },
            anomalies_detection: {
                name: 'Anomalies Detection Agent',
                status: 'online',
                icon: this.getSVGIcon('alert'),
                description: 'Detects anomalies in space data and launch conditions'
            },
            google_adk: {
                name: 'Google ADK',
                status: 'online',
                icon: this.getSVGIcon('brain'),
                description: 'AI-powered coordination and validation'
            },
            system: {
                name: 'System',
                status: 'online',
                icon: this.getSVGIcon('settings'),
                description: 'System messages and coordination'
            }
        };
        this.currentAgent = null;
        this.isTyping = false;
        this.autoScroll = true;
        
        this.init();
        this.startUptime();
    }

    getSVGIcon(type) {
        const icons = {
            rocket: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 0 0 0-2.91-.09z"></path>
                <path d="m12 15-3-3a22 22 0 0 1 2-3.95A12.88 12.88 0 0 1 22 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 0 1-4 2z"></path>
                <path d="M9 12H4s.55-3.03 2-4c1.62-1.08 5 0 5 0"></path>
                <path d="M12 15v5s3.03-.55 4-2c1.08-1.62 0-5 0-5"></path>
            </svg>`,
            weather: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M17.5 19H9a7 7 0 1 1 6.71-9h1.79a4.5 4.5 0 1 1 0 9Z"></path>
                <path d="M22 10a3 3 0 0 0-3-3h-2.207a5.502 5.502 0 0 0-10.702.5"></path>
            </svg>`,
            document: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                <polyline points="14 2 14 8 20 8"></polyline>
                <line x1="16" y1="13" x2="8" y2="13"></line>
                <line x1="16" y1="17" x2="8" y2="17"></line>
                <polyline points="10 9 9 9 8 9"></polyline>
            </svg>`,
            brain: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96.44L2 10a2.5 2.5 0 0 1 0-4.96A2.5 2.5 0 0 1 4.5 2Z"></path>
                <path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96.44L22 10a2.5 2.5 0 0 0 0-4.96A2.5 2.5 0 0 0 19.5 2Z"></path>
            </svg>`,
            settings: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"></path>
                <circle cx="12" cy="12" r="3"></circle>
            </svg>`,
            user: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                <circle cx="12" cy="7" r="4"></circle>
            </svg>`,
            robot: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
                <circle cx="12" cy="16" r="1"></circle>
                <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
            </svg>`,
            satellite: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="3"></circle>
                <path d="M12 1v6m0 6v6M5.64 5.64l4.24 4.24m4.24 4.24l4.24 4.24M1 12h6m6 0h6M5.64 18.36l4.24-4.24m4.24-4.24l4.24-4.24"></path>
            </svg>`,
            alert: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"></path>
                <line x1="12" y1="9" x2="12" y2="13"></line>
                <line x1="12" y1="17" x2="12.01" y2="17"></line>
            </svg>`
        };
        return icons[type] || icons.settings;
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
        this.addSystemMessage('Welcome to INTOSPACE AI! Ask me anything about SpaceX launches, weather, satellite tracking, anomaly detection, or let me coordinate multiple agents for complex space-related tasks.');
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
            { text: 'Find next SpaceX launch', icon: 'fas fa-rocket' },
            { text: 'Check weather conditions', icon: 'fas fa-cloud-sun' },
            { text: 'Analyze launch readiness', icon: 'fas fa-chart-line' },
            { text: 'Get mission summary', icon: 'fas fa-file-alt' },
            { text: 'Show raw data', icon: 'fas fa-database' }
        ];

        const quickActionsContainer = document.getElementById('quick-actions');
        
        // Keep the auto-scroll button
        const autoScrollBtn = document.getElementById('auto-scroll-btn');
        
        quickActions.forEach(action => {
            const button = document.createElement('button');
            button.className = 'quick-action';
            button.innerHTML = `<i class="${action.icon}"></i> ${action.text}`;
            button.addEventListener('click', () => {
                document.getElementById('chat-input').value = action.text;
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
    }    renderMessage(message) {
        const messagesContainer = document.getElementById('chat-messages');
        const messageElement = document.createElement('div');
        messageElement.className = `message ${message.type} message-bubble fade-in-up`;
        messageElement.setAttribute('data-message-id', message.id);
        messageElement.style.opacity = '0';
        messageElement.style.animationDelay = `${this.messages.length * 0.05}s`;

        const agent = message.agent ? this.agents[message.agent] : null;
        const avatar = agent ? agent.icon : (message.type === 'user' ? this.getSVGIcon('user') : this.getSVGIcon('settings'));
        const senderName = agent ? agent.name : (message.type === 'user' ? 'You' : 'System');

        messageElement.innerHTML = `
            <div class="message-avatar float-animation">
                ${avatar}
            </div>
            <div class="message-content">
                <div class="message-bubble space-hover">
                    <div class="message-text">${message.content}</div>
                </div>
                <div class="message-meta">
                    <span>${senderName}</span>
                    <span>•</span>
                    <span>${this.formatTime(message.timestamp)}</span>
                </div>
                <div class="message-actions">
                    <button class="message-action button-ripple" onclick="copyMessage('${message.id}')">
                        <i class="fas fa-copy"></i> Copy
                    </button>
                    ${message.type !== 'user' ? `
                        <button class="message-action button-ripple" onclick="regenerateResponse('${message.id}')">
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
    // Simple toast notification - white theme
    const toast = document.createElement('div');
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #000000;
        color: #ffffff;
        padding: 12px 20px;
        border-radius: 8px;
        border: 2px solid #000000;
        z-index: 10000;
        font-size: 14px;
        font-weight: 500;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
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
