class JoinRelationship:

    def withRelation(self,eagerRelationship,fromTable=None,fromTableForeignKey=None):
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
        formattedColumns = []
        for column in columns:
            formattedColumns.append(f"{tableName}.{column}")
        return formattedColumns