import "./ProgressChart.css";

function ProgressChart({
  progress = 0,
}) {
  return (
    <section className="progress-chart">
      <div className="progress-header">
        <div>
          <span>Learning progress</span>
          <h3>Overall progress</h3>
        </div>

        <strong>
          {Math.round(progress * 100)}%
        </strong>
      </div>

      <div className="progress-track">
        <span
          style={{
            width: `${progress * 100}%`,
          }}
        />
      </div>
    </section>
  );
}

export default ProgressChart;