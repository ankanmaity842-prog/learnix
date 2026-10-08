import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import "./Dashboard.css";

const API_URL =
  import.meta.env.VITE_API_URL || "http://localhost:8000/api";

function getToken() {
  return (
    localStorage.getItem("access_token") ||
    localStorage.getItem("token")
  );
}

async function apiRequest(endpoint) {
  const token = getToken();

  const response = await fetch(`${API_URL}${endpoint}`, {
    headers: {
      "Content-Type": "application/json",
      ...(token
        ? {
            Authorization: `Bearer ${token}`,
          }
        : {}),
    },
  });

  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }

  return response.json();
}

function formatHours(minutes = 0) {
  const value = Number(minutes) || 0;

  if (value < 60) {
    return `${value}m`;
  }

  return `${(value / 60).toFixed(1)}h`;
}

function formatTopicName(topic) {
  if (!topic) {
    return "your current topic";
  }

  return topic
    .replace(/[-_]/g, " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function Dashboard() {
  const [progress, setProgress] = useState(null);
  const [progressDashboard, setProgressDashboard] = useState(null);
  const [history, setHistory] = useState([]);
  const [knowledge, setKnowledge] = useState(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let mounted = true;

    async function loadDashboard() {
      try {
        setLoading(true);
        setError("");

        const [
          progressData,
          dashboardData,
          historyData,
          knowledgeData,
        ] = await Promise.all([
          apiRequest("/progress/"),
          apiRequest("/progress/dashboard"),
          apiRequest("/learning/history"),
          apiRequest("/knowledge/map"),
        ]);

        if (!mounted) {
          return;
        }

        setProgress(progressData);
        setProgressDashboard(dashboardData);
        setHistory(historyData?.sessions || []);
        setKnowledge(knowledgeData);
      } catch (err) {
        console.error("Dashboard loading failed:", err);

        if (mounted) {
          setError(
            "We couldn't load your learning data. Please try again."
          );
        }
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    }

    loadDashboard();

    return () => {
      mounted = false;
    };
  }, []);

  const stats = useMemo(() => {
    const totalSessions = history.length;

    const completedSessions = history.filter(
      (session) =>
        session.completed === true ||
        Number(session.watch_percentage) >= 0.9
    ).length;

    const learningMinutes = history.reduce(
      (total, session) =>
        total +
        (Number(session.watch_time_seconds) || 0) / 60,
      0
    );

    return {
      sessions: totalSessions,
      completed:
        progress?.topics_completed ??
        completedSessions,
      learningTime: formatHours(learningMinutes),
      streak:
        progress?.learning_streak ??
        progressDashboard?.learning_streak ??
        0,
    };
  }, [history, progress, progressDashboard]);

  const currentSession = history.find(
    (session) => !session.completed
  );

  const currentTopic =
    currentSession?.topic ||
    currentSession?.topic_name ||
    currentSession?.title ||
    null;

  const currentProgress = Math.round(
    Number(
      currentSession?.watch_percentage ??
        progressDashboard?.overall_progress ??
        progress?.overall_progress ??
        0
    ) * 100
  );

  const knowledgeStats = useMemo(() => {
    const nodes =
      knowledge?.nodes ||
      knowledge?.topics ||
      knowledge?.knowledge ||
      [];

    if (!Array.isArray(nodes)) {
      return {
        strong: 0,
        review: 0,
        learning: 0,
      };
    }

    return nodes.reduce(
      (result, item) => {
        const score = Number(
          item.mastery_score ??
            item.score ??
            item.mastery ??
            0
        );

        if (score >= 0.75) {
          result.strong += 1;
        } else if (score >= 0.4) {
          result.learning += 1;
        } else {
          result.review += 1;
        }

        return result;
      },
      {
        strong: 0,
        review: 0,
        learning: 0,
      }
    );
  }, [knowledge]);

  return (
    <main className="dashboard-page">
      <section className="dashboard-header">
        <div>
          <span>LEARNING DASHBOARD</span>

          <h1>Welcome back</h1>

          <p>
            See what you have learned, continue unfinished
            sessions and discover what to focus on next.
          </p>
        </div>

        <Link to="/search" className="primary-button">
          Explore topics
        </Link>
      </section>

      {error && (
        <div className="dashboard-error">
          {error}
        </div>
      )}

      <section className="dashboard-stats">
        <article>
          <span>Learning sessions</span>

          <strong>
            {loading ? "—" : stats.sessions}
          </strong>

          <small>
            Sessions recorded
          </small>
        </article>

        <article>
          <span>Topics completed</span>

          <strong>
            {loading ? "—" : stats.completed}
          </strong>

          <small>
            Completed topics
          </small>
        </article>

        <article>
          <span>Learning time</span>

          <strong>
            {loading ? "—" : stats.learningTime}
          </strong>

          <small>
            Recorded watch time
          </small>
        </article>

        <article>
          <span>Current streak</span>

          <strong>
            {loading ? "—" : stats.streak}
          </strong>

          <small>
            Consecutive days
          </small>
        </article>
      </section>

      <section className="dashboard-grid">
        <article className="dashboard-card dashboard-current">
          <span>CONTINUE LEARNING</span>

          <h2>
            {currentTopic
              ? formatTopicName(currentTopic)
              : "Start your first learning session"}
          </h2>

          <p>
            {currentTopic
              ? "Pick up where you left off and continue building your understanding."
              : "Search for a topic and start a learning session. Your progress will appear here automatically."}
          </p>

          <div className="dashboard-progress">
            <span
              style={{
                width: `${Math.min(
                  Math.max(currentProgress, 0),
                  100
                )}%`,
              }}
            />
          </div>

          <div className="dashboard-progress-info">
            <span>
              {currentTopic
                ? `${currentProgress}% complete`
                : "No active session"}
            </span>

            <Link
              to={
                currentTopic
                  ? "/learning"
                  : "/search"
              }
            >
              {currentTopic
                ? "Continue →"
                : "Find a topic →"}
            </Link>
          </div>
        </article>

        <article className="dashboard-card">
          <span>KNOWLEDGE PROFILE</span>

          <h2>
            What you know
          </h2>

          <p>
            Your knowledge profile is built from learning
            activity and assessment results.
          </p>

          <div className="knowledge-summary">
            <div>
              <strong>
                {loading
                  ? "—"
                  : knowledgeStats.strong}
              </strong>

              <span>Strong</span>
            </div>

            <div>
              <strong>
                {loading
                  ? "—"
                  : knowledgeStats.review}
              </strong>

              <span>Review</span>
            </div>

            <div>
              <strong>
                {loading
                  ? "—"
                  : knowledgeStats.learning}
              </strong>

              <span>Learning</span>
            </div>
          </div>

          <Link
            to="/knowledge"
            className="dashboard-link"
          >
            View knowledge map →
          </Link>
        </article>
      </section>

      <section className="dashboard-activity">
        <div className="activity-heading">
          <div>
            <span>RECENT ACTIVITY</span>

            <h2>
              Your learning activity
            </h2>
          </div>

          <Link to="/progress">
            View all
          </Link>
        </div>

        <div className="activity-list">
          {loading ? (
            <div className="activity-empty">
              Loading your activity...
            </div>
          ) : history.length === 0 ? (
            <div className="activity-empty">
              <strong>
                Your learning history is empty.
              </strong>

              <span>
                Start a topic to begin building your
                learning history.
              </span>

              <Link to="/search">
                Explore topics →
              </Link>
            </div>
          ) : (
            history.slice(0, 5).map((session, index) => {
              const topic =
                session.topic ||
                session.topic_name ||
                "Learning session";

              const completed =
                session.completed === true;

              const percentage = Math.round(
                Number(
                  session.watch_percentage || 0
                ) * 100
              );

              return (
                <div
                  key={
                    session.id ??
                    session.session_id ??
                    index
                  }
                >
                  <section>
                    <strong>
                      {formatTopicName(topic)}
                    </strong>

                    <span>
                      {completed
                        ? "Learning session completed"
                        : `${percentage}% watched`}
                    </span>
                  </section>

                  <small
                    className={
                      completed
                        ? "activity-status completed"
                        : "activity-status"
                    }
                  >
                    {completed
                      ? "Completed"
                      : "In progress"}
                  </small>
                </div>
              );
            })
          )}
        </div>
      </section>

      <section className="dashboard-discovery">
        <div>
          <span>KEEP LEARNING</span>

          <h2>
            Ready to explore something new?
          </h2>

          <p>
            Search any topic and let Learnix find
            educational resources suited to your
            learning journey.
          </p>
        </div>

        <Link
          to="/search"
          className="secondary-button"
        >
          Explore topics
        </Link>
      </section>
    </main>
  );
}

export default Dashboard;