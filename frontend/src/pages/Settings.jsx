import React, { useState, useEffect } from 'react';
import Navbar from '../components/Navbar';
import apiClient from '../api/client';

function Settings() {
  const [sheetUrl, setSheetUrl] = useState(null);
  const [sheetLoading, setSheetLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [syncResult, setSyncResult] = useState(null); // { count, error }

  useEffect(() => {
    const fetchSheetLink = async () => {
      try {
        const res = await apiClient.get('/sheet/link');
        setSheetUrl(res.data.sheet_url || null);
      } catch (err) {
        console.error('Failed to fetch sheet link:', err);
        setSheetUrl(null);
      } finally {
        setSheetLoading(false);
      }
    };
    fetchSheetLink();
  }, []);

  const handleSyncNow = async () => {
    setSyncing(true);
    setSyncResult(null);
    try {
      const res = await apiClient.post('/sheet/sync');
      const count = res.data.synced ?? 0;
      setSyncResult({ count, error: null });
      // Refresh sheet link in case it was just created
      const linkRes = await apiClient.get('/sheet/link');
      setSheetUrl(linkRes.data.sheet_url || null);
    } catch (err) {
      console.error('Sync failed:', err);
      setSyncResult({ count: null, error: 'Sync failed. Please try again.' });
    } finally {
      setSyncing(false);
      // Auto-clear result after 6 seconds
      setTimeout(() => setSyncResult(null), 6000);
    }
  };

  // ── Styles ─────────────────────────────────────────────────────────────────
  const cardStyle = {
    backgroundColor: '#16162a',
    border: '1px solid #23233c',
    borderRadius: '14px',
    padding: '28px 32px',
    marginBottom: '20px',
  };

  const sectionLabelStyle = {
    fontSize: '0.7rem',
    fontWeight: '700',
    textTransform: 'uppercase',
    letterSpacing: '0.08em',
    color: '#64748b',
    marginBottom: '10px',
  };

  const sectionTitleStyle = {
    fontSize: '1.2rem',
    fontWeight: '700',
    color: '#fff',
    margin: '0 0 6px 0',
    letterSpacing: '-0.02em',
  };

  const descStyle = {
    color: '#94a3b8',
    fontSize: '0.9rem',
    lineHeight: '1.6',
    margin: '0 0 20px 0',
  };

  const primaryBtnStyle = {
    display: 'inline-flex',
    alignItems: 'center',
    gap: '8px',
    padding: '11px 22px',
    backgroundColor: '#4f46e5',
    color: '#fff',
    border: 'none',
    borderRadius: '8px',
    fontWeight: '600',
    fontSize: '0.9rem',
    cursor: 'pointer',
    textDecoration: 'none',
    boxShadow: '0 4px 12px rgba(79,70,229,0.3)',
    transition: 'background-color 0.15s ease',
    marginRight: '12px',
  };

  const secondaryBtnStyle = {
    display: 'inline-flex',
    alignItems: 'center',
    gap: '8px',
    padding: '11px 22px',
    backgroundColor: '#1a1a35',
    color: '#cbd5e1',
    border: '1px solid #23233c',
    borderRadius: '8px',
    fontWeight: '600',
    fontSize: '0.9rem',
    cursor: syncing ? 'not-allowed' : 'pointer',
    opacity: syncing ? 0.65 : 1,
    transition: 'all 0.15s ease',
  };

  const renderFeedback = () => {
    if (!syncResult) return null;
    const isError = syncResult.error;
    return (
      <div style={{
        marginTop: '14px',
        padding: '12px 16px',
        borderRadius: '8px',
        backgroundColor: isError ? 'rgba(239,68,68,0.1)' : 'rgba(16,185,129,0.1)',
        border: `1px solid ${isError ? 'rgba(239,68,68,0.3)' : 'rgba(16,185,129,0.3)'}`,
        color: isError ? '#f87171' : '#34d399',
        fontSize: '0.9rem',
        fontWeight: '600',
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
      }}>
        {isError ? '❌' : '✅'}
        {isError
          ? syncResult.error
          : syncResult.count > 0
            ? `${syncResult.count} event${syncResult.count !== 1 ? 's' : ''} successfully synced to your Google Sheet!`
            : 'All events are already synced — nothing new to push.'}
      </div>
    );
  };

  return (
    <div className="settings-container">
      <Navbar />
      <div className="settings-content">
        <h1 className="settings-title">
          Settings
        </h1>
        <p className="settings-subtitle">
          Manage your synchronization mode and configurations.
        </p>

        {/* Google Sheets Card */}
        <div style={{
          backgroundColor: 'var(--color-surface)',
          border: '1px solid var(--color-border)',
          borderRadius: '14px',
          padding: '28px 32px',
          marginBottom: '20px',
          boxShadow: 'var(--shadow-sm)'
        }} className="settings-card">
          <div style={sectionLabelStyle}>Google Sheets Integration</div>
          <h2 style={sectionTitleStyle}>📊 SmartInbox Tracker Spreadsheet</h2>
          <p style={descStyle}>
            Your extracted events are automatically synced to a private Google Sheets tracker.
            You can view the live spreadsheet or manually trigger a sync at any time.
          </p>

          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px', alignItems: 'center' }}>
            {/* Open Sheet Button */}
            {sheetLoading ? (
              <span style={{ color: 'var(--color-text-secondary)', fontSize: '0.9rem' }}>Loading sheet link…</span>
            ) : sheetUrl ? (
              <a
                href={sheetUrl}
                target="_blank"
                rel="noopener noreferrer"
                style={{
                  ...primaryBtnStyle,
                  backgroundColor: 'var(--color-accent)',
                  boxShadow: 'var(--shadow-sm)'
                }}
                onMouseEnter={e => e.currentTarget.style.backgroundColor = 'var(--color-accent-hover)'}
                onMouseLeave={e => e.currentTarget.style.backgroundColor = 'var(--color-accent)'}
              >
                <span>📋</span> Open My Google Sheet Tracker
              </a>
            ) : (
              <span style={{
                padding: '11px 16px',
                backgroundColor: 'var(--color-bg)',
                border: '1px solid var(--color-border)',
                borderRadius: '8px',
                color: 'var(--color-text-secondary)',
                fontSize: '0.9rem',
              }}>
                No sheet linked yet — click Sync Now to create one
              </span>
            )}

            {/* Sync Now Button */}
            <button
              onClick={handleSyncNow}
              disabled={syncing}
              style={{
                ...secondaryBtnStyle,
                backgroundColor: 'var(--color-surface)',
                border: '1px solid var(--color-border)',
                color: 'var(--color-text-secondary)',
              }}
              onMouseEnter={e => { if (!syncing) e.currentTarget.style.backgroundColor = 'var(--color-bg)'; }}
              onMouseLeave={e => { if (!syncing) e.currentTarget.style.backgroundColor = 'var(--color-surface)'; }}
            >
              <span>{syncing ? '⏳' : '🔄'}</span>
              {syncing ? 'Syncing…' : 'Sync Now'}
            </button>
          </div>

          {renderFeedback()}

          {/* Sheet URL display */}
          {!sheetLoading && sheetUrl && (
            <div style={{
              marginTop: '16px',
              padding: '10px 14px',
              backgroundColor: 'var(--color-bg)',
              borderRadius: '8px',
              border: '1px solid var(--color-border)',
            }}>
              <span style={{ fontSize: '0.75rem', color: 'var(--color-text-secondary)', fontWeight: '600' }}>LINKED SHEET</span>
              <div style={{ marginTop: '4px', fontSize: '0.8rem', color: 'var(--color-accent)', wordBreak: 'break-all' }}>
                {sheetUrl}
              </div>
            </div>
          )}
        </div>
      </div>

      <style>{`
        .settings-container {
          background-color: var(--color-bg);
          min-height: 100vh;
          color: var(--color-text-primary);
          font-family: system-ui, sans-serif;
        }
        .settings-content {
          max-width: 800px;
          margin: 0 auto;
          padding: 40px 20px;
        }
        .settings-title {
          font-size: 2.5rem;
          font-weight: 800;
          letter-spacing: -0.04em;
          margin: 0;
        }
        .settings-subtitle {
          color: var(--color-text-secondary);
          margin-top: 8px;
          margin-bottom: 40px;
        }

        @media (max-width: 768px) {
          .settings-content {
            padding: 24px 16px;
          }
          .settings-title {
            font-size: 2rem;
          }
          .settings-subtitle {
            margin-bottom: 24px;
          }
          .settings-card {
            padding: 20px 16px !important;
          }
        }
      `}</style>
    </div>
  );
}


export default Settings;
