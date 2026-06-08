import { LineChart, Line, XAxis, YAxis, Tooltip, ReferenceLine, ResponsiveContainer } from 'recharts'
import '../styles/SeasonChart.css'

function SeasonChart({ history, predicted, actual }) {
  const data = [
    ...history,
    {
      season: 'Predicted',
      predicted: predicted,
      actual: actual ? actual : null
    }
  ]

  return (
    <div className="chart card">
      <h3 className="chart-title">Scoring History</h3>
      <ResponsiveContainer width="100%" height={250}>
        <LineChart data={data}>
          <XAxis dataKey="season" tick={{ fill: 'var(--muted)', fontSize: 11 }} interval="preserveStartEnd" />
          <YAxis tick={{ fill: 'var(--muted)', fontSize: 11 }} domain={['auto', 'auto']} />
          <Tooltip
            contentStyle={{ background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: '8px' }}
            labelStyle={{ color: 'var(--white)' }}
          />
          <ReferenceLine x="Predicted" stroke="var(--border)" strokeDasharray="4 4" />
          <Line type="monotone" dataKey="ppg" stroke="var(--accent)" strokeWidth={2} dot={{ fill: 'var(--accent)', r: 3 }} name="PPG" />
          <Line type="monotone" dataKey="predicted" stroke="var(--accent)" strokeWidth={2} dot={{ fill: 'var(--accent)', r: 6 }} name="Predicted" connectNulls />
          <Line type="monotone" dataKey="actual" stroke="var(--green)" strokeWidth={2} dot={{ fill: 'var(--green)', r: 6 }} name="Actual" connectNulls />
        </LineChart>
      </ResponsiveContainer>
      <div className="chart-legend">
        <span className="legend-item"><span className="legend-dot accent"></span>Predicted</span>
        <span className="legend-item"><span className="legend-dot green"></span>Actual</span>
      </div>
    </div>
  )
}

export default SeasonChart