import React, { useEffect } from 'react';
import { useSearchParams, useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

function AuthSuccess() {
  const [searchParams] = useSearchParams();
  const { login } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    const token = searchParams.get('token');

    if (token) {
      login(token);
      // Redirect to dashboard after storing the token
      navigate('/dashboard', { replace: true });
    }
    // If no token, render the error state below
  }, []); // Run once on mount

  // Show error if there's no token param in the URL
  const hasToken = !!searchParams.get('token');

  if (!hasToken) {
    return (
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
        backgroundColor: '#0f0f1b',
        color: '#fff',
        fontFamily: 'system-ui, sans-serif',
        gap: '16px',
        textAlign: 'center',
        padding: '20px'
      }}>
        <h2 style={{ fontSize: '1.5rem', color: '#f87171' }}>Login failed, no token received.</h2>
        <p style={{ color: '#94a3b8' }}>Google authentication did not return a valid session.</p>
        <Link to="/" style={{ color: '#6366f1', textDecoration: 'underline', fontSize: '1rem' }}>
          ← Back to Home
        </Link>
      </div>
    );
  }

  // Token is present — show a brief loading state while the useEffect runs
  return (
    <div style={{
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      height: '100vh',
      backgroundColor: '#0f0f1b',
      color: '#94a3b8',
      fontFamily: 'system-ui, sans-serif',
      fontSize: '1.1rem'
    }}>
      Redirecting to your dashboard…
    </div>
  );
}

export default AuthSuccess;
