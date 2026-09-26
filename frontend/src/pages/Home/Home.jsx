import { Link } from "react-router-dom";
import "./Home.css";

const features = [
  {
    number: "01",
    title: "Explore any topic",
    description:
      "Discover educational resources across programming, science, mathematics, business, humanities and more.",
  },
  {
    number: "02",
    title: "Learn at your level",
    description:
      "Recommendations adapt to your learning level, preferred language and existing knowledge.",
  },
  {
    number: "03",
    title: "Build your learning path",
    description:
      "Understand prerequisites, identify knowledge gaps and follow a structured path toward your goal.",
  },
];

function Home() {
  return (
    <main className="home-page">
      <section className="home-hero">
        <div className="home-hero-content">
          <span className="home-eyebrow">PERSONALIZED LEARNING PLATFORM</span>

          <h1>
            Learn with purpose.
            <br />
            <span>Grow with Learnix.</span>
          </h1>

          <p>
            Discover educational content, understand difficult concepts and
            build a personalized learning journey around the subjects that
            matter to you.
          </p>

          <div className="home-actions">
            <Link to="/search" className="primary-button">
              Start learning
            </Link>

            <Link to="/register" className="secondary-button">
              Create an account
            </Link>
          </div>

          <div className="home-trust">
            <span>Any topic</span>
            <span>Multiple languages</span>
            <span>Personalized learning</span>
          </div>
        </div>

        <div className="home-visual">
          <div className="learning-dashboard-preview">
            <div className="preview-top">
              <div>
                <span>LEARNING OVERVIEW</span>
                <h3>Your learning journey</h3>
              </div>

              <div className="preview-avatar">L</div>
            </div>

            <div className="preview-progress-section">
              <div className="preview-progress-header">
                <span>Overall progress</span>
                <strong>68%</strong>
              </div>

              <div className="preview-progress">
                <span style={{ width: "68%" }} />
              </div>
            </div>

            <div className="preview-stat-grid">
              <div>
                <strong>24</strong>
                <span>Sessions</span>
              </div>

              <div>
                <strong>16</strong>
                <span>Completed</span>
              </div>

              <div>
                <strong>12.4h</strong>
                <span>Learning time</span>
              </div>
            </div>

            <div className="preview-current">
              <span>CURRENT LEARNING</span>
              <h4>Continue where you left off</h4>

              <div className="preview-lesson">
                <div className="lesson-icon">▶</div>

                <div>
                  <strong>Recommended lesson</strong>
                  <span>Personalized for your level</span>
                </div>

                <span className="lesson-arrow">→</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="home-section">
        <div className="section-heading">
          <span>WHY LEARNIX</span>
          <h2>A learning experience built around you</h2>
          <p>
            Learnix combines educational discovery, personalization and
            progress tracking into one learning experience.
          </p>
        </div>

        <div className="feature-grid">
          {features.map((feature) => (
            <article className="feature-card" key={feature.number}>
              <span className="feature-number">{feature.number}</span>
              <h3>{feature.title}</h3>
              <p>{feature.description}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="home-cta">
        <div>
          <span>BEGIN YOUR JOURNEY</span>
          <h2>There is always something new to learn.</h2>
          <p>
            Choose a topic, define your learning preferences and start
            building knowledge.
          </p>
        </div>

        <Link to="/search" className="primary-button">
          Explore topics
        </Link>
      </section>
    </main>
  );
}

export default Home;