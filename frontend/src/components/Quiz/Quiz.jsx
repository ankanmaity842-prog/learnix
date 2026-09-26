import { useState } from "react";
import "./Quiz.css";

function Quiz({ question }) {
  const [selected, setSelected] = useState(null);
  const [submitted, setSubmitted] = useState(false);

  if (!question) {
    return (
      <div className="quiz-empty">
        No quiz available.
      </div>
    );
  }

  return (
    <section className="quiz">
      <span>Knowledge check</span>

      <h2>{question.question}</h2>

      <div className="quiz-options">
        {question.options.map(
          (option, index) => (
            <button
              key={option}
              className={
                selected === index
                  ? "selected"
                  : ""
              }
              onClick={() =>
                setSelected(index)
              }
            >
              <span>
                {String.fromCharCode(
                  65 + index
                )}
              </span>

              {option}
            </button>
          )
        )}
      </div>

      <button
        className="quiz-submit"
        disabled={selected === null}
        onClick={() => setSubmitted(true)}
      >
        Check answer
      </button>

      {submitted && (
        <p className="quiz-result">
          {selected === question.answer
            ? "Correct answer."
            : "Review this concept and try again."}
        </p>
      )}
    </section>
  );
}

export default Quiz;