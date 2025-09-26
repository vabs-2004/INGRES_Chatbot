import './navbar.css';

function Navbar({ openChat }) {
  return (
    <nav className="navbar">
      <div className="logo-container">
        <img
          src="https://img.icons8.com/?size=100&id=ErR2tuOLRaTc&format=png&color=000000"
          alt="Logo"
          className="logo-icon"
        />
        <h1 className="logo">INGRES</h1>
      </div>

      <div className="nav-links">
        <a href="#home">Home</a>
        <a href="#about">About</a>
        <a href="#features">Features</a>
        <a href="#impact">Impact</a>
        <a href="#contact">Contact</a>
      </div>

      {/* Try INGRES button now calls openChat */}
      <button className="btn-primary" onClick={openChat}>
        Try INGRES
      </button>
    </nav>
  );
}

export default Navbar;
