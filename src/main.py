import psutil as p
import time
from datetime import datetime

def converter_bytes_para_gigabytes(valor):
    return valor / (1024 * 1024 * 1024)

def iniciar_captura():
    continuar_captura = True
    while continuar_captura:
        cpu = {
            "uso_porcentagem": p.cpu_percent(interval=1),
            "uso_usuario": p.cpu_times_percent(interval=1).user,
            "uso_sistema": p.cpu_times_percent(interval=1).system,
            "sem_uso": p.cpu_times_percent(interval=1).idle,
        }

        informacao_memoria = p.virtual_memory()
        memoria = {
            "total": converter_bytes_para_gigabytes(informacao_memoria.total),
            "disponivel": converter_bytes_para_gigabytes(informacao_memoria.available),
            "percentual": informacao_memoria.percent,
        }

        informacao_disco = p.disk_usage('/')
        disco = {
            "total": converter_bytes_para_gigabytes(informacao_disco.total),
            "usado": converter_bytes_para_gigabytes(informacao_disco.used),
            "livre": converter_bytes_para_gigabytes(informacao_disco.free),
            "percentual": informacao_disco.percent,
        }

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        mostrar_dados(cpu, memoria, disco, timestamp)
        time.sleep(10) 

def mostrar_dados(cpu, memoria, disco, timestamp):
    print("\n==================== CAPTURA ====================")
    print("Horário da captura:", timestamp)

    print("\n==================== CPU ====================")
    print(f"Uso em porcentagem(%): {cpu['uso_porcentagem']}")
    print(f"Uso do usuário: {cpu['uso_usuario']}")
    print(f"Uso do sistema: {cpu['uso_sistema']}")
    print(f"Sem uso: {cpu['sem_uso']}")

    print("\n=================== MEMÓRIA ==================")
    print(f"Memória total: {memoria['total']:.2f} GB")
    print(f"Memória disponível: {memoria['disponivel']:.2f} GB")
    print(f"Uso de memória: {memoria['percentual']}%")

    print("\n=================== DISCO ====================")
    print(f"Disco total: {disco['total']:.2f} GB")
    print(f"Disco usado: {disco['usado']:.2f} GB")
    print(f"Disco livre: {disco['livre']:.2f} GB")
    print(f"Uso do disco: {disco['percentual']}%")
    print("================================================")

def iniciar():
    linha = "================================================"
    print(linha)
    print("           🖥️  MONITORAMENTO DO SISTEMA          ")
    print(linha)
    print("👋 Bem-vindo!")
    print("📊 Este programa vai coletar periodicamente a cada 10s os seguintes dados:")
    print("   - Uso da CPU")
    print("   - Uso da Memória RAM")
    print("   - Uso do Disco")
    print("   - Horário da captura (timestamp)")
    print("\n❌ Pressione [CTRL + C] a qualquer momento para finalizar.")
    print(linha + "\n")
    iniciar_captura()

iniciar()