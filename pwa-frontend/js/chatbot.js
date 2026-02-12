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
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          data: [patientId, text]   // VERY IMPORTANT FORMAT
        }),
      }
    );

    const result = await response.json();

    if (result.data && result.data.length > 0) {
      addMessage(result.data[0], "bot");
    } else {
      addMessage("No response from assistant.", "bot");
    }

  } catch (err) {
    console.error(err);
    addMessage("⚠️ Chatbot service unavailable.", "bot");
  } finally {
    sendBtn.disabled = false;
  }
}
