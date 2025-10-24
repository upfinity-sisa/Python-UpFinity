from dotenv import load_dotenv
from mysql.connector import connect, Error
import psutil as p
import os
import datetime
from time import sleep

load_dotenv()

def inserir_metricas(idComponente, valor):
  config = {       
    'user': os.getenv("USER_DB"),
    'password': os.getenv("PASSWORD_DB"),
    'host': os.getenv("HOST_DB"),
    'database': os.getenv("DATABASE_DB")
    }
  
  try:
    db = connect(**config)
    if (db.is_connected):
      with db.cursor() as cursor:
        query = f"INSERT INTO captura (idComponente, valor, dtCaptura) VALUES ({idComponente}, {valor}, now());"
        cursor.execute(query)
        db.commit()
      
      cursor.close()
      db.close()

  except Error as e:
    print(f"Error to connect with MySQL - {e}")


def inserir_alerta(idTipoAlerta):
  config = {
  'user': os.getenv("USER_DB"),
  'password': os.getenv("PASSWORD_DB"),
  'host': os.getenv("HOST_DB"),
  'database': os.getenv("DATABASE_DB")
  }

  try:
    db = connect(**config)
    if (db.is_connected):
      with db.cursor() as cursor:
        query = f"INSERT INTO alerta (idCaptura, idTPalerta) VALUES ((select idCaptura from captura order by idCaptura desc limit 1), {idTipoAlerta});"
        cursor.execute(query)
        db.commit()
      
      cursor.close()
      db.close()

  except Error as e:
    print(f"Error to connect with MySQL - {e}")

for i in range(20):
  porcentagem_cpu = p.cpu_percent(interval=1, percpu=False)
  porcentagem_ram = p.virtual_memory().percent
  porcentagem_disco = p.disk_usage("/").percent
  mac_address = p.net_if_addrs().get('wlo1')[2][1]
  hora_registro = datetime.datetime.now().strftime("%H:%M:%S")
  
  os.system("clear")  
  print("""
      ███████    ███████████  ██████████ ███████████      ███████    ██████   █████
    ███▒▒▒▒▒███ ▒▒███▒▒▒▒▒███▒▒███▒▒▒▒▒█▒▒███▒▒▒▒▒███   ███▒▒▒▒▒███ ▒▒██████ ▒▒███ 
  ███     ▒▒███ ▒███    ▒███ ▒███  █ ▒  ▒███    ▒███  ███     ▒▒███ ▒███▒███ ▒███ 
  ▒███      ▒███ ▒██████████  ▒██████    ▒██████████  ▒███      ▒███ ▒███▒▒███▒███ 
  ▒███      ▒███ ▒███▒▒▒▒▒███ ▒███▒▒█    ▒███▒▒▒▒▒███ ▒███      ▒███ ▒███ ▒▒██████ 
  ▒▒███     ███  ▒███    ▒███ ▒███ ▒   █ ▒███    ▒███ ▒▒███     ███  ▒███  ▒▒█████ 
  ▒▒▒███████▒   ███████████  ██████████ █████   █████ ▒▒▒███████▒   █████  ▒▒█████
    ▒▒▒▒▒▒▒    ▒▒▒▒▒▒▒▒▒▒▒  ▒▒▒▒▒▒▒▒▒▒ ▒▒▒▒▒   ▒▒▒▒▒    ▒▒▒▒▒▒▒    ▒▒▒▒▒    ▒▒▒▒▒     
  
          """)

  print("Registro inserido com sucesso!")
  print(f"Hora do registro: {hora_registro}")
  print(f"-="*20)

  if porcentagem_cpu > 90.0:
    print(f"Porcentagem de uso da CPU: {porcentagem_cpu}% - ALERTA CRITICO DE CPU!")
    inserir_metricas(1, porcentagem_cpu)
    inserir_alerta(1)
  elif porcentagem_cpu > 75.0:
    print(f"Porcentagem de uso da CPU: {porcentagem_cpu}% - ALERTA MODERADO DE CPU!")
    inserir_metricas(1, porcentagem_cpu)
    inserir_alerta(2)
  else:
    print(f"Porcentagem de uso da CPU: {porcentagem_cpu}%")
    inserir_metricas(1, porcentagem_cpu)

  if porcentagem_ram > 95.0:
    print(f"Porcentagem de uso da RAM: {porcentagem_ram}% - ALERTA CRÍTICO DE MEMÓRIA RAM!")
    inserir_metricas(2, porcentagem_ram)
    inserir_alerta(1)
  elif porcentagem_ram > 80.0:
    print(f"Porcentagem de uso da RAM: {porcentagem_ram}% - ALERTA MODERADO DE MEMÓRIA RAM!")
    inserir_metricas(2, porcentagem_ram)
    inserir_alerta(2)
  else:
    print(f"Porcentagem de uso da RAM: {porcentagem_ram}%")
    inserir_metricas(2, porcentagem_ram)
  
  if porcentagem_disco > 95.0:
    print(f"Porcentagem de uso do DISCO: {porcentagem_disco}% - ALERTA CRÍTICO DE USO DE DISCO!")
    inserir_metricas(3, porcentagem_disco)
    inserir_alerta(1)
  elif porcentagem_disco > 85.0:
    print(f"Porcentagem de uso do DISCO: {porcentagem_disco}% - ALERTA MODERADO DE MEMÓRIA RAM!")
    inserir_metricas(3, porcentagem_disco)
    inserir_alerta(2)
  else:
    print(f"Porcentagem de uso do DISCO: {porcentagem_disco}%")
    inserir_metricas(3, porcentagem_disco)
  
  print(f"Mac adress: {mac_address}")
  print(f"-="*20)
  sleep(1)
