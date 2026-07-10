import React from 'react';
import './EventTable.css';

function EventTable({ events, onMarkDone, onDelete, onSnooze }) {
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
    <div className="table-responsive">
      <table className="event-table">
        <thead>
          <tr>
            <th>Title</th>
            <th>Type</th>
            <th>Date</th>
            <th>Time</th>
            <th>Location</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {events.map((event) => (
            <tr key={event.id} className="event-row">
              <td className="event-title-cell">
                <div className="event-title">{event.title}</div>
                {event.description && (
                  <div className="event-description">{event.description}</div>
                )}
              </td>
              <td>
                <span className={`badge ${getTypeBadgeClass(event.type)}`}>
                  {event.type}
                </span>
              </td>
              <td>{event.date}</td>
              <td>{event.time || '—'}</td>
              <td>
                <span className="event-location">
                  {event.location || '—'}
                </span>
              </td>
              <td>
                <span className={`badge ${getStatusBadgeClass(event.status)}`}>
                  {event.status}
                </span>
              </td>
              <td>
                <div className="action-buttons">
                  {event.status !== 'DONE' && (
                    <button 
                      onClick={() => onMarkDone(event.id)} 
                      className="btn-action btn-done"
                      title="Mark as Done"
                    >
                      Done
                    </button>
                  )}
                  {event.status !== 'SNOOZED' && event.status !== 'DONE' && (
                    <button 
                      onClick={() => onSnooze(event.id)} 
                      className="btn-action btn-snooze"
                      title="Snooze"
                    >
                      Snooze
                    </button>
                  )}
                  <button 
                    onClick={() => onDelete(event.id)} 
                    className="btn-action btn-delete"
                    title="Delete"
                  >
                    Delete
                  </button>
                </div>
              </td>
            </tr>
          ))}
          {events.length === 0 && (
            <tr>
              <td colSpan="7" className="empty-state">
                No events found.
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}

export default EventTable;
