document.addEventListener("DOMContentLoaded", () => {
  const toggleBtn = document.getElementById("chatbot-toggle");
  const chatbot   = document.getElementById("chatbot-container");
  const closeBtn  = document.getElementById("chatbot-close");
  const sendBtn   = document.getElementById("chatbot-send");
  const input     = document.getElementById("chatbot-input");
  const messages  = document.getElementById("chatbot-messages");

  if (!toggleBtn || !sendBtn || !input || !messages || !chatbot) {
    console.error("❌ Chatbot elements missing in DOM");
    return;
  }

  /* =========================================
     🔁 AUTO SWITCH BACKEND
     ========================================= */
  const API_BASE =
    window.location.hostname === "localhost"
      ? "http://localhost:5000"
      : "https://emergency-health-locker.onrender.com";

  /* =========================================
     🔒 START CLOSED
     ========================================= */
  chatbot.classList.add("chatbot-hidden");

  let greeted = false;

  /* =========================================
     🐻 OPEN CHAT (ONLY OPEN)
     ========================================= */
  toggleBtn.addEventListener("click", () => {
    chatbot.classList.remove("chatbot-hidden");

    if (!greeted) {
      addMessage(
        "Hi, I am Nexa 👋 Ask me about your blood group, allergies, medications, or reports.",
        "bot"
      );
      greeted = true;
    }
  });

  /* =========================================
     ❌ CLOSE CHAT
     ========================================= */
  closeBtn?.addEventListener("click", () => {
    chatbot.classList.add("chatbot-hidden");
  });

  /* =========================================
     📩 SEND MESSAGE
     ========================================= */
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

    addMessage(text, "user");
    input.value = "";
    sendBtn.disabled = true;

    try {
      const response = await fetch(`${API_BASE}/api/chatbot/message`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: text,
          patientId: localStorage.getItem("patient_id"),
        }),
      });

      if (!response.ok) throw new Error("Server error");

      const data = await response.json();
      addMessage(data.reply || "No response from assistant.", "bot");
    } catch (err) {
      console.error(err);
      addMessage("⚠️ Chatbot service is unavailable.", "bot");
    } finally {
      sendBtn.disabled = false;
    }
  }
});
