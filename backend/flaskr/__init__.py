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
        if start > len(selection):
            abort(404)
        questions = [question.format() for question in selection]
        current_questions = questions[start:end]
        return current_questions

        # This method id added to sort list od categories


    def format_categories(categories):
        if len(categories) == 0:
            abort(404)
        format_categories = {}
        index = 0
        for index in range(len(categories)):
            format_categories[categories[index].id] = categories[index].type
        return format_categories


    @app.after_request
    def after_request(response):
        response.headers.add(
            'Access-Control-Allow-Headers',
            'Content-Type, Authorization'
            )
        response.headers.add(
            'Access-Control-Allow-Methods',
            'GET, POST, PATCH, DELETE, OPTIONS'
            )
        return(response)


    @app.route('/categories', methods=['GET'])
    def get_categories():
        try:
            categories = Category.query.order_by(Category.type).all()
            if len(categories) == 0:
                abort(404)
        except:
            abort(422)
        return(jsonify({
            'success': True,
            'categories': format_categories(categories),
            'status_code': 200
            })), 200


    @app.route('/questions', methods=['GET'])
    def retrieve_questions():
        try:
            categories = Category.query.order_by(Category.type).all()
            if len(categories) == 0:
                abort(404)
        except:
            abort(422)
        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)
        if len(current_questions) == 0:
            abort(404)
        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(Question.query.all()),
            'categories': format_categories(categories),
            'current_category': None
        })


    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.filter(Question.id == question_id).one_or_none()
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


    @app.route('/questions', methods=['POST'])
    def add_question():
        data = request.get_json()
        searchTerm = data.get('searchTerm', None)
        if searchTerm:
            try:
                categories = Category.query.all()
                formatted_categories = format_categories(categories)
                selection = Question.query.filter(Question.question.contains(data['searchTerm'])).order_by(Question.id).all()
                current_questions = paginate_questions(request, selection)
                if len(current_questions) == 0:
                    abort(404)
                return jsonify({
                    'success': True,
                    'questions': current_questions,
                    'total_questions': len(selection),
                    'categories': formatted_categories
                })
            except:
                abort(404)

        else:
            if (data.get('question') and data.get('answer') and data.get('category') and data.get('difficulty')):
                new_question = Question(
                    question=data.get('question', None),
                    answer=data.get('answer', None),
                    category=data.get('category', None),
                    difficulty=data.get('difficulty', None)
                    )
                try:
                    Question.insert(new_question)
                    return jsonify({
                        'success': True,
                        'status_code': 201,
                        'question_id': new_question.id,
                    }), 201
                except:
                    abort(422)
            else:
                abort(422)


    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def retrieve_questions_by_category_id(category_id):
        try:
            category = Category.query.get(category_id)
        except:
            abort(404)

        try:
            questions = Question.query.filter(Question.category == category_id).order_by(Question.id).all()
            selection = Question.query.filter(Question.category == category_id).order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)
            if len(current_questions) == 0:
                abort(404)
            return jsonify({
                'success': True,
                'questions': current_questions,
                'total_questions': len(
                    Question.query.filter(Question.category == category_id).all()
                    ),
            }), 200
        except:
            abort(404)


    @app.route('/quizzes', methods=['POST'])
    def have_a_quiz():
        try:
            data = request.json
            if not ('previous_questions' in data and 'quiz_category' in data):
                abort(422)
            category_id = data['quiz_category']['id']
            previous_questions = data['previous_questions']
            if category_id == 0:
                questions = Question.query.order_by(Question.id).all()
            else:
                questions = Question.query.filter(Question.category == category_id).order_by(Question.id).all()
            i = 0
            while i < 1:
                question = random.choice(questions)
                if question not in previous_questions:
                    previous_questions.append(question)
                    i = 1
            return jsonify({
                'status_code': 200,
                'success': True,
                'question': {
                    'id': question.id,
                    'question': question.question,
                    'answer': question.answer,
                    'difficulty': question.difficulty,
                    'category': question.category
                    },
            }), 200
        except:
            abort(422)


    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'resource not found'
        }), 404


    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 400,
            'message': 'bad request'
        }), 400


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


    return app
