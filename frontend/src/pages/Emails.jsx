import React from 'react';
import Navbar from '../components/Navbar';

function Emails() {
  return (
    <div className="emails-container">
      <Navbar />
      <div className="emails-content">
        <h1 className="emails-title">
          Emails
        </h1>
        <p className="emails-subtitle">
          Browse your fetched emails and see their processing status.
        </p>
      </div>

      <style>{`
        .emails-container {
          background-color: var(--color-bg);
          min-height: 100vh;
          color: var(--color-text-primary);
          font-family: system-ui, sans-serif;
        }
        .emails-content {
          max-width: 1200px;
          margin: 0 auto;
          padding: 40px 20px;
        }
        .emails-title {
          font-size: 2.5rem;
          font-weight: 800;
          letter-spacing: -0.04em;
          margin: 0;
        }
        .emails-subtitle {
          color: var(--color-text-secondary);
          margin-top: 8px;
        }

        @media (max-width: 768px) {
          .emails-content {
            padding: 24px 16px;
          }
          .emails-title {
            font-size: 2rem;
          }
        }
      `}</style>
    </div>
  );
}
export default Emails;

