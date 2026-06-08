import '../styles/PredictionPanel.css'

function PredictionPanel({ player }) {
  return (
    <div className="prediction card">
      <h3 className="prediction-title">2025–26 Prediction</h3>
      <div className="prediction-rows">
        <div className="prediction-row">
          <span className="prediction-label">Predicted</span>
          <span className="prediction-value accent">{player.predicted}</span>
        </div>
        <div className="prediction-row">
          <span className="prediction-label">Last Season</span>
          <span className="prediction-value">{player.ppg}</span>
        </div>
        {player.actual && (
          <div className="prediction-row">
            <span className="prediction-label">Actual</span>
            <span className="prediction-value">{player.actual}</span>
          </div>
        )}
      </div>
    </div>
  )
}

export default PredictionPanel