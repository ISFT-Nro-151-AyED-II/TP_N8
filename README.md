# 🐍 Algoritmos y Estructuras de Datos II - Trabajo Práctico N°8 - Unidad N°2 (Cuarta Parte)

**Instituto Superior de Formación Técnica Nº 151** **Carrera:** Tecnicatura Superior en Análisis de Sistemas  
**Materia:** Algoritmos y Estructuras de Datos II  
**Tema:** Python꞉ GUI Frameworks, Tkinter, SQLite  
**Autor:** David Hernán Bravo  

---

## 🎯 Resumen Técnico del Entregable

Este repositorio contiene la resolución práctica de la cuarta parte de la Unidad N°2. El enfoque principal del desarrollo no fue únicamente lograr que el código funcione, sino aplicar principios de **Arquitectura Limpia (Clean Architecture)**, separando estrictamente la Lógica de Negocio (Core), el Acceso a Datos y la Interfaz Gráfica (UI) para evitar el anti-patrón de código espagueti.

El trabajo se divide en dos módulos independientes:

### 🧮 1. Calculadora (Ejercicio 3.1)
Implementación de una calculadora funcional con evaluación segura de expresiones matemáticas y una interfaz gráfica anclada geométricamente.
* **Patrón aplicado:** Separación de UI (Tkinter) y Motor de Evaluación (Regex + Manejo defensivo de excepciones).

* **Ejecución:** `python "01-Calculadora/Main.py"`

* 📄 **Documentación técnica:** [Ver DESARROLLO.md de la Calculadora](./01-Calculadora/DESARROLLO.md)

### 🛠️ 2. Repair Center (Ejercicios 3.2 y 3.3)
Sistema de gestión de tickets de servicio técnico con autenticación de usuarios y persistencia de datos relacional. 
* **Patrón aplicado:** Arquitectura Multicapa (Presentación, Dominio, Datos) con Inyección de Dependencias.

* **Base de Datos:** SQLite automatizado (Auto-seeding y validación de directorios).

* **Ejecución:** `python "02-RepairCenter/Main.py"`

* *Nota: Las credenciales por defecto para evaluar el sistema son Usuario: `admin` / Contraseña: `1234`.*

* 📄 **Documentación técnica:** [Ver DESARROLLO.md del Repair Center](./02-RepairCenter/DESARROLLO.md)

---

## ⚙️ Requisitos y Ejecución

* **Lenguaje:** Python 3.14.2

* **Librerías estándar utilizadas:** `tkinter`, `sqlite3`, `os`, `re`, `sys` (No se requieren instalaciones mediante `pip`).

* **Sistemas Operativos:** Compatible con Windows y Linux (rutas relativas implementadas).

Para probar cualquier aplicación, ubicarse en la raíz de este directorio y ejecutar el script principal (`Main.py`) del proyecto correspondiente.
