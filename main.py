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
        
def buscar_informacoes_paremtros(dados):
    conn = conectar_banco()
    cursor = conn.cursor()
    query = "SELECT funcaoPsutil, unidadeMedida, limiti, "

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
        buscar_informacoes_paremtros(resultado[0])
    else:
        print(f"\n⚠️ Este ATM ({dados['mac_adress']}) não foi encontrado no sistema. ⚠️\n")
        return None



def procurar_mac_adress():
    #Exemplo mais para frente será o mac da maquina
    dados_atm = {
        "mac_adress": "1A:1A:1A:1A:1A:1A",
        "ip_adress": "111.111.1.11"
    }
    validar_atm(dados_atm)

    



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