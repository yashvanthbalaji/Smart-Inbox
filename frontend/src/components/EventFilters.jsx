import React from 'react';
import './EventFilters.css';

const TYPE_OPTIONS = [
  { label: 'All', value: 'ALL' },
  { label: 'Meeting', value: 'MEETING' },
  { label: 'Exam', value: 'EXAM' },
  { label: 'Deadline', value: 'DEADLINE' },
  { label: 'Interview', value: 'INTERVIEW' },
  { label: 'Reminder', value: 'REMINDER' },
  { label: 'Other', value: 'OTHER' },
];

const STATUS_OPTIONS = [
  { label: 'All', value: 'ALL' },
  { label: 'Pending', value: 'PENDING' },
  { label: 'Done', value: 'DONE' },
  { label: 'Snoozed', value: 'SNOOZED' },
];

function EventFilters({ activeType, onTypeChange, activeStatus, onStatusChange }) {
  return (
    <div className="filters-container">
      <div className="filter-group">
        <span className="filter-label">Type</span>
        <div className="filter-pills">
          {TYPE_OPTIONS.map((opt) => (
            <button
              key={opt.value}
              className={`filter-pill filter-pill-type-${opt.value.toLowerCase()} ${activeType === opt.value ? 'active' : ''}`}
              onClick={() => onTypeChange(opt.value)}
            >
              {opt.label}
            </button>
          ))}
        </div>
      </div>

      <div className="filter-group">
        <span className="filter-label">Status</span>
        <div className="filter-pills">
          {STATUS_OPTIONS.map((opt) => (
            <button
              key={opt.value}
              className={`filter-pill filter-pill-status-${opt.value.toLowerCase()} ${activeStatus === opt.value ? 'active' : ''}`}
              onClick={() => onStatusChange(opt.value)}
            >
              {opt.label}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

export default EventFilters;
