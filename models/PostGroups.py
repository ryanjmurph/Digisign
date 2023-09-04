# Pius Gumo
# 14/08/2023
# Pivot model for linking posts to groups

from database.database import MYSQL

connection = MYSQL().get_connection()


class PostGroup:
    def __init__(self) -> None:
        pass

    def savePostToGroups(groups, post_id):
        for group in groups:
            with connection.cursor() as cursor:
                sql = "INSERT INTO post_group (post_id, group_id) VALUES (%s, %s)"
                cursor.execute(sql, (post_id, group))
                connection.commit()

    def deletePostFromGroups(post_id):
        with connection.cursor() as cursor:
            sql = "DELETE FROM post_group WHERE post_id=%s"
            cursor.execute(sql, (post_id))
            connection.commit()

    def getPostGroups(post_id):
        with connection.cursor() as cursor:
            sql = "SELECT group_id FROM post_group WHERE post_id=%s"
            cursor.execute(sql, (post_id))
            result = cursor.fetchall()
            return result
