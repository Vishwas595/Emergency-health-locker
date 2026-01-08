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

  // OPEN
  toggle.addEventListener("click", () => {
    chatbot.classList.remove("chatbot-hidden");
  });

  // CLOSE
  if (closeBtn) {
    closeBtn.addEventListener("click", () => {
      chatbot.classList.add("chatbot-hidden");
    });
  }

  // SEND MESSAGE (UI only)
  if (sendBtn && input) {
    sendBtn.addEventListener("click", sendMessage);
    input.addEventListener("keydown", e => {
      if (e.key === "Enter") sendMessage();
    });
  }

  function sendMessage() {
    const text = input.value.trim();
    if (!text) return;

    addBubble(text, "user");
    input.value = "";

    setTimeout(() => {
      addBubble(
        "I can help you with your medical profile, allergies, blood group, and reports.",
        "bot"
      );
    }, 600);
  }

  function addBubble(text, type) {
    const div = document.createElement("div");
    div.className = type === "user" ? "chatbot-user" : "chatbot-bot";
    div.innerHTML = `<span>${text}</span>`;
    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
  }
});
