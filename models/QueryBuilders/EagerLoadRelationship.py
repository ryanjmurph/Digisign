class JoinRelationship:

    def withRelation(self,eagerRelationship,fromTable=None,fromTableForeignKey=None):
        """
        Returns a SQL query string that joins the current table with the specified eager relationship table.

        Parameters:
        - eagerRelationship (dict): A dictionary containing the columns, table, foreign_key, and local_key of the eager relationship.
        - fromTable (str): The name of the table to join from. If not provided, the current table's name will be used.
        - fromTableForeignKey (str): The foreign key of the table to join from. If not provided, the current table's foreign key will be used.

        Returns:
        - sql (str): A SQL query string that joins the current table with the specified eager relationship table.
        """
        if not fromTable:
            currentTable = self.getTableName()
        else:
            currentTable = fromTable
              
        columns = eagerRelationship["columns"].split(",")
        onTable = eagerRelationship["table"]
        onTableForeignKey = eagerRelationship["foreign_key"]
        onTableLocalKey = eagerRelationship["local_key"]

        currentTableForeignKey = fromTableForeignKey if fromTableForeignKey else self.getForeignKey()

        columnsString = ",".join(JoinRelationship.formatColumnsWithTableName(columns,onTable))

        sql = f"SELECT {columnsString} FROM {currentTable} INNER JOIN {onTable} ON {currentTable}.{onTableForeignKey} = {onTable}.{onTableLocalKey} WHERE {currentTable}.{fromTableForeignKey} = {self.id}"
        return sql

    def formatColumnsWithTableName(columns,tableName):
        """
        Returns a list of formatted column names with the specified table name.

        Parameters:
        - columns (list): A list of column names to format.
        - tableName (str): The name of the table to prefix the column names with.

        Returns:
        - formattedColumns (list): A list of formatted column names with the specified table name.
        """
        formattedColumns = []
        for column in columns:
            formattedColumns.append(f"{tableName}.{column}")
        return formattedColumns