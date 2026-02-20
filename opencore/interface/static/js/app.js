document.addEventListener('DOMContentLoaded', () => {
    const messageInput = document.getElementById('message-input');
    const messagesDiv = document.getElementById('messages');
    const sendBtn = document.getElementById('send-btn');
    const agentList = document.getElementById('agent-list');

    // Focus input on load
    messageInput.focus();

    messageInput.addEventListener('keypress', (event) => {
        if (event.key === 'Enter') {
            sendMessage();
        }
    });

    sendBtn.addEventListener('click', sendMessage);

    async function sendMessage() {
        const text = messageInput.value.trim();
        if (!text) return;

        // Add user message
        addMessage('user', text);
        messageInput.value = '';
        sendBtn.disabled = true;

        // Add typing indicator
        const typingId = addTypingIndicator();

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: text })
            });

            if (!response.ok) {
                throw new Error(`Error: ${response.statusText}`);
            }

            const data = await response.json();

            // Remove typing indicator
            removeMessage(typingId);

            // Add assistant message
            addMessage('assistant', data.response);

            // Update agent list
            updateAgents(data.agents);

        } catch (error) {
            removeMessage(typingId);
            addMessage('assistant', `Error: ${error.message}`, true);
        } finally {
            sendBtn.disabled = false;
            messageInput.focus();
        }
    }

    function addMessage(role, text, isError = false) {
        const wrapper = document.createElement('div');
        wrapper.className = `message-wrapper ${role}`;

        const header = document.createElement('div');
        header.className = 'message-header';

        const avatar = document.createElement('div');
        avatar.className = 'agent-avatar';
        avatar.style.width = '24px';
        avatar.style.height = '24px';
        avatar.style.fontSize = '10px';

        if (role === 'user') {
            header.innerText = 'You';
            avatar.innerText = 'ME';
            header.appendChild(avatar); // Right aligned for user
            wrapper.style.alignItems = 'flex-end';
        } else {
            avatar.innerText = 'AI';
            header.prepend(avatar); // Left aligned for assistant
            header.innerHTML += ' <span>Manager</span>';
        }

        const content = document.createElement('div');
        content.className = 'message-content';
        if (isError) content.style.border = '1px solid var(--error)';

        // Check for tool outputs in text (simple heuristic for now)
        // If the text contains specific markers or JSON-like structures, format them
        if (text.includes("Executing") || text.includes("Error:")) {
             // Basic formatting for tool logs
             content.innerHTML = text.replace(/\n/g, '<br>');
        } else {
             content.innerText = text;
        }

        wrapper.appendChild(header);
        wrapper.appendChild(content);

        messagesDiv.appendChild(wrapper);
        scrollToBottom();
        return wrapper.id = 'msg-' + Date.now();
    }

    function addTypingIndicator() {
        const wrapper = document.createElement('div');
        wrapper.className = 'message-wrapper assistant';
        wrapper.id = 'typing-' + Date.now();

        const header = document.createElement('div');
        header.className = 'message-header';
        header.innerHTML = '<div class="agent-avatar" style="width:24px;height:24px;font-size:10px;">AI</div> <span>Manager is thinking...</span>';

        const indicator = document.createElement('div');
        indicator.className = 'typing-indicator';
        indicator.innerHTML = '<div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div>';

        wrapper.appendChild(header);
        wrapper.appendChild(indicator);
        messagesDiv.appendChild(wrapper);
        scrollToBottom();
        return wrapper.id;
    }

    function removeMessage(id) {
        const el = document.getElementById(id);
        if (el) el.remove();
    }

    function scrollToBottom() {
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }

    function updateAgents(agents) {
        agentList.innerHTML = '';
        agents.forEach(agentName => {
            const li = document.createElement('li');
            li.className = 'agent-item';

            // Generate initials
            const initials = agentName.substring(0, 2).toUpperCase();

            // Determine role (mock logic for now, ideally backend sends full object)
            let role = 'Agent';
            if (agentName === 'Manager') role = 'Orchestrator';
            else if (agentName.includes('Coder')) role = 'Developer';

            li.innerHTML = `
                <div class="agent-avatar">${initials}</div>
                <div class="agent-info">
                    <span class="agent-name">${agentName}</span>
                    <span class="agent-role">${role}</span>
                </div>
                <div class="status-dot"></div>
            `;
            agentList.appendChild(li);
        });
    }

    // Initial population
    fetch('/agents')
        .then(res => res.json())
        .then(data => updateAgents(data.agents))
        .catch(console.error);
});
