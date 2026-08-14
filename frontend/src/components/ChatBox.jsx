import { useEffect, useRef } from "react";

import MessageBubble from "./MessageBubble";

export default function ChatBox({
  messages,
  isLoading,
  firstLoad,
}) {

  const bottomRef = useRef(null);

  useEffect(() => {

    bottomRef.current?.scrollIntoView({
      behavior: "smooth",
    });

  }, [messages, isLoading]);

  return (
    <div className="chat-box">

      {messages.map((message, index) => (

        <MessageBubble
          key={index}
          sender={message.sender}
          text={message.text}
        />

      ))}

      {isLoading && (

        <MessageBubble
          sender="bot"
          text={
            firstLoad
              ? "🔄 Preparing the Ekta Trust AI Assistant...\n\nThis may take a few moments while the system initializes."
              : "🤖 Thinking..."
          }
        />

      )}

      <div ref={bottomRef} />

    </div>
  );

}