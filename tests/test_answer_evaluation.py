import unittest

from tools import evaluate_user_answers


class AnswerEvaluationTests(unittest.TestCase):
    def test_evaluate_user_answers_returns_items_for_each_question(self):
        questions = ["Tell me about a project you delivered."]
        answers = ["I led a migration that improved deployment time by 30%."]

        evaluations = evaluate_user_answers(
            role="Backend Engineer",
            resume_summary="Strong Python and SQL background.",
            gaps=["Add metric-based examples"],
            questions=questions,
            answers=answers,
        )

        self.assertEqual(len(evaluations), 1)
        self.assertEqual(evaluations[0]["question"], questions[0])
        self.assertIn("score", evaluations[0])
        self.assertIn("feedback", evaluations[0])


if __name__ == "__main__":
    unittest.main()
