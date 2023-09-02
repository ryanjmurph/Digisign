# Pius Gumo
# 20/08/2023
# Queries Parent class for the models to have shared methods

import re


class Query(object):
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

    def getDatabaseConnection(self):
        # check if connection is defined in the child class
        # otherwise raise an error
        if hasattr(self, "connection"):
            return self.connection

        raise Exception("Database connection not found in the Model being extended")

    def get(self):
        connection = self.getDatabaseConnection()

        sql = f"SELECT * FROM {self.getTableName()} {self.getClauses()}"

        print(f"SQL: {sql}")

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

    def update(self, data):
        if not self.id:
            raise Exception("Cannot update a record without an id")

        sql = f"UPDATE {self.getTableName()} SET "
        for key in data:
            sql += f"{key} = '{data[key]}', "
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
