setwd("~/faculdade/upfinity/calculo/Python-UpFinity")
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



#Exibindo o boxplot dos dados

par(mfrow = c(1, 1))

boxplot(df_capturas$cpu, df_capturas$ram, df_capturas$disco,
        names = c("CPU", "RAM", "Disco"),
        main = "Distribuição dos Recursos Monitorados",
        col = c("#6ce5e8", "#41b8d5", "#2db2b7"))



par(mfrow = c(2, 3))



#Exibind os histogramas


#CPU
hist(df_capturas$cpu,
     main = "Distribuição de Uso da CPU",
     xlab = "Uso da CPU (%)",
     col = "#6ce5e8",
     border = "white",
     xlim = c(min(df_capturas$cpu), alerta_grave_cpu))

abline(v = alerta_moderado_cpu, col = "yellow", lwd = 2, lty = 2)
abline(v = alerta_grave_cpu, col = "red", lwd = 2, lty = 2)
legend("topleft",
       legend = c("Alerta Moderado", "Alerta Crítico"),
       col = c("yellow", "red"),
       lty = 2, lwd = 2)


#RAM
hist(df_capturas$ram,
     main = "Distribuição de Uso da memória RAM",
     xlab = "Uso da RAM (%)",
     col = "#41b8d5",
     border = "white",
     xlim = c(min(df_capturas$ram), alerta_grave_ram))

abline(v = alerta_moderado_ram, col = "yellow", lwd = 2, lty = 2)
abline(v = alerta_grave_ram, col = "red", lwd = 2, lty = 2)
legend("topleft",
       legend = c("Alerta Moderado", "Alerta Crítico"),
       col = c("yellow", "red"),
       lty = 2, lwd = 2)


#Disco
hist(df_capturas$disco,
     main = "Distribuição de Uso da Memória de Disco",
     xlab = "Uso do Disco (%)",
     col = "#2db2b7",
     border = "white",
     xlim = c(min(df_capturas$disco), alerta_grave_disco))

abline(v = alerta_moderado_disco, col = "yellow", lwd = 2, lty = 2)
abline(v = alerta_grave_disco, col = "red", lwd = 2, lty = 2)
legend("topleft",
       legend = c("Alerta Moderado", "Alerta Crítico"),
       col = c("yellow", "red"),
       lty = 2, lwd = 2)



#Exibindo os gráficos de linha


#CPU
plot(df_capturas$cpu, type = "l", col = "#6ce5e8", lwd = 2,
     main = "Uso da CPU conforme o tempo",
     xlab = "Tempo (capturas)",
     ylab = "Uso da CPU (%)",
     ylim = c(min(df_capturas$cpu), alerta_grave_cpu))

abline(h = alerta_moderado_cpu, col = "yellow", lwd = 2, lty = 2)
abline(h = alerta_grave_cpu, col = "red", lwd = 2, lty = 2)
legend("topleft",
       legend = c("Alerta Moderado", "Alerta Crítico"),
       col = c("yellow", "red"),
       lty = 2, lwd = 2)


#RAM
plot(df_capturas$ram, type = "l", col = "#41b8d5", lwd = 2,
     main = "Uso da RAM conforme o tempo",
     xlab = "Tempo (capturas)",
     ylab = "Uso da RAM (%)",
     ylim = c(min(df_capturas$ram), alerta_grave_ram))

abline(h = alerta_moderado_ram, col = "yellow", lwd = 2, lty = 2)
abline(h = alerta_grave_ram, col = "red", lwd = 2, lty = 2)
legend("topleft",
       legend = c("Alerta Moderado", "Alerta Crítico"),
       col = c("yellow", "red"),
       lty = 2, lwd = 2)


#Disco
plot(df_capturas$disco, type = "l", col = "#2db2b7", lwd = 2,
     main = "Uso do Disco conforme o tempo",
     xlab = "Tempo (capturas)",
     ylab = "Uso do Disco (%)",
     ylim = c(min(df_capturas$disco), alerta_grave_disco))

abline(h = alerta_moderado_disco, col = "yellow", lwd = 2, lty = 2)
abline(h = alerta_grave_disco, col = "red", lwd = 2, lty = 2)
legend("topleft",
       legend = c("Alerta Moderado", "Alerta Crítico"),
       col = c("yellow", "red"),
       lty = 2, lwd = 2)

