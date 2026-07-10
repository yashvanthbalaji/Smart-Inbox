import React, { useState, useEffect } from 'react';
import FullCalendar from '@fullcalendar/react';
import dayGridPlugin from '@fullcalendar/daygrid';
import Navbar from '../components/Navbar';
import EventModal from '../components/EventModal';
import apiClient from '../api/client';
import './Calendar.css';

function Calendar() {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedEvent, setSelectedEvent] = useState(null);

  useEffect(() => {
    const fetchEvents = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await apiClient.get('/events');
        setEvents(response.data);
      } catch (err) {
        console.error('Failed to fetch events for calendar:', err);
        setError('Failed to load events. Please try refreshing the page.');
      } finally {
        setLoading(false);
      }
    };

    fetchEvents();
  }, []);

  const getEventColor = (type) => {
    switch (type) {
      case 'MEETING': return '#2563eb';
      case 'EXAM': return '#dc2626';
      case 'DEADLINE': return '#db2777';
      case 'INTERVIEW': return '#9333ea';
      case 'REMINDER': return '#d97706';
      default: return '#4b5563';
    }
  };

  // Transform events for FullCalendar
  const transformedEvents = events
    .filter(e => e.date) // Only render events that have a date
    .map(e => {
      const startValue = e.time ? `${e.date}T${e.time}` : e.date;
      const typeClass = `fc-event-${(e.type || 'other').toLowerCase()}`;

      return {
        id: String(e.id),
        title: e.title,
        start: startValue,
        date: startValue,
        backgroundColor: getEventColor(e.type),
        borderColor: getEventColor(e.type),
        classNames: [typeClass],
        extendedProps: {
          description: e.description,
          location: e.location,
          type: e.type,
          status: e.status
        }
      };
    });

  const handleEventClick = (clickInfo) => {
    const fcEvent = clickInfo.event;
    
    // Parse out simple date and time strings
    let dateStr = null;
    let timeStr = null;
    if (fcEvent.startStr) {
      if (fcEvent.startStr.includes('T')) {
        const parts = fcEvent.startStr.split('T');
        dateStr = parts[0];
        timeStr = parts[1].substring(0, 5); // get HH:MM
      } else {
        dateStr = fcEvent.startStr;
      }
    }

    const eventDetails = {
      id: fcEvent.id,
      title: fcEvent.title,
      date: dateStr,
      time: timeStr,
      type: fcEvent.extendedProps.type,
      location: fcEvent.extendedProps.location,
      description: fcEvent.extendedProps.description,
      status: fcEvent.extendedProps.status
    };

    setSelectedEvent(eventDetails);
  };

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
          Loading calendar events…
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
          color: '#f87171',
          textAlign: 'center'
        }}>
          <p style={{ margin: 0 }}>⚠️ {error}</p>
        </div>
      );
    }

    return (
      <div className="calendar-wrapper">
        <FullCalendar
          plugins={[dayGridPlugin]}
          initialView="dayGridMonth"
          events={transformedEvents}
          eventClick={handleEventClick}
          height="auto"
        />
      </div>
    );
  };

  return (
    <div className="calendar-page-container">
      <Navbar />
      <div className="calendar-main-content">
        <div className="calendar-header">
          <h1 className="calendar-title">Calendar</h1>
          <p className="calendar-subtitle">
            {loading ? 'Fetching your events…' : `Displaying ${transformedEvents.length} scheduled event(s). Click any event to view details.`}
          </p>
        </div>

        {renderContent()}
      </div>

      <EventModal
        event={selectedEvent}
        onClose={() => setSelectedEvent(null)}
      />
    </div>
  );
}

export default Calendar;
