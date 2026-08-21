import os
import mysql.connector


def get_db():

    return mysql.connector.connect(
        host=os.getenv(
            "MYSQL_HOST",
            "mysql"
        ),

        port=int(
            os.getenv(
                "MYSQL_PORT",
                3306
            )
        ),

        user=os.getenv(
            "MYSQL_USER",
            "root"
        ),

        password=os.getenv(
            "MYSQL_ROOT_PASSWORD"
        ),

        database=os.getenv(
            "MYSQL_DATABASE",
            "gitdoctor"
        )
    )