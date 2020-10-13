import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random, operator

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  CORS(app)

  Question_Per_Page = 10
  def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * Question_Per_Page 
    end = start + QUESTIONS_PER_PAGE 
    if start >len(selection):
      abort(404)
    questions = [question.format() for question in selection]
    current_questions = questions[start:end]
    return current_questions

    # This method id added to sort list od categories
  def format_categories(categories):
    if len(categories) ==0:
      abort(404)
    format_categories = {}
    index = 0
    for index in range(len(categories)):
      format_categories[categories[index].id] = categories[index].type
    return format_categories
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS')
    return(response)



  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories', methods=['GET'])
  def get_categories():
    try:
      categories = Category.query.order_by(Category.type).all()
      if len(categories) ==0:
        abort(404)
    except:
      abort(500)
    return(jsonify({
      'success': True,
      'categories': format_categories(categories),
      'status_code': 200
      })), 200

  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions')
  def retrieve_questions():
    try:
      categories = Category.query.order_by(Category.type).all()
      if len(categories) ==0:
        abort(404)
    except:
      abort(500)
    selection = Question.query.order_by(Question.id).all()
    current_questions = paginate_questions(request, selection)
    if len(current_questions)==0:
      abort(404)  
    return jsonify({
      'success': True,
      'questions': current_questions,
      'total_questions': len(Question.query.all()),
      'categories': format_categories(categories),
      'current_category': None
    })
  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    try:
      question = Question.query.filter(Question.id == question_id).one_or_none()
      if question is None:
        abort(404)
      question.delete()
      selection = Question.query.order_by(Question.id).all()
      current_questions = paginate_questions(request, selection)
      return jsonify({
        'status_code': 200,
        'success': True,
        'deleted': question_id,
        'questions': current_questions,
        'total_questions': len(Question.query.all()) 
        }), 200
    except:
      abort(422)




  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions', methods=['POST'])
  def add_question():
    data = request.get_json()
    searchTerm = data.get('searchTerm',None)
    if searchTerm:
      try:

        categories = Category.query.all()
        formatted_categories = format_categories(categories)
        selection = Question.query.filter(Question.question.contains(data['searchTerm'])).all()
        current_questions = paginate_questions(request, selection)
        if len(current_questions)==0:
          abort(404)  
        return jsonify({
          'success': True,
          'questions': current_questions,
          'total_questions': len(selection),
          'categories': formatted_categories
        })
      except:
        abort(422)

    else:
      new_question = Question(question= data.get('question', None),answer= data.get('answer', None),category= data.get('category', None),difficulty= data.get('difficulty', None))
      try:
        Question.insert(new_question)
        return jsonify({
        'success': True,
        'status_code': 201,
        'question_id': new_question.id,
        }), 201
      except:
        abort(422)

      
  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''

  @app.route('/questions/search', methods=['POST'])
  def search_questions():
    print('----------------->')
    body = request.get_json()
    search_term = body.get('searchTerm', None)

    if search_term:
        search_results = Question.query.filter(
            Question.question.ilike(f'%{search_term}%')).all()

        return jsonify({
            'success': True,
            'questions': [question.format() for question in search_results],
            'total_questions': len(search_results),
            'current_category': None
        })
    abort(404)

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id>/questions')
  def retrieve_questions_by_category_id(category_id):
    print('-------------> cat id :', category_id)
    questions = Question.query.filter(Question.category == category_id).all()


    selection = Question.query.filter(Question.category == category_id).order_by(Question.id).all()
    current_questions = paginate_questions(request, selection)
    if len(current_questions)==0:
      abort(404)  
    return jsonify({
      'success': True,
      'questions': current_questions,
      'total_questions': len(Question.query.filter(Question.category == category_id).all()),
    })
  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes', methods=['POST'])
  def quiz():
    list_of_question = []
    print('------------------------> triggred')
    data = request.json
    category_id = data['quiz_category']['id']
    print('---------------------------------------> data', data['quiz_category']['id'])
    if  category_id ==0:
      questions = Question.query.order_by(Question.id).all()
    else:
      questions = Question.query.filter(Question.category == category_id).order_by(Question.id).all()
    i=0
    while i<1:
      question = random.choice(questions)
      if question not in list_of_question :
        list_of_question.append(question) 
        i=1
    print('------------------------------------> the question', question)
    return jsonify({
      'success': True, 
      'question': {'id': question.id, 'question': question.question, 'answer': question.answer}
    })
  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''

  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      'success': False,
      'error': 404,
      'message': 'source not found'
    }), 404


  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      'success': False,
      'error': 400,
      'message': 'bad request'
    }), 400


  @app.errorhandler(405)
  def method_not_allowed(error):
    return jsonify({
      'success': False,
      'error': 405,
      'message': 'Method Not Allowed'
    }), 405

  @app.errorhandler(500)
  def method_not_allowed(error):
    return jsonify({
      'success': False,
      'error': 500,
      'message': 'internal server error'
    }), 500

  @app.errorhandler(422)
  def method_not_allowed(error):
    return jsonify({
      'success': False,
      'error': 422,
      'message': 'Unprocessable Entity'
    }), 422





  @app.route('/')
  def index():
    return ('hello world')

  return app

    