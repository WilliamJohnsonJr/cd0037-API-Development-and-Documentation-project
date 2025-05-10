import os
import unittest

import json

from sqlalchemy import text, create_engine

from flaskr import create_app
from models import db, Question, Category
from seed_test_db import make_categories, make_questions


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.database_name = "trivia_test"
        self.database_user = "postgres"
        self.database_password = "password"
        self.database_host = "localhost:5432"
        self.database_path = f"postgresql://{self.database_user}:{self.database_password}@{self.database_host}/{self.database_name}"
        self.engine = create_engine(self.database_path)

        # Create app with the test configuration
        self.app = create_app(
            {
                "SQLALCHEMY_DATABASE_URI": self.database_path,
                "SQLALCHEMY_TRACK_MODIFICATIONS": False,
                "TESTING": True,
            }
        )
        self.client = self.app.test_client()

        # Clean out the db if anything is already there
        with self.engine.connect() as connection:
            connection.execute(text("DROP TABLE IF EXISTS questions;"))
            connection.execute(text("DROP TABLE IF EXISTS categories;"))
            connection.close()

        # Bind the app to the current context and create all tables
        with self.app.app_context():
            db.create_all()
            db.session.add_all(make_categories(self.app))
            db.session.add_all(make_questions(self.app))
            db.session.commit()

    def tearDown(self):
        """Executed after each test"""
        with self.engine.connect() as connection:
            connection.execute(text("DROP TABLE questions;"))
            connection.execute(text("DROP TABLE categories;"))
            connection.close()
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

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

    def test_create_question_non_json_400(self):
        payload = 0b10101010
        res = self.client.post("/questions", data=bytes(payload), content_type='application/json')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertFalse(data["success"])
        self.assertEqual(data["error"], "Bad Request")

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

    def test_create_question_415(self):
        new_question = 0b10101010
        res = self.client.post("/questions", data=bytes(new_question), content_type='application/octet-stream')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 415)
        self.assertFalse(data["success"])
        self.assertEqual(data["error"], "Unsupported Media Type")

    def test_lookup_questions(self):
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
        self.assertEqual(data["total_questions"], 19)
        self.assertEqual(data["current_category"], {"id": 4, "type": "History"})

    def test_lookup_questions_non_json_400(self):
        payload = 0b10101010
        res = self.client.post("/questions/search", data=bytes(payload), content_type='application/json')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertFalse(data["success"])
        self.assertEqual(data["error"], "Bad Request")

    def test_lookup_questions_404(self):
        payload = {"searchTerm": "rutabaga"}
        res = self.client.post("/questions/search", json=payload)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data["success"])
        self.assertEqual(data["error"], "Not Found")

    def test_lookup_questions_no_category_404(self):
        payload = {"searchTerm": "rutabaga"}

        with self.app.app_context():
            # question_id = 0
            question = Question(
                question="rutabaga",
                answer="answer_goes_here",
                category=6,
                difficulty=5,
            )
            question.insert()
            # question_id = question.id

            category = Category.query.filter(Category.id == 6).one_or_none()
            if(category):
                category.delete()

            res = self.client.post("/questions/search", json=payload)
            data = json.loads(res.data)

            self.assertEqual(res.status_code, 404)
            self.assertFalse(data["success"])
            self.assertEqual(data["error"], "Not Found")

    def test_lookup_questions_415(self):
        payload = 0b10101010
        res = self.client.post("/questions/search", data=bytes(payload), content_type='application/octet-stream')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 415)
        self.assertFalse(data["success"])
        self.assertEqual(data["error"], "Unsupported Media Type")

    def test_get_questions_by_category(self):
        res = self.client.get("/categories/3/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(
            data["questions"],
            [
                {
                    "answer": "Lake Victoria",
                    "category": 3,
                    "difficulty": 2,
                    "id": 13,
                    "question": "What is the largest lake in Africa?",
                },
                {
                    "answer": "The Palace of Versailles",
                    "category": 3,
                    "difficulty": 3,
                    "id": 14,
                    "question": "In which royal palace would you find the Hall of Mirrors?",
                },
                {
                    "answer": "Agra",
                    "category": 3,
                    "difficulty": 2,
                    "id": 15,
                    "question": "The Taj Mahal is located in which Indian city?",
                },
            ],
        )
        self.assertEqual(data["total_questions"], 19)
        self.assertEqual(data["current_category"], {"id": 3, "type": "Geography"})

    def test_get_questions_by_category_404(self):
        res = self.client.get("/categories/399/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["error"], "Not Found")

    def test_lookup_quiz_question(self):
        payload={"previous_questions": [20, 21], "quiz_category": {"id": 1, "type": "Science"}}
        res = self.client.post("/quizzes", json=payload, content_type="application/json")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(
            data,
            {
                "question": {
                    "answer": "Blood",
                    "category": 1,
                    "difficulty": 4,
                    "id": 22,
                    "question": "Hematology is a branch of medicine involving the "
                    "study of what?",
                },
                "success": True,
            },
        )

    def test_lookup_quiz_question_non_json_400(self):
        payload = 0b10101010
        res = self.client.post("/quizzes", data=bytes(payload), content_type='application/json')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertFalse(data["success"])
        self.assertEqual(data["error"], "Bad Request")

    def test_lookup_quiz_question_400(self):
        payload = {"cookies": "yum"}
        res = self.client.post("/quizzes", data=payload, content_type='application/json')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertFalse(data["success"])
        self.assertEqual(data["error"], "Bad Request")

    def test_lookup_quiz_question_415(self):
        payload = 0b10101010
        res = self.client.post("/quizzes", data=bytes(payload), content_type='application/octet-stream')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 415)
        self.assertFalse(data["success"])
        self.assertEqual(data["error"], "Unsupported Media Type")


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
