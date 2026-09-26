import "./KnowledgePage.css";

function KnowledgePage() {
  return (
    <main className="knowledge-page">
      <section className="knowledge-header">
        <span>KNOWLEDGE PROFILE</span>
        <h1>Your knowledge overview</h1>
        <p>
          Understand your strengths, identify areas that need review and
          monitor how your knowledge develops over time.
        </p>
      </section>

      <section className="knowledge-stats">
        <article>
          <span>Strong knowledge</span>
          <strong>8</strong>
          <small>topics</small>
        </article>

        <article>
          <span>Needs review</span>
          <strong>4</strong>
          <small>topics</small>
        </article>

        <article>
          <span>In progress</span>
          <strong>3</strong>
          <small>topics</small>
        </article>
      </section>

      <section className="knowledge-map-section">
        <div className="knowledge-section-heading">
          <span>KNOWLEDGE GRAPH</span>
          <h2>Topic relationships</h2>
        </div>

        <div className="knowledge-map">
          <div className="knowledge-node strong">Foundation</div>
          <div className="knowledge-node strong">Core concepts</div>
          <div className="knowledge-node current">Current topic</div>
          <div className="knowledge-node weak">Advanced concepts</div>
        </div>
      </section>
    </main>
  );
}

export default KnowledgePage;