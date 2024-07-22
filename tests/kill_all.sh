#!/bin/bash

# Obtiene el directorio del script
script_dir=$(dirname "$(readlink -f "$0")")

# Obtiene el directorio padre
parent_dir=$(dirname "$script_dir")

# Busca y termina todos los procesos de Python en el directorio padre y sus subdirectorios
ps aux | grep -E 'python' | awk -v parent_dir="$parent_dir" '
{
    # Extrae el PID y el comando
    pid = $2;
    cmd = $11;
    
    # Verifica si el comando se está ejecutando desde el directorio padre o sus subdirectorios
    if (index(cmd, parent_dir) == 1) {
        print pid;
    }
}' | xargs -r kill -9

# Busca y termina todos los procesos que ejecutan main.go en cualquier lugar
ps aux | grep -E 'main\.go' | awk '
{
    # Extrae el PID
    pid = $2;
    print pid;
}' | xargs -r kill -9

echo "Todos los procesos de Python en $parent_dir y sus subdirectorios, y los procesos que ejecutan main.go en cualquier lugar han sido detenidos."
