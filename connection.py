import pymysql


class Connection:
    """
    Classe de conexão ao banco de dados. Originalmente é um banco de dados local.
    Adaptado para MySQL usando pymysql.
    """

    def __init__(self):
        server = "localhost"
        database = "iron_man"
        username = "iron_man"
        password = "iron_man"

        self.conexao = pymysql.connect(
            host=server,
            user=username,
            password=password,
            database=database,
            port=10010,
            cursorclass=pymysql.cursors.DictCursor,
        )
