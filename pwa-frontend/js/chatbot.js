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
            console.log("📤 Sending to HF:", patientId, text);

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
            console.log("✅ Call Result:", callResult);

            if (!callResult.event_id) {
                throw new Error("No event_id received");
            }

            // Step 2: Stream result using event_id
            const eventId = callResult.event_id;
            const pollUrl = POLL_URL + eventId;
            
            console.log("🔄 Polling:", pollUrl);

            await new Promise(resolve => setTimeout(resolve, 500));

            const pollResponse = await fetch(pollUrl);
            
            if (!pollResponse.ok) {
                throw new Error(`Poll failed: ${pollResponse.status}`);
            }

            const reader = pollResponse.body.getReader();
            const decoder = new TextDecoder();

            let buffer = "";
            let resultData = null;

            while (true) {
                const { value, done } = await reader.read();
                
                if (done) break;
                
                if (value) {
                    buffer += decoder.decode(value, { stream: true });
                    
                    // Process complete lines
                    const lines = buffer.split('\n');
                    buffer = lines.pop() || ""; // Keep incomplete line in buffer
                    
                    for (const line of lines) {
                        console.log("📄 Line:", line);
                        
                        if (line.startsWith('data: ')) {
                            const dataStr = line.slice(6).trim();
                            
                            if (!dataStr) continue;
                            
                            try {
                                const parsed = JSON.parse(dataStr);
                                console.log("✨ Parsed:", parsed);
                                
                                // Handle array format: ["Blood Type: O+"]
                                if (Array.isArray(parsed) && parsed.length > 0) {
                                    resultData = parsed[0];
                                    console.log("🎯 Found result:", resultData);
                                    break;
                                }
                            } catch (e) {
                                console.warn("⚠️ Parse error:", e, "Data:", dataStr);
                            }
                        }
                    }
                    
                    if (resultData) break;
                }
            }

            console.log("✅ Final result:", resultData);

            if (resultData) {
                addMessage(resultData, "bot");
            } else {
                addMessage("⚠️ No response from assistant.", "bot");
            }

        } catch (error) {
            console.error("❌ Chatbot error:", error);
            addMessage("⚠️ Service unavailable. Please try again.", "bot");
        } finally {
            sendBtn.disabled = false;
        }
    }
});