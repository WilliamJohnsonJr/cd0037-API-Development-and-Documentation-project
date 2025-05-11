# Backend - Trivia API

## Setting up the Backend

### Install Dependencies

1. **Python 3.7** - Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

2. **Virtual Environment** - We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organized. Instructions for setting up a virual environment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

3. **PIP Dependencies** - Once your virtual environment is setup and running, install the required dependencies by navigating to the `/backend` directory and running:

```bash
pip install -r requirements.txt
```

#### Key Pip Dependencies

- [Flask](http://flask.pocoo.org/) is a lightweight backend microservices framework. Flask is required to handle requests and responses.

- [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM we'll use to handle the lightweight SQL database. You'll primarily work in `app.py`and can reference `models.py`.

- [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/#) is the extension we'll use to handle cross-origin requests from our frontend server.

### Set up the Database

With Postgres running, create a `trivia` database:

```bash
createdb trivia
```

Populate the database using the `trivia.psql` file provided. From the `backend` folder in terminal run:

```bash
psql trivia < trivia.psql
```

### Create .env.json file

Create a `.env.json` file in the `backend` directory containing:
- `db_user` (If in doubt use a default of `"postgres"`, but change that if going to production)
- `db_password` (If in doubt use a default of `"password"`, but change that if going to production)
Example:
```json
{
  "db_user": "postgres",
  "db_password": "password"
}
```

### Run the Server

From within the `backend` directory first ensure you are working using your created virtual environment.

To run the server, execute:

```bash
flask run --reload
```

The `--reload` flag will detect file changes and restart the server automatically.

## Testing

To deploy the tests, run

```bash
dropdb trivia_test
createdb trivia_test
psql trivia_test < trivia.psql
python test_flaskr.py
```

Once you have created the database for the first time, the test suite will automatically reset and re-seed the test database's data after each run. After you have created the test database, just run:
`python test_flaskr.py`

## Documentation

`GET '/categories'`
- Fetches a list of all categories.
- Request Arguments: None
- Returns: 
  - 200: A success object containing:
    - `success`: `boolean`
    - `categories`: list of `{id: int, type: string}` objects

    Example payload:
    ```json
    {
      "success": true,
      "categories": [
        {"id": 1, "type": "Science"},
        {"id": 2, "type": "Art"},
        {"id": 3, "type": "Geography"},
        {"id": 4, "type": "History"},
        {"id": 5, "type": "Entertainment"},
        {"id": 6, "type": "Sports"}
      ]
    }
    ```
  - 404: A Not Found error object

    Example payload:
    ```json
      {"success": false, "error": "Not Found"}
    ```
  - 405: A Method Not Allowed error containing:
    - `success`: `boolean`
    - `error`: `str`

    Example payload:
    ```json
      {
        "success": false,
        "error": "Method Not Allowed"
      }  
    ```
  - 500: An Internal Server Error error containing:
    - `success`: `boolean`
    - `error`: `str`

    Example payload:
    ```json
      {
        "success": false,
        "error": "Internal Server Error"
      }  
    ```

`GET '/categories/<int:category_id>/questions'`
- Fetches a list of questions by category
- Request Arguments:
  - Path parameters:
    - category_id: `int`
  - Query parameters: None
- Returns:
  - 200: A success object containing:
    - `success`: boolean
    - `questions`: a list of `{id: int, question: str, answer: str, category: int, difficulty: int}` objects
    - `current_category`: the category matching the provided `category_id` as a `{id: int, type: str}` object
    - `total_questions`: int showing the total number of questions in the requested category

    Example payload:
    ```json
      {
        "success": true,
        "questions": [
          {
            "answer": "Lake Superior",
            "category": 3,
            "difficulty": 3,
            "question": "What is the largest freshwater lake in the world by surface area?",
          }
        ],
        "current_category": 3,
        "total_questions": 1
      }
    ```
  - 404: A Not Found error object containing:
    - `success`: `boolean`
    - `error`: `str`

    Example payload:
    ```json
      {
        "success": false,
        "error": "Not Found"
      }
    ```
  - 405: A Method Not Allowed error containing:
    - `success`: `boolean`
    - `error`: `str`

    Example payload:
    ```json
      {
        "success": false,
        "error": "Method Not Allowed"
      }  
    ```
  - 500: An Internal Server Error error containing:
    - `success`: `boolean`
    - `error`: `str`

    Example payload:
    ```json
      {
        "success": false,
        "error": "Internal Server Error"
      }  
    ```

`GET '/questions?page={int}'`
- Fetches a list of all questions, paginated in groups of 10
- Request Arguments:
  - Path parameters: None
  - Query parameters:
    - `page`: `int` Defaults to `1` if not provided or if an improper value is provided for `page`
- Returns:
  - 200: A success object containing:
    - `success`: `boolean`
    - `categories`: a list of `{id: int, type: str}` category objects for all categories
    - `questions`: a list of `{id: int, question: str, answer: str, category: int, difficulty: int}` objects
    - `current_category`: a category `{id: int, type: str}` object matching the category of the first `question` in the `questions` list
    - `total_questions`: `int` showing the total number of questions in the system

    Example payload:
    ```json
      {
          "categories": [
              {
                  "id": 1,
                  "type": "Science"
              },
              {
                  "id": 2,
                  "type": "Art"
              },
              {
                  "id": 3,
                  "type": "Geography"
              },
              {
                  "id": 4,
                  "type": "History"
              },
              {
                  "id": 5,
                  "type": "Entertainment"
              },
              {
                  "id": 6,
                  "type": "Sports"
              }
          ],
          "current_category": {
              "id": 5,
              "type": "Entertainment"
          },
          "questions": [
              {
                  "answer": "Apollo 13",
                  "category": 5,
                  "difficulty": 4,
                  "id": 2,
                  "question": "What movie earned Tom Hanks his third straight Oscar nomination, in 1996?"
              },
              {
                  "answer": "Tom Cruise",
                  "category": 5,
                  "difficulty": 4,
                  "id": 4,
                  "question": "What actor did author Anne Rice first denounce, then praise in the role of her beloved Lestat?"
              },
              {
                  "answer": "Maya Angelou",
                  "category": 4,
                  "difficulty": 2,
                  "id": 5,
                  "question": "Whose autobiography is entitled 'I Know Why the Caged Bird Sings'?"
              },
              {
                  "answer": "Edward Scissorhands",
                  "category": 5,
                  "difficulty": 3,
                  "id": 6,
                  "question": "What was the title of the 1990 fantasy directed by Tim Burton about a young man with multi-bladed appendages?"
              },
              {
                  "answer": "Muhammad Ali",
                  "category": 4,
                  "difficulty": 1,
                  "id": 9,
                  "question": "What boxer's original name is Cassius Clay?"
              },
              {
                  "answer": "Brazil",
                  "category": 6,
                  "difficulty": 3,
                  "id": 10,
                  "question": "Which is the only team to play in every soccer World Cup tournament?"
              },
              {
                  "answer": "Uruguay",
                  "category": 6,
                  "difficulty": 4,
                  "id": 11,
                  "question": "Which country won the first ever soccer World Cup in 1930?"
              },
              {
                  "answer": "George Washington Carver",
                  "category": 4,
                  "difficulty": 2,
                  "id": 12,
                  "question": "Who invented Peanut Butter?"
              },
              {
                  "answer": "Lake Victoria",
                  "category": 3,
                  "difficulty": 2,
                  "id": 13,
                  "question": "What is the largest lake in Africa?"
              },
              {
                  "answer": "The Palace of Versailles",
                  "category": 3,
                  "difficulty": 3,
                  "id": 14,
                  "question": "In which royal palace would you find the Hall of Mirrors?"
              }
          ],
          "success": true,
          "total_questions": 19
      }
    ```
  - 404: A Not Found error object containing:
    - `success`: `boolean`
    - `error`: `str`

    Example payload:
    ```json
      {
        "success": false,
        "error": "Not Found"
      }
    ```
  - 405: A Method Not Allowed error containing:
    - `success`: `boolean`
    - `error`: `str`

    Example payload:
    ```json
      {
        "success": false,
        "error": "Method Not Allowed"
      }  
    ```
  - 500: An Internal Server Error error containing:
    - `success`: `boolean`
    - `error`: `str`

    Example payload:
    ```json
      {
        "success": false,
        "error": "Internal Server Error"
      }  
    ```

`POST '/questions'`
- Creates a question
- Request Arguments: None
- Request Body: an object containing:
  - `answer`: `str` the answer to the question 
  - `category`: `int` the `id` of the question's category
  - `difficulty`: `int` the difficulty of the question on a scale of 1 to 5
  - `question`: `str` the question

  Example request body:
  ```json
    {
        "answer": "Lake Superior",
        "category": 3,
        "difficulty": 3,
        "question": "What is the largest freshwater lake in the world by surface area?",
    }
  ```
- Returns:
  - 201: A success object containing:
    - `answer`: `str` the answer to the question 
    - `category`: `int` the id of the question's category
    - `difficulty`: `int` the difficulty of the question on a scale of 1 to 5
    - `id`: `int` the id of the created question
    - `question`: `str` the question

    Example payload:
    ```json
      {
          "answer": "Lake Superior",
          "category": 3,
          "difficulty": 3,
          "id": 20,
          "question": "What is the largest freshwater lake in the world by surface area?",
      }
    ```
  - 400: A Bad Request error containing:
    - `success`: `boolean`
    - `error`: `str`

    Example payload:
    ```json
      {
        "success": false,
        "error": "Bad Request"
      }  
    ```
  - 405: A Method Not Allowed error containing:
    - `success`: `boolean`
    - `error`: `str`

    Example payload:
    ```json
      {
        "success": false,
        "error": "Method Not Allowed"
      }  
    ```
  - 415: An Unsupported Media Type error containing:
    - `success`: `boolean`
    - `error`: `str`

    Example payload:
    ```json
      {
        "success": false,
        "error": "Unsupported Media Type"
      }  
    ```
  - 422: An Unprocessable Content error containing:
    - `success`: `boolean`
    - `error`: `str`

    Example payload:
    ```json
      {
        "success": false,
        "error": "Unprocessable Content"
      }  
    ```
  - 500: An Internal Server Error error containing:
    - `success`: `boolean`
    - `error`: `str`

    Example payload:
    ```json
      {
        "success": false,
        "error": "Internal Server Error"
      }  
    ```

`POST '/questions/search'`
- Fetches a list of questions that have a case insensitive match for the provided search string
- Request Arguments: None
- Request Body: an object containing:
  - `search_term`: `str` the string to search with

  Example request body:
  ```json
    {
        "search_term": "Superior"
    }
  ```
- Returns:
  - 200: A success object containing:
    - `success`: `boolean`
    - `questions`: a list of question objects containing:
      - `answer`: `str` the answer to the question 
      - `category`: `int` the id of the question's category
      - `difficulty`: `int` the difficulty of the question on a scale of 1 to 5
      - `id`: `int` the id of the created question
      - `question`: `str` the question
    - `total_questions`: `int` the total number of questions including the search string
    - `current_category`: a category object `{id: int, type: str}` of the category of the first question in the list

    Example payload:
    ```json
      {
        "success": true,
        "questions": [
          {
            "answer": "Lake Superior",
            "category": 3,
            "difficulty": 3,
            "id": 20,
            "question": "What is the largest freshwater lake in the world by surface area?"
          },
        ],
        "total_questions": 1,
        "current_category": {"id": 3, "type": "Geography"}
      }
    ```
  - 400: A Bad Request error containing:
    - `success`: `boolean`
    - `error`: `str`

    Example payload:
    ```json
      {
        "success": false,
        "error": "Bad Request"
      }  
    ```
  - 405: A Method Not Allowed error containing:
    - `success`: `boolean`
    - `error`: `str`

    Example payload:
    ```json
      {
        "success": false,
        "error": "Method Not Allowed"
      }  
    ```
  - 415: An Unsupported Media Type error containing:
    - `success`: `boolean`
    - `error`: `str`

    Example payload:
    ```json
      {
        "success": false,
        "error": "Unsupported Media Type"
      }  
    ```
  - 422: An Unprocessable Content error containing:
    - `success`: `boolean`
    - `error`: `str`

    Example payload:
    ```json
      {
        "success": false,
        "error": "Unprocessable Content"
      }  
    ```
  - 500: An Internal Server Error error containing:
    - `success`: `boolean`
    - `error`: `str`

    Example payload:
    ```json
      {
        "success": false,
        "error": "Internal Server Error"
      }  
    ```

`DELETE '/questions/<int:question_id>'`
- Deletes a question
- Request arguments:
  - Path parameters:
    - `question_id`: `int`
  - Query parameters: None
- Returns:
  - 200: A success object containing:
    - `success`: `boolean`
    - `id`: `int` the id of the deleted question

    Example payload:
    ```json
      {
        "success": true,
        "id": 3
      }
    ```
  - 400: A Bad Request error containing:
    - `success`: `boolean`
    - `error`: `str`

    Example payload:
    ```json
      {
        "success": false,
        "error": "Bad Request"
      }  
    ```
  - 405: A Method Not Allowed error containing:
    - `success`: `boolean`
    - `error`: `str`

    Example payload:
    ```json
      {
        "success": false,
        "error": "Method Not Allowed"
      }  
    ```
  - 500: An Internal Server Error error containing:
    - `success`: `boolean`
    - `error`: `str`

    Example payload:
    ```json
      {
        "success": false,
        "error": "Internal Server Error"
      }  
    ```
`POST '/quizzes'`
- Fetch a random list of questions to play the quiz
- Request arguments: None
- Request body:
  - An object containing:
    - `quiz_category`: `int | None` the category (if any) to pull questions from for the quiz
    - `previous_questions`: a list of `int`s of the previous questions answered in the quiz

  Example request body:
  ```json
    {"previous_questions":[9],"quiz_category":0}
  ```
- Returns:
  - 200: A success object containing:
    - `success`: `boolean`
    - `question`: `None` or a question object containing the next question in the quiz:
      - `answer`: `str` the answer to the question 
      - `category`: `int` the id of the question's category
      - `difficulty`: `int` the difficulty of the question on a scale of 1 to 5
      - `id`: `int` the id of the created question
      - `question`: `str` the question

    Example payload:
    ```json
      {
          "question": {
              "answer": "Apollo 13",
              "category": 5,
              "difficulty": 4,
              "id": 2,
              "question": "What movie earned Tom Hanks his third straight Oscar nomination, in 1996?"
          },
          "success": true
      }
    ```
  - 400: A Bad Request error containing:
    - `success`: `boolean`
    - `error`: `str`

    Example payload:
    ```json
      {
        "success": false,
        "error": "Bad Request"
      }  
    ```
  - 405: A Method Not Allowed error containing:
    - `success`: `boolean`
    - `error`: `str`

    Example payload:
    ```json
      {
        "success": false,
        "error": "Method Not Allowed"
      }  
    ```
  - 415: An Unsupported Media Type error containing:
    - `success`: `boolean`
    - `error`: `str`

    Example payload:
    ```json
      {
        "success": false,
        "error": "Unsupported Media Type"
      }  
    ```
  - 422: An Unprocessable Content error containing:
    - `success`: `boolean`
    - `error`: `str`

    Example payload:
    ```json
      {
        "success": false,
        "error": "Unprocessable Content"
      }  
    ```
  - 500: An Internal Server Error error containing:
    - `success`: `boolean`
    - `error`: `str`

    Example payload:
    ```json
      {
        "success": false,
        "error": "Internal Server Error"
      }  
    ```
