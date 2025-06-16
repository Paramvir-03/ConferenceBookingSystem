import React, { useEffect, useState } from 'react';
import axios from 'axios';
import './App.css';

// Login Form
function LoginForm({ onLogin }) {
  const [formData, setFormData] = useState({ username: '', password: '' });

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    axios.post('http://127.0.0.1:8000/api/login/', formData)
      .then(res => {
        localStorage.setItem('token', res.data.token);
        localStorage.setItem('user_id', res.data.user_id);
        localStorage.setItem('is_admin', res.data.is_admin);
        onLogin(res.data.token, res.data.user_id, res.data.is_admin);
      })
      .catch(err => {
        alert("Login failed");
        console.error(err.response?.data || err.message);
      });
  };

  return (
    <form onSubmit={handleSubmit}>
      <h2>Login</h2>
      <input type="text" name="username" placeholder="Username" onChange={handleChange} required />
      <input type="password" name="password" placeholder="Password" onChange={handleChange} required />
      <button type="submit">Login</button>
    </form>
  );
}

function RegisterForm({ onSwitchToLogin }) {
  const [formData, setFormData] = useState({ username: '', password: '' });

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    axios.post('http://127.0.0.1:8000/api/register/', formData)
      .then(() => {
        alert("Registration successful! Please log in.");
        onSwitchToLogin();
      })
      .catch(err => {
        alert("Registration failed.");
        console.error(err.response?.data || err.message);
      });
  };

  return (
    <form onSubmit={handleSubmit}>
      <h2>Register</h2>
      <input type="text" name="username" placeholder="Username" onChange={handleChange} required />
      <input type="password" name="password" placeholder="Password" onChange={handleChange} required />
      <button type="submit">Register</button>
      <p>Already have an account? <button type="button" onClick={onSwitchToLogin}>Login</button></p>
    </form>
  );
}

function ManageRooms({ token }) {
  const [rooms, setRooms] = useState([]);
  const [roomName, setRoomName] = useState('');

  // ✅ Fetch rooms ONLY when token is available
  useEffect(() => {
    if (token) {
      fetchRooms();
    }
  }, [token]);

  const fetchRooms = () => {
    axios.get('http://127.0.0.1:8000/api/rooms/', {
      headers: { Authorization: `Token ${token}` }
    })
      .then(res => setRooms(res.data))
      .catch(err => {
        console.error("Error fetching rooms:", err.response?.data || err.message);
      });
  };

  const handleAddRoom = () => {
    if (!roomName.trim()) return alert("Room name cannot be empty.");

    axios.post('http://127.0.0.1:8000/api/rooms/', {
      name: roomName,
      capacity: 10,
      available: true }, {
      headers: { Authorization: `Token ${token}` }
    })
      .then(() => {
        setRoomName('');
        fetchRooms();
      })
      .catch(err => {
        console.error("Error adding room:", err.response?.data || err.message);
        alert("You might not have permission to add rooms.");
      });
  };

  const handleDeleteRoom = (roomId) => {
    axios.delete(`http://127.0.0.1:8000/api/rooms/${roomId}/`, {
      headers: { Authorization: `Token ${token}` }
    })
      .then(fetchRooms)
      .catch(err => {
        console.error("Error deleting room:", err.response?.data || err.message);
        alert("You might not have permission to delete rooms.");
      });
  };

  return (
    <div>
      <h3>Manage Rooms</h3>
      <input
        type="text"
        value={roomName}
        onChange={(e) => setRoomName(e.target.value)}
        placeholder="New room name"
      />
      <button onClick={handleAddRoom}>Add Room</button>
      <ul>
        {rooms.map((room) => (
          <li key={room.id}>
            {room.name}
            <button onClick={() => handleDeleteRoom(room.id)}>Delete</button>
          </li>
        ))}
      </ul>
    </div>
  );
}
function ManageUsers({ token }) {
  const [users, setUsers] = useState([]);

  const fetchUsers = () => {
    axios.get('http://127.0.0.1:8000/api/users/', {
      headers: { Authorization: `Token ${token}` }
    })
    .then(res => setUsers(res.data))
    .catch(err => console.error("Error fetching users:", err));
  };

  useEffect(fetchUsers, [token]);

  const toggleAdmin = (userId) => {
    axios.patch(`http://127.0.0.1:8000/api/toggle-admin/${userId}/`, {}, {
      headers: { Authorization: `Token ${token}` }
    })
    .then(() => {
      alert("User role updated!");
      fetchUsers();
    })
    .catch(err => {
      alert(err.response?.data?.error || "Error toggling role.");
    });
  };

  const deleteUser = (userId) => {
    if (window.confirm("Are you sure you want to delete this user?")) {
      axios.delete(`http://127.0.0.1:8000/api/users/${userId}/`, {
        headers: { Authorization: `Token ${token}` }
      })
      .then(() => {
        alert("User deleted.");
        fetchUsers();
      })
      .catch(err => {
        alert("Error deleting user.");
        console.error(err);
      });
    }
  };

  return (
    <div>
      <h3>Manage Users</h3>
      <table border="1" cellPadding="5">
        <thead>
          <tr>
            <th>Username</th>
            <th>Role</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {users.map(user => (
            <tr key={user.id}>
              <td>{user.username}</td>
              <td>{user.is_staff ? "Admin" : "User"}</td>
              <td>
                <button onClick={() => toggleAdmin(user.id)}>
                  {user.is_staff ? "Demote to User" : "Promote to Admin"}
                </button>
                &nbsp;
                <button onClick={() => deleteUser(user.id)} style={{ color: 'red' }}>
                  Delete
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
function ReserveForUsers({ token }) {
  const [rooms, setRooms] = useState([]);
  const [users, setUsers] = useState([]);
  const [form, setForm] = useState({
    room: '',
    user_id: '',
    start_time: '',
    end_time: '',
  });

  useEffect(() => {
    axios.get('http://127.0.0.1:8000/api/rooms/')
      .then(res => setRooms(res.data));
    axios.get('http://127.0.0.1:8000/api/users/', {
      headers: { Authorization: `Token ${token}` }
    }).then(res => setUsers(res.data));
  }, [token]);

  const handleChange = e => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = e => {
    e.preventDefault();
    axios.post('http://127.0.0.1:8000/api/book/', form, {
      headers: { Authorization: `Token ${token}` }
    }).then(() => {
      alert("Booking created for user!");
      setForm({ room: '', user_id: '', start_time: '', end_time: '' });
    }).catch(err => {
      alert(err.response?.data?.error || "Booking failed.");
    });
  };

  return (
    <div>
      <h3>Reserve for Users</h3>
      <form onSubmit={handleSubmit}>
        <label>User:</label>
        <select name="user_id" value={form.user_id} onChange={handleChange} required>
          <option value="">-- Select User --</option>
          {users.map(u => (
            <option key={u.id} value={u.id}>{u.username}</option>
          ))}
        </select><br />

        <label>Room:</label>
        <select name="room" value={form.room} onChange={handleChange} required>
          <option value="">-- Select Room --</option>
          {rooms.map(r => (
            <option key={r.id} value={r.id}>{r.name}</option>
          ))}
        </select><br />

        <label>Start Time:</label>
        <input type="datetime-local" name="start_time" value={form.start_time} onChange={handleChange} required /><br />
        <label>End Time:</label>
        <input type="datetime-local" name="end_time" value={form.end_time} onChange={handleChange} required /><br />

        <button type="submit">Book Room for User</button>
      </form>
    </div>
  );
}

// Booking Form
function BookingForm({ bookingToEdit, onUpdateDone, userId, token }) {
  const [rooms, setRooms] = useState([]);
  const isEditing = !!bookingToEdit;
  const [users, setUsers] = useState([]);


  const [formData, setFormData] = useState({
    user: userId,
    room: '',
    start_time: '',
    end_time: ''
  });
useEffect(() => {
  if (localStorage.getItem('is_admin') === 'true') {
    axios.get('http://127.0.0.1:8000/api/users/', {
      headers: { Authorization: `Token ${token}` }
    })
      .then(res => setUsers(res.data))
      .catch(err => console.error("Error fetching users:", err));
  }
}, [token]);


  useEffect(() => {
    axios.get('http://127.0.0.1:8000/api/rooms/')
      .then(res => setRooms(res.data))
      .catch(err => console.error("Error fetching rooms:", err));
  }, []);

  useEffect(() => {
    if (isEditing) {
      setFormData({
        user: bookingToEdit.user,
        room: bookingToEdit.room,
        start_time: bookingToEdit.start_time.slice(0, 16),
        end_time: bookingToEdit.end_time.slice(0, 16)
      });
    } else {
      setFormData((prev) => ({ ...prev, user: userId }));
    }
  }, [bookingToEdit, userId]);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const url = isEditing
      ? `http://127.0.0.1:8000/api/bookings/update/${bookingToEdit.id}/`
      : 'http://127.0.0.1:8000/api/book/';

    const method = isEditing ? axios.patch : axios.post;

    method(url, formData, {
      headers: { Authorization: `Token ${token}` }
    })
      .then(() => {
        alert(isEditing ? 'Booking updated!' : 'Room booked successfully!');
        setFormData({ user: userId, room: '', start_time: '', end_time: '' });
        onUpdateDone();
      })
      .catch(err => {
          const errorMsg=
              err.response?.data?.error || "Booking failed. Please check your input.";
          alert(errorMsg);
        console.error(err.response?.data || err.message);
      });
  };

  return (
    <form onSubmit={handleSubmit}>
      <h2>{isEditing ? 'Update Booking' : 'Book a Room'}</h2>
        {localStorage.getItem('is_admin') === 'true' && (
  <select name="user" value={formData.user} onChange={handleChange} required>
    <option value="">Select User</option>
    {users.map(user => (
      <option key={user.id} value={user.id}>{user.username}</option>
    ))}
  </select>
)}

      <select name="room" value={formData.room} onChange={handleChange} required>
        <option value="">Select Room</option>
        {rooms.map(room => (
          <option key={room.id} value={room.id}>{room.name}</option>
        ))}
      </select>
      <input type="datetime-local" name="start_time" value={formData.start_time} onChange={handleChange} required />
      <input type="datetime-local" name="end_time" value={formData.end_time} onChange={handleChange} required />
      <button type="submit">{isEditing ? 'Update' : 'Book'}</button>
    </form>
  );
}

// Booking List
function BookingList({ onEdit, token }) {
  const [bookings, setBookings] = useState([]);

  const fetchBookings = () => {
    axios.get('http://127.0.0.1:8000/api/bookings/', {
      headers: { Authorization: `Token ${token}` }
    })
      .then(response => setBookings(response.data))
      .catch(error => console.error("Error fetching bookings:", error));
  };

  useEffect(fetchBookings, [token]);

  const handleDelete = (id) => {
    axios.delete(`http://127.0.0.1:8000/api/bookings/${id}/`, {
      headers: { Authorization: `Token ${token}` }
    })
      .then(() => {
        alert("Booking deleted");
        fetchBookings();
      })
      .catch(err => {
        alert("Failed to delete");
        console.error(err);
      });
  };

  return (
    <div>
      <h2>All Bookings</h2>
      <ul>
        {bookings.map((booking) => (
          <li key={booking.id}>
            Room: {booking.room_name || booking.room} | By: User ID {booking.user} |
            From: {booking.start_time_local || booking.start_time} |
            To: {booking.end_time_local || booking.end_time}
            <button onClick={() => handleDelete(booking.id)}>Delete</button>
            <button onClick={() => onEdit(booking)}>Edit</button>
          </li>
        ))}
      </ul>
    </div>
  );
}



// App Entry Point
function App() {
    const [showManageUsers, setShowManageUsers] = useState(false);

  const [editingBooking, setEditingBooking] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [userId, setUserId] = useState(localStorage.getItem('user_id'));
  const [showRegister, setShowRegister] = useState(false);  // 👈 Toggle state
  const [isAdmin, setIsAdmin] = useState(localStorage.getItem('is_admin') === 'true');

  const handleLogin = (token, userId, isAdmin) => {
      localStorage.setItem('token', token);
      localStorage.setItem('user_id', userId);
      localStorage.setItem('is_admin', isAdmin);

  setToken(token);
  setUserId(userId);
  setIsAdmin(isAdmin);
};

  const handleUpdateDone = () => {
    setEditingBooking(null);
  };

  const handleLogout = () => {
  if (window.confirm("Are you sure you want to logout?")) {
    localStorage.clear();
    setToken(null);
    setUserId(null);
    setIsAdmin(false);
  }
};

  if (!token) {
    return showRegister ? (
      <RegisterForm onSwitchToLogin={() => setShowRegister(false)} />
    ) : (
      <>
        <LoginForm onLogin={handleLogin} />
        <p>Don't have an account? <button onClick={() => setShowRegister(true)}>Register</button></p>
      </>
    );
  }

  return (

    <div className="App">
        <p>Logged in as: {isAdmin ? "Admin" : "User"}</p>

      <h1>Room Booking System</h1>
      <button onClick={handleLogout}>Logout</button>
        {isAdmin && (
  <div className="admin-panel">
    <h2>Admin Panel</h2>
    <ManageRooms token={token} />
    <ManageUsers token={token} />
    <ReserveForUsers token={token} />
    <button onClick={() => alert("All Reservations already below")}>View All Reservations</button>
  </div>
)}

      <BookingForm bookingToEdit={editingBooking} onUpdateDone={handleUpdateDone} userId={userId} token={token} />
      <BookingList onEdit={setEditingBooking} token={token} />
    </div>
  );
}


export default App;
