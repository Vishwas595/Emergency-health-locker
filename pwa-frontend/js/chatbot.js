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

  // ============================
  // Hugging Face API URL
  // ============================
  const HF_API =
    "https://vishwas001805-biobert-emergency.hf.space/run/medical_assistant";

  // ============================
  // Start closed
  // ============================
  chatbot.classList.add("chatbot-hidden");

  // ============================
  // Open chatbot
  // ============================
  toggleBtn.addEventListener("click", () => {
    chatbot.classList.remove("chatbot-hidden");
  });

  // ============================
  // Close chatbot
  // ============================
  if (closeBtn) {
    closeBtn.addEventListener("click", () => {
      chatbot.classList.add("chatbot-hidden");
    });
  }

  // ============================
  // Send button click
  // ============================
  sendBtn.addEventListener("click", sendMessage);

  // ============================
  // Enter key send
  // ============================
  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      sendMessage();
    }
  });

  // ============================
  // Add message to UI
  // ============================
  function addMessage(text, sender) {
    const msg = document.createElement("div");
    msg.className = sender === "user" ? "chatbot-user" : "chatbot-bot";
    msg.innerHTML = `<span>${text}</span>`;
    messages.appendChild(msg);
    messages.scrollTop = messages.scrollHeight;
  }

  // ============================
  // Main send function
  // ============================
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
      const response = await fetch(HF_API, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          data: [patientId, text]   // REQUIRED FORMAT FOR GRADIO
        })
      });

      if (!response.ok) {
        throw new Error("Network response not OK");
      }

      const result = await response.json();

      if (result.data && result.data.length > 0) {
        addMessage(result.data[0], "bot");
      } else {
        addMessage("No response from assistant.", "bot");
      }

    } catch (error) {
      console.error("Chatbot error:", error);
      addMessage("⚠️ Chatbot service unavailable.", "bot");
    } finally {
      sendBtn.disabled = false;
    }
  }

});
