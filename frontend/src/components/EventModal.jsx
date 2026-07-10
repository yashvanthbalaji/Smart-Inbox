import React from 'react';
import './EventModal.css';

function EventModal({ event, onClose }) {
  if (!event) return null;

  const getTypeBadgeClass = (type) => {
    switch (type) {
      case 'MEETING': return 'badge-type-meeting';
      case 'EXAM': return 'badge-type-exam';
      case 'DEADLINE': return 'badge-type-deadline';
      case 'INTERVIEW': return 'badge-type-interview';
      case 'REMINDER': return 'badge-type-reminder';
      default: return 'badge-type-other';
    }
  };

  const getStatusBadgeClass = (status) => {
    switch (status) {
      case 'DONE': return 'badge-status-done';
      case 'SNOOZED': return 'badge-status-snoozed';
      default: return 'badge-status-pending';
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2 className="modal-title">{event.title}</h2>
          <button className="modal-close-btn" onClick={onClose}>&times;</button>
        </div>
        
        <div className="modal-body">
          <div className="modal-meta-row">
            <div className="modal-meta-item">
              <span className="meta-label">Type</span>
              <span className={`badge ${getTypeBadgeClass(event.type)}`}>
                {event.type}
              </span>
            </div>
            
            <div className="modal-meta-item">
              <span className="meta-label">Status</span>
              <span className={`badge ${getStatusBadgeClass(event.status)}`}>
                {event.status}
              </span>
            </div>
          </div>

          <div className="modal-info-grid">
            <div className="modal-info-item">
              <span className="info-icon">📅</span>
              <div>
                <div className="info-label">Date</div>
                <div className="info-value">{event.date || '—'}</div>
              </div>
            </div>

            <div className="modal-info-item">
              <span className="info-icon">⏰</span>
              <div>
                <div className="info-label">Time</div>
                <div className="info-value">{event.time || '—'}</div>
              </div>
            </div>

            <div className="modal-info-item">
              <span className="info-icon">📍</span>
              <div>
                <div className="info-label">Location</div>
                <div className="info-value">{event.location || '—'}</div>
              </div>
            </div>
          </div>

          {event.description && (
            <div className="modal-description-section">
              <div className="description-label">Description</div>
              <p className="description-text">{event.description}</p>
            </div>
          )}
        </div>

        <div className="modal-footer">
          <button className="modal-btn-close" onClick={onClose}>Close</button>
        </div>
      </div>
    </div>
  );
}

export default EventModal;
