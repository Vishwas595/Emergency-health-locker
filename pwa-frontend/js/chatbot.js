document.addEventListener("DOMContentLoaded", () => {
    const toggleBtn = document.getElementById("chatbot-toggle");
    const chatbot = document.getElementById("chatbot-container");
    const closeBtn = document.getElementById("chatbot-close");
    const sendBtn = document.getElementById("chatbot-send");
    const input = document.getElementById("chatbot-input");
    const messages = document.getElementById("chatbot-messages");

    if (!toggleBtn || !chatbot || !sendBtn || !input || !messages) {
        console.error("❌ Chatbot elements missing in DOM");
        return;
    }

    // ================================
    // CONFIGURATION
    // ================================
    const SPACE_NAME = "Vishwas001805/biobert-emergency";
    let gradioApp = null;

    // ================================
    // START CLOSED
    // ================================
    chatbot.classList.add("chatbot-hidden");

    // ================================
    // OPEN CHATBOT
    // ================================
    toggleBtn.addEventListener("click", async () => {
        chatbot.classList.remove("chatbot-hidden");
        
        // Initialize Gradio client once
        if (!gradioApp) {
            try {
                console.log("Connecting to Gradio Space...");
                gradioApp = await window.gradio.client(SPACE_NAME);
                console.log("✅ Connected to Gradio Space");
            } catch (error) {
                console.error("Failed to connect:", error);
                addMessage("⚠️ Could not connect to medical assistant.", "bot");
            }
        }
    });

    // ================================
    // CLOSE CHATBOT
    // ================================
    if (closeBtn) {
        closeBtn.addEventListener("click", () => {
            chatbot.classList.add("chatbot-hidden");
        });
    }

    // ================================
    // SEND BUTTON
    // ================================
    sendBtn.addEventListener("click", sendMessage);

    // ================================
    // ENTER KEY
    // ================================
    input.addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
            e.preventDefault();
            sendMessage();
        }
    });

    // ================================
    // ADD MESSAGE TO UI
    // ================================
    function addMessage(text, sender) {
        const msg = document.createElement("div");
        msg.className = sender === "user" ? "chatbot-user" : "chatbot-bot";
        msg.innerHTML = `<span>${text}</span>`;
        messages.appendChild(msg);
        messages.scrollTop = messages.scrollHeight;
    }

    // ================================
    // SEND MESSAGE FUNCTION
    // ================================
    async function sendMessage() {
        const text = input.value.trim();
        if (!text) return;

        const patientId = localStorage.getItem("patient_id");
        if (!patientId) {
            addMessage("⚠️ Patient not logged in.", "bot");
            return;
        }

        addMessage(text, "user");
        input.value = "";
        sendBtn.disabled = true;

        try {
            // Connect if not already connected
            if (!gradioApp) {
                console.log("Connecting to Gradio Space...");
                gradioApp = await window.gradio.client(SPACE_NAME);
                console.log("✅ Connected");
            }

            console.log("Sending:", patientId, text);

            // Call the medical_assistant function
            const result = await gradioApp.predict("/medical_assistant", {
                patient_id: patientId,
                message: text
            });

            console.log("Result:", result);

            // Display response
            if (result && result.data) {
                addMessage(result.data, "bot");
            } else {
                addMessage("No response from assistant.", "bot");
            }

        } catch (error) {
            console.error("Chatbot error:", error);
            addMessage("⚠️ Service unavailable. Please try again.", "bot");
        } finally {
            sendBtn.disabled = false;
        }
    }
});