"""
Módulo: monitoramento_atm_python/main.py
Autor: Jhoel Diego Mamani Mita
Data: 01/09/2025
Descrição: Sistema de monitoramento de ATMs. Captura métricas de CPU, RAM,
disco e rede, registra no banco e gera alertas automáticos caso os limites
configurados sejam ultrapassados.

Dependências:
- psutil
- mysql.connector
- dotenv

"""
import psutil as p
import time
from utils.Database import Fazer_consulta_banco
from datetime import datetime, timedelta

"""
    Util: Fazer_consulta_banco(config)

    Recebe um dicionário com:
        config = {
            "query": "SQL AQUI",
            "params": (param1, param2, ...)(Pose ser nulo)
        }

    retorna o resultado banco seja qual for o tipo SELECT, UPDATE, DELETE, INSERT
"""

# =========================================================
# VARIÁVEIS GLOBAIS 
# =========================================================
# # Dicionário de funções para captura de métricas.
# As funções são lambdas para serem executadas somente quando chamadas.
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

informacoes_atm = set()


# =========================================================
# FUNÇÃO PRINCIPAL (MENU) 
# =========================================================
def main():
    """
    Função principal (menu) do sistema.

    - Exibe o logo e menu ao usuário.
    - Permite iniciar o monitoramento ou encerrar o sistema.
    - Atualiza status do ATM para 'Inativo' ao encerrar.
    """
    global informacoes_atm
    global logo
    global menu_resumido
    global saida

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


    # Atualiza status ATM para inativo já que o ATM parou de enviar dados para o ATM
    Fazer_consulta_banco({

        "query": "UPDATE Atm SET statusAtm = 'Inativo' WHERE idAtm = %s",
        "params": (informacoes_atm.get('idAtm'),)

    })
    print("\n Status Atm atualizado para INATIVO")
    horario = horario_atual()

    consulta = Fazer_consulta_banco({

        "query": """
                    INSERT INTO Alerta (fkAtm, tipoAlerta, nivel, dataHoraInicio)
                    VALUES (%s, %s, %s,%s)
                """,
        "params": (informacoes_atm.get('idAtm'),
                    'Atm está off-line', 'critico', horario)

        })
    print(consulta)
    print("Alerta atm gerado")

# =========================================================
# LOOP DE MONITORAMENTO -  
# =========================================================
def coletar_dados():
    """
    Loop de monitoramento contínuo.

    - Valida informações do ATM a partir de MAC e IP.
    - Obtém parâmetros de monitoramento configurados no banco.
    - Atualiza status do ATM para 'Ativo'.
    - Coleta dados periodicamente de acordo com o dicionário `acoes`.
    - Insere registros no banco e processa alertas.
    - Pausa 10 segundos entre cada coleta.
    """
    coletar_dados_continuo = True

    dados_mac_ip = procurar_mac_address()
    informacoes_atm_local = validar_dados_atm(dados_mac_ip)

    if informacoes_atm_local is None:
        return

    informcao_parametros = procura_parametros_atm(informacoes_atm_local)

    if informcao_parametros is None:
        return

    Fazer_consulta_banco({

        "query": "UPDATE Atm SET statusAtm = 'Ativo' WHERE idAtm = %s",
        "params": (informacoes_atm_local.get('idAtm'),)

    })
    verificar_alerta_atm= Fazer_consulta_banco({
        "query": """
            SELECT idAlerta 
            FROM Alerta
            WHERE fkAtm = %s  AND dataHoraFinal IS NULL
            ORDER BY dataHoraInicio DESC
            LIMIT 1
        """,
        "params": (informacoes_atm_local.get('idAtm'),)

    })
    print("\n Status Atm atualizado para ATIVO ")

    horario = horario_atual()
    if len(verificar_alerta_atm) == 1:
        Fazer_consulta_banco({
                     "query": "UPDATE Alerta SET dataHoraFinal = %s  WHERE idAlerta = %s",
                    "params": (horario, verificar_alerta_atm[0][0],)
            })
        print("status Alerta atualizado")


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
                    fkParametro=medida['id_param'],
                    tipo=tipo_componente,
                    valor=float(valor_dado),
                    limite=float(medida['limite'])
                )

        print('\n╚═══════════════════════════════════════════════════════════════════════╝')

        time.sleep(10)


# =========================================================
# CAPTURA DE DADOS-
# =========================================================
def capturar_dado(tipo):
    """
    Captura o valor de um parâmetro específico usando o dicionário `acoes`.

    Parâmetros:
    tipo (str): Nome do parâmetro (ex: 'CPU_porcentagem', 'RAM_percentual').

    Retorna:
    float | None: Valor do parâmetro ou None em caso de erro.
    """
    global acoes
    try:

        funcao = acoes.get(tipo)
        return funcao() if funcao else None
    
    except Exception as e:

        print(f"⚠️ Erro ao coletar valor para {tipo}: {e}")
        return None


# =========================================================
# FUNÇÕES DE BANCO DE DADOS VERIFICAÇÕES
# =========================================================
def procurar_mac_address():
    """
    Retorna informações de MAC e IP do ATM.

    Atualmente retorna dados simulados, substituível por coleta real na sprint 2.
    
    Retorna:
    dict: {'mac_address': str, 'ip_address': str}
    """
    return {

        "mac_address": "00:1A:2B:3C:4D:5E",
        "ip_address": "192.168.1.1"

    }

def validar_dados_atm(dados):
    global informacoes_atm

    resultado = Fazer_consulta_banco({

        "query": "SELECT idAtm, hostname FROM Atm WHERE macAddress = %s AND ip = %s",
        "params": (dados.get('mac_address'), dados.get('ip_address'))

    })

    print(resultado)

    if resultado:

        informacoes_atm = {

            'idAtm': resultado[0][0],
            'hostname': resultado[0][1],
            'mac_address': dados['mac_address'],
            'ip_address': dados['ip_address']

        }

        print('╔════════════════════════════════════════════════════╗')
        print(f"   🔹 Monitoramento iniciado com sucesso! 🔹\n"
              f"   🖥️ ATM ID: {informacoes_atm['idAtm']}\n"
              f"   💻 Hostname: {informacoes_atm['hostname']}\n"
              f"   📡 MAC: {informacoes_atm['mac_address']}\n"
              f"   🌐 IP: {informacoes_atm['ip_address']}\n"
              f"   ✅ Seja bem-vindo(a)! ✅\n")
        print('╚════════════════════════════════════════════════════╝')

        return informacoes_atm
    else:

        print(f"\n❌ Este ATM ({dados['mac_address']}) não foi encontrado no sistema. ❌\n")
        return None



def procura_parametros_atm(dados):

    resultado = Fazer_consulta_banco({

        "query": """
            SELECT ac.idAtmComponente, c.funcaoMonitorada, c.unidadeMedida, p.limite
            From AtmComponente as ac 
            JOIN Parametro as p on ac.idAtmComponente = p.fkAtmComponente
            JOIN Componente as c on ac.fkComponente = c.idComponente
            WHERE ac.fkAtm = %s;
        """,
        "params": (dados.get('idAtm'),)

    })

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



def inserir_registro(valor, fk_parametro):
    valor = float(valor)

    resultado = Fazer_consulta_banco({

        "query": "INSERT INTO Registro (valor, horario, fkAtmComponente) VALUES (%s, NOW(), %s);",
        "params": (valor, fk_parametro)

    })
    if resultado >= 0:

        print(resultado, "registro inserido")


# =========================================================
# FUNÇÕES DE ALERTA 
# =========================================================
def horario_atual():
    """
    Retorna o horário atual formatado como string: YYYY-MM-DD HH:MM:SS
    """
    agora = datetime.now()
    return agora.strftime("%Y-%m-%d %H:%M:%S")


def processar_leitura_com_alerta(fkParametro, tipo, valor, limite):
    horario = horario_atual()
    """
    Processa o registro de leitura de um parâmetro e gerencia alertas.

    - Determina o nível do alerta com base no valor e limite.
    - Verifica se já existe um alerta aberto para o parâmetro:
        - Se não existir, cria um novo.
        - Se existir e nível diferente ou alerta expirado (>5 min), fecha o antigo e cria novo.
        - Se valor voltou ao normal, fecha o alerta existente.

    Parâmetros:
    fkParametro (int): ID do parâmetro no banco.
    tipo (str): Tipo do parâmetro monitorado.
    valor (float): Valor coletado.
    limite (float): Limite configurado para alerta.
    """
    valor = float(valor)
    # Determina nível do alerta baseado no valor coletado
    if valor >= limite * 1.2:
        nivel = "Critico"
    elif valor >= limite:
        nivel = "Alerta"
    elif valor >= limite * 0.9:
        nivel = "Atenção"
    else:
        nivel = None

    alerta_aberto = Fazer_consulta_banco({

        "query": """
            SELECT idAlerta, nivel, dataHoraInicio
            FROM Alerta
            WHERE fkAtmComponente = %s AND tipoAlerta = %s AND dataHoraFinal IS NULL
            ORDER BY dataHoraInicio DESC
            LIMIT 1
        """,
        "params": (fkParametro, tipo)

    })

    alerta_aberto = alerta_aberto[0] if alerta_aberto else None

    def alerta_expirado(data_hora_inicio):

        if isinstance(data_hora_inicio, datetime):
            return datetime.now() - data_hora_inicio > timedelta(minutes=5)
        
        return False

    if nivel:#aqui caso o registro fonecido não seja alto ele ficará None
        if not alerta_aberto:
            Fazer_consulta_banco({

                "query": """
                    INSERT INTO Alerta (fkAtmComponente, tipoAlerta, nivel,valorInicial,  dataHoraInicio)
                    VALUES (%s, %s, %s,%s, %s)
                """,
                "params": (fkParametro, tipo, nivel, valor, horario)

            })

            print(f"  Alerta ABERTO para {tipo} (nível: {nivel})")

        else:
            data_hora_inicio = alerta_aberto[2]

            if alerta_aberto[1] != nivel or alerta_expirado(data_hora_inicio):

                consulta = Fazer_consulta_banco({

                    "query": "UPDATE Alerta SET dataHoraFinal = %s, valorFinal = %s WHERE idAlerta = %s",
                    "params": (horario, alerta_aberto[0],valor)
                
                })
                print("====================================================")
                print(consulta)
                print("====================================================")
                Fazer_consulta_banco({
                
                    "query": """
                        INSERT INTO Alerta (fkAtmComponente, tipoAlerta, nivel,valorInicial,  dataHoraInicio)
                        VALUES (%s, %s, %s,%s, %s)
                    """,
                
                    "params": (fkParametro, tipo, nivel, valor, horario)
                })
                print(f"  Alerta atualizado criando NOVO registro para {tipo} (nível: {nivel})")

    else:
        if alerta_aberto:

            consulta = Fazer_consulta_banco({
                
                "query": "UPDATE Alerta SET dataHoraFinal = %s, valorFinal = %s WHERE idAlerta = %s",
                "params": (horario, valor, alerta_aberto[0])
            
            })
            print(consulta)
            print("------------------+++++++++++++++++++++++++")
            print(horario)
            print(alerta_aberto[0])
            print(valor)
            print(f"  Alerta FECHADO para {tipo}")





# EXECUÇÃO
main()