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

    // ✅ CORRECT ENDPOINT (from cURL docs)
    const CALL_URL = "https://vishwas001805-biobert-emergency.hf.space/gradio_api/call/medical_assistant";
    const POLL_URL = "https://vishwas001805-biobert-emergency.hf.space/gradio_api/call/medical_assistant/";

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

            // Step 1: POST to get event_id
            const callResponse = await fetch(CALL_URL, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    data: [patientId, text]
                })
            });

            if (!callResponse.ok) {
                throw new Error(`HTTP ${callResponse.status}`);
            }

            const callResult = await callResponse.json();
            console.log("Call Result:", callResult);

            if (!callResult.event_id) {
                throw new Error("No event_id received");
            }

            // Step 2: GET result using event_id
            const eventId = callResult.event_id;
            const pollUrl = POLL_URL + eventId;
            
            console.log("Polling:", pollUrl);

            // Wait briefly before polling
            await new Promise(resolve => setTimeout(resolve, 500));

            const pollResponse = await fetch(pollUrl);
            const reader = pollResponse.body.getReader();
            const decoder = new TextDecoder();

            let done = false;
            let resultData = null;

            while (!done) {
                const { value, done: doneReading } = await reader.read();
                done = doneReading;
                
                if (value) {
                    const chunk = decoder.decode(value);
                    console.log("Chunk:", chunk);
                    
                    // Parse SSE format
                    const lines = chunk.split('\n');
                    for (const line of lines) {
                        if (line.startsWith('data: ')) {
                            try {
                                const jsonData = JSON.parse(line.slice(6));
                                if (jsonData.msg === 'process_completed' && jsonData.output) {
                                    resultData = jsonData.output.data[0];
                                    done = true;
                                    break;
                                }
                            } catch (e) {
                                // Ignore parsing errors
                            }
                        }
                    }
                }
            }

            if (resultData) {
                addMessage(resultData, "bot");
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