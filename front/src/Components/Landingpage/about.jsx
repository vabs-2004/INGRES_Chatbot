import React from 'react';
import './about.css';

const About = () => {
  return (
<div className="about" id="about">
      <div className="about-left">
        <img src="/images/about.png" alt="About Illustration" className="about-img" />
        <img src="/images/play-icon.png" alt="Play Icon" className="play-icon" />
      </div>
      <div className="about-right">
        <h3>ABOUT INGRES</h3>
        <h2>Nurturing Smarter Water Resource Management</h2>
        <p>
          INGRES is an AI-driven platform designed to revolutionize groundwater resource monitoring, analysis, and management.
        </p>
        <p>
          Our intelligent chatbot serves as a virtual assistant allowing effortless groundwater level queries and predictive analytics.
        </p>
        <p>
          At INGRES, we envision a future where smart water solutions support sustainability.
        </p>
      </div>
    </div>
  );
};

export default About;

