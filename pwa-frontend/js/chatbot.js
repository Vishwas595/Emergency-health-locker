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
    let gradioClient = null;

    // ================================
    // START CLOSED
    // ================================
    chatbot.classList.add("chatbot-hidden");

    // ================================
    // OPEN CHATBOT
    // ================================
    toggleBtn.addEventListener("click", async () => {
        chatbot.classList.remove("chatbot-hidden");
        
        // Initialize Gradio client on first open
        if (!gradioClient) {
            try {
                gradioClient = await window.gradio.client(SPACE_NAME);
                console.log("✅ Gradio client connected");
            } catch (error) {
                console.error("Failed to connect to Gradio:", error);
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
        msg.innerHTML = `${text}`;
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
            // Initialize client if not already done
            if (!gradioClient) {
                gradioClient = await window.gradio.client(SPACE_NAME);
            }

            // Call the medical_assistant function
            const result = await gradioClient.predict("/medical_assistant", [
                patientId,
                text
            ]);

            // Display response
            if (result && result.data && result.data.length > 0) {
                addMessage(result.data[0], "bot");
            } else {
                addMessage("No response from assistant.", "bot");
            }

        } catch (error) {
            console.error("Chatbot error:", error);
            addMessage("⚠️ Chatbot service unavailable. Please try again.", "bot");
        } finally {
            sendBtn.disabled = false;
        }
    }
});