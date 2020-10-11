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
        #self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        self.database_path = 'postgres://postgres:123456@localhost:5432/test_trivia_api_db'
        setup_db(self.app, self.database_path)

        self.new_question = {
            'question': 'What is your age?',
            'answer': 33,
            'category': 'science',
            'difficulty': 5
        }
    '''
    def tearDown(self):
        """Executed after each test"""
        pass
    '''

    def test_get_paginated_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])

    def test_search_questions(self):
        res = self.client().post('/questions', json = {'searchTerm': 'age'})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])

       





# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()