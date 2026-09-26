import { useState } from "react";
import "./QuizPage.css";

const options = [
  "A concept that does not require any learning process",
  "A concept learned from relevant examples or information",
  "A method that only works with one specific subject",
  "A process that does not require evaluation",
];

function QuizPage() {
  const [selected, setSelected] = useState(null);

  return (
    <main className="quiz-page">
      <section className="quiz-header">
        <span>KNOWLEDGE CHECK</span>
        <h1>Test your understanding</h1>
        <p>
          Answer a few questions to measure how well you understood the
          selected lesson.
        </p>

        <div className="quiz-progress">
          <div>
            <span>Question 1 of 5</span>
            <strong>20%</strong>
          </div>

          <div className="quiz-progress-bar">
            <span style={{ width: "20%" }} />
          </div>
        </div>
      </section>

      <section className="quiz-card">
        <span className="question-label">QUESTION 01</span>

        <h2>
          Which statement best describes the concept introduced in this
          lesson?
        </h2>

        <div className="quiz-options">
          {options.map((option, index) => (
            <button
              key={option}
              className={selected === index ? "selected" : ""}
              onClick={() => setSelected(index)}
            >
              <span>{String.fromCharCode(65 + index)}</span>
              {option}
            </button>
          ))}
        </div>

        <div className="quiz-footer">
          <span>Select the best answer</span>

          <button
            className="primary-button"
            disabled={selected === null}
          >
            Next question
          </button>
        </div>
      </section>
    </main>
  );
}

export default QuizPage;