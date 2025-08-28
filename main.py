import psutil as p
from mysql.connector import connect, Error


def conectar_banco():
    config = {
      'user': "upfinity_insert_select",
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
    print(dados['idAtm'])
    conn = conectar_banco()
    cursor = conn.cursor()
    query = """
    SELECT p.idParametro, c.funcaoMonitorada, c.unidadeMedida
    FROM Parametro as p
    JOIN Componente as c ON p.fkComponente = c.idComponente
    WHERE p.fkAtm = %s;
    """
    cursor.execute(query, (dados['idAtm'],))
    resultado = cursor.fetchall()
    
    cursor.close()
    conn.close()

    print("indo......")
    print(resultado)

    configuracoes = {}
    print("indo......")

    for id_param, tipo, unidade in resultado:
        if tipo not in configuracoes:
            configuracoes[tipo] = []
        configuracoes[tipo].append({'id_param': id_param, 'unidade': unidade})

    print("configura")
    print(configuracoes)
    return configuracoes


def validar_atm(dados):
    conn = conectar_banco()
    cursor = conn.cursor()

    query = "SELECT idAtm, hostname FROM Atm WHERE macAddress = %s AND ip = %s"
    cursor.execute(query, (dados['mac_address'], dados['ip_address']))
    resultado = cursor.fetchone()  

    cursor.close()
    conn.close()

    if resultado:
        atm_info = {
            'idAtm': resultado[0],
            'hostname': resultado[1],
            'mac_address': dados['mac_address'],
            'ip_address': dados['ip_address']
        }

        print(f"\n🔹 Monitoramento iniciado com sucesso! 🔹\n"
              f"   🖥️ ATM ID: {atm_info['idAtm']}\n"
              f"   💻 Hostname: {atm_info['hostname']}\n"
              f"   📡 MAC: {atm_info['mac_address']}\n"
              f"   🌐 IP: {atm_info['ip_address']}\n"
              f"✅ Seja bem-vindo(a)! ✅\n")

        return atm_info
    else:
        print(f"\n❌ Este ATM ({dados['mac_address']}) não foi encontrado no sistema. ❌\n")
        return None




def procurar_mac_address():
    print('mac.................')
    #Exemplo mais para frente será o mac da maquina
    atm_info = {
        "mac_address": "00:1A:2B:3C:4D:5E",
        "ip_address": "192.168.1.100"
    }
    return atm_info

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
            # db.commit()
    else:
        if alerta_aberto:
            cursor.execute("""
                UPDATE alerta
                SET data_fim = NOW(), status = 'fechado'
                WHERE id_alerta = %s
            """, (alerta_aberto[0],))
            # db.commit()

def inserir_registro(valor, fk_parametro):
    conn = conectar_banco()
    cursor = conn.cursor()
    query = "INSERT INTO Registro (valor, horario, fkParametro) VALUES (%s, NOW(), %s);"
    cursor.execute(query, (valor, fk_parametro))
    conn.commit()
    print(cursor.rowcount, "registro inserido")
    cursor.close()
    conn.close()


def coletar_dados():
    coletar_dados_continuo = True
    dados_mac_ip = procurar_mac_address()
    print(dados_mac_ip)
    print('dmi.................')
    atm_info = validar_atm(dados_mac_ip)
    print('dmiatm.................')
    print(atm_info)
    if atm_info == None:
        return
    informcao_parametros = buscar_informacoes_paremtros(atm_info)
    print("parametro.............")
    if atm_info == None or dados_mac_ip == None or informcao_parametros == None:
        return
    while coletar_dados_continuo:
        for tipo_componente, medidas in informcao_parametros.items():
            for medida in medidas:
                valor_dado = capturar_dado(tipo_componente)
                print(f"\nColeta: [{tipo_componente}] ({medida['unidade']}) → Valor: {valor_dado}")

                # Inserir no registro junto com o fkParametro
                inserir_registro(valor_dado, medida['id_param'])
                # limite_valor = procurar_limite ()
                # print(limite_valor)
                # if limite_valor: 
    
    


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
                coletar_dados() 
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