export default function ConfidenceBar({ value }) {
  return (
    <div className="progress">
      <div
        className="progress-fill"
        style={{ width: `${value}%` }}
      />
    </div>
  );
}
