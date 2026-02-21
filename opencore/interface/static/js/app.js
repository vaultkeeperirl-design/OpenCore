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
        if (sendBtn.disabled) return;

        const text = messageInput.value.trim();
        if (!text) return;

        const originalBtnText = sendBtn.innerText;

        // Add user message
        addMessage('user', text);
        messageInput.value = '';

        sendBtn.innerText = 'WAIT...';
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

            // Add assistant message with typing effect
            await addMessageWithTypingEffect('assistant', data.response);

            // Update agent list
            updateAgents(data.agents);

        } catch (error) {
            removeMessage(typingId);
            addMessage('assistant', `SYSTEM_ERROR: ${error.message}`, true);
        } finally {
            sendBtn.innerText = originalBtnText;
            sendBtn.disabled = false;
            messageInput.focus();
        }
    }

    function addMessage(role, text, isError = false) {
        const wrapper = createMessageWrapper(role, isError);
        const content = wrapper.querySelector('.message-content');

        if (text.includes("Executing") || text.includes("Error:")) {
             content.innerHTML = `<span style="color:var(--neon-blue)">> </span>` + text.replace(/\n/g, '<br>');
             content.style.fontFamily = "'Fira Code', monospace";
        } else {
             content.innerText = text;
        }

        messagesDiv.appendChild(wrapper);
        scrollToBottom();
        return wrapper.id;
    }

    async function addMessageWithTypingEffect(role, text) {
        const wrapper = createMessageWrapper(role, false);
        const content = wrapper.querySelector('.message-content');

        // A11y: Mark as busy while typing so screen readers wait
        wrapper.setAttribute('aria-busy', 'true');

        messagesDiv.appendChild(wrapper);
        scrollToBottom();

        // Terminal typing effect
        content.innerText = '';
        const chars = text.split('');
        for (let i = 0; i < chars.length; i++) {
            content.textContent += chars[i];
            // Occasionally scroll to bottom during long messages
            if (i % 50 === 0) scrollToBottom();
            // Random delay for realism
            await new Promise(r => setTimeout(r, Math.random() * 10 + 5));
        }

        // A11y: Mark as finished
        wrapper.setAttribute('aria-busy', 'false');
        scrollToBottom();
    }

    function createMessageWrapper(role, isError) {
        const wrapper = document.createElement('div');
        wrapper.className = `message-wrapper ${role}`;
        wrapper.id = 'msg-' + Date.now();

        const header = document.createElement('div');
        header.className = 'message-header';

        if (role === 'user') {
            header.innerHTML = `USER_ID: ME <div class="agent-avatar" style="border-color:var(--neon-pink); color:var(--neon-pink); box-shadow:0 0 5px var(--neon-pink)">U</div>`;
            wrapper.style.alignItems = 'flex-end';
        } else {
            header.innerHTML = `<div class="agent-avatar">AI</div> SYSTEM_CORE: MANAGER`;
        }

        const content = document.createElement('div');
        content.className = 'message-content';
        if (isError) {
            content.style.borderColor = 'var(--error)';
            content.style.color = 'var(--error)';
            content.style.textShadow = '0 0 5px var(--error)';
        }

        wrapper.appendChild(header);
        wrapper.appendChild(content);
        return wrapper;
    }

    function addTypingIndicator() {
        const wrapper = document.createElement('div');
        wrapper.className = 'message-wrapper assistant';
        wrapper.id = 'typing-' + Date.now();

        // A11y: Hide typing indicator from screen readers
        wrapper.setAttribute('aria-hidden', 'true');

        const header = document.createElement('div');
        header.className = 'message-header';
        header.innerHTML = '<div class="agent-avatar">AI</div> PROCESSING...';

        const content = document.createElement('div');
        content.className = 'message-content';
        content.style.padding = '10px';
        content.innerHTML = '<div class="typing-indicator"><div class="typing-block"></div><div class="typing-block"></div><div class="typing-block"></div></div>';

        wrapper.appendChild(header);
        wrapper.appendChild(content);
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

            // Determine role styling
            let role = 'UNIT';
            if (agentName === 'Manager') role = 'ORCHESTRATOR';
            else if (agentName.includes('Coder')) role = 'DEV_UNIT';

            li.innerHTML = `
                <div class="agent-avatar">${initials}</div>
                <div class="agent-info">
                    <span class="agent-name">${agentName}</span>
                    <span class="agent-role">[${role}]</span>
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
