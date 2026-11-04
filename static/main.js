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

async function chatGemini() {
    const message = messageInput.value.trim();

    if (!message) {
        return;
    }

    addMessage(message, "user");
    messageInput.value = "";

    try {
        const response = await fetch("/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                message: message
            })
        });

        const data = await response.json();

        if (data.error) {
            addMessage(data.error, "bot");
            return;
        }

        addMessage(data.response, "bot");

    } catch (error) {
        addMessage(
            "Something went wrong. Please try again.",
            "bot"
        );

        console.error(error);
    }
}

sendBtn.addEventListener("click", chatGemini);

messageInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
        chatGemini();
    }
});
