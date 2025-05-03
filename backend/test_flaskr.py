import os
import unittest

import json

from flaskr import create_app
from models import db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.database_name = "trivia_test"
        self.database_user = "postgres"
        self.database_password = "password"
        self.database_host = "localhost:5432"
        self.database_path = f"postgresql://{self.database_user}:{self.database_password}@{self.database_host}/{self.database_name}"

        # Create app with the test configuration
        self.app = create_app(
            {
                "SQLALCHEMY_DATABASE_URI": self.database_path,
                "SQLALCHEMY_TRACK_MODIFICATIONS": False,
                "TESTING": True,
            }
        )
        self.client = self.app.test_client()

        # Bind the app to the current context and create all tables
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        """Executed after each test"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_get_questions(self):
        res = self.client.get("/questions")
        data = json.loads(res.data)
        questions = data["questions"]
        question6 = [question for question in questions if question["id"] == 6][0]

        self.assertEqual(res.status_code, 200)
        self.assertEqual(
            list(data.keys()),
            [
                "categories",
                "current_category",
                "questions",
                "success",
                "total_questions",
            ],
        )
        self.assertEqual(len(list(data["categories"].keys())), 6)
        self.assertDictEqual(
            data["current_category"], {"id": 5, "type": "Entertainment"}
        )
        self.assertEqual(len(data["questions"]), 10)
        self.assertEqual(data["success"], True)
        self.assertGreaterEqual(data["total_questions"], 18)
        self.assertEqual([question["id"] for question in questions], [2, 4, 5, 6, 9, 10, 11, 12, 13, 14])
        self.assertEqual(
            question6["answer"], "Edward Scissorhands"
        )

    def test_get_questions_pagination(self):
        res = self.client.get("/questions?page=2")
        data = json.loads(res.data)
        questions = data["questions"]

        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(list(data["categories"].keys())), 6)
        self.assertLessEqual(len(data["questions"]), 9)
        self.assertGreaterEqual(data["total_questions"], 18)
        self.assertEqual([question["id"] for question in questions], [15, 16, 17, 18, 19, 20, 21, 22, 23])
        self.assertDictEqual(
            questions[0],
            {
                "answer": "Agra",
                "category": 3,
                "difficulty": 2,
                "id": 15,
                "question": "The Taj Mahal is located in which Indian city?",
            },
        )

    def test_delete_question(self):
        res = self.client.delete('/questions/2')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['id'], 2)
        self.assertRaises(Question.query.filter(Question.id == 2).first_or_404())


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
