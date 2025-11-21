from dotenv import load_dotenv
from mysql.connector import connect, Error
import psutil as p
import os
import datetime
from time import sleep
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

load_dotenv()

config = {
  'user': os.getenv("USER_DB"), 
  'password': os.getenv("PASSWORD_DB"),
  'host': os.getenv("HOST_DB"),
  'database': os.getenv("DATABASE_DB"),
  'port': os.getenv("PORT_DB")
}

def carregar_parametros(idEmpresa, fkTipoComponente, fkTipoAlerta):
    db = None
    try:
        db = connect(**config)
        if db.is_connected():
            with db.cursor() as cursor:
                query = f"SELECT limiteMax FROM Parametro WHERE fkEmpresa = %s AND fkTipoComponente = %s AND fkTipoAlerta = %s"
                cursor.execute(query, (idEmpresa, fkTipoComponente, fkTipoAlerta,))
                resultado = cursor.fetchall()
                return resultado
    except Error as e:
        print(f"Error to connect with MySQL - {e}")
    finally:
        if db and db.is_connected():
            db.close()
            
def inserir_metricas(idComponente, fkAtm, valor):
    try:
        db = connect(**config)
        if db.is_connected():
            with db.cursor() as cursor:
                query = "INSERT INTO Captura (fkComponente, fkAtm, valor, horario) VALUES (%s, %s, %s, now())"
                cursor.execute(query, (idComponente, fkAtm, valor))
                db.commit()
                
                id_gerado = cursor.lastrowid 
                return id_gerado
                
    except Error as e:
        print(f"INSERIR METRICAS - Erro: {e}")
        return None
    finally:
        if 'db' in locals() and db.is_connected():
            db.close()
            
def inserir_alerta(idTipoAlerta, idCapturaEspecifica):
    try:
        db = connect(**config)
        if db.is_connected():
            with db.cursor() as cursor:
                query = "INSERT INTO Alerta (fkTipoAlerta, fkCaptura) VALUES (%s, %s)"
                cursor.execute(query, (idTipoAlerta, idCapturaEspecifica))
                db.commit()
                
    except Error as e:
        print(f"Erro ao inserir alerta: {e}")
    finally:
        if 'db' in locals() and db.is_connected():
            db.close()

def capturar_ipv4():
  interfaces = p.net_if_addrs()
  for nome, enderecos in interfaces.items():
    for e in enderecos:
      if e.family == 2 and e.address != "127.0.0.1":
        return e.address
  return None
  
def buscar_dados_atm(ipv4):
    try:
        db = connect(**config)
        if (db.is_connected):
            with db.cursor() as cursor:
                query = "SELECT idAtm, fkEmpresa FROM Atm WHERE IP = %s"
                cursor.execute(query, (ipv4,))
                resulta = cursor.fetchone()
                return resulta 
        
    except Error as e:
        print(f"Buscar dados do ATM - Error to connect with MySQL - {e}")
    finally:
        if 'db' in locals() and db.is_connected():
            db.close()
            
def verificar_cadastrar_componente(idComponente, fkAtm, fkTipoComponente):
  try:
    db = connect(**config)
    if (db.is_connected):
      with db.cursor() as cursor:
        query = f"SELECT idComponente FROM Componente WHERE idComponente = %s AND fkAtm = %s AND fkTipoComponente = %s"
        cursor.execute(query, (idComponente, fkAtm, fkTipoComponente))
        result = cursor.fetchone()

        if result:
          return result[0]
        
        insert = f"INSERT INTO Componente (idComponente, fkAtm, fkTipoComponente) VALUES (%s,%s,%s)"
        cursor.execute(insert, (idComponente,fkAtm, fkTipoComponente))
        db.commit()
        return idComponente
  
  except Error as e:
    print(f"Erro em verificar ou cadastrar o componente: {e}")

def atualizar_status(idAtm, status):
  try:
    db = connect(**config)
    if (db.is_connected):
      with db.cursor() as cursor:
        query = f"UPDATE Atm SET statusMonitoramento = %s WHERE idAtm = %s"
        cursor.execute(query, (status, idAtm))
        db.commit()
  except Error as e:
    print(f"Erro ao atualizar status do atm: {e}")

def verificar_alerta_existente(idAtm, idComponente, idTipoAlerta):
    try:
        db = connect(**config)
        if db.is_connected():
            with db.cursor() as cursor:
                query = """
                    SELECT a.idAlerta 
                    FROM Alerta a
                    JOIN Captura c ON a.fkCaptura = c.idCaptura
                    WHERE c.fkAtm = %s 
                    AND c.fkComponente = %s 
                    AND a.fkTipoAlerta = %s 
                    AND a.statusAlerta = 1
                """
                cursor.execute(query, (idAtm, idComponente, idTipoAlerta))
                resultado = cursor.fetchone()
                return True if resultado else False
    except Error as e:
        print(f"Erro ao verificar alerta existente: {e}")
        return False
    finally:
        if 'db' in locals() and db.is_connected():
            db.close()

def buscar_canal(idEmpresa):
  try:
    db = connect(**config)
    if (db.is_connected):
      with db.cursor() as cursor:
        query = f"SELECT idSlack FROM Empresa WHERE idEmpresa = %s"
        cursor.execute(query, (idEmpresa,))
        resultado = cursor.fetchone()
        return resultado[0] if resultado else None

  except Error as e:
    print(f"Error to connect with MySQL - {e}")

slack_token = os.environ["SLACK_BOT_TOKEN"]
client = WebClient(token=slack_token)

ipv4 = capturar_ipv4()

dadosAtm = buscar_dados_atm(ipv4)

idAtm = dadosAtm[0]
idEmpresa = dadosAtm[1]

limite_critico_cpu = carregar_parametros(idEmpresa, 1, 1)[0][0]
limite_moderado_cpu = carregar_parametros(idEmpresa, 1, 2)[0][0]

limite_critico_ram = carregar_parametros(idEmpresa, 2, 1)[0][0]
limite_moderado_ram = carregar_parametros(idEmpresa, 2, 2)[0][0]

limite_critico_disco = carregar_parametros(idEmpresa, 3, 1)[0][0]
limite_moderado_disco = carregar_parametros(idEmpresa, 3, 2)[0][0]

if not idAtm:
  print(f"Nenhum ATM foi encontrado com esse ipv4 - {ipv4}")
  print("Encerrando...")
  exit()

id_cpu = verificar_cadastrar_componente(1 , idAtm, 1)
id_ram = verificar_cadastrar_componente(2, idAtm, 2)
id_disco = verificar_cadastrar_componente(3, idAtm, 3)

limite_critico_cpu = carregar_parametros(idEmpresa, 1, 1)[0][0]
limite_importante_cpu = carregar_parametros(idEmpresa, 1, 2)[0][0]

limite_critico_ram = carregar_parametros(idEmpresa, 2, 1)[0][0]
limite_importante_ram = carregar_parametros(idEmpresa, 2, 2)[0][0]

limite_critico_disco = carregar_parametros(idEmpresa, 3, 1)[0][0]
limite_importante_disco = carregar_parametros(idEmpresa, 3, 2)[0][0]

idCanalSlack = buscar_canal(idEmpresa)
print(f"CANAL SLACK: {idCanalSlack}")

atualizar_status(idAtm, 0)


print("Componentes do seu ATM foram cadastrados com sucesso!")

for i in range(20):
  porcentagem_cpu = p.cpu_percent(interval=1, percpu=False)
  porcentagem_ram = p.virtual_memory().percent
  porcentagem_disco = p.disk_usage("/").percent
  hora_registro = datetime.datetime.now().strftime("%H:%M:%S")
  
  status_cpu = 0
  status_ram = 0
  status_disco = 0
  
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

  id_captura_cpu = inserir_metricas(id_cpu, idAtm, porcentagem_cpu)
  id_captura_ram = inserir_metricas(id_ram, idAtm, porcentagem_ram)
  id_captura_disco = inserir_metricas(id_disco, idAtm, porcentagem_disco)

  if porcentagem_cpu > limite_critico_cpu:
    print(f"Porcentagem de uso da CPU: {porcentagem_cpu}% - ALERTA CRITICO DE CPU!")
    status_cpu = 1
    
    if not verificar_alerta_existente(idAtm, id_cpu, 1):
      inserir_alerta(1, id_captura_cpu)
      atualizar_status(idAtm, 1)
      client.chat_postMessage(channel=idCanalSlack, text=f"🚨 ALERTA CRÍTICO: CPU do ATM {idAtm} em {porcentagem_cpu}%!")
    
  elif porcentagem_cpu > limite_moderado_cpu:
    print(f"Porcentagem de uso da CPU: {porcentagem_cpu}% - ALERTA MODERADO DE CPU!")
    status_cpu = 2
    
    if not verificar_alerta_existente(idAtm, id_cpu, 2):
      inserir_alerta(2, id_captura_cpu)
      atualizar_status(idAtm, 2)
      client.chat_postMessage(channel=idCanalSlack, text=f"⚠️ ALERTA MODERADO: CPU do ATM {idAtm} em {porcentagem_cpu}%!")
      
  else:
    print(f"Porcentagem de uso da CPU: {porcentagem_cpu}%")

  if porcentagem_ram > limite_critico_ram:
    print(f"Porcentagem de uso da RAM: {porcentagem_ram}% - ALERTA CRÍTICO DE MEMÓRIA RAM!")
    status_ram = 1
    
    if not verificar_alerta_existente(idAtm, id_ram, 1):
      inserir_alerta(1, id_captura_ram)
      atualizar_status(idAtm, 1)
      client.chat_postMessage(channel=idCanalSlack, text=f"🚨 ALERTA CRÍTICO: RAM do ATM {idAtm} em {porcentagem_ram}%!")
      
  elif porcentagem_ram > limite_moderado_ram:
    print(f"Porcentagem de uso da RAM: {porcentagem_ram}% - ALERTA MODERADO DE MEMÓRIA RAM!")
    status_ram = 2
    
    if not verificar_alerta_existente(idAtm, id_ram, 2):
      inserir_alerta(2, id_captura_ram)
      atualizar_status(idAtm, 2)
      client.chat_postMessage(channel=idCanalSlack, text=f"⚠️ ALERTA MODERADO: RAM do ATM {idAtm} em {porcentagem_ram}%!")

  else:
    print(f"Porcentagem de uso da RAM: {porcentagem_ram}%")
    
  if porcentagem_disco > limite_critico_disco:
    print(f"Porcentagem de uso do DISCO: {porcentagem_disco}% - ALERTA CRÍTICO DE USO DE DISCO!")
    status_disco = 1
    
    if not verificar_alerta_existente(idAtm, id_disco, 1):
      inserir_alerta(1, id_captura_disco)
      atualizar_status(idAtm, 1)
      client.chat_postMessage(channel=idCanalSlack, text=f"🚨 ALERTA CRÍTICO: DISCO do ATM {idAtm} em {porcentagem_disco}%!")

  elif porcentagem_disco > limite_moderado_disco:
    print(f"Porcentagem de uso do DISCO: {porcentagem_disco}% - ALERTA MODERADO DE DISCO!")
    status_disco = 2
    
    if not verificar_alerta_existente(idAtm, id_disco, 2):
      inserir_alerta(2, id_captura_disco)
      atualizar_status(idAtm, 2)
      client.chat_postMessage(channel=idCanalSlack, text=f"⚠️ ALERTA MODERADO: DISCO do ATM {idAtm} em {porcentagem_disco}%!")
      
  else:
    print(f"Porcentagem de uso do DISCO: {porcentagem_disco}%")
    
  status_final_atm = 0

  if status_cpu == 1 or status_ram == 1 or status_disco == 1:
    status_final_atm = 1
    
  elif status_cpu == 2 or status_ram == 2 or status_disco == 2:
    status_final_atm = 2
   
  atualizar_status(idAtm, status_final_atm)  
    
  print(f"-="*20)
  sleep(1)
