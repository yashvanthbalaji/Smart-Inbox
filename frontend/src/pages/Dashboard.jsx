import React, { useState, useEffect } from 'react';
import Navbar from '../components/Navbar';
import EventTable from '../components/EventTable';
import EventFilters from '../components/EventFilters';
import apiClient from '../api/client';

function Dashboard() {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeType, setActiveType] = useState('ALL');
  const [activeStatus, setActiveStatus] = useState('ALL');
  const [toast, setToast] = useState(null);

  useEffect(() => {
    const fetchEvents = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await apiClient.get('/events');
        setEvents(response.data);
      } catch (err) {
        console.error('Failed to fetch events:', err);
        setError('Failed to load events. Please try refreshing the page.');
      } finally {
        setLoading(false);
      }
    };

    fetchEvents();
  }, []);

  const showToast = (message, type = 'success') => {
    setToast({ message, type });
    setTimeout(() => {
      setToast(null);
    }, 4000);
  };

  const handleMarkDone = async (id) => {
    try {
      const response = await apiClient.post(`/events/${id}/done`);
      // Update local state immediately
      setEvents(prev => prev.map(e => e.id === id ? { ...e, status: 'DONE' } : e));
      showToast(`Event "${response.data.title}" marked as done!`);
    } catch (err) {
      console.error('Failed to mark event done:', err);
      showToast('Failed to update event status.', 'error');
    }
  };

  const handleSnooze = async (id) => {
    try {
      const response = await apiClient.post(`/events/${id}/snooze`);
      // Update local state immediately
      setEvents(prev => prev.map(e => e.id === id ? { ...e, status: 'SNOOZED' } : e));
      showToast(`Event "${response.data.title}" has been snoozed.`);
    } catch (err) {
      console.error('Failed to snooze event:', err);
      showToast('Failed to snooze event.', 'error');
    }
  };

  const handleDelete = async (id) => {
    try {
      await apiClient.post(`/events/${id}/delete`);
      // Get the title of the deleted event for Toast
      const targetEvent = events.find(e => e.id === id);
      const title = targetEvent ? targetEvent.title : 'Event';
      
      // Update local state immediately
      setEvents(prev => prev.filter(e => e.id !== id));
      showToast(`"${title}" deleted successfully.`);
    } catch (err) {
      console.error('Failed to delete event:', err);
      showToast('Failed to delete event.', 'error');
    }
  };

  const handleExportPDF = async () => {
    try {
      showToast('Generating events PDF…');
      const response = await apiClient.get('/export/pdf', {
        responseType: 'blob'
      });

      // Create a blob URL and trigger browser download
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'smartinbox_events.pdf');
      
      document.body.appendChild(link);
      link.click();
      
      // Cleanup DOM
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      showToast('PDF downloaded successfully!');
    } catch (err) {
      console.error('Failed to export PDF:', err);
      showToast('Failed to export events PDF.', 'error');
    }
  };

  // Filter events by active type and status
  const filteredEvents = events.filter((event) => {
    const typeMatch = activeType === 'ALL' || event.type === activeType;
    const statusMatch = activeStatus === 'ALL' || event.status === activeStatus;
    return typeMatch && statusMatch;
  });

  const renderContent = () => {
    if (loading) {
      return (
        <div style={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          padding: '80px 20px',
          color: '#64748b',
          fontSize: '1rem',
          gap: '12px'
        }}>
          <span style={{ fontSize: '1.5rem' }}>⏳</span>
          Loading events…
        </div>
      );
    }

    if (error) {
      return (
        <div style={{
          backgroundColor: 'rgba(239, 68, 68, 0.08)',
          border: '1px solid rgba(239, 68, 68, 0.25)',
          borderRadius: '12px',
          padding: '24px',
          marginTop: '24px',
          color: '#f87171',
          textAlign: 'center'
        }}>
          <p style={{ margin: 0, fontSize: '1rem' }}>⚠️ {error}</p>
        </div>
      );
    }

    return (
      <>
        <EventFilters
          activeType={activeType}
          onTypeChange={setActiveType}
          activeStatus={activeStatus}
          onStatusChange={setActiveStatus}
        />
        <EventTable
          events={filteredEvents}
          onMarkDone={handleMarkDone}
          onDelete={handleDelete}
          onSnooze={handleSnooze}
        />
      </>
    );
  };

  return (
    <div className="dashboard-container">
      <Navbar />
      <div className="dashboard-content">
        <div className="dashboard-header">
          <div>
            <h1 className="dashboard-title">
              Dashboard
            </h1>
            <p className="dashboard-subtitle">
              {loading ? 'Fetching your extracted events…' : `${events.length} event${events.length !== 1 ? 's' : ''} extracted from your inbox`}
            </p>
          </div>
          {!loading && !error && events.length > 0 && (
            <button
              onClick={handleExportPDF}
              className="btn-export-pdf"
              style={{
                padding: '10px 20px',
                backgroundColor: 'var(--color-accent)',
                color: '#fff',
                border: 'none',
                borderRadius: '8px',
                fontWeight: '600',
                cursor: 'pointer',
                fontSize: '0.9rem',
                boxShadow: 'var(--shadow-sm)',
                transition: 'all 0.2s ease',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                marginTop: '6px'
              }}
              onMouseEnter={(e) => e.currentTarget.style.backgroundColor = 'var(--color-accent-hover)'}
              onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'var(--color-accent)'}
            >
              <span>📥</span> Export PDF
            </button>
          )}
        </div>

        {renderContent()}
      </div>

      {/* Premium Toast Notification overlay */}
      {toast && (
        <div style={{
          position: 'fixed',
          bottom: '24px',
          right: '24px',
          backgroundColor: toast.type === 'success' ? '#10b981' : '#ef4444',
          color: '#fff',
          padding: '14px 24px',
          borderRadius: '10px',
          boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.4)',
          zIndex: 1000,
          fontWeight: '600',
          fontSize: '0.95rem',
          display: 'flex',
          alignItems: 'center',
          gap: '10px',
          animation: 'slideIn 0.25s cubic-bezier(0.16, 1, 0.3, 1)',
          border: '1px solid rgba(255, 255, 255, 0.1)'
        }}>
          <span>{toast.type === 'success' ? '✅' : '❌'}</span>
          <span>{toast.message}</span>
        </div>
      )}

      {/* Responsive styles for Dashboard layout */}
      <style>{`
        .dashboard-container {
          background-color: var(--color-bg);
          min-height: 100vh;
          color: var(--color-text-primary);
          font-family: system-ui, sans-serif;
          position: relative;
        }
        .dashboard-content {
          max-width: 1200px;
          margin: 0 auto;
          padding: 40px 20px;
        }
        .dashboard-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          margin-bottom: 32px;
          gap: 16px;
        }
        .dashboard-title {
          font-size: 2.5rem;
          font-weight: 800;
          letter-spacing: -0.04em;
          margin: 0;
        }
        .dashboard-subtitle {
          color: var(--color-text-secondary);
          margin-top: 8px;
          margin-bottom: 0;
        }

        @keyframes slideIn {
          from {
            transform: translateY(20px) scale(0.9);
            opacity: 0;
          }
          to {
            transform: translateY(0) scale(1);
            opacity: 1;
          }
        }

        @media (max-width: 768px) {
          .dashboard-content {
            padding: 24px 16px;
          }
          .dashboard-header {
            flex-direction: column;
            align-items: flex-start;
            gap: 16px;
            margin-bottom: 24px;
          }
          .dashboard-title {
            font-size: 2rem;
          }
          .btn-export-pdf {
            width: 100%;
            justify-content: center;
          }
        }
      `}</style>
    </div>

  );
}

export default Dashboard;
