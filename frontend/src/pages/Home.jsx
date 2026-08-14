import { useState } from "react";

import Header from "../components/Header";
import ChatBox from "../components/ChatBox";
import ChatInput from "../components/ChatInput";

import { sendMessage } from "../services/api";

export default function Home() {

  const [messages, setMessages] = useState([
    {
      sender: "bot",
      text:
        "Welcome to the Ekta Trust AI Assistant.\n\nI can help answer questions about Ekta Trust's initiatives, schemes, events, registrations, training programmes and other information available on the official website.",
    },
  ]);

  const [isLoading, setIsLoading] = useState(false);

  const [firstLoad, setFirstLoad] = useState(true);

  const sessionId =
    localStorage.getItem("session_id") ||
    crypto.randomUUID();

  localStorage.setItem(
    "session_id",
    sessionId
  );

  async function handleSend(question) {

    if (!question.trim() || isLoading) return;

    const userMessage = {
      sender: "user",
      text: question,
    };

    setMessages((prev) => [
      ...prev,
      userMessage,
    ]);

    setIsLoading(true);

    try {

      const response = await sendMessage(
        question,
        sessionId
      );

      const botMessage = {
        sender: "bot",
        text: response.answer,
      };

      setMessages((prev) => [
        ...prev,
        botMessage,
      ]);

    } catch {

      setMessages((prev) => [
        ...prev,
        {
          sender: "bot",
          text:
            "Sorry, I'm currently unable to process your request.\n\nPlease try again in a few moments.",
        },
      ]);

    } finally {

      setIsLoading(false);

      setFirstLoad(false);

    }

  }

  return (
    <div className="app">

      <Header />

      <ChatBox
        messages={messages}
        isLoading={isLoading}
        firstLoad={firstLoad}
      />

      <ChatInput
        onSend={handleSend}
        isLoading={isLoading}
      />

    </div>
  );

}