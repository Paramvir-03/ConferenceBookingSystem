import React from 'react';
import { Link } from 'react-router-dom';

export default function Home() {
  return (
    <div style={{ padding: '20px' }}>
      <h1>🏢 Conference Room Booking</h1>
      <p>Welcome! Use the links below to get started.</p>
      <nav>
        <ul style={{ listStyle: 'none', paddingLeft: 0 }}>
          <li><Link to="/rooms">📋 View Rooms</Link></li>
          <li><Link to="/my-bookings">📅 My Bookings</Link></li>
        </ul>
      </nav>
    </div>
  );
}
