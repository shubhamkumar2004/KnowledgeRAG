import { useState } from "react";

export default function ChatInput({
  onSend,
  isLoading,
}) {

  const [question, setQuestion] = useState("");

  function handleSubmit() {

    if (!question.trim() || isLoading) return;

    onSend(question);

    setQuestion("");
  }

  return (
    <div className="chat-input">

      <input
        type="text"
        placeholder={
          isLoading
            ? "Please wait while I prepare your response..."
            : "Ask anything about Ekta Trust..."
        }
        value={question}
        disabled={isLoading}
        onChange={(e) =>
          setQuestion(e.target.value)
        }
        onKeyDown={(e) => {
          if (e.key === "Enter") {
            handleSubmit();
          }
        }}
      />

      <button
        onClick={handleSubmit}
        disabled={isLoading}
      >
        {isLoading ? "Thinking..." : "Send"}
      </button>

    </div>
  );

}