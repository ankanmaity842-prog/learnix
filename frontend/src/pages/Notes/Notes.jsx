import { Link } from "react-router-dom";
import "./Notes.css";

function Notes() {
  return (
    <main className="notes-page">
      <section className="notes-header">
        <div>
          <span>LEARNING NOTES</span>
          <h1>Lesson notes</h1>
          <p>
            Review concise notes generated from your selected learning
            material.
          </p>
        </div>

        <button className="secondary-button">
          Download notes
        </button>
      </section>

      <section className="notes-layout">
        <aside className="notes-navigation">
          <span>CONTENTS</span>
          <a href="#overview">Overview</a>
          <a href="#key-concepts">Key concepts</a>
          <a href="#summary">Summary</a>
        </aside>

        <article className="notes-content">
          <section id="overview">
            <span>01</span>
            <h2>Overview</h2>
            <p>
              These notes summarize the key ideas covered in the selected
              learning resource and provide a concise reference for revision.
            </p>
          </section>

          <section id="key-concepts">
            <span>02</span>
            <h2>Key concepts</h2>
            <ul>
              <li>Important definitions and terminology</li>
              <li>Core concepts introduced in the lesson</li>
              <li>Relationships between major ideas</li>
              <li>Practical examples and applications</li>
            </ul>
          </section>

          <section id="summary">
            <span>03</span>
            <h2>Summary</h2>
            <p>
              Use these notes as a revision reference before attempting the
              knowledge check.
            </p>
          </section>

          <Link to="/quiz" className="primary-button">
            Test your understanding
          </Link>
        </article>
      </section>
    </main>
  );
}

export default Notes;