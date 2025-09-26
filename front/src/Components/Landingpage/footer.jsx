import './footer.css';
function Footer({ openChat }) {
  return (
    <footer id="contact" className="footer">
      <h3>
        Start Your <span className="highlight">Water Intelligence</span> Journey Today
      </h3>
      <p>
        Join thousands of professionals who trust INGRES for sustainable water management.
      </p>
      <button className="btn-primary" onClick={openChat}>
        Start Free Conversation
      </button>
      <p className="copyright">
        © 2025 INGRES. Trusted by water professionals worldwide.
      </p>
    </footer>
  );
}

export default Footer;
