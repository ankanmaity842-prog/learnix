import "./KnowledgeGap.css";

function KnowledgeGap({
  gaps = [],
}) {
  return (
    <section className="knowledge-gap">
      <div className="section-heading">
        <div>
          <span>Personalized learning</span>
          <h3>Knowledge gaps</h3>
        </div>
      </div>

      {gaps.length ? (
        <div className="gap-list">
          {gaps.map((gap) => (
            <div className="gap-item" key={gap.topic}>
              <div>
                <strong>{gap.topic}</strong>
                <span>
                  {Math.round(
                    gap.score * 100
                  )}
                  % understanding
                </span>
              </div>

              <div className="gap-progress">
                <span
                  style={{
                    width: `${gap.score * 100}%`,
                  }}
                />
              </div>
            </div>
          ))}
        </div>
      ) : (
        <p className="empty-gap">
          Complete some lessons to discover
          your knowledge gaps.
        </p>
      )}
    </section>
  );
}

export default KnowledgeGap;