from mysql.connector import connect, Error
from dotenv import load_dotenv
import os

load_dotenv()

def Fazer_consulta_banco(config):
    """
    Recebe um dicionário com:
        config = {
            "query": "SQL AQUI",
            "params": (param1, param2, ...)
        }
    """
    instrucaoSQL = config.get("query")
    valores = config.get("params", None)  # None caso não tenha parâmetros

    db_config = {
        'user': os.getenv("USER_DB"),
        'password': os.getenv("PASSWORD_DB"),
        'host': os.getenv("HOST_DB"),
        'database': os.getenv("DATABASE_DB")
    }

    try:
        conn = connect(**db_config)
        cursor = conn.cursor()

        if valores:
            # garante que valores é uma tupla
            cursor.execute(instrucaoSQL, valores if isinstance(valores, tuple) else (valores,))
        else:
            cursor.execute(instrucaoSQL)

        if instrucaoSQL.strip().lower().startswith("select"):
            resultado = cursor.fetchall()
            conn.close()
            return resultado
        else:
            conn.commit()
            linhas = cursor.rowcount
            conn.close()
            return linhas

    except Exception as e:
        print("Error to connect with MySQL -", e)
        return None
