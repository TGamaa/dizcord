// static/script.js
document.addEventListener("DOMContentLoaded", () => {
    const chatMessages = document.getElementById("chat-messages");
    const messageInput = document.getElementById("message-input");
    const sendBtn = document.getElementById("send-btn");
    const usernameBtn = document.getElementById("username-btn");
    const userInfo = document.getElementById("user-info");

    let username = "Anonymous";
    let ws;

    function setUsername() {
        const newUsername = prompt("Please enter your username:", username);
        if (newUsername) {
            username = newUsername;
            userInfo.textContent = username;
            initWebSocket();
        }
    }

    usernameBtn.addEventListener("click", setUsername);

    function initWebSocket() {
        if (ws) {
            ws.close();
        }

        // Clear existing messages
        chatMessages.innerHTML = '';

        const clientId = username; // Use username as a simple client ID
        ws = new WebSocket(`ws://localhost:8000/ws/${clientId}`);

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            addMessageToChat(data);
        };

        ws.onopen = () => {
            addMessageToChat({ username: "System", message: "Connected to chat!" });
        };

        ws.onclose = () => {
            addMessageToChat({ username: "System", message: "Disconnected. Attempting to reconnect..." });
            // Optional: implement a reconnect mechanism
        };

        ws.onerror = (error) => {
            addMessageToChat({ username: "System", message: "An error occurred." });
            console.error("WebSocket Error:", error);
        };
    }

    function addMessageToChat(data) {
        const messageElement = document.createElement("div");
        messageElement.classList.add("message");

        const headerElement = document.createElement("div");
        headerElement.classList.add("message-header");

        const usernameElement = document.createElement("span");
        usernameElement.classList.add("message-username");
        usernameElement.textContent = data.username;

        const timestampElement = document.createElement("span");
        timestampElement.classList.add("message-timestamp");
        timestampElement.textContent = new Date().toLocaleTimeString();
        if (data.timestamp && data.timestamp !== "now") {
            timestampElement.textContent = new Date(data.timestamp).toLocaleTimeString();
        }

        const contentElement = document.createElement("div");
        contentElement.classList.add("message-content");
        contentElement.textContent = data.message;
        
        headerElement.appendChild(usernameElement);
        headerElement.appendChild(timestampElement);
        messageElement.appendChild(headerElement);
        messageElement.appendChild(contentElement);

        chatMessages.appendChild(messageElement);
        chatMessages.scrollTop = chatMessages.scrollHeight; // Auto-scroll to the bottom
    }

    function sendMessage() {
        if (messageInput.value && ws && ws.readyState === WebSocket.OPEN) {
            const messageData = {
                username: username,
                message: messageInput.value,
            };
            ws.send(JSON.stringify(messageData));
            messageInput.value = "";
        }
    }

    sendBtn.addEventListener("click", sendMessage);
    messageInput.addEventListener("keypress", (event) => {
        if (event.key === "Enter") {
            sendMessage();
        }
    });

    // Initial prompt for username
    setUsername();
});