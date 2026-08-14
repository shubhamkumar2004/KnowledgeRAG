const API_URL = "http://127.0.0.1:8000";

export async function sendMessage(question, sessionId) {
  const response = await fetch(`${API_URL}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      session_id: sessionId,
      question: question,
    }),
  });

  if (!response.ok) {
    throw new Error("Unable to contact the chatbot.");
  }

  return await response.json();
}