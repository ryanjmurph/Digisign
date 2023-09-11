# Pius Gumo
# 20/08/2023
# Queries Parent class for the models to have shared methods

import re
from models.QueryBuilders.EagerLoadRelationship import JoinRelationship


class Query(JoinRelationship):
    def __init__(self) -> None:
        pass

    def raw(self, sql):
        connection = self.getDatabaseConnection()

        with connection.cursor() as cursor:
            cursor.execute(sql)
            result = cursor.fetchall()
            return result

    def where(self, column, value, operator="="):
        self.where_clause = f"WHERE {column} {operator} '{value}'"
        return self

    def addSort(self, column, order):
        self.sort_clause = f"ORDER BY {column} {order}"
        return self

    def addLimit(self, limit):
        self.limit_clause = f"LIMIT {limit}"
        return self
    
    def getCasts(self):
        casts = getattr(self, "casts", {})
        return casts
    
    def isAttributeCastable(self, casts,attribute):
        return attribute in casts.keys()
    
    def castAttribute(self, casts,attribute,value):
        if self.isAttributeCastable(casts,attribute):
            if casts[attribute] == "int":
                return int(value)
            elif casts[attribute] == "float":
                return float(value)
            elif casts[attribute] == "bool":
                return bool(value)
            elif casts[attribute] == "string":
                return str(value)
            else:
                return value
        else:
            return value

    
    def save(self):
        connection = self.getDatabaseConnection()
        casts = self.getCasts()

        sql = f"INSERT INTO {self.getTableName()} ("
        for key in self.__dict__:
            if key == "id":
                continue
            sql += f"{key}, "
        sql = sql[:-2]
        sql += ") VALUES ("
        for key in self.__dict__:
            if key == "id":
                continue
            if self.isAttributeCastable(casts,key):
                sql += f"{self.castAttribute(casts,key,self.__dict__[key])}, "
            else:
                sql += f"'{self.__dict__[key]}', "
        sql = sql[:-2]
        sql += ")"

        with connection.cursor() as cursor:
            cursor.execute(sql)
            connection.commit()

        return self.find(connection.insert_id())

    def getDatabaseConnection(self):
        # check if connection is defined in the child class
        # otherwise raise an error
        if hasattr(self, "connection"):
            return self.connection

        raise Exception("Database connection not found in the Model being extended")
    
    def find(self, id):
        connection = self.getDatabaseConnection()

        sql = f"SELECT * FROM {self.getTableName()} WHERE id = {id}"

        with connection.cursor() as cursor:
            cursor.execute(sql)
            result = cursor.fetchone()
            return self.castResultToModel(result)

    def get(self):
        connection = self.getDatabaseConnection()

        sql = f"SELECT * FROM {self.getTableName()} {self.getClauses()}"

        with connection.cursor() as cursor:
            cursor.execute(sql)
            result = cursor.fetchall()
            return result

    def getClauses(self) -> str:
        clauses_string = ""

        where_clause = getattr(self, "where_clause", "")
        sort_clause = getattr(self, "sort_clause", "")
        limit_clause = getattr(self, "limit_clause", "")

        clauses_string = f"{where_clause} {sort_clause} {limit_clause}"
        return clauses_string
    
    def prepareValues(self,values):
        # for insert and update queries, we cast any values in the dict to the correct type
        casts = self.getCasts()
        for key in values:
            if self.isAttributeCastable(casts,key):
                values[key] = self.castAttribute(casts,key,values[key])

        return values
    
    def makeValuesSafe(self,values):
        # if value is a string, escape it to prevent sql injection
        # if value is a number, leave it as it is
        # if value is None, set it to NULL

        for key in values:
            if type(values[key]) == str:
                values[key] = self.getDatabaseConnection().escape(values[key])
            elif values[key] == None:
                values[key] = "NULL"

        return values

    def update(self, data):
        if not self.id:
            raise Exception("Cannot update a record without an id")
        
        data = self.prepareValues(data)
        data = self.makeValuesSafe(data)

        sql = f"UPDATE {self.getTableName()} SET "
        
        for key in data:
            sql += f"{key} = {data[key]}, "
        sql = sql[:-2]

        sql += f" WHERE id = {self.id}"

        print(f"SQL: {sql}")

        connection = self.getDatabaseConnection()

        with connection.cursor() as cursor:
            cursor.execute(sql)
            connection.commit()

        return self.find(self.id)

    def first(self):
        # run the query and return the first result
        connection = self.getDatabaseConnection()

        clauses = self.getClauses()
        # strip the limit clause
        limit_clause = getattr(self, "limit_clause", "")
        clauses = clauses.replace(limit_clause, "")

        sql = f"SELECT * FROM {self.getTableName()} {clauses} LIMIT 1"

        with connection.cursor() as cursor:
            cursor.execute(sql)
            result = cursor.fetchone()
            return result

    def getTableName(self):
        # check if table.name is defined in the child class
        # otherwise take the class name and make it snake case and plural and lowercase

        if hasattr(self, "table_name"):
            return self.table_name

        class_name = self.__class__.__name__
        return str(self.snake_case(class_name) + "s").lower()

    def snake_case(self, string):
        return re.sub(r"(?<!^)(?=[A-Z])", "_", string).lower()
    
    def castResultToModel(self,result):
        casts = self.getCasts()
        model = self.__class__()
        for key in result:
            if self.isAttributeCastable(casts,key):
                setattr(model,key,self.castAttribute(casts,key,result[key]))
            else:
                setattr(model,key,result[key])
        return model
