import psutil as p
import pandas
import time

vt_capturas = []

def capturar():

    valor_cpu = p.cpu_percent(interval=1, percpu=False)
    valor_disco = p.disk_usage('/').percent
    valor_ram = p.virtual_memory().percent

    capturas = {
    "cpu": valor_cpu,
    "ram": valor_ram,
    "disco": valor_disco,
    }

    vt_capturas.append(capturas)

    time.sleep(2)
    print("captura realizada")


for i in range(50):
    capturar()

df = pandas.DataFrame(vt_capturas)
print(df)

df.to_csv("capturas.csv", index=False)