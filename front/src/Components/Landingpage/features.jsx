import './features.css';
function Features() {
  const features = [
    {
      title: "AI-Powered Queries",
      desc: "Natural language processing to understand complex groundwater questions.",
      bg: "card-1",
    },
    {
      title: "Real-Time Data Integration",
      desc: "Live access to groundwater monitoring networks, satellite data, and sensors.",
      bg: "card-2",
    },
    {
      title: "Multilingual Support",
      desc: "Communicate in 15+ languages with local measurement units.",
      bg: "card-3",
    },
    {
      title: "Interactive Visualizations",
      desc: "Dynamic charts, maps, and 3D models to visualize aquifer systems.",
      bg: "card-4",
    },
    {
      title: "Predictive Analytics",
      desc: "Forecast water availability, drought conditions, and optimal usage.",
      bg: "card-5",
    },
    {
      title: "Multi-User Collaboration",
      desc: "Share insights, create reports, and collaborate with team members.",
      bg: "card-6",
    },
  ];

  return (
    <section id="features" className="section">
      <h2>
        Advanced Features for <span className="highlight">Water Intelligence</span>
      </h2>
      <div className="features-grid">
        {features.map((f, i) => (
          <div key={i} className={`card ${f.bg}`}>
            <h3>{f.title}</h3>
            <p>{f.desc}</p>
          </div>
        ))}
      </div>
    </section>
  );
}

export default Features;
