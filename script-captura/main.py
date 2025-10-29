from dotenv import load_dotenv
from mysql.connector import connect, Error
import psutil as p
import os
import datetime
from time import sleep

load_dotenv()

config = {
  'user': os.getenv("USER_DB"), 
  'password': os.getenv("PASSWORD_DB"),
  'host': os.getenv("HOST_DB"),
  'database': os.getenv("DATABASE_DB"),
  'port': os.getenv("PORT_DB")
}

def carregar_parametros(idEmpresa, fkTipoComponente, fkTipoAlerta):
  try:
    db = connect(**config)
    if (db.is_connected):
      with db.cursor() as cursor:
        query = f"SELECT limiteMax FROM Parametro WHERE fkEmpresa = %s AND fkTipoComponente = %s AND fkTipoAlerta = %s"
        cursor.execute(query, (idEmpresa,fkTipoComponente,fkTipoAlerta,))
        resultado = cursor.fetchall()
        return resultado
    
      db.close()

  except Error as e:
    print(f"Error to connect with MySQL - {e}")

def inserir_metricas(idComponente, fkAtm, valor):
  try:
    db = connect(**config)
    if (db.is_connected):
      with db.cursor() as cursor:
        query = f"INSERT INTO Captura (fkComponente, fkAtm, valor, horario) VALUES (%s, %s, %s, now());"
        cursor.execute(query, (idComponente, fkAtm, valor,))
        db.commit()
      
      db.close()

  except Error as e:
    print(f"INSERIR METRICAS - Error to connect with MySQL - {e}")


def inserir_alerta(idTipoAlerta):
  try:
    db = connect(**config)
    if (db.is_connected):
      with db.cursor() as cursor:
        query = f"INSERT INTO Alerta (fkTipoAlerta, fkCaptura) VALUES (%s, (SELECT idCaptura FROM Captura ORDER BY idCaptura DESC LIMIT 1))"
        cursor.execute(query)
        db.commit()
      
      db.close()

  except Error as e:
    print(f"Error to connect with MySQL - {e}")

limite_critico_cpu = carregar_parametros(1, 1, 1)[0][0]
limite_importante_cpu = carregar_parametros(1, 1, 2)[0][0]

limite_critico_ram = carregar_parametros(1, 2, 1)[0][0]
limite_importante_ram = carregar_parametros(1, 2, 2)[0][0]

limite_critico_disco = carregar_parametros(1, 3, 1)[0][0]
limite_importante_disco = carregar_parametros(1, 3, 2)[0][0]

for i in range(20):
  porcentagem_cpu = p.cpu_percent(interval=1, percpu=False)
  porcentagem_ram = p.virtual_memory().percent
  porcentagem_disco = p.disk_usage("/").percent
  hora_registro = datetime.datetime.now().strftime("%H:%M:%S")
  
  os.system("clear")  
  print("""
  ██╗   ██╗██████╗ ███████╗██╗███╗   ██╗██╗████████╗██╗   ██╗
██║   ██║██╔══██╗██╔════╝██║████╗  ██║██║╚══██╔══╝╚██╗ ██╔╝
██║   ██║██████╔╝█████╗  ██║██╔██╗ ██║██║   ██║    ╚████╔╝ 
██║   ██║██╔═══╝ ██╔══╝  ██║██║╚██╗██║██║   ██║     ╚██╔╝  
╚██████╔╝██║     ██║     ██║██║ ╚████║██║   ██║      ██║   
 ╚═════╝ ╚═╝     ╚═╝     ╚═╝╚═╝  ╚═══╝╚═╝   ╚═╝      ╚═╝                                                   
          """)

  print("Registro inserido com sucesso!")
  print(f"Hora do registro: {hora_registro}")
  print(f"-="*20)

  inserir_metricas(1, 1, porcentagem_cpu)
  inserir_metricas(2, 1, porcentagem_ram)
  inserir_metricas(3, 1, porcentagem_disco)

  if porcentagem_cpu > limite_critico_cpu:
    print(f"Porcentagem de uso da CPU: {porcentagem_cpu}% - ALERTA CRITICO DE CPU!")
    inserir_alerta(1)
  elif porcentagem_cpu > limite_importante_cpu:
    print(f"Porcentagem de uso da CPU: {porcentagem_cpu}% - ALERTA MODERADO DE CPU!")
    inserir_alerta(2)
  else:
    print(f"Porcentagem de uso da CPU: {porcentagem_cpu}%")

  if porcentagem_ram > limite_critico_ram:
    print(f"Porcentagem de uso da RAM: {porcentagem_ram}% - ALERTA CRÍTICO DE MEMÓRIA RAM!")
    inserir_alerta(1)
  elif porcentagem_ram > limite_importante_ram:
    print(f"Porcentagem de uso da RAM: {porcentagem_ram}% - ALERTA MODERADO DE MEMÓRIA RAM!")
    inserir_alerta(2)
  else:
    print(f"Porcentagem de uso da RAM: {porcentagem_ram}%")
    
  if porcentagem_disco > limite_critico_disco:
    print(f"Porcentagem de uso do DISCO: {porcentagem_disco}% - ALERTA CRÍTICO DE USO DE DISCO!")
    inserir_alerta(1)
  elif porcentagem_disco > limite_importante_disco:
    print(f"Porcentagem de uso do DISCO: {porcentagem_disco}% - ALERTA MODERADO DE MEMÓRIA RAM!")
    inserir_alerta(2)
  else:
    print(f"Porcentagem de uso do DISCO: {porcentagem_disco}%")
    
  print(f"-="*20)
  sleep(1)
