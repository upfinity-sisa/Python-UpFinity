from mysql.connector import connect, Error
from dotenv import load_dotenv
import os

load_dotenv()

def Conectar_banco(instrucaoSQL, valores=None):
    config = {
      'user': os.getenv("USER_DB"),
      'password': os.getenv("PASSWORD_DB"),
      'host': os.getenv("HOST_DB"),
      'database': os.getenv("DATABASE_DB")
    }
    try:
        conn = connect(**config)
        cursor = conn.cursor()

        if valores:
            cursor.execute(instrucaoSQL, (valores,) if not isinstance(valores, tuple) else valores)
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
