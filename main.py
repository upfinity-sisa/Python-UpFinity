import psutil as p
from mysql.connector import connect, Error


def conectar_banco():
    config = {
      'user': "upfinity_insert",
      'password': "Urubu100@",
      'host': 'localhost',
      'database': "upfinity"
    }
    try:
        return connect(**config)
    except Error as erro:
        print('Error to connect with MySQL -', erro) 
        

def capturar_dado(tipo):
    try:
        acoes = {
            "CPU_porcentagem": lambda: p.cpu_percent(),
            "CPU_frequencia": lambda: round(p.cpu_freq().current / 1000, 1),

            "RAM_disponivel": lambda: round(p.virtual_memory().available / (1024 ** 3), 2),
            "RAM_percentual": lambda: p.virtual_memory().percent,

            "DISK_disponivel": lambda: round(p.disk_usage('/').free / (1024 ** 3), 2),
            "DISK_percentual": lambda: p.disk_usage('/').percent,

            "REDE_recebida": lambda: round(p.net_io_counters().packets_recv / (1024 * 1024), 2),
            "REDE_enviada": lambda: round(p.net_io_counters().packets_sent / (1024 * 1024), 2),

            "PROCESSOS_ativos": lambda: sum(1 for p in p.process_iter(['status']) if p.info['status'] == 'running'),
            "PROCESSOS_desativado": lambda: sum(1 for p in p.process_iter(['status']) if p.info['status'] != 'running'),
        }

        funcao = acoes.get(tipo)   
        return funcao() if funcao else None

    except Exception as e:
        print(f"⚠️ Erro ao coletar valor para {tipo}: {e}")
        return None
    
def buscar_informacoes_paremtros(dados):
    conn = conectar_banco()
    cursor = conn.cursor()
    query = "SELECT c.funcaop, c.unidadeMedida, p.limite FROM Parametro as p JOIN Componente as c ON p.fkComponente = c.idComponente WHERE p.fkAtm;"
    cursor.execute(query, dados[0].fkAtm)
    resultado = cursor.fetchall() 
    cursor.close()
    conn.close()

    configuracoes = {}
    for tipo, unidade in resultado:
        if tipo not in configuracoes:
            configuracoes[tipo] = []
        configuracoes[tipo].append(unidade)
    return configuracoes

def validar_atm(dados):
    conn = conectar_banco()
    cursor = conn.cursor()
    query = "SELECT idAtm, macAdress, ip FROM Atm WHERE macAdress = %s AND ip = %s"
    cursor.execute(query, dados['mac_adress', dados['ip_adress']])
    resultado = cursor.fetchall() 
    cursor.close()
    conn.close()

    if resultado:
        print(f"\n✅ Monitoramento iniciado com sucesso para o ATM com o Mac Adress: {dados['mac_adress']} ✅\n")
        return resultado[0]
    else:
        print(f"\n⚠️ Este ATM ({dados['mac_adress']}) não foi encontrado no sistema. ⚠️\n")
        return None



def procurar_mac_adress():
    #Exemplo mais para frente será o mac da maquina
    dados_atm = {
        "mac_adress": "1A:1A:1A:1A:1A:1A",
        "ip_adress": "111.111.1.11"
    }
    return dados_atm

def procurar_limite(fkAtm, tipo_componente, unidade):
    conn = conectar_banco()
    cursor = conn.cursor()
    query = "SELECT idParametro, limite FROM parametrizacao WHERE fkAtm = %s AND tipo = %s AND unidadeMedida = %s"
    cursor.execute(query, fkAtm, tipo_componente, unidade)
    resultado = cursor.fetchall() 
    cursor.close()
    conn.close()
    return resultado[0]
def processar_leitura(componente_id, valor, limite):
    conn = conectar_banco()
    cursor = conn.cursor()
    query = """
        SELECT id_alerta, status
        FROM alerta
        WHERE componente_id = %s 
          AND tipo_alerta = 'umidade_alta'
          AND status = 'aberto'
        ORDER BY data_inicio DESC
        LIMIT 1
    """
    cursor.execute(query, componente_id)
    alerta_aberto = cursor.fetchone()
    cursor.close()
    conn.close()

    if valor > limite:
        if not alerta_aberto:
            cursor.execute("""
                INSERT INTO alerta (componente_id, tipo_alerta, data_inicio, status)
                VALUES (%s, 'umidade_alta', NOW(), 'aberto')
            """, (componente_id,))
            db.commit()
    else:
        if alerta_aberto:
            cursor.execute("""
                UPDATE alerta
                SET data_fim = NOW(), status = 'fechado'
                WHERE id_alerta = %s
            """, (alerta_aberto[0],))
            db.commit()

     

def coletar_dados():
    dados_mac_ip = procurar_mac_adress
    dados_atm = validar_atm(dados_mac_ip)
    if dados_atm == None:
        return
    informcao_parametros = buscar_informacoes_paremtros(dados_atm)
    if dados_atm and dados_mac_ip and informcao_parametros: 
        coletar_dados_continuo = True
        while coletar_dados_continuo:
            for tipo_componente, medidas in informcao_parametros.items():
                for unidade in medidas:
                    valor_dado = capturar_dado(tipo_componente)
                    print(f"\n Coleta: [{tipo_componente}] ({unidade}) → Valor: {valor_dado}")

                    limite_valor = procurar_limite ()

                    if limite_valor: 

    else:
        return 
    
    


def main():
    logo = """
    ║══════════════════════════════════════════════════════════════════════════════════╣                                                                 
    ║ ███    ███  ██████  ███    ██ ██ ████████  ██████  ██████  ██ ███    ██  ██████  ║
    ║ ████  ████ ██    ██ ████   ██ ██    ██    ██    ██ ██   ██ ██ ████   ██ ██       ║
    ║ ██ ████ ██ ██    ██ ██ ██  ██ ██    ██    ██    ██ ██████  ██ ██ ██  ██ ██   ███ ║
    ║ ██  ██  ██ ██    ██ ██  ██ ██ ██    ██    ██    ██ ██   ██ ██ ██  ██ ██ ██    ██ ║
    ║ ██      ██  ██████  ██   ████ ██    ██     ██████  ██   ██ ██ ██   ████  ██████  ║
    ║                                                                                  ║
    ║             ██    ██ ██████  ███████ ██ ███    ██ ██ ████████ ██    ██           ║
    ║             ██    ██ ██   ██ ██      ██ ████   ██ ██    ██     ██  ██            ║
    ║             ██    ██ ██████  █████   ██ ██ ██  ██ ██    ██      ████             ║
    ║             ██    ██ ██      ██      ██ ██  ██ ██ ██    ██       ██              ║
    ║              ██████  ██      ██      ██ ██   ████ ██    ██       ██              ║
    ║                                                                                  ║
    ║══════════════════════════════════════════════════════════════════════════════════╣
    ║                     SISTEMA DE MONITORAMENTO DA UPFINITY                         ║
    ║══════════════════════════════════════════════════════════════════════════════════╣                                                                                                                
        [1] ▶ Iniciar Monitoramento\n
        [2] ▶ Sair       
    ╚══════════════════════════════════════════════════════════════════════════════════╝  
    """
    menu_resumido = """
        [1] ▶ Iniciar Monitoramento
        [2] ▶ Sair
    """
    saida = """
    ╔════════════════════════════════════════════════════╗
    ║              Encerrando o Upfinity System          ║
    ║════════════════════════════════════════════════════╣
    ║   Sessão finalizada com sucesso.                   ║
    ║   Todos os serviços foram encerrados.              ║
    ║   Até a próxima utilização.                        ║
    ╚════════════════════════════════════════════════════╝
    """

    print(logo) 

    while True:
        try:
            resposta_usuario = int(input("  Escolha uma opção: "))
            if resposta_usuario == 1:
                procurar_mac_adress() 
                break  
            elif resposta_usuario == 2:
                print(saida)
                break
            else:
                print("Opção inválida! Tente novamente.")
                print(menu_resumido)  
        except KeyboardInterrupt:
            print("\n Monitoramento Interrompido! ")
            print(saida)
            break
        except ValueError:
            print("Por favor, digite um número válido.")
            print(menu_resumido)  

main()