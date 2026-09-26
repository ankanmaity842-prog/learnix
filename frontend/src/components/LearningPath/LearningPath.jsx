import "./LearningPath.css";

function LearningPath({
  path = [],
}) {
  return (
    <section className="learning-path">
      <div className="path-header">
        <span>AI learning plan</span>
        <h3>Your learning path</h3>
      </div>

      <div className="path-list">
        {path.map((item, index) => (
          <div className="path-item" key={item.topic}>
            <div className="path-number">
              {index + 1}
            </div>

            <div className="path-content">
              <strong>{item.topic}</strong>
              <span>{item.status}</span>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

export default LearningPath;