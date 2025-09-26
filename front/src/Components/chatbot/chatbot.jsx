import React, { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "./Chatbot.css";

const Chatbot = ({ showChatbot, closeChat }) => {
  const [chatList, setChatList] = useState([]);
  const [userInput, setUserInput] = useState("");
  const chatboxRef = useRef(null);
  const textareaRef = useRef(null);
  const navigate = useNavigate();

  const prePromptedQA = {
    "total ground water difference between mehrauli and rohini":
      "FRESH difference for TOTAL GROUND WATER AVAILABILITY IN THE AREA between ROHINI and MEHRAULI = 1006.02\nSALINE difference for TOTAL GROUND WATER AVAILABILITY IN THE AREA between ROHINI and MEHRAULI = 0.00",

    "total number of saline districts of tamilnadu":
      "Total number of saline districts in TAMILNADU = 5\nDistricts: MAYILADUTHURAI, PUDUKKOTTAI, RAMANATHAPURAM, THIRUVARUR, TIRUVALLUR",

    "total fresh groundwater in civil lines":
      "Total FRESH in CIVIL LINES = 1428.24",

    "total saline groundwater in car nicobar island":
      "Total SALINE in CAR NICOBAR = 313.56",

    "total unconfined aquifers of rohini":
      "Total unconfined aquifers in ROHINI: Fresh = 2025.15, Saline = 0.00"
  };

  const suggestedQuestions = Object.keys(prePromptedQA);

  const scrollToBottom = () => {
    if (chatboxRef.current) {
      chatboxRef.current.scrollTop = chatboxRef.current.scrollHeight;
    }
  };

  const handleSend = async (customMessage = null) => {
  const messageToSend = customMessage !== null ? customMessage : userInput.trim();
  if (!messageToSend) return;

  // Add user message to chat
  setChatList((prev) => [...prev, { message: messageToSend, type: "outgoing" }]);
  setUserInput("");
  scrollToBottom();

  // Check if it's a pre-prompted question (case-insensitive)
  const lowerMsg = messageToSend.toLowerCase();
  if (prePromptedQA[lowerMsg]) {
    const answer = prePromptedQA[lowerMsg];
    setChatList((prev) => [...prev, { message: answer, type: "incoming" }]);
    scrollToBottom();
    return; // skip API call
  }

  // Otherwise call YOUR backend API
  setChatList((prev) => [...prev, { message: "Thinking....", type: "incoming" }]);
  scrollToBottom();

  try {
    const response = await fetch("http://127.0.0.1:8000/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: messageToSend }),
    });

    const data = await response.json();
    const botMessage = data?.answer || "No response from backend";

    setChatList((prev) => {
      const updated = [...prev];
      updated[updated.length - 1] = { message: botMessage, type: "incoming" };
      return updated;
    });
    scrollToBottom();
  } catch (error) {
    setChatList((prev) => {
      const updated = [...prev];
      updated[updated.length - 1] = {
        message: "Oops! Something went wrong. Please try again.",
        type: "incoming error",
      };
      return updated;
    });
    scrollToBottom();
  }
};

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey && window.innerWidth > 800) {
      e.preventDefault();
      handleSend();
    }
  };

const handleLastHindiOutput = async () => {
  const lastBotMessageIndex = [...chatList].reverse().findIndex(
    (chat) => chat.type === "incoming"
  );

  if (lastBotMessageIndex === -1) return;

  const actualIndex = chatList.length - 1 - lastBotMessageIndex;
  const lastMessage = chatList[actualIndex].message;

    try {
    const response = await fetch("http://127.0.0.1:8005/translate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ q: lastMessage, target: "hi" }),
    });
    console.log(response);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const result = await response.json();
    const translatedText = result?.data?.translations?.[0]?.translatedText;

    if (translatedText) {
      setChatList((prev) => [
        ...prev,
        { message: translatedText, type: "incoming" },
      ]);
      scrollToBottom();
    } else {
      throw new Error("No translation found.");
    }
  } catch (error) {
    console.error("Translation Error:", error);
    setChatList((prev) => [
      ...prev,
      {
        message: "⚠️ Translation failed. Please try again.",
        type: "incoming error",
      },
    ]);
    scrollToBottom();
  }
};


  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "55px";
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [userInput]);

  return (
    <div className={showChatbot ? "chatbot-wrapper show-chatbot" : "chatbot-wrapper"}>
      <div className={`chatbot ${showChatbot ? "show-chatbot" : ""}`}>
        <header>
          INGRES AI Assistant
          <span className="close-btn" onClick={closeChat}>
            &#x2715;
          </span>
        </header>

        <ul className="chatbox" ref={chatboxRef}>
          <li className="chat incoming">
            <p>👋 Hi! Ask me about groundwater levels, predictions, or analytics.</p>
          </li>

          <li className="chat incoming">
            <div className="suggested-questions">
              {suggestedQuestions.map((q, idx) => (
                <button
                  key={idx}
                  onClick={() => handleSend(q)}
                  className="suggested-question-btn"
                >
                  {q}
                </button>
              ))}
              <button
                className="suggested-question-btn view-stats-btn"
                onClick={() => {
                  closeChat();
                  navigate("/dashboard");
                }}
              >
                📊 View Stats
              </button>
            </div>
          </li>
          {/* render chat */}
          {chatList.map((chat, idx) => (
            <li key={idx} className={`chat ${chat.type}`}>
              <p className={chat.type === "incoming error" ? "error" : ""}>
                {chat.message}
              </p>
            </li>
          ))}
        </ul>

        <div className="chat-input">
          <textarea
            ref={textareaRef}
            placeholder="Type your message..."
            value={userInput}
            onChange={(e) => setUserInput(e.target.value)}
            onKeyDown={handleKeyDown}
            required
          />
          <span
            id="send-btn"
            className="material-symbols-outlined"
            onClick={() => handleSend()}
          >
            send
          </span>
          <button className="translator-button" onClick={()=>handleLastHindiOutput()}>translate to hindi</button>
        </div>
      </div>
    </div>
  );
};

export default Chatbot;