import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import LandingPage from "./Components/LandingPage/LandingPage";
import Dashboard from "./Components/Dashboard/Dashboard";
import Chatbot from "./Components/chatbot/chatbot";
import { useState } from "react";
import "./App.css";

function App() {
  const [chatOpen, setChatOpen] = useState(false);

  const openChat = () => setChatOpen(true);  // used in Navbar & Hero
  const closeChat = () => setChatOpen(false);

  return (
    <Router>
      {chatOpen && (
        <Chatbot showChatbot={chatOpen} closeChat={closeChat} />
      )}

      <Routes>
        <Route path="/" element={<LandingPage openChat={openChat} />} />
        <Route path="/dashboard" element={<Dashboard openChat={openChat} />} />
      </Routes>
    </Router>
  );
}

export default App;
