/**
 * App.jsx — Root Application Component
 * Sets up routing (single page app — no auth needed per spec)
 */

import Home from './pages/Home';
import './index.css';

export default function App() {
  return (
    <>
      {/* Liquid background container (radial-gradient background only) */}
      <div className="liquid-bg-container">
      </div>
      
      <Home />
    </>
  );
}
