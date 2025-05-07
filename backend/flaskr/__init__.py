from flask import Flask, request, abort, jsonify
from flask_cors import CORS
import random
from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)

    if test_config is None:
        setup_db(app)
    else:
        database_path = test_config.get("SQLALCHEMY_DATABASE_URI")
        setup_db(app, database_path=database_path)

    """
    Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app, origins=["*"])

    """
    Use the after_request decorator to set Access-Control-Allow
    """

    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type, Authorization"
        )
        response.headers.add(
            "Access-Control-Allow-Headers", "OPTIONS, GET, POST, PATCH, DELETE"
        )
        return response

    """
    Create an endpoint to handle GET requests
    for all available categories.
    """

    @app.route("/categories")
    def get_categories():
        res = Category.query.order_by(Category.type).all()
        categories = [category.format() for category in res]
        if len(categories) == 0:
            return abort(404)
        return jsonify({"success": True, "categories": categories})

    """
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.
    
    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """

    @app.route("/questions", methods=["GET", "POST"])
    def get_questions():
        if request.method == "GET":
            page = request.args.get("page", type=int) or 1
            res = Question.query.order_by(Question.id).all()
            count = Question.query.count()
            questions = [question.format() for question in res]
            categories = (
                Category.query.order_by(Category.id)
                .all()
            )
            categories = [category.format() for category in categories]
            start = (page - 1) * QUESTIONS_PER_PAGE
            end = start + QUESTIONS_PER_PAGE
            questions = questions[start:end]
            if len(questions) == 0:
                abort(404)
            current_category = [
                category
                for category in categories
                if category["id"] == questions[0]["category"]
            ]

            current_category = current_category[0]
            return jsonify(
                {
                    "success": True,
                    "questions": questions,
                    "total_questions": count,
                    "categories": {
                        category["id"]: category["type"] for category in categories
                    },
                    "current_category": current_category,
                }
            )
        if request.method == "POST":
            """
            Create an endpoint to POST a new question,
            which will require the question and answer text,
            category, and difficulty score.

            TEST: When you submit a question on the "Add" tab,
            the form will clear and the question will appear at the end of the last page
            of the questions list in the "List" tab.
            """
            if request.content_type != "application/json":
                abort(415)
            body = request.get_json()
            if not (
                isinstance(body.get('answer'), str) 
                and isinstance(body.get('category'), int) 
                and isinstance(body.get('difficulty'), int) 
                and isinstance(body.get('question'), str)
            ):
                abort(400)

            question = Question(
                answer=body.get("answer"),
                category=body.get("category"),
                difficulty=body.get("difficulty"),
                question=body.get("question"),
            )
            question.insert()
            return jsonify({"success": True, "question": question.format()}), 201
        abort(405)

    """
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):
        question: Question = Question.query.filter(
            Question.id == question_id
        ).first_or_404()
        id = question.id
        question.delete()

        return jsonify({"success": True, "id": id})

    """
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route("/questions/search", methods=["POST"])
    def lookup_question():
        if request.content_type != "application/json":
            abort(415)
        body = request.get_json()
        search_term = body.get("searchTerm", None)
        if not isinstance(body.get("searchTerm"), str):
            abort(400)
        search_term = f"%{search_term}%"
        questions = (
            Question.query.filter(Question.question.ilike(search_term))
            .order_by(Question.id)
            .all()
        )
        count = Question.query.count()
        if(len(questions) > 0):
            current_category = Category.query.filter(
                Category.id == questions[0].category
            ).one_or_404()
        else:
            abort(404)

        return (
            jsonify(
                {
                    "success": True,
                    "questions": [question.format() for question in questions],
                    "total_questions": count,
                    "current_category": current_category.format(),
                }
            ),
            200,
        )

    """
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route("/categories/<int:category_id>/questions")
    def get_questions_by_category(category_id: int):
        category = Category.query.filter(Category.id == category_id).first_or_404()
        current_category = category
        count = Question.query.count()
        questions = Question.query.filter(Question.category == category_id).order_by(Question.id).all()

        return jsonify({
            "success": True,
            "total_questions": count,
            "questions": [question.format() for question in questions],
            "current_category": current_category.format(),
        }), 200

    """
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route("/quizzes", methods=["POST"])
    def lookup_quiz_question():
        if request.content_type != "application/json":
            abort(415)
        body = request.get_json()

        quiz_category = body.get("quiz_category", None)
        previous_questions = body.get("previous_questions", [])

        questions = Question.query.filter(Question.id.not_in(previous_questions)).all()
        if quiz_category:
            if Category.query.filter(Category.id == quiz_category["id"]).count() < 1:
                abort(404)
            questions = [question for question in questions if question.category == quiz_category["id"]]

        question = None
        if len(questions) > 0:
            question = random.choice([question.format() for question in questions])

        return jsonify({"success": True, "question": question}), 200

    """
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"success": False, "error": "Bad Request"}), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"success": False, "error": "Not Found"}), 404

    @app.errorhandler(405)
    def not_allowed(error):
        return jsonify({"success": False, "error": "Method Not Allowed"}), 405
    
    @app.errorhandler(415)
    def unsupported_media_type(error):
        return jsonify({"success": False, "error": "Unsupported Media Type"}), 415
    
    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({"success": False, "error": "Internal Server Error"}), 500

    return app
