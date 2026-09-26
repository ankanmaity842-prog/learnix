import { Link } from "react-router-dom";
import "./LearningPathPage.css";

function LearningPathPage() {
  const steps = [
    {
      number: "01",
      title: "Foundation",
      description: "Build the prerequisite knowledge required for your target.",
      status: "completed",
    },
    {
      number: "02",
      title: "Core concepts",
      description: "Understand the fundamental concepts behind the subject.",
      status: "current",
    },
    {
      number: "03",
      title: "Practical understanding",
      description: "Apply what you have learned through examples and practice.",
      status: "upcoming",
    },
    {
      number: "04",
      title: "Advanced concepts",
      description: "Move toward more complex ideas and applications.",
      status: "upcoming",
    },
  ];

  return (
    <main className="learning-path-page">
      <section className="path-header">
        <div>
          <span>PERSONALIZED LEARNING PATH</span>
          <h1>Your learning path</h1>
          <p>
            A structured sequence based on your current knowledge, learning
            level and target topic.
          </p>
        </div>

        <div className="path-progress">
          <strong>68%</strong>
          <span>overall progress</span>
        </div>
      </section>

      <section className="path-list">
        {steps.map((step) => (
          <article className={`path-step ${step.status}`} key={step.number}>
            <div className="step-number">{step.number}</div>

            <div className="step-content">
              <span>
                {step.status === "completed"
                  ? "COMPLETED"
                  : step.status === "current"
                    ? "CURRENT"
                    : "UPCOMING"}
              </span>

              <h2>{step.title}</h2>
              <p>{step.description}</p>

              {step.status === "current" && (
                <Link to="/learning" className="primary-button">
                  Continue learning
                </Link>
              )}
            </div>
          </article>
        ))}
      </section>
    </main>
  );
}

export default LearningPathPage;