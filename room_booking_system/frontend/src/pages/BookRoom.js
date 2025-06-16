import React from 'react';
import { useParams } from 'react-router-dom';

export default function BookRoom() {
  const { id } = useParams();
  return <h2>Booking Form for Room ID: {id}</h2>;
}
