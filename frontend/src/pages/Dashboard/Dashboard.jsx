import { Link } from "react-router-dom";
import "./Dashboard.css";

function Dashboard() {
  return (
    <main className="dashboard-page">
      <section className="dashboard-header">
        <div>
          <span>LEARNING DASHBOARD</span>
          <h1>Welcome back</h1>
          <p>
            Continue learning, review your progress and explore something new.
          </p>
        </div>

        <Link to="/search" className="primary-button">
          Explore topics
        </Link>
      </section>

      <section className="dashboard-stats">
        <article>
          <span>Learning sessions</span>
          <strong>24</strong>
          <small>Total sessions</small>
        </article>

        <article>
          <span>Completed</span>
          <strong>16</strong>
          <small>Lessons completed</small>
        </article>

        <article>
          <span>Learning time</span>
          <strong>12.4h</strong>
          <small>This month</small>
        </article>

        <article>
          <span>Current streak</span>
          <strong>7</strong>
          <small>Days</small>
        </article>
      </section>

      <section className="dashboard-grid">
        <article className="dashboard-card">
          <span>CONTINUE LEARNING</span>
          <h2>Your current learning path</h2>

          <p>
            Continue with your current lesson and maintain your learning
            progress.
          </p>

          <div className="dashboard-progress">
            <span style={{ width: "68%" }} />
          </div>

          <div className="dashboard-progress-info">
            <span>68% complete</span>
            <Link to="/learning">Continue →</Link>
          </div>
        </article>

        <article className="dashboard-card">
          <span>KNOWLEDGE PROFILE</span>
          <h2>Knowledge overview</h2>

          <div className="knowledge-summary">
            <div>
              <strong>8</strong>
              <span>Strong</span>
            </div>

            <div>
              <strong>4</strong>
              <span>Review</span>
            </div>

            <div>
              <strong>3</strong>
              <span>Learning</span>
            </div>
          </div>

          <Link to="/knowledge" className="dashboard-link">
            View knowledge map →
          </Link>
        </article>
      </section>

      <section className="dashboard-activity">
        <div className="activity-heading">
          <div>
            <span>RECENT ACTIVITY</span>
            <h2>Your learning activity</h2>
          </div>

          <Link to="/progress">View all</Link>
        </div>

        <div className="activity-list">
          <div>
            <section>
              <strong>Completed learning session</strong>
              <span>Recently completed</span>
            </section>
            <small>Completed</small>
          </div>

          <div>
            <section>
              <strong>Learning session in progress</strong>
              <span>Continue your current lesson</span>
            </section>
            <small>In progress</small>
          </div>

          <div>
            <section>
              <strong>Knowledge review</strong>
              <span>Review recommended concepts</span>
            </section>
            <small>Review</small>
          </div>
        </div>
      </section>
    </main>
  );
}

export default Dashboard;