import React, { useState } from 'react'
import { CalendarDays, AlertCircle, Sparkles } from 'lucide-react'

export default function MealPlan() {
  const [plan, setPlan] = useState(null)
  const [loading, setLoading] = useState(false)
  const [errorMsg, setErrorMsg] = useState('')

  const generatePlan = async () => {
    setLoading(true)
    setErrorMsg('')
    
    // Simulate getting inventory from centralized state or local storage
    const inventory = [{name: 'Eggs'}, {name: 'Bread'}, {name: 'Milk'}] 
    const prefs = localStorage.getItem('mealPrefs') ? JSON.parse(localStorage.getItem('mealPrefs')) : {}

    try {
      const response = await fetch('/api/generate-plan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ inventory, preferences: prefs })
      })

      const data = await response.json()
      if (!response.ok) throw new Error(data.detail || 'Generation failed')
      
      setPlan(data.plan)
    } catch (err) {
      setErrorMsg(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      <div className="header">
        <h1>Weekly Meal Plan</h1>
        <button 
          className="btn-primary" 
          onClick={generatePlan} 
          disabled={loading}
          style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}
        >
          <Sparkles size={18} /> {loading ? 'Generating AI Plan...' : 'Generate New Plan'}
        </button>
      </div>

      {errorMsg && (
        <div className="glass-panel error-panel">
          <AlertCircle size={24} /> {errorMsg}
        </div>
      )}

      {!plan && !loading && !errorMsg && (
        <div className="glass-panel" style={{ textAlign: 'center', padding: '4rem 2rem' }}>
          <CalendarDays size={48} style={{ color: 'var(--text-secondary)', marginBottom: '1rem' }} />
          <h2>No plan active</h2>
          <p style={{ color: 'var(--text-secondary)' }}>Click generate to let AI optimize your weekly meals.</p>
        </div>
      )}

      {plan && (
        <div style={{ display: 'grid', gap: '1rem' }}>
          {plan.map((item, i) => (
            <div key={i} className="glass-panel" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <h3 style={{ color: 'var(--secondary-color)', fontSize: '1.2rem' }}>{item.day}</h3>
                <p style={{ fontSize: '1.1rem', fontWeight: 500, margin: '0.25rem 0' }}>{item.meal}</p>
              </div>
              <div style={{ background: 'rgba(255,255,255,0.1)', padding: '0.5rem 1rem', borderRadius: '8px', fontSize: '0.9rem' }}>
                ⏱ {item.time}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
