import uuid

from pymongo import MongoClient


class Database:
    def __init__(self, host, port): # '127.0.0.1' 27017 for local run
        self._client = MongoClient(host, port)
        self._db = self._client['task']
        self._task = self._db['task']
        self._user = self._db['user']
        self._project = self._db['project']
        self._column = self._db['column']

    def getUserProjects(self, user_id):
        tmp = list(dict(self._user.find_one({"user_id": user_id}))["projects"])
        projects = []
        for p_id in tmp:
            projects.append(self._project.find_one({"project_id": p_id},{"_id":0}))
        return {"projects": projects}

    def getProjectTable(self, project_id):
        columns_of_project = list(self._column.find({"project_id": project_id}, {"_id": 0}))
        for i_column in range(0, len(columns_of_project)):
            tsks = []
            for task_id in columns_of_project[i_column]["tasks"]:
                tsks.append(self._task.find_one({"task_id": task_id}, {"_id": 0}))
            columns_of_project[i_column]["tasks"] = tsks
        return {"project_table": columns_of_project}

    def getTasksForDate(self, user_id, project_id, date):
        tasks = list(self._task.find({
            "project_id": project_id,
            "deadline": {
                "$gt": date - 1,
                "$lt": date + 86400
            },
            "performers": {
                "$in": [user_id]
            }
        }, {"_id": 0}))
        return {"tasks": tasks}

    def addColumn(self, name, column_id, tasks, project_id):
        self._column.insert_one({
            'name': name,
            'column_id': column_id,
            'tasks': tasks,
            'project_id': project_id,
        })
        for task_id in tasks:
            self._task.update_one({"task_id": task_id}, {"column_id": column_id})

    def addTask(self, data):
        self._task.insert_one(data)
        self._column.update_one({"column_id" : data["column_id"]}, {"$push" : {"tasks" : data["task_id"]}})
        pass

    def addProject(self, data):
        self._project.insert_one(data)
        for performer in data['performers']:
            self._user.update_one({"user_id": performer}, {"$push" : {"projects" : data["project_id"]}})
        self._user.update_one({"user_id": data["owner_id"]}, {"$push": {"projects": data["project_id"]}})
        pass

    def updateTask(self, task_id, data):
        self._task.replace_one({'task_id' : task_id}, data)
        pass

    def updateColumn(self, column_id, data):
        self._column.replace_one({'column_id' : column_id}, data)
        pass

    def deleteColumn(self, column_id):
        tasks = self._column.find_one({"column_id": column_id})['tasks']
        for task_id in tasks:
            self._task.delete_one({"task_id" : task_id})
        self._column.delete_one({"column_id" : column_id})
        pass

    def deleteTask(self, task_id):
        self._task.delete_one({"task_id" : task_id})
        self._column.update_one({"tasks" : {"$in": [task_id]}}, {'$pull' : {'tasks' : [task_id]}})
        pass

    def deleteProject(self, project_id):
        self._task.delete_many({"project_id" : project_id})
        self._column.delete_many({"project_id" : project_id})
        self._project.delete_one({"project_id" : project_id})
        pass

    def updateUserInfo(self, user_id, data):
        self._user.replace_one({"user_id" : user_id}, data)
        pass

    def checkProjectIdUnique(self, project_id):
        try:
            tmp = self._project.find_one({"project_id": project_id})
            return False
        except:
            return True

    def checkColumnIdUnique(self, column_id):
        try:
            tmp = self._column.find_one({"column_id": column_id})
            return False
        except:
            return True

    def checkTaskIdUnique(self, task_id):
        try:
            tmp = self._task.find_one({"task_id": task_id})
            return tmp is None
        except:
            return True

    def checkUserIdUnique(self, user_id):
        try:
            tmp = self._user.find_one({"user_id": user_id})
            return False
        except:
            return True

    def loginUser(self, login, pswd):
        data = dict(self._user.find_one({"login": login, "password": pswd}))
        return {"user_id": data["user_id"]}

    def findToken(self, token):
        return len(list(self._user.find({"user_id" : token}))) >= 1

    def registerUser(self, login, pswd, name):
        token = str(uuid.uuid4())
        self._user.insert_one({
            "login": login,
            "password": pswd,
            "name": name,
            "user_id": token,
            "projects": []
        })
        return {"user_id": token}