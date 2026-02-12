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

  // ================================
  // 🔹 HUGGING FACE API URL
  // ================================
  const HF_API =
    "https://vishwas001805-biobert-emergency.hf.space/run/medical_assistant";

  // ================================
  // 🔹 START CLOSED
  // ================================
  chatbot.classList.add("chatbot-hidden");

  // ================================
  // 🔹 OPEN CHAT
  // ================================
  toggleBtn.addEventListener("click", () => {
    chatbot.classList.remove("chatbot-hidden");
  });

  // ================================
  // 🔹 CLOSE CHAT
  // ================================
  closeBtn?.addEventListener("click", () => {
    chatbot.classList.add("chatbot-hidden");
  });

  // ================================
  // 🔹 SEND EVENTS
  // ================================
  sendBtn.addEventListener("click", sendMessage);

  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      sendMessage();
    }
  });

  // ================================
  // 🔹 ADD MESSAGE FUNCTION
  // ================================
  function addMessage(text, sender) {
    const msg = document.createElement("div");
    msg.className =
      sender === "user" ? "chatbot-user" : "chatbot-bot";

    msg.innerHTML = `<span>${text}</span>`;
    messages.appendChild(msg);
    messages.scrollTop = messages.scrollHeight;
  }

  // ================================
  // 🔹 MAIN SEND FUNCTION
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

      const response = await fetch(HF_API, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          data: [patientId, text]   // IMPORTANT FORMAT
        })
      });

      if (!response.ok) {
        throw new Error("Network response was not ok");
      }

      const result = await response.json();
      console.log("HF Response:", result);

      if (result && result.data) {

        if (Array.isArray(result.data) && result.data.length > 0) {
          addMessage(result.data[0], "bot");
        } else {
          addMessage("⚠️ Assistant returned empty response.", "bot");
        }

      } else if (result.error) {
        addMessage("⚠️ " + result.error, "bot");
      } else {
        addMessage("⚠️ Unexpected server response.", "bot");
      }

    } catch (error) {
      console.error("Chatbot error:", error);
      addMessage("⚠️ Chatbot service unavailable.", "bot");
    } finally {
      sendBtn.disabled = false;
    }
  }

});
