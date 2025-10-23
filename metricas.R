setwd("~/faculdade/upfinity/calculo/Rmetricas")
getwd()

df_capturas <- read.csv("capturas.csv")

is.data.frame(df_capturas)

media_cpu <- mean(df_capturas$cpu)
media_ram <- mean(df_capturas$ram)
media_disco <- mean(df_capturas$disco)

mediana_cpu <- mean(df_capturas$cpu)
mediana_ram <- mean(df_capturas$ram)
mediana_disco <- mean(df_capturas$disco)

desvio_cpu <- sd(df_capturas$cpu)
desvio_ram <- sd(df_capturas$ram)
desvio_disco <- sd(df_capturas$disco)

alerta_moderado_cpu <- round(media_cpu + desvio_cpu, 2)
alerta_grave_cpu <- round(media_cpu + 2 * desvio_cpu, 2)

alerta_moderado_ram <- round(media_ram + desvio_ram, 2)
alerta_grave_ram <- round(media_ram + 2 * desvio_ram, 2)

alerta_moderado_disco <- round(media_disco + desvio_disco, 2)
alerta_grave_disco <- round(media_disco + 2 * desvio_disco, 2)

print("Alerta moderado para CPU: ")
print(alerta_moderado_cpu)
print("Alerta grave para CPU: ")
print(alerta_grave_cpu)
print("Alerta moderado para RAM: ")
print(alerta_moderado_ram)
print("Alerta grave para RAM: ")
print(alerta_grave_ram)
print("Alerta moderado para Disco: ")
print(alerta_moderado_disco)
print("Alerta grave para Disco: ")
print(alerta_grave_disco)