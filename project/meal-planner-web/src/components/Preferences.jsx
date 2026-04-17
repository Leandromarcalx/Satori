import React, { useState, useEffect } from 'react'
import { Save, Clock, Info } from 'lucide-react'

export default function Preferences() {
  const [prefs, setPrefs] = useState({
    dietary: '',
    cookDays: 3,
    cookHours: 1.5
  })
  const [saved, setSaved] = useState(false)

  // Load from local storage on mount
  useEffect(() => {
    const local = localStorage.getItem('mealPrefs')
    if (local) {
      setPrefs(JSON.parse(local))
    }
  }, [])

  const handleChange = (e) => {
    const { name, value } = e.target
    setPrefs(prev => ({ ...prev, [name]: value }))
    setSaved(false)
  }

  const handleSave = (e) => {
    e.preventDefault()
    localStorage.setItem('mealPrefs', JSON.stringify(prefs))
    setSaved(true)
    setTimeout(() => setSaved(false), 3000)
  }

  return (
    <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      <div className="header">
        <h1>Preferences & Constraints</h1>
      </div>

      <form onSubmit={handleSave} className="glass-panel" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
        
        <div>
          <label style={{ display: 'flex', gap: '0.5rem', marginBottom: '0.5rem', fontWeight: 500 }}>
            <Info size={18} color="var(--primary-color)" /> Dietary Restrictions / Hates
          </label>
          <input 
            type="text" 
            name="dietary" 
            placeholder="e.g. Vegetarian, No peanuts, Hate mushrooms..."
            value={prefs.dietary}
            onChange={handleChange}
          />
        </div>

        <div style={{ display: 'flex', gap: '2rem' }}>
          <div style={{ flex: 1 }}>
            <label style={{ display: 'flex', gap: '0.5rem', marginBottom: '0.5rem', fontWeight: 500 }}>
              <Clock size={18} color="var(--primary-color)" /> Cooking Days per Week
            </label>
            <input 
              type="number" 
              name="cookDays" 
              min="1" max="7"
              value={prefs.cookDays}
              onChange={handleChange}
            />
          </div>

          <div style={{ flex: 1 }}>
            <label style={{ display: 'flex', gap: '0.5rem', marginBottom: '0.5rem', fontWeight: 500 }}>
              <Clock size={18} color="var(--primary-color)" /> Max Hours per Cooking Day
            </label>
            <input 
              type="number" 
              name="cookHours" 
              step="0.5" min="0.5" max="8"
              value={prefs.cookHours}
              onChange={handleChange}
            />
          </div>
        </div>

        <div style={{ display: 'flex', justifyContent: 'flex-start', alignItems: 'center', gap: '1rem', marginTop: '1rem' }}>
          <button type="submit" className="btn-primary" style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
            <Save size={20} /> Save Preferences
          </button>
          
          {saved && <span style={{ color: 'var(--success)' }}>Saved successfully!</span>}
        </div>
      </form>
    </div>
  )
}
