import "./CVInsights.css";

function CVInsights({
  insights = {},
}) {
  const metrics = [
    ["Visual simplicity", insights.visual_simplicity],
    ["Visual complexity", insights.visual_complexity],
    ["Slides", insights.slide_count],
    ["Code frames", insights.code_frame_count],
    ["Diagrams", insights.diagram_frame_count],
  ];

  return (
    <section className="cv-insights">
      <div className="cv-header">
        <span>Computer vision analysis</span>
        <h3>Visual learning insights</h3>
      </div>

      <div className="cv-grid">
        {metrics.map(([label, value]) => (
          <div className="cv-metric" key={label}>
            <span>{label}</span>
            <strong>
              {typeof value === "number"
                ? value < 1
                  ? `${Math.round(value * 100)}%`
                  : value
                : "—"}
            </strong>
          </div>
        ))}
      </div>
    </section>
  );
}

export default CVInsights;