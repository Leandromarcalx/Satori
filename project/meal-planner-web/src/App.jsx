import React from 'react'
import { BrowserRouter as Router, Routes, Route, NavLink } from 'react-router-dom'
import { LayoutDashboard, Receipt, Settings, CalendarDays } from 'lucide-react'
import ReceiptUploader from './components/ReceiptUploader'
import Preferences from './components/Preferences'
import MealPlan from './components/MealPlan'
import './App.css'

function Dashboard() {
  return (
    <div className="animate-fade-in">
      <div className="header">
        <h1>Dashboard</h1>
      </div>
      <div className="glass-panel">
        <h2>Welcome back!</h2>
        <p>Your current pantry has items loaded. Ready to cook something delicious?</p>
      </div>
    </div>
  )
}

function App() {
  return (
    <Router>
      <div className="app-container">
        <aside className="sidebar">
          <div className="sidebar-title">MealAI Planner</div>
          <nav>
            <NavLink to="/" end className={({isActive}) => isActive ? "nav-link active" : "nav-link"}>
              <LayoutDashboard size={20} />
              Dashboard
            </NavLink>
            <NavLink to="/plan" className={({isActive}) => isActive ? "nav-link active" : "nav-link"}>
              <CalendarDays size={20} />
              Meal Plan
            </NavLink>
            <NavLink to="/receipts" className={({isActive}) => isActive ? "nav-link active" : "nav-link"}>
              <Receipt size={20} />
              Receipts
            </NavLink>
            <NavLink to="/settings" className={({isActive}) => isActive ? "nav-link active" : "nav-link"}>
              <Settings size={20} />
              Preferences
            </NavLink>
          </nav>
        </aside>

        <main className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/plan" element={<MealPlan />} />
            <Route path="/receipts" element={<ReceiptUploader />} />
            <Route path="/settings" element={<Preferences />} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

export default App
