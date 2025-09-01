# Bucle para verificar la conexión a Internet
whoami
while true; do
    if ping -c 1 8.8.8.8 &> /dev/null; then
        echo "Conexión a Internet detectada."

        # Verificar si el archivo alma.py existe
        if [ -f /home/delight/home/delight/pico/alma.py ]; then
            echo "Archivo alma.py encontrado. Ejecutando el programa..."
            #Ultra necesario aclara donde estas con el cd
            cd /home/delight/home/delight/pico 

            /usr/bin/python3 /home/delight/home/delight/pico/alma.py
        else
            echo "Error: El archivo alma.py no se encuentra en la ruta especificada."
        fi

        # Salir del bucle una vez ejecutado el programa
        break
    else
        echo "Sin conexión a Internet. Intentando nuevamente en 5 segundos..."
        sleep 5
    fi
done
