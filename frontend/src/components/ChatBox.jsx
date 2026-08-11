import MessageBubble from "./MessageBubble";

export default function ChatBox() {

  const messages = [
    {
      sender: "bot",
      text:
        "Hello! I am the Ekta Trust AI Assistant. How can I help you today?",
    },
  ];

  return (
    <div className="chat-box">

      {messages.map((message, index) => (
        <MessageBubble
          key={index}
          sender={message.sender}
          text={message.text}
        />
      ))}

    </div>
  );
}