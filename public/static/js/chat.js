/**
 * UrbanAdvisor AI - Real Estate Market Advisory Chatbot Controller
 * Manages floating widget state, context awareness, and natural dialogue.
 */

window.latestValuationContext = null;

document.addEventListener('DOMContentLoaded', () => {
    initChatDrawer();
    initChatForm();
    initSuggestionChips();
});

function initChatDrawer() {
    const floatBtn = document.getElementById('advisorFloatingBtn');
    const drawer = document.getElementById('advisorChatDrawer');
    const closeBtn = document.getElementById('advisorCloseBtn');
    const resetBtn = document.getElementById('advisorResetBtn');

    if (!floatBtn || !drawer) return;

    floatBtn.addEventListener('click', () => {
        drawer.classList.toggle('active');
        if (drawer.classList.contains('active')) {
            updateContextBanner();
            document.getElementById('advisorInput')?.focus();
            scrollToBottom();
        }
    });

    if (closeBtn) {
        closeBtn.addEventListener('click', () => drawer.classList.remove('active'));
    }

    if (resetBtn) {
        resetBtn.addEventListener('click', resetConversation);
    }
}

function updateContextBanner() {
    const banner = document.getElementById('advisorContextBanner');
    if (!banner) return;

    if (window.latestValuationContext) {
        const c = window.latestValuationContext;
        banner.style.display = 'flex';
        banner.innerHTML = `
            <span><i class="bi bi-geo-alt-fill text-accent me-1"></i> Active: <strong>${c.location}</strong> (${c.area})</span>
            <span class="text-white"><strong>${c.price_inr}</strong></span>
        `;
    } else {
        banner.style.display = 'none';
    }
}

function initChatForm() {
    const form = document.getElementById('advisorForm');
    const input = document.getElementById('advisorInput');

    if (!form || !input) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const msg = input.value.trim();
        if (!msg) return;

        input.value = '';
        appendMessage('user', msg);
        showTypingIndicator();

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: msg,
                    context: window.latestValuationContext
                })
            });

            const data = await response.json();
            removeTypingIndicator();
            appendMessage('assistant', data.reply || 'Apologies, could you rephrase your question?');

        } catch (err) {
            console.error('Chat error:', err);
            removeTypingIndicator();
            appendMessage('assistant', 'Unable to reach the advisory server. Please check your network connection.');
        }
    });
}

function initSuggestionChips() {
    const chips = document.querySelectorAll('.advisor-chip');
    chips.forEach(chip => {
        chip.addEventListener('click', () => {
            const promptText = chip.getAttribute('data-prompt');
            const input = document.getElementById('advisorInput');
            if (input) {
                input.value = promptText;
                document.getElementById('advisorForm')?.dispatchEvent(new Event('submit'));
            }
        });
    });
}

function appendMessage(sender, text) {
    const body = document.getElementById('advisorMessagesBody');
    if (!body) return;

    const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const formattedText = formatChatMessage(text);

    const msgDiv = document.createElement('div');
    msgDiv.className = `advisor-msg ${sender}`;
    msgDiv.innerHTML = `
        <div class="msg-bubble">${formattedText}</div>
        <div class="msg-time">${timeStr}</div>
    `;

    body.appendChild(msgDiv);
    scrollToBottom();
}

function formatChatMessage(text) {
    if (!text) return '';
    // Format bold **text**
    let formatted = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    // Format bullet points
    formatted = formatted.replace(/\n• (.*?)(?=\n|$)/g, '<br>• $1');
    // Format newlines
    formatted = formatted.replace(/\n\n/g, '<p></p>');
    formatted = formatted.replace(/\n/g, '<br>');
    return formatted;
}

function showTypingIndicator() {
    const body = document.getElementById('advisorMessagesBody');
    if (!body) return;

    const typingDiv = document.createElement('div');
    typingDiv.id = 'advisorTypingIndicator';
    typingDiv.className = 'advisor-msg assistant';
    typingDiv.innerHTML = `
        <div class="msg-bubble" style="padding: 10px 16px;">
            <div class="typing-dots">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        </div>
    `;
    body.appendChild(typingDiv);
    scrollToBottom();
}

function removeTypingIndicator() {
    const typing = document.getElementById('advisorTypingIndicator');
    if (typing) typing.remove();
}

function resetConversation() {
    const body = document.getElementById('advisorMessagesBody');
    if (!body) return;

    body.innerHTML = `
        <div class="advisor-msg assistant">
            <div class="msg-bubble">
                <p>Hello! I am <strong>Aarav Mehta</strong>, your personal real estate market advisor.</p>
                <p>Whether you're looking to verify if an appraisal price is fair, evaluate neighborhood capital growth, or structure a winning negotiation offer, I'm here to assist. Ask me anything below!</p>
            </div>
            <div class="msg-time">Just now</div>
        </div>
    `;
    scrollToBottom();
}

function scrollToBottom() {
    const body = document.getElementById('advisorMessagesBody');
    if (body) {
        body.scrollTop = body.scrollHeight;
    }
}
