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
      "https://vishwas001805-biobert-emergency.hf.space/queue/join",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          data: [patientId, text],
          fn_index: 0
        })
      }
    );

    const result = await response.json();
    console.log("HF Queue Response:", result);

    // Wait for result polling
    if (result.hash) {

      const statusUrl =
        `https://vishwas001805-biobert-emergency.hf.space/queue/data?hash=${result.hash}`;

      let completed = false;
      let output = null;

      while (!completed) {

        const statusResponse = await fetch(statusUrl);
        const statusData = await statusResponse.json();

        if (statusData.status === "COMPLETE") {
          completed = true;
          output = statusData.output.data[0];
        }

        await new Promise(r => setTimeout(r, 1000));
      }

      addMessage(output || "No response from assistant.", "bot");

    } else {
      addMessage("⚠️ Assistant queue error.", "bot");
    }

  } catch (error) {
    console.error("Chatbot error:", error);
    addMessage("⚠️ Chatbot service unavailable.", "bot");
  } finally {
    sendBtn.disabled = false;
  }
}
