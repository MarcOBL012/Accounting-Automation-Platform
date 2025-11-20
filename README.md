# Sistema Contable

Sistema de gestión contable desarrollado con Django para el registro y seguimiento de transacciones financieras.

## Características

- Registro de asientos contables
- Gestión de saldos iniciales
- Libro diario
- Estado de resultados
- Estado de situación financiera
- Mayor de cuentas
- Filtros por tipo de cuenta y cuenta específica

## Requisitos

- Python 3.8 o superior
- Django 4.2 o superior
- pip (gestor de paquetes de Python)
- Git (opcional, para clonar el repositorio)

## Instalación y Configuración

### Opción 1: Instalación Tradicional

#### Opción 1: Clonar el repositorio
```bash
git clone [URL_DEL_REPOSITORIO]
cd financiera
```

#### Opción 2: Descargar el código fuente
1. Descargar el código fuente como ZIP
2. Extraer el contenido en una carpeta
3. Abrir terminal en la carpeta extraída

### 2. Configuración del Entorno Virtual

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Windows:
venv\Scripts\activate
# En Linux/Mac:
source venv/bin/activate
```

### 3. Instalación de Dependencias

```bash
# Instalar todas las dependencias desde requirements.txt
pip install -r requirements.txt
cd AppWeb
```

### 4. Configuración de la Base de Datos

```bash
# Crear las migraciones
python manage.py makemigrations

# Aplicar las migraciones
python manage.py migrate
```

### 5. Ejecutar el Servidor

```bash
# Iniciar el servidor de desarrollo
python manage.py runserver
```

### 6. Acceder al Sistema

1. Abrir el navegador
2. Ir a `http://localhost:8000`

### Opción 2: Usando Docker

1. Iniciar la aplicación:
```bash
docker-compose up --build
```

2. Para ejecutar en segundo plano:
```bash
docker-compose up -d
```

3. Para detener la aplicación:
```bash
docker-compose down
```

4. Acceder al sistema
- Abrir el navegador
- Ir a `http://localhost:8000`