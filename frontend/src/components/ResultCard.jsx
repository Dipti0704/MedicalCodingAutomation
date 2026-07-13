import ConfidenceBar from "./ConfidenceBar";

const STATUS_LABELS = {
  pending: "Pending review",
  approved: "Approved",
  rejected: "Rejected",
};

export default function ResultCard({ title, codes, onDecide }) {
  return (
    <div className="card">
      <div className="section-title">{title}</div>

      {codes.length === 0 && (
        <div className="empty">No codes detected</div>
      )}

      {codes.map((item) => (
        <div className="result-item" key={item.review_id}>
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

          {item.explanation && (
            <div className="explanation">
              {item.explanation}
            </div>
          )}

          {item.related_codes && item.related_codes.length > 0 && (
            <div className="related-codes">
              <div className="related-codes-title">Related codes in this category</div>
              {item.related_codes.map((related) => (
                <div className="related-code-row" key={related.code}>
                  <span className="related-code">{related.code}</span>
                  <span className="related-description">{related.description}</span>
                </div>
              ))}
            </div>
          )}

          <div className="review-row">
            <span className={`status-badge status-${item.status}`}>
              {STATUS_LABELS[item.status]}
            </span>

            <div className="review-actions">
              <button
                type="button"
                className="approve-button"
                disabled={item.status === "approved"}
                onClick={() => onDecide(item.review_id, "approved")}
              >
                Approve
              </button>
              <button
                type="button"
                className="reject-button"
                disabled={item.status === "rejected"}
                onClick={() => onDecide(item.review_id, "rejected")}
              >
                Reject
              </button>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
