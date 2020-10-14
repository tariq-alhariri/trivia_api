# Import all dependencies
import unittest, json, os
from flaskr import create_app
from models import setup_db, Question, Category


class FlaskrTestCase(unittest.TestCase):
    """This class represents the resource test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "test_trivia_api_db"
        self.username = 'postgres'
        self.password = '123456'
        self.url = 'localhost:5432'
        self.database_path = "postgres://{}:{}@{}/{}".format(self.username, self.password, self.url, self.database_name)
        setup_db(self.app, self.database_path)

        self.new_question = {
            'question': 'What is your age?',
            'answer': 33,
            'category': 'science',
            'difficulty': 5
        }

    def tearDown(self):
        """Executed after each test"""
        pass

    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])

    def test_get_questions_per_categories(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])

    def test_get_non_existed_categories(self):
        res = self.client().get('/categories/1000/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertTrue(data['message'], 'resource not found')

    def test_get_paginated_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['categories'])
        self.assertTrue(data['questions'])

    def test_get_notfound_pages_of_questions(self):
        res = self.client().get('/questions/?page=10000')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['message'], 'resource not found')

    def test_search_questions(self):
        res = self.client().post('/questions', json={'searchTerm': 'b'})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])

    def test_search_questions_no_results_found(self):
        res = self.client().post('/questions', json={
            'searchTerm': '$#@IHUHGUYGBJKN'
            })
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_add_question(self):
        num_of_questions_before_adding = len(Question.query.all())
        res = self.client().post('/questions', json={
            'question': 'What is your age?',
            'answer': 33,
            'category': 1,
            'difficulty': 5})
        num_of_questions_after_adding = len(Question.query.all())
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 201)
        self.assertEqual(data['success'], True)
        self.assertEqual(num_of_questions_after_adding, num_of_questions_before_adding + 1)

    def test_failed_add_question(self):
        res = self.client().post('/questions', json={
            'question': 'What is your age?',
            'category': 1,
            'difficulty': 5})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)

    def test_delete_question(self):
        question = Question.query.order_by(Question.id.desc()).first()
        res = self.client().delete('/questions/' + str(question.id))
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['questions'])
        self.assertEqual(data['deleted'], question.id)

    def test_delete_unexisted_question(self):
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertTrue(data['message'], 'resource not found')

    def test_start_quiz(self):
        res = self.client().post('/quizzes', json={
            'previous_questions': [],
            'quiz_category': {'type': 'Science', 'id': '1'}
            })
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['question'], True)

    def test_failed_start_quiz(self):
        res = self.client().post('/quizzes', json={
            'previous_questions': [],
            'quizz_category': {'type': 'Science', 'id': '1'}
            })
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertTrue(data['message'], 'Unprocessable Entity')
        self.assertEqual(data['success'], False)

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
