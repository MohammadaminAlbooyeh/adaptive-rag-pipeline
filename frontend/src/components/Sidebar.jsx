import React from 'react';
import { Link } from 'react-router-dom';

function Sidebar() {
  return (
    <nav className="sidebar">
      <ul>
        <li><Link to="/">Home</Link></li>
        <li><Link to="/query">Query</Link></li>
        <li><Link to="/documents">Documents</Link></li>
        <li><Link to="/strategies">Strategies</Link></li>
        <li><Link to="/analytics">Analytics</Link></li>
        <li><Link to="/history">History</Link></li>
      </ul>
    </nav>
  );
}

export default Sidebar;
