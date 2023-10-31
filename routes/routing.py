import time

from flask import Blueprint, request, abort
from flask_httpauth import HTTPTokenAuth
from json import dumps, loads

from mongodb.mongodb import Database

routes_bp = Blueprint('routes_bp', __name__)
auth = HTTPTokenAuth(scheme='Bearer')
db = Database('127.0.0.1', 27017)


@auth.verify_token
def verify_token(token):
    try:
        return db.findToken(token)
    except:
        abort(401)
    return False


@routes_bp.route('/<user_id>/projects', methods=['GET'])
@auth.login_required
def getUserProjects(user_id):
    # try:
    if request.authorization.token == user_id and not db.checkUserIdUnique(user_id):
        return dumps(db.getUserProjects(user_id))
    else:
        abort(400)
        return "error"
    # except:
    #     abort(404)
    #     return "error"


@routes_bp.route('/<project_id>/table', methods=['GET'])
@auth.login_required
def getProjectTable(project_id):
    try:
        return dumps(db.getProjectTable(project_id))
    except:
        abort(404)
        return 'error'


@routes_bp.route('/<user_id>/<project_id>/<date>', methods=['GET'])
@auth.login_required
def getTasksForDate(user_id, project_id, date):
    try:
        return dumps(db.getTasksForDate(user_id, project_id, int(date)))
    except:
        abort(404)
        return "error"


@routes_bp.route('/<project_id>/column', methods=['POST'])
@auth.login_required
def addColumn(project_id):
    try:
        data = dict(loads(request.headers.get('column')))
        if data['column_id'] is None or not (type(data['column_id']) is str):
            abort(400)
        if data['project_id'] is None or not (type(data['project_id']) is str) or project_id != data['project_id']:
            abort(400)
        if 'tasks' in data.keys() and (data['tasks'] is None or not (type(data['tasks']) is list)):
            data['tasks'] = []
        elif 'tasks' in data.keys() and not (type(data['tasks']) is list):
            abort(400)
        else:
            data['tasks'] = []
        if data['name'] is None or not (type(data['name']) is str):
            abort(400)
        if not db.checkProjectIdUnique(data['project_id']):
            db.addColumn(data['name'], data['column_id'], data['tasks'], data['project_id'])
        else:
            abort(404)
    except:
        abort(400)
    return 'ok'


@routes_bp.route('/<project_id>/<column_id>/task', methods=['POST'])
@auth.login_required
def addTask(project_id, column_id):
    try:
        data = loads(request.headers.get('task'))
        if data['name'] is None or not (type(data['name']) is str):
            abort(400)
        if data['column_id'] is None or not (type(data['column_id']) is str) or data['column_id'] != column_id:
            abort(400)
        if data['task_id'] is None or not (type(data['task_id']) is str):
            abort(400)
        if data['project_id'] is None or not (type(data['project_id']) is str) or data['project_id'] != project_id:
            abort(400)
        if 'performers' not in data.keys():
            data['performers'] = []
        elif not (type(data['performers']) is list):
            abort(400)
        if 'deadline' not in data.keys():
            data['deadline'] = None
        elif not (type(data['deadline']) is int):
            abort(400)
        if 'description' not in data.keys():
            data['description'] = None
        elif not (type(data['description']) is str):
            abort(400)
        if db.checkTaskIdUnique(data['task_id']):
            db.addTask(data)
        else:
            abort(404)
    except:
        abort(400)
    return 'ok'


@routes_bp.route('/addUser', methods=['POST'])
def addUser():
    try:
        data = loads(request.headers.get('user'))
        if data['name'] is None or not (type(data['name']) is str):
            abort(400)
        if data['login'] is None or not (type(data['login']) is str):
            abort(400)
        if data['password'] is None or not (type(data['password']) is str):
            abort(400)
        db.registerUser(data["login"], data["password"], data["name"])
    except:
        abort(400)
    return 'ok'


@routes_bp.route('/<user_id>/project', methods=['POST'])
@auth.login_required
def addProject(user_id):
    try:
        data = dict(loads(request.headers.get('project')))
        if data['project_id'] is None or not (type(data['project_id']) is str):
            abort(400)
        if data['owner_id'] is None or not (type(data['owner_id']) is str) or user_id != data['owner_id']:
            abort(400)
        if data['color'] is None or not (type(data['color']) is int):
            abort(400)
        if data['name'] is None or not (type(data['name']) is str):
            abort(400)
        if 'performers' not in data.keys():
            data['performers'] = []
        elif not (type(data['performers']) is list):
            abort(400)
        db.addProject(data)
    except:
        abort(400)
    return 'ok'


@routes_bp.route('/updtask/<project_id>/<task_id>', methods=['PUT'])
@auth.login_required
def updateTask(project_id, task_id):
    try:
        data = loads(request.headers.get('task'))
        if data['name'] is None or not (type(data['name']) is str):
            abort(400)
        if data['column_id'] is None or not (type(data['column_id']) is str):
            abort(400)
        if data['task_id'] is None or not (type(data['task_id']) is str):
            abort(400)
        if data['project_id'] is None or not (type(data['project_id']) is str) or data['project_id'] != project_id:
            abort(400)
        if 'performers' not in data.keys():
            data['performers'] = []
        elif not (type(data['performers']) is list):
            abort(400)
        if 'deadline' not in data.keys():
            data['deadline'] = None
        elif not (type(data['deadline']) is int):
            abort(400)
        if 'description' not in data.keys():
            data['description'] = None
        elif not (type(data['description']) is str):
            abort(400)
        if not db.checkTaskIdUnique(data['task_id']):
            db.updateTask(data['task_id'], data)
        else:
            abort(404)
    except:
        abort(400)
    return 'ok'


@routes_bp.route('/updclm/<project_id>/<column_id>', methods=['PUT'])
@auth.login_required
def updateColumn(project_id, column_id):
    try:
        data = dict(loads(request.headers.get('column')))
        if data['column_id'] is None or not (type(data['column_id']) is str):
            abort(400)
        if data['project_id'] is None or not (type(data['project_id']) is str) or project_id != data['project_id']:
            abort(400)
        if 'tasks' in data.keys() and (data['tasks'] is None or not (type(data['tasks']) is list)):
            data['tasks'] = []
        elif 'tasks' in data.keys() and not (type(data['tasks']) is list):
            abort(400)
        else:
            data['tasks'] = []
        if data['name'] is None or not (type(data['name']) is str):
            abort(400)
        if not db.checkProjectIdUnique(data['project_id']):
            db.updateColumn(data['column_id'], data)
        else:
            abort(404)
    except:
        abort(400)
    return 'ok'


@routes_bp.route('/dltclm/<project_id>/<column_id>', methods=['DELETE'])
@auth.login_required
def deleteColumn(project_id, column_id):
    try:
        if not db.checkColumnIdUnique(column_id):
            db.deleteColumn(column_id)
        else:
            abort(404)
            return "error"
    except:
        abort(404)
        return "error"
    return "ok"


@routes_bp.route('/loginUser', methods=['GET'])
def loginUser():
    try:
        data = dict(loads(request.headers.get('user')))
        return db.loginUser(data["login"], data["password"])
    except:
        abort(404)
    return 'error'


@routes_bp.route('/dlttsk/<task_id>', methods=['DELETE'])
@auth.login_required
def deleteTask(task_id):
    try:
        if not db.checkTaskIdUnique(task_id):
            db.deleteTask(task_id)
        else:
            abort(404)
    except:
        abort(404)
        return 'error'
    return 'ok'


@routes_bp.route('/dltprj/<project_id>', methods=['DELETE'])
@auth.login_required
def deleteProject(project_id):
    try:
        db.deleteProject(project_id)
    except:
        abort(404)
        return "error"
    return "ok"


@routes_bp.route('/upd/<user_id>', methods=['PUT'])
@auth.login_required
def updateUserInfo(user_id):
    try:
        data = loads(request.headers.get('user'))
        if data['name'] is None or not (type(data['name']) is str):
            abort(400)
        if data['login'] is None or not (type(data['login']) is str):
            abort(400)
        if data['password'] is None or not (type(data['password']) is str):
            abort(400)
        data['user_id'] = user_id
        if user_id == request.authorization.token:
            db.updateUserInfo(user_id, data)
        else:
            abort(401)
    except:
        abort(400)
    return 'ok'
