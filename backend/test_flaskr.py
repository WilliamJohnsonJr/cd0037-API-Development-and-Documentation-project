import os
import unittest

import json

from sqlalchemy import text

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

    """
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
        self.assertEqual(
            [question["id"] for question in questions],
            [2, 4, 5, 6, 9, 10, 11, 12, 13, 14],
        )
        self.assertEqual(question6["answer"], "Edward Scissorhands")

    def test_get_questions_pagination(self):
        res = self.client.get("/questions?page=2")
        data = json.loads(res.data)
        questions = data["questions"]

        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(list(data["categories"].keys())), 6)
        self.assertLessEqual(len(data["questions"]), 9)
        self.assertGreaterEqual(data["total_questions"], 18)
        self.assertEqual(
            [question["id"] for question in questions],
            [15, 16, 17, 18, 19, 20, 21, 22, 23],
        )
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

    def test_get_questions_error(self):
        res = self.client.get("/questions?page=200")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertDictEqual(data, {"error": "Not Found", "success": False})

    def test_delete_question(self):
        res = self.client.delete("/questions/2")
        data = json.loads(res.data)
        with self.app.app_context():
            question_or_none = Question.query.filter(Question.id == 2).one_or_none()
            self.assertEqual(res.status_code, 200)
            self.assertEqual(data["success"], True)
            self.assertEqual(data["id"], 2)
            self.assertEqual(question_or_none, None)

            # Clean up db
            question = Question(
                answer="Apollo 13",
                category=5,
                difficulty=4,
                question="What movie earned Tom Hanks his third straight Oscar nomination, in 1996?",
            )
            question.id = 2
            question.insert()

    def test_delete_question_error(self):
        res = self.client.delete("/questions/200")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["error"], "Not Found")

    def test_create_question(self):
        new_question = {
            "answer": "Lake Superior",
            "category": 3,
            "difficulty": 3,
            "question": "What is the largest freshwater lake in the world by surface area?",
        }
        res = self.client.post("/questions", json=new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 201)
        self.assertTrue(isinstance(data["question"]["id"], int))
        self.assertEqual(data["question"]["answer"], "Lake Superior")

        # Clean up db
        with self.app.app_context():
            question_to_remove = Question.query.filter(
                Question.id == data["question"]["id"]
            ).one_or_none()
            if question_to_remove:
                question_to_remove.delete()

    def test_create_question_400(self):
        # Fails, since category must be an int
        new_question = {
            "answer": "Lake Superior",
            "category": "McIntosh",
            "difficulty": 3,
            "question": "What is the largest freshwater lake in the world by surface area?",
        }

        res = self.client.post("/questions", json=new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data, {"success": False, "error": "Bad Request"})

    def test_create_question_405(self):
        # Fails, since category must be an int
        new_question = {
            "answer": "Lake Superior",
            "category": 3,
            "difficulty": 3,
            "question": "What is the largest freshwater lake in the world by surface area?",
        }

        res = self.client.patch("/questions", json=new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data, {"success": False, "error": "Method Not Allowed"})

    def test_search_questions(self):
        payload = {"searchTerm": "title"}
        res = self.client.post("/questions/search", json=payload)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertEqual(
            data["questions"],
            [
                {
                    "answer": "Maya Angelou",
                    "category": 4,
                    "difficulty": 2,
                    "id": 5,
                    "question": "Whose autobiography is entitled 'I Know Why the Caged Bird Sings'?",
                },
                {
                    "answer": "Edward Scissorhands",
                    "category": 5,
                    "difficulty": 3,
                    "id": 6,
                    "question": "What was the title of the 1990 fantasy directed by Tim Burton about a young man with multi-bladed appendages?",
                },
            ],
        )


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
