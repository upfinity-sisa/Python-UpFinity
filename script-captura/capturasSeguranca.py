import psutil
import mysql.connector
import time
import re
import os
import datetime
import hashlib
from dotenv import load_dotenv
load_dotenv()

con = {
  'user': os.getenv("USER_DB"), 
  'password': os.getenv("PASSWORD_DB"),
  'host': os.getenv("HOST_DB"),
  'database': os.getenv("DATABASE_DB"),
  'port': os.getenv("PORT_DB")
}


db = mysql.connector.connect(**con)
cursor = db.cursor()

#=====================LOGINS==================================

def salvarNoBancoLogin(horario, IPinvasor):
    sql_insert = "insert into Invasao (horarioCaptura, horarioInvasao, IP, fkSeguranca) values (now(), %s, %s, 3);"
    valores = (horario, IPinvasor)
    cursor.execute(sql_insert, valores)
    db.commit()

pattern = re.compile(r"pam_unix\(.*auth\): authentication failure")
def abrirLogFiles(log_file, one_week_ago):
    with open(log_file, "r", errors="ignore") as f:
        for line in f:
            if pattern.search(line):
                # extrai rhost=IP
                match = re.search(r"rhost=([\d\.]+)", line)
                if not match:
                    continue
                ip = match.group(1).strip()
                if not ip:
                    continue

                # extrai a data (primeira palavra da linha, assume ISO)
                date_str = line.split()[0]
                try:
                    timestamp = datetime.datetime.fromisoformat(date_str)
                    mysql_datetime = timestamp.strftime("%Y-%m-%d %H:%M:%S")
                except ValueError:
                    # pula linhas com data inválida
                    continue

                if timestamp >= one_week_ago:
                    # imprime apenas data e IP
                    salvarNoBancoLogin(mysql_datetime, ip)
                    print(f"Horário: {mysql_datetime} || IP do invasor: {ip}")

def rodarLogins():
    log_file = "/var/log/auth.log"
    log_file1 = "/var/log/auth.log.1"

    TZ = datetime.timezone(datetime.timedelta(hours=-3))
    one_week_ago = datetime.datetime.now(TZ) - datetime.timedelta(days=7)

    abrirLogFiles(log_file, one_week_ago)
    abrirLogFiles(log_file1, one_week_ago)

    
# rodarLogins()
rodarLogins()

#==================CAPTURA DE ARQUIVOS======================

vt_arqs = [
    "/etc/hosts",
    "/etc/systemd/resolved.conf",
    "/run/systemd/resolve/resolv.conf",
    "/etc/resolv.conf",
    "/bin/bash",
    "/bin/sh",
    "/usr/bin/sudo",
    "/usr/bin/passwd",
    "/usr/bin/chsh",
    "/usr/bin/chmod",
    "/usr/bin/chown",
    "/usr/bin/ssh",
    "/usr/bin/wget",
    "/usr/bin/curl",
    "/usr/bin/scp",
    "/usr/bin/sftp",
    "/usr/bin/ls",
    "/usr/bin/ps",
    "/usr/bin/top",
    "/usr/bin/find",
    "/home/breno-upfinity/seg/arq.txt",
    "/lib/x86_64-linux-gnu/libc.so.6",
    "/lib/x86_64-linux-gnu/ld-linux-x86-64.so.2"
]

def capturar_hash(caminho):
    h = hashlib.sha256()
    with open(caminho, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def salvarItensSalvosHash(nome, arqHash):
    cursor.execute("select salvamento from Seguranca where fkAtm = 1 and categoria = 'arquivo';")
    resultado = cursor.fetchall()
    if resultado[0][0] == 0:
        sql_insert = "insert into ItemSalvo (categoria, conteudo01, conteudo02, fkSeguranca) values ('arquivo', %s, %s, 1);"
        valores = (nome, arqHash)
        cursor.execute(sql_insert, valores)
        db.commit()

def salvarNoBancoHash(nome, arqHash, horario):
    cursor.execute("select * from ItemSalvo where categoria = 'arquivo' and fkSeguranca = 1;")
    hashs = cursor.fetchall()
    alerta = None
    possuiAlertalocal = 0;
    sql_insert = "select possuiAlerta from ArquivoCritico where fkSeguranca = 1 and nome = %s and idArquivoCritico = (select max(idArquivoCritico) from ArquivoCritico where fkSeguranca = 1 and nome = %s);"
    valores = (nome, nome)
    cursor.execute(sql_insert, valores)
    possuiAlertaBanco = cursor.fetchall()
    if len(possuiAlertaBanco) != 0:
        if possuiAlertaBanco[0][0] == 1:
            possuiAlertalocal = 1
    if possuiAlertalocal == 0:
        for i in range(len(hashs)):
            if hashs[i][2] == nome:
                if hashs[i][3] != arqHash:

                    possuiAlertalocal = 1;
                    sql_insert = "insert into AlertaSeguranca (categoria, mensagem, horario) values (%s, %s, %s);"
                    valores = ("arquivo", f"O hash do arquivo {nome} foi alterado", horario)
                    cursor.execute(sql_insert, valores)
                    db.commit()
                    alerta = cursor.lastrowid
    sql_insert = "insert into ArquivoCritico (nome, hashArqCritico, fkSeguranca, fkAlertaSeguranca, horario, possuiAlerta) values (%s, %s, 1, %s, %s, %s);"
    valores = (nome, arqHash, alerta, horario, possuiAlertalocal)
    cursor.execute(sql_insert, valores)
    db.commit()
    salvarItensSalvosHash(nome, arqHash)

horario_mysql = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
for i in range(len(vt_arqs)):
        salvarNoBancoHash(vt_arqs[i], capturar_hash(vt_arqs[i]), horario_mysql)
        print("Captura HASH realizada")


sql_insert = "update Seguranca set salvamento = 1 where fkAtm = 1 and categoria = 'arquivo';"
cursor.execute(sql_insert)
db.commit()

def rodarHash():
    horario_mysql = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for i in range(len(vt_arqs)):
        salvarNoBancoHash(vt_arqs[i], capturar_hash(vt_arqs[i]), horario_mysql)
        print("Captura HASH realizada")



#========================CAPTURA DE CONEXOES=========================
def salvarItensSalvosConexoes(porta, IPremoto):
    cursor.execute("select salvamento from Seguranca where fkAtm = 1 and categoria = 'conexao';")
    resultado = cursor.fetchall()
    if resultado[0][0] == 0:
        sql_insert = "insert into ItemSalvo (categoria, conteudo01, conteudo02, fkSeguranca) values ('conexao', %s, %s, 2);"
        valores = (porta, IPremoto)
        cursor.execute(sql_insert, valores)
        db.commit()

def salvarNoBancoConexoes(porta, IPremoto, ultimoHorario):
    salvarItensSalvosConexoes(porta, IPremoto)
    cursor.execute("select * from ItemSalvo where categoria = 'conexao' and fkSeguranca = 2;")
    conexoes = cursor.fetchall()
    BooleanAlerta = 1
    alerta = None
    possuiAlertaLocal = 0
    sql_insert = "select possuiAlerta from ConexaoAberta where fkSeguranca = 2 and portaLocal = %s and idConexaoAberta = (select max(idConexaoAberta) from ConexaoAberta where fkSeguranca = 2 and portaLocal = %s);"
    valores = (porta, porta)
    cursor.execute(sql_insert, valores)
    possuiAlertaBanco = cursor.fetchall()
    for i in range(len(conexoes)):
        if conexoes[i][2] == str(porta):
            BooleanAlerta = 0 #Descobrindo se a conexao está na lista
    if BooleanAlerta == 1: #Se a conexão não estiver na lista
        if len(possuiAlertaBanco) != 0: 
            if possuiAlertaBanco[0][0] == 1: #Caso ele já possua um alerta -> seta outro
                sql_insert = "select idConexaoAberta from ConexaoAberta where horario = %s and portaLocal = %s and fkSeguranca = 2;"
                valores = (ultimoHorario ,str(porta))
                cursor.execute(sql_insert, valores)
                resultado = cursor.fetchall()
                if len(resultado) > 0:
                    possuiAlertaLocal = 1
        if possuiAlertaLocal == 0: # caso não tenha setado nenhum alerta -> Verifica se pode enviar um alerta novo
            sql_insert = "insert into AlertaSeguranca (categoria, mensagem, horario) values (%s, %s, now());"
            valores = ("conexao", f"Conexão suspeita identificada na porta: {porta}")
            cursor.execute(sql_insert, valores)
            db.commit()
            alerta = cursor.lastrowid
            possuiAlertaLocal = 1
    sql_insert = "insert into ConexaoAberta (portaLocal, IPremoto, fkSeguranca, fkAlertaSeguranca, horario, possuiAlerta) values (%s, %s, 2, %s, now(), %s);"
    valores = (porta, IPremoto, alerta, possuiAlertaLocal)
    cursor.execute(sql_insert, valores)
    db.commit()


cursor.execute("select max(horario) from ConexaoAberta where fkSeguranca = 2")
ultimoHorario = cursor.fetchall()[0][0]
print(ultimoHorario)
conexoes = psutil.net_connections(kind="inet")
for conn in conexoes:
    if conn.raddr:
        porta_local = conn.laddr.port
        ip_remoto = conn.raddr.ip
        salvarNoBancoConexoes(porta_local, ip_remoto, ultimoHorario)
        print("Captura CONEXÃO realizada")

sql_insert = "update Seguranca set salvamento = (datediff(now(), criadoEm) > 7) where fkAtm = 1 and categoria = 'conexao';"
cursor.execute(sql_insert)
db.commit()

def rodarConexoes():
    cursor.execute("select max(horario) from ConexaoAberta where fkSeguranca = 2")
    ultimoHorario = cursor.fetchall()[0][0]
    conexoes = psutil.net_connections(kind="inet")
    for conn in conexoes:
        if conn.raddr:
            porta_local = conn.laddr.port
            ip_remoto = conn.raddr.ip
            salvarNoBancoConexoes(porta_local, ip_remoto, ultimoHorario)
            print("Captura CONEXÃO realizada")


def rodarTudo():
    time.sleep(2)
    rodarHash()
    rodarLogins()
    rodarConexoes()
    print("rodou")


while True:
    rodarTudo()