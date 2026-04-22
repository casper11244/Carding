#!/bin/bash

echo "Compilando Generador de Tarjetas..."

# Crear directorio de clases compiladas
mkdir -p target/classes
mkdir -p output

# Compilar todos los archivos Java
javac -d target/classes \
    src/main/java/com/tarjetagenerator/model/*.java \
    src/main/java/com/tarjetagenerator/service/*.java \
    src/main/java/com/tarjetagenerator/ui/*.java \
    src/main/java/com/tarjetagenerator/Main.java

echo "✓ Compilación completada"
echo ""
echo "Para ejecutar: java -cp target/classes com.tarjetagenerator.Main"
echo "Con base de datos: java -cp target/classes:lib/h2-2.2.224.jar com.tarjetagenerator.Main"