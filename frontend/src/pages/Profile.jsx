import React, { useState, useEffect } from 'react';
import Navbar from '../components/Navbar';
import apiClient from '../api/client';
import useAuth from '../context/AuthContext';

function Profile() {
  const { user: authUser } = useAuth();
  const [userInfo, setUserInfo] = useState(authUser || null);
  const [loading, setLoading] = useState(!authUser);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        setLoading(true);
        const response = await apiClient.get('/me');
        setUserInfo(response.data);
      } catch (err) {
        console.error('Failed to fetch user profile:', err);
        setError('Failed to load profile details.');
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, []);

  const getInitial = (name, email) => {
    if (name && name.trim()) return name.trim()[0].toUpperCase();
    if (email && email.trim()) return email.trim()[0].toUpperCase();
    return 'U';
  };

  const initial = userInfo ? getInitial(userInfo.name, userInfo.email) : 'U';

  return (
    <div className="dashboard-container">
      <Navbar />

      <main className="dashboard-content" style={{ maxWidth: '800px', margin: '40px auto', padding: '0 20px' }}>
        <div className="header-section" style={{ marginBottom: '30px', textAlign: 'center' }}>
          <h1 style={{ fontSize: '2rem', fontWeight: '800', color: '#1e293b', marginBottom: '8px' }}>
            User Profile
          </h1>
          <p style={{ color: '#64748b' }}>Account details for your SmartInbox session</p>
        </div>

        {loading ? (
          <div style={{ textAlign: 'center', padding: '60px 0', color: '#64748b' }}>
            Loading profile information…
          </div>
        ) : error && !userInfo ? (
          <div style={{ padding: '20px', backgroundColor: '#fef2f2', border: '1px solid #fecaca', borderRadius: '12px', color: '#991b1b', textAlign: 'center' }}>
            {error}
          </div>
        ) : (
          <div style={{
            backgroundColor: '#ffffff',
            borderRadius: '16px',
            boxShadow: '0 4px 20px rgba(0, 0, 0, 0.05)',
            border: '1px solid #e2e8f0',
            padding: '40px',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: '24px'
          }}>
            {/* Avatar circle */}
            <div style={{
              width: '96px',
              height: '96px',
              borderRadius: '50%',
              background: 'linear-gradient(135deg, #2563eb 0%, #3b82f6 100%)',
              color: '#ffffff',
              fontSize: '2.5rem',
              fontWeight: '700',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 8px 16px rgba(37, 99, 235, 0.25)'
            }}>
              {initial}
            </div>

            <div style={{ width: '100%', maxWidth: '500px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div style={{ padding: '16px 20px', backgroundColor: '#f8fafc', borderRadius: '12px', border: '1px solid #f1f5f9' }}>
                <span style={{ fontSize: '0.85rem', fontWeight: '600', textTransform: 'uppercase', color: '#94a3b8', letterSpacing: '0.05em' }}>Full Name</span>
                <div style={{ fontSize: '1.15rem', fontWeight: '600', color: '#0f172a', marginTop: '4px' }}>
                  {userInfo?.name || 'SmartInbox User'}
                </div>
              </div>

              <div style={{ padding: '16px 20px', backgroundColor: '#f8fafc', borderRadius: '12px', border: '1px solid #f1f5f9' }}>
                <span style={{ fontSize: '0.85rem', fontWeight: '600', textTransform: 'uppercase', color: '#94a3b8', letterSpacing: '0.05em' }}>Email Address</span>
                <div style={{ fontSize: '1.15rem', fontWeight: '600', color: '#0f172a', marginTop: '4px' }}>
                  {userInfo?.email || 'N/A'}
                </div>
              </div>

              <div style={{ padding: '16px 20px', backgroundColor: '#f8fafc', borderRadius: '12px', border: '1px solid #f1f5f9' }}>
                <span style={{ fontSize: '0.85rem', fontWeight: '600', textTransform: 'uppercase', color: '#94a3b8', letterSpacing: '0.05em' }}>Account Status</span>
                <div style={{ fontSize: '1rem', fontWeight: '600', color: '#16a34a', marginTop: '4px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#16a34a' }}></span>
                  Active & Connected via Google OAuth
                </div>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default Profile;
