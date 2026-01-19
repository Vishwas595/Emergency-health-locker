document.addEventListener("DOMContentLoaded", () => {
  const toggleBtn = document.getElementById("chatbot-toggle");
  const chatbot   = document.getElementById("chatbot-container");
  const closeBtn  = document.getElementById("chatbot-close");
  const sendBtn   = document.getElementById("chatbot-send");
  const input     = document.getElementById("chatbot-input");
  const messages  = document.getElementById("chatbot-messages");

  if (!toggleBtn || !sendBtn || !input || !messages || !chatbot) {
    console.error("Chatbot elements not found in DOM");
    return;
  }

  const BACKEND_URL = "http://localhost:5000"; // use Render URL when deployed

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

    addMessage(text, "user");
    input.value = "";

    try {
      const response = await fetch(`${BACKEND_URL}/api/chatbot/message`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: text,
          patientId: localStorage.getItem("patientid"),
        }),
      });

      const data = await response.json();
      addMessage(data.reply || "No response from server.", "bot");
    } catch (err) {
      console.error(err);
      addMessage("Unable to reach chatbot service.", "bot");
    }
  }
});
