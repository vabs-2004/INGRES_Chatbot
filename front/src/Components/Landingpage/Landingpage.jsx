import Navbar from "./navbar";
import Hero from "./hero";
import About from "./about";
import Features from "./features";
import Impact from "./impact";
import Footer from "./footer";

function LandingPage({ openChat }) {
  return (
    <div className="app">
      <Navbar openChat={openChat} />  {/* pass openChat here */}
      <Hero openChat={openChat} />
      <About />
      <Features />
      <Impact />
      <Footer openChat={openChat} />
    </div>
  );
}

export default LandingPage;
