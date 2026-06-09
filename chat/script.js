// JavaScript extracted from original chat.html inline script
const API_URL = "https://3a70f64384f8586f-dot-asia-southeast1.notebooks.googleusercontent.com/proxy/8000/chat";
const messagesContainer = document.getElementById("chat-messages");
const chatInput = document.getElementById("chat-input");
const threadInput = document.getElementById("thread-id");
const sendBtn = document.getElementById("send-btn");
const sendIcon = document.getElementById("send-icon");
const errorToast = document.getElementById("error-toast");
const toastMessage = document.getElementById("toast-message");

// Allow sending message by hitting Enter key
chatInput.addEventListener("keypress", function(event) {
    if (event.key === "Enter") {
        event.preventDefault();
        sendMessage();
    }
});

// Initialize unique thread ID on load
window.addEventListener("load", () => {
    const randomId = "thread_" + Math.floor(Math.random() * 900000 + 100000);
    threadInput.value = randomId;
});

function useSuggestion(text) {
    chatInput.value = text;
    chatInput.focus();
}

function showToast(message) {
    toastMessage.textContent = message;
    errorToast.classList.add("show");
    setTimeout(() => {
        errorToast.classList.remove("show");
    }, 4000);
}

function formatTime() {
    const now = new Date();
    let hours = now.getHours();
    let minutes = now.getMinutes();
    const ampm = hours >= 12 ? 'PM' : 'AM';
    hours = hours % 12;
    hours = hours ? hours : 12; // the hour '0' should be '12'
    minutes = minutes < 10 ? '0' + minutes : minutes;
    return `${hours}:${minutes} ${ampm}`;
}

function appendMessage(text, sender) {
    const messageRow = document.createElement("div");
    messageRow.classList.add("message-row", sender);

    const wrapper = document.createElement("div");
    wrapper.classList.add("message-wrapper");

    const avatarDiv = document.createElement("div");
    avatarDiv.classList.add("avatar");
    avatarDiv.innerHTML = sender === "bot"
        ? '<i class="fa-solid fa-robot"></i>'
        : '<i class="fa-solid fa-user"></i>';

    const contentDiv = document.createElement("div");
    contentDiv.classList.add("message-content");

    // Format potential line breaks, bold text, or inline code snippets
    let formattedText = escapeHTML(text)
        .replace(/\n/g, "<br>")
        .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
        .replace(/`(.*?)`/g, "<code>$1</code>");

    contentDiv.innerHTML = formattedText;

    const timeSpan = document.createElement("span");
    timeSpan.classList.add("timestamp");
    timeSpan.textContent = formatTime();
    contentDiv.appendChild(timeSpan);

    wrapper.appendChild(avatarDiv);
    wrapper.appendChild(contentDiv);
    messageRow.appendChild(wrapper);
    messagesContainer.appendChild(messageRow);

    // Auto scroll to bottom
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function escapeHTML(text) {
    return text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

async function sendMessage() {
    const queryText = chatInput.value.trim();
    const threadId = threadInput.value.trim() || "default_thread";

    if (!queryText) return;

    // Clear input and display user message
    chatInput.value = "";
    appendMessage(queryText, "user");

    // Disable input and button while loading
    chatInput.disabled = true;
    sendBtn.disabled = true;
    sendIcon.className = "fa-solid fa-spinner fa-spin";

    // Add loading/typing indicator bubble
    const loadingRow = document.createElement("div");
    loadingRow.classList.add("message-row", "bot");
    loadingRow.id = "typing-loader";
    loadingRow.innerHTML = `
        <div class="message-wrapper">
            <div class="avatar"><i class="fa-solid fa-robot"></i></div>
            <div>
                <div class="message-content">
                    <div class="typing-indicator">
                        <span></span>
                        <span></span>
                        <span></span>
                    </div>
                </div>
            </div>
        </div>`;
    messagesContainer.appendChild(loadingRow);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;

    try {
        // The API expects Form Data (urlencoded or multipart)
        const formData = new URLSearchParams();
        formData.append("query", queryText);
        formData.append("thread_id", threadId);

        const response = await fetch(API_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
            },
            body: formData
        });

        if (!response.ok) {
            throw new Error(`Server returned HTTP ${response.status}`);
        }

        const data = await response.json();

        // Remove typing indicator
        const loader = document.getElementById("typing-loader");
        if (loader) loader.remove();

        // Show bot response
        if (data && data.response) {
            appendMessage(data.response, "bot");
        } else {
            appendMessage("Received an empty response from the assistant.", "bot");
        }
    } catch (error) {
        console.error("Fetch Error:", error);
        // Remove typing indicator
        const loader = document.getElementById("typing-loader");
        if (loader) loader.remove();
        showToast("Cannot connect to local banking API.");
        appendMessage("Sorry, I'm having trouble connecting to the server. Please verify the API server is running locally on port 8000.", "bot");
    } finally {
        // Re-enable controls
        chatInput.disabled = false;
        sendBtn.disabled = false;
        sendIcon.className = "fa-solid fa-paper-plane";
        chatInput.focus();
    }
}
