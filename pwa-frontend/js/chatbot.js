document.addEventListener("DOMContentLoaded", () => {
  const toggle = document.getElementById("chatbot-toggle");
  const chatbot = document.getElementById("chatbot-container");
  const closeBtn = document.getElementById("chatbot-close");
  const sendBtn = document.getElementById("chatbot-send");
  const input = document.getElementById("chatbot-input");
  const messages = document.getElementById("chatbot-messages");

  if (!toggle || !chatbot) {
    console.error("Chatbot elements missing");
    return;
  }

  // OPEN CHAT (click mascot OR image)
  toggle.addEventListener("click", openChat);
  toggle.querySelector("img")?.addEventListener("click", openChat);

  function openChat() {
    chatbot.classList.remove("chatbot-hidden");
  }

  // CLOSE CHAT
  closeBtn?.addEventListener("click", () => {
    chatbot.classList.add("chatbot-hidden");
  });

  // SEND MESSAGE
  sendBtn?.addEventListener("click", sendMessage);
  input?.addEventListener("keydown", e => {
    if (e.key === "Enter") sendMessage();
  });

  async function sendMessage() {
    const text = input.value.trim();
    if (!text) return;

    addBubble(text, "user");
    input.value = "";

    try {
      const res = await fetch(
        "https://emergency-health-locker.onrender.com/api/chatbot/message",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            message: text,
            patientId: localStorage.getItem("patient_id")
          })
        }
      );

      const data = await res.json();
      addBubble(data.reply || "No response from assistant.", "bot");
    } catch (err) {
      console.error(err);
      addBubble("⚠️ Chatbot service unavailable.", "bot");
    }
  }

  function addBubble(text, type) {
    const div = document.createElement("div");
    div.className = type === "user" ? "chatbot-user" : "chatbot-bot";
    div.innerHTML = `<span>${text}</span>`;
    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
  }
});
