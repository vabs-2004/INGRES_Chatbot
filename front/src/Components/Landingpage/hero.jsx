import { Link } from "react-router-dom";
import './hero.css';


function Hero({ openChat }) {
  return (
    <section className="hero" id="home">
      
      {/* Logo */}
      <div >
        <h1 className="logo-text">INGRES</h1>
      </div>

      {/* Main Heading */}
      <h2>
        AI-Driven ChatBot for <span className="highlight">Groundwater Resource Estimation</span>
      </h2>

      <p>
        Revolutionizing water resource management through intelligent AI conversations, real-time data analysis, and predictive modeling.
      </p>

      {/* Buttons */}
      <div className="hero-buttons">
        <button className="btn-primary" onClick={openChat}>
          Start Conversation
        </button>
        <Link to="/dashboard" className="btn-secondary-link btn-primary">
          View Stats

        </Link>
      </div>

      {/* Persistent Chat Message Bubble */}
      {/* <div className="chat-message-bubble" onClick={openChat}>
        
      </div> */}
    </section>
  );
}

export default Hero;
