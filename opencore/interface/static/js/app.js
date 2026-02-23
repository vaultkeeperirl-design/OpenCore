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

        const originalBtnHTML = sendBtn.innerHTML;

        // Add user message
        addMessage('user', text);
        messageInput.value = '';

        // UX: Show spinner and accessible state
        sendBtn.innerHTML = '<span class="spinner" aria-hidden="true"></span> PROCESSING';
        sendBtn.setAttribute('aria-busy', 'true');
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
            sendBtn.innerHTML = originalBtnHTML;
            sendBtn.removeAttribute('aria-busy');
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

        // Create accessible structure:
        // 1. Full text for screen readers (hidden visually)
        const srText = document.createElement('span');
        srText.style.cssText = 'position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0;';
        srText.textContent = text;

        // 2. Animated text for sighted users (hidden from screen readers)
        const visualText = document.createElement('span');
        visualText.setAttribute('aria-hidden', 'true');

        content.appendChild(srText);
        content.appendChild(visualText);

        messagesDiv.appendChild(wrapper);
        scrollToBottom();

        // Terminal typing effect
        const chars = text.split('');
        for (let i = 0; i < chars.length; i++) {
            visualText.textContent += chars[i];
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

    // --- Configuration Modal Logic ---
    const settingsToggle = document.getElementById('settings-toggle');
    const settingsModal = document.getElementById('settings-modal');
    const closeButtons = document.querySelectorAll('.close-modal');
    const configForm = document.getElementById('config-form');
    const llmModelSelect = document.getElementById('llm-model');
    const customModelInput = document.getElementById('custom-model');
    const saveStatus = document.getElementById('save-status');

    if (settingsToggle) {
        settingsToggle.addEventListener('click', async () => {
            settingsModal.style.display = 'flex';
            settingsModal.setAttribute('aria-hidden', 'false');
            await loadConfig();
        });

        closeButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                settingsModal.style.display = 'none';
                settingsModal.setAttribute('aria-hidden', 'true');
            });
        });

        // Close on outside click
        settingsModal.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal-overlay')) {
                settingsModal.style.display = 'none';
                settingsModal.setAttribute('aria-hidden', 'true');
            }
        });

        llmModelSelect.addEventListener('change', () => {
            if (llmModelSelect.value === 'custom') {
                customModelInput.style.display = 'block';
            } else {
                customModelInput.style.display = 'none';
            }
        });

        configForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            saveStatus.textContent = "Saving...";
            saveStatus.className = "status-message";

            const formData = new FormData(configForm);
            const data = Object.fromEntries(formData.entries());

            // Handle custom model
            if (data.LLM_MODEL === 'custom') {
                 data.LLM_MODEL = data.CUSTOM_MODEL;
            }

            try {
                const res = await fetch('/config', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                const result = await res.json();

                if (result.status === 'success') {
                    saveStatus.textContent = "Configuration saved. System reloaded.";
                    saveStatus.className = "status-message status-success";
                    setTimeout(() => {
                        settingsModal.style.display = 'none';
                        saveStatus.textContent = "";
                    }, 1500);
                } else {
                    saveStatus.textContent = "Error: " + result.message;
                    saveStatus.className = "status-message status-error";
                }
            } catch (error) {
                saveStatus.textContent = "Network Error: " + error.message;
                saveStatus.className = "status-message status-error";
            }
        });
    }

    async function loadConfig() {
        try {
            const res = await fetch('/config');
            const config = await res.json();

            // Populate fields
            const options = Array.from(llmModelSelect.options).map(o => o.value);
            if (options.includes(config.LLM_MODEL)) {
                llmModelSelect.value = config.LLM_MODEL;
                customModelInput.style.display = 'none';
            } else {
                llmModelSelect.value = 'custom';
                customModelInput.value = config.LLM_MODEL;
                customModelInput.style.display = 'block';
            }

            if (config.VERTEX_PROJECT) document.getElementById('vertex-project').value = config.VERTEX_PROJECT;
            if (config.VERTEX_LOCATION) document.getElementById('vertex-location').value = config.VERTEX_LOCATION;
            if (config.OLLAMA_API_BASE) document.getElementById('ollama-base').value = config.OLLAMA_API_BASE;

            // Status indicators
            document.getElementById('openai-status').textContent = config.HAS_OPENAI_KEY ? " (Key Set)" : "";
            document.getElementById('anthropic-status').textContent = config.HAS_ANTHROPIC_KEY ? " (Key Set)" : "";
            document.getElementById('dashscope-status').textContent = config.HAS_DASHSCOPE_KEY ? " (Key Set)" : "";
            document.getElementById('gemini-status').textContent = config.HAS_GEMINI_KEY ? " (Key Set)" : "";
            document.getElementById('groq-status').textContent = config.HAS_GROQ_KEY ? " (Key Set)" : "";

        } catch (e) {
            console.error("Failed to load config", e);
        }
    }
});
