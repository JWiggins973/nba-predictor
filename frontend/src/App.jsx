import { useState, useEffect } from 'react'
import './index.css'
import Header from './components/Header.jsx'
import SearchBar from './components/SearchBar.jsx'
import PlayerCard from './components/PlayerCard.jsx'
import PredictionPanel from './components/PredictionPanel.jsx'
import SeasonChart from './components/SeasonChart.jsx'

const API = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

function formatPlayer(data) {
  return {
    name: data.player,
    team: data.team,
    ppg: data.last_season_ppg.toFixed(1),
    predicted: data.predicted_ppg.toFixed(1),
    actual: data.actual_ppg ? data.actual_ppg.toFixed(1) : null,
    rpg: data.last_season_stats.reb.toFixed(1),
    apg: data.last_season_stats.ast.toFixed(1),
    usg: (data.last_season_stats.usg_pct * 100).toFixed(1),
    ts: (data.last_season_stats.ts_pct * 100).toFixed(1),
  }
}

function App() {
  const [player, setPlayer] = useState(null)
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [players, setPlayers] = useState([])

  useEffect(() => {
    fetch(`${API}/players`)
      .then(res => res.json())
      .then(data => setPlayers(data.players))
  }, [])

  async function handleSearch(name) {
    setLoading(true)
    setError(null)
    setPlayer(null)
    setHistory([])

    try {
      const [predictRes, historyRes] = await Promise.all([
        fetch(`${API}/predict/${name}`),
        fetch(`${API}/history/${name}`)
      ])

      if (!predictRes.ok) throw new Error('Player not found')

      const predictData = await predictRes.json()
      const historyData = await historyRes.json()

      setPlayer(formatPlayer(predictData))

      setHistory(historyData.history)

    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <Header />
      <SearchBar onSearch={handleSearch} players={players} />
      {loading && <p className="status">Loading...</p>}
      {error && <p className="status error">{error}</p>}
      {player && <PlayerCard player={player} />}
      {player && <PredictionPanel player={player} />}
      {player && <SeasonChart history={history} predicted={parseFloat(player.predicted)} actual={player.actual ? parseFloat(player.actual) : null} />}
    </div>
  )
}

export default App