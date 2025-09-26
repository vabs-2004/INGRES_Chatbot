import './impact.css';
function Impact() {
  return (
    <section id="impact" className="section">
      <h2>
        Transforming <span className="highlight">Water Management</span> Worldwide
      </h2>
      <p className="section-desc">
        INGRES is making a measurable difference in water conservation, environmental protection, and sustainable resource management.
      </p>
      <div className="impact-grid">
        <div className="impact-card">
          <h3 className="blue">2.5B</h3>
          <p>Liters Saved</p>
        </div>
        <div className="impact-card">
          <h3 className="green">340K</h3>
          <p>Tons CO₂ Reduced</p>
        </div>
        <div className="impact-card">
          <h3 className="purple">98.7%</h3>
          <p>Accuracy Rate</p>
        </div>
      </div>
    </section>
  );
}

export default Impact;
