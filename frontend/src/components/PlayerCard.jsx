import '../styles/PlayerCard.css'

function PlayerCard({ player }) {
  return (
    <div className="playercard card">
      <div className="playercard-header">
        <h2 className="playercard-name">{player.name}</h2>
        <span className="playercard-team">{player.team}</span>
      </div>
      <div className="playercard-stats">
        <div className="stat">
          <span className="stat-value">{player.ppg}</span>
          <span className="stat-label">PPG</span>
        </div>
        <div className="stat">
          <span className="stat-value">{player.rpg}</span>
          <span className="stat-label">RPG</span>
        </div>
        <div className="stat">
          <span className="stat-value">{player.apg}</span>
          <span className="stat-label">APG</span>
        </div>
        <div className="stat">
          <span className="stat-value">{player.usg}%</span>
          <span className="stat-label">USG</span>
        </div>
        <div className="stat">
          <span className="stat-value">{player.ts}%</span>
          <span className="stat-label">TS%</span>
        </div>
      </div>
    </div>
  )
}

export default PlayerCard