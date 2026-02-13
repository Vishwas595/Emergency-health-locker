document.addEventListener("DOMContentLoaded", () => {
    const toggleBtn = document.getElementById("chatbot-toggle");
    const chatbot = document.getElementById("chatbot-container");
    const closeBtn = document.getElementById("chatbot-close");
    const sendBtn = document.getElementById("chatbot-send");
    const input = document.getElementById("chatbot-input");
    const messages = document.getElementById("chatbot-messages");

    if (!toggleBtn || !chatbot || !sendBtn || !input || !messages) {
        console.error("❌ Chatbot elements missing");
        return;
    }

    // ✅ CORRECT ENDPOINT
    const API_URL = "https://vishwas001805-biobert-emergency.hf.space/call/medical_assistant";

    chatbot.classList.add("chatbot-hidden");

    toggleBtn.addEventListener("click", () => {
        chatbot.classList.remove("chatbot-hidden");
    });

    if (closeBtn) {
        closeBtn.addEventListener("click", () => {
            chatbot.classList.add("chatbot-hidden");
        });
    }

    sendBtn.addEventListener("click", sendMessage);

    input.addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
            e.preventDefault();
            sendMessage();
        }
    });

    function addMessage(text, sender) {
        const msg = document.createElement("div");
        msg.className = sender === "user" ? "chatbot-user" : "chatbot-bot";
        msg.innerHTML = `<span>${text}</span>`;
        messages.appendChild(msg);
        messages.scrollTop = messages.scrollHeight;
    }

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
            console.log("Sending to HF:", patientId, text);

            // ✅ CORRECT FORMAT: Use named parameters
            const response = await fetch(API_URL, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    patient_id: patientId,
                    message: text
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const result = await response.json();
            console.log("HF Response:", result);

            // Handle Gradio queue response
            if (result.event_id) {
                // Poll for result using event_id
                const eventId = result.event_id;
                const pollUrl = `https://vishwas001805-biobert-emergency.hf.space/call/medical_assistant/${eventId}`;
                
                console.log("Polling:", pollUrl);
                
                // Wait a bit before polling
                await new Promise(resolve => setTimeout(resolve, 1000));
                
                const pollResponse = await fetch(pollUrl);
                const pollResult = await pollResponse.json();
                
                console.log("Poll Result:", pollResult);
                
                if (pollResult && pollResult.data) {
                    addMessage(pollResult.data, "bot");
                } else {
                    addMessage("No response from assistant.", "bot");
                }
            } else if (result.data) {
                // Direct response
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