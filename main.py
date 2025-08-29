import psutil as p
from utils.Database import Conectar_banco 
import time

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

atm_info = set()

def capturar_dado(tipo):
    global acoes
    try:
        funcao = acoes.get(tipo)   
        return funcao() if funcao else None

    except Exception as e:
        print(f"⚠️ Erro ao coletar valor para {tipo}: {e}")
        return None
    
def buscar_informacoes_paremtros(dados):
    resultado = Conectar_banco("""
    SELECT p.idParametro, c.funcaoMonitorada, c.unidadeMedida, p.limite
    FROM Parametro as p
    JOIN Componente as c ON p.fkComponente = c.idComponente
    WHERE p.fkAtm = %s;
    """, dados.get('idAtm'))

    configuracoes = {}

    for id_param, tipo, unidade, limite in resultado:
        if tipo not in configuracoes:
            configuracoes[tipo] = []
        configuracoes[tipo].append({
            'id_param': id_param, 
            'unidade': unidade, 
            'limite': limite
        })
    return configuracoes


def validar_atm(dados):
    resultado = Conectar_banco("SELECT idAtm, hostname FROM Atm WHERE macAddress = %s AND ip = %s",
                                (dados.get('mac_address'), dados.get('ip_address')))
    global atm_info
    print(resultado)
    if resultado:
        atm_info = {
            'idAtm': resultado[0][0],
            'hostname': resultado[0][1],
            'mac_address': dados['mac_address'],
            'ip_address': dados['ip_address']
        }
        print('╔════════════════════════════════════════════════════╗')
        print(f"   🔹 Monitoramento iniciado com sucesso! 🔹\n"
              f"   🖥️ ATM ID: {atm_info['idAtm']}\n"
              f"   💻 Hostname: {atm_info['hostname']}\n"
              f"   📡 MAC: {atm_info['mac_address']}\n"
              f"   🌐 IP: {atm_info['ip_address']}\n"
              f"   ✅ Seja bem-vindo(a)! ✅\n")
        print('╚════════════════════════════════════════════════════╝')
        return atm_info
    else:
        print(f"\n❌ Este ATM ({dados['mac_address']}) não foi encontrado no sistema. ❌\n")
        return None




def procurar_mac_address():
    atm_info = {
        "mac_address": "00:1A:2B:3C:4D:5E",
        "ip_address": "192.168.1.100"
    }
    return atm_info

def procurar_limite(fkAtm, tipo_componente, unidade):
    resultado = Conectar_banco("SELECT idParametro, limite FROM parametrizacao WHERE fkAtm = %s AND tipo = %s AND unidadeMedida = %s", 
                               fkAtm, tipo_componente, unidade)
    return resultado[0]

def inserir_registro(valor, fk_parametro):
    resultado = Conectar_banco("INSERT INTO Registro (valor, horario, fkParametro) VALUES (%s, NOW(), %s);",
                               (valor, fk_parametro))
    if resultado >= 0: 
        print(resultado, "registro inserido")
    else : 
        None

def processar_leitura_com_alerta(fkParametro, tipo, valor, limite):
    if valor >= limite * 1.2:
        nivel = "Critico"
    elif valor >= limite:
        nivel = "Alerta"
    elif valor >= limite * 0.9:
        nivel = "Atenção"
    else:
        nivel = None

    alerta_aberto = Conectar_banco("""
        SELECT idAlerta, nivel
        FROM Alerta
        WHERE fkParametro = %s AND tipoAlerta = %s AND dataHoraFinal IS NULL
        ORDER BY dataHoraInicio DESC
        LIMIT 1
    """, (fkParametro, tipo))

    alerta_aberto = alerta_aberto[0] if alerta_aberto else None

    if nivel:
        if not alerta_aberto:
            Conectar_banco("""
                INSERT INTO Alerta (fkParametro, tipoAlerta, nivel, dataHoraInicio)
                VALUES (%s, %s, %s, NOW())
            """, (fkParametro, tipo, nivel))
            print(f"  Alerta ABERTO para {tipo} (nível: {nivel})")

        else:
            if alerta_aberto[1] != nivel:
                Conectar_banco("UPDATE Alerta SET dataHoraFinal = NOW() WHERE idAlerta = %s", alerta_aberto[0])
                Conectar_banco("""
                    INSERT INTO Alerta (fkParametro, tipoAlerta, nivel, dataHoraInicio)
                    VALUES (%s, %s, %s, NOW())
                """, (fkParametro, tipo, nivel))
                print(f"  Alerta atualizado criando NOVO registro para {tipo} (nível: {nivel})")

    else:
        if alerta_aberto:
            Conectar_banco("UPDATE Alerta SET dataHoraFinal = NOW() WHERE idAlerta = %s", alerta_aberto[0])
            print(f"  Alerta FECHADO para {tipo}")

def coletar_dados():
    coletar_dados_continuo = True

    dados_mac_ip = procurar_mac_address()
    atm_info = validar_atm(dados_mac_ip)

    if atm_info == None:
        return
    informcao_parametros = buscar_informacoes_paremtros(atm_info)

    if atm_info == None or dados_mac_ip == None or informcao_parametros == None:
        return
    Conectar_banco("UPDATE Atm SET statusAtm = 'Ativo' WHERE idAtm = %s", atm_info.get('idAtm'))
    print("ATIVADO =======================================================================")

    
    while coletar_dados_continuo:
            print('╔═══════════════════════════════════════════════════════════════════════╗')
            for tipo_componente, medidas in informcao_parametros.items():
                for medida in medidas:

                    valor_dado = capturar_dado(tipo_componente)
                    print(
                        f"\n  - Coleta: {tipo_componente} "
                        f"({medida['unidade']}) → Valor: {valor_dado} {medida['unidade']} "
                        f"→ Limite Configurado: {medida['limite']}"
                    )
                    inserir_registro(valor_dado, medida['id_param'])
                    processar_leitura_com_alerta(
                        fkParametro = medida['id_param'],
                        tipo = tipo_componente,
                        valor = float(valor_dado),
                        limite = float(medida['limite'])
                    )
            print('\n╚═══════════════════════════════════════════════════════════════════════╝')
            time.sleep(10)

            
def main():
    global atm_info
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
    Conectar_banco("UPDATE Atm SET statusAtm = 'Inativo' WHERE idAtm = %s", atm_info.get('idAtm'))
    print("DESATIVADO =======================================================================")
    print("\n Status Atm atualizado ")  

main()