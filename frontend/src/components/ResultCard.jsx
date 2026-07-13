import ConfidenceBar from "./ConfidenceBar";

export default function ResultCard({ title, codes }) {
  return (
    <div className="card">
      <div className="section-title">{title}</div>

      {codes.length === 0 && (
        <div className="empty">No codes detected</div>
      )}

      {codes.map((item, index) => (
        <div className="result-item" key={index}>
          <div className="code-row">
            <span className="code">{item.code}</span>
            <span className="confidence-badge">
              {item.confidence}%
            </span>
          </div>

          <div className="description">
            {item.description}
          </div>

          <ConfidenceBar value={item.confidence} />
        </div>
      ))}
    </div>
  );
}
