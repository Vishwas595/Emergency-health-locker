document.addEventListener("DOMContentLoaded", function () {

  const toggleBtn = document.getElementById("chatbot-toggle");
  const chatbot = document.getElementById("chatbot-container");
  const closeBtn = document.getElementById("chatbot-close");
  const sendBtn = document.getElementById("chatbot-send");
  const input = document.getElementById("chatbot-input");
  const messages = document.getElementById("chatbot-messages");

  if (!toggleBtn || !chatbot) {
    console.error("❌ Chatbot elements missing");
    return;
  }

  // =========================
  // OPEN CHATBOT
  // =========================
  toggleBtn.addEventListener("click", function () {
    chatbot.classList.remove("chatbot-hidden");
  });

  // =========================
  // CLOSE CHATBOT
  // =========================
  closeBtn.addEventListener("click", function () {
    chatbot.classList.add("chatbot-hidden");
  });

  // =========================
  // ADD MESSAGE FUNCTION
  // =========================
  function addMessage(text, sender) {
    const msg = document.createElement("div");
    msg.className = sender === "user" ? "chatbot-user" : "chatbot-bot";
    msg.innerHTML = `<span>${text}</span>`;
    messages.appendChild(msg);
    messages.scrollTop = messages.scrollHeight;
  }

  // =========================
  // SEND MESSAGE TO HF SPACE
  // =========================
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
      const response = await fetch(
        "https://vishwas001805-biobert-emergency.hf.space/run/medical_assistant",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            data: [patientId, text]
          }),
        }
      );

      const result = await response.json();

      if (result.data && result.data.length > 0) {
        addMessage(result.data[0], "bot");
      } else {
        addMessage("No response from assistant.", "bot");
      }

    } catch (error) {
      console.error(error);
      addMessage("⚠️ Chatbot service unavailable.", "bot");
    } finally {
      sendBtn.disabled = false;
    }
  }

  sendBtn.addEventListener("click", sendMessage);

  input.addEventListener("keydown", function (e) {
    if (e.key === "Enter") {
      e.preventDefault();
      sendMessage();
    }
  });

});
