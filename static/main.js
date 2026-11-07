const messageInput = document.getElementById("chat");
const sendBtn = document.getElementById("btn");
const messages = document.getElementById("messages");

const converter = new showdown.Converter();

function addMessage(message, type) {
    const div = document.createElement("div");

    div.className = `message ${type}`;

    if (type === "bot") {
        div.innerHTML = converter.makeHtml(message);
    } else {
        div.textContent = message;
    }

    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
}

function showQuotaWarning() {
    const div = document.createElement("div");
    div.className = "message bot";
    div.textContent = "The free AI token limit has been reached. Please try again later.";
    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
}

async function chatGemini() {
    const message = messageInput.value.trim();

    if (!message || sendBtn.disabled) {
        return;
    }

    addMessage(message, "user");
    messageInput.value = "";

    const thinking = document.createElement("div");
    thinking.className = "message bot thinking";
    thinking.setAttribute("role", "status");
    thinking.textContent = "Thinking…";
    messages.appendChild(thinking);
    messages.scrollTop = messages.scrollHeight;

    sendBtn.disabled = true;
    messageInput.disabled = true;

    try {
        const response = await fetch("/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ message })
        });

        const data = await response.json();

        if (data.error) {
            addMessage(data.error, "bot");
            return;
        }

        addMessage(data.response, "bot");

    } catch (error) {
        addMessage("Something went wrong. Please try again.", "bot");
        console.error(error);
    } finally {
        thinking.remove();
        sendBtn.disabled = false;
        messageInput.disabled = false;
        messageInput.focus();
    }
}

sendBtn.addEventListener("click", chatGemini);

messageInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
        chatGemini();
    }
});
