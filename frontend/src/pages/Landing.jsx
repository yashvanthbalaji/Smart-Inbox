import React from 'react';
import './Landing.css';

function Landing() {
  const apiBaseUrl = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';
  const loginUrl = `${apiBaseUrl}/auth/google`;
  return (
    <div className="landing-page">
      {/* Top Header Navbar */}
      <header className="landing-navbar">
        <a href="/" className="landing-logo">
          Smart<span>Inbox</span>
        </a>
      </header>

      {/* Hero Section */}
      <section className="landing-hero">
        <div className="landing-badge">Powered by Gemini AI</div>
        <h1 className="landing-headline">
          Never miss a deadline buried in your inbox
        </h1>
        <p className="landing-subheadline">
          SmartInbox automatically reads your Gmail, extracts meetings, exams, deadlines, 
          and interviews using Gemini, and presents them in a clean dashboard or syncs them directly to Google Sheets.
        </p>

        {/* Google OAuth Login Button */}
        <a href={loginUrl} className="landing-cta-btn">
          {/* SVG Google "G" Logo */}
          <svg className="google-icon-svg" viewBox="0 0 24 24">
            <path
              fill="#ffffff"
              d="M12.24 10.285V14.4h6.887c-.648 2.41-2.519 4.114-5.136 4.114-3.553 0-6.433-2.88-6.433-6.433s2.88-6.433 6.433-6.433c1.633 0 3.125.61 4.274 1.62l3.086-3.086C19.265 2.19 15.99 1 12.24 1 6.032 1 1 6.032 1 12.24s5.032 11.24 11.24 11.24c5.897 0 10.867-4.226 10.867-11.24 0-.693-.075-1.375-.21-1.955H12.24z"
            />
          </svg>
          Sign in with Google
        </a>
      </section>

      {/* Below the Fold Features Section */}
      <section className="landing-features-section">
        <div className="landing-features-container">
          <div className="features-header">
            <h2 className="features-title">How it works</h2>
            <p className="features-subtitle">Tame your inbox chaos in three simple steps</p>
          </div>

          <div className="landing-features-grid">
            <div className="feature-card">
              <div className="feature-icon-circle">1</div>
              <h3 className="feature-card-title">Connect Gmail</h3>
              <p className="feature-card-desc">
                Authorize SmartInbox securely with read-only Google OAuth to connect your inbox.
              </p>
            </div>

            <div className="feature-card">
              <div className="feature-icon-circle">2</div>
              <h3 className="feature-card-title">AI reads your emails</h3>
              <p className="feature-card-desc">
                Gemini automatically scans new emails and extracts vital event times, titles, locations, and descriptions.
              </p>
            </div>

            <div className="feature-card">
              <div className="feature-icon-circle">3</div>
              <h3 className="feature-card-title">See everything in one place</h3>
              <p className="feature-card-desc">
                View everything on a modern web calendar, manage statuses inside the dashboard, or sync live to a custom Google Sheet.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="landing-footer">
        <p>&copy; {new Date().getFullYear()} SmartInbox Inc. All rights reserved.</p>
      </footer>
    </div>
  );
}

export default Landing;
