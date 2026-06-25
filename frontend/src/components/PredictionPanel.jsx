import '../styles/PredictionPanel.css'


function PredictionPanel({ onExplain, player, explained }) {
  return (
    <div className="prediction card">
      <h3 className="prediction-title">{player.predictedSeason} Prediction</h3>
      <div className="prediction-rows">
        <div className="prediction-row">
          <span className="prediction-label">Predicted</span>
          <span className="prediction-value accent">{player.predicted}</span>
        </div>      
        {player.actual && (
          <div className="prediction-row">
            <span className="prediction-label">Actual</span>
            <span className="prediction-value">{player.actual}</span>
          </div>
        )}
        {player.actual && !explained &&(
          <button className="prediction-btn" onClick={() => onExplain(player.name)}>
            <span className="prediction-button-text">Why the difference or similarity?</span>

          </button>
        )}  
        {explained && <p className="prediction-explanation">{explained}</p>}
      </div>
    </div>
  )
}

export default PredictionPanel