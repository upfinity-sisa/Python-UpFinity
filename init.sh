#!/bin/bash
echo ''
echo "Criando configurações de BD"
echo "Configure arquivo de configuração '.env' abaixo"
echo ''

echo ''
echo "Credenciais de acesso ao MySql Server"
read -p "Insira o ip do host: " HOST
read -p "Insira o user para inserção no banco: " USER
read -p "Insira a senha do user $USER: " SENHA
echo ''
read -p "Insira o database: " DATABASE
echo ''

cat > '.env' <<EOF
HOST_DB = '$HOST'
USER_DB = '$USER'
PASSWORD_DB = '$SENHA'
DATABASE_DB = '$DATABASE'
EOF

echo ''
echo 'As credenciais configuradas são:'
echo '--------------------------------'
cat '.env'
echo '--------------------------------'

read -p "As credenciais estão corretas? (S/N) " INICIAR_API

echo ''
if [ $INICIAR_API = 'S' ]; then 
    echo '.env Criado'
    read -p "Seu SO é Linux(S/N): " SO
    if [ "$SO" = 'S' ]; then
        echo 'Instalando as bibliotecas no Linux'
        python3 -m venv venv-ambiente-Captura
        source venv-ambiente-Captura/bin/activate
        pip install -r requirements.txt
    else
        echo 'Instalando as bibliotecas no Windows'
        python -m venv venv-ambiente-Captura
        ./venv-ambiente-Captura/Scripts/python.exe -m pip install -r requirements.txt
        read -p "Deseja iniciar o programa(S/N): " START
        if [ "$START" = 'S' ]; then
            ./venv-ambiente-Captura/Scripts/python.exe "Captura Hardware.py"
        fi
    fi
else 
    echo 'RECONFIGURE AS CREDENCIAIS...'
    ./init.sh
fi