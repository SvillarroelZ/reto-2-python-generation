# 🚀 Proyecto 2 — Cloud Instance Manager (CLI)

Variables • Estructuras de datos • Condicionales • Funciones • Validaciones • Excepciones • AWS • JMESPath

---

## 🎯 Objetivo del proyecto

En este proyecto vas a construir **una aplicación de línea de comandos (CLI)** en Python que permita **administrar instancias en la nube** (por ejemplo, EC2 en AWS), con operaciones como:

- Crear instancias  
- Detener instancias  
- Iniciar / reiniciar instancias  
- Terminar instancias  
- Listar las instancias actuales  
- Filtrar instancias por estado u otros criterios  

Todo esto usando:

- **Estructuras de datos** (listas, diccionarios, tuplas)  
- **Condicionales (`if / elif / else`)**  
- **Funciones**  
- **Validaciones de entrada**  
- **Manejo de excepciones (`try / except`)**  
- Un cliente de AWS con **boto3** y filtros con **JMESPath**

> ⚠️ IMPORTANTE: Este proyecto es didáctico. Usa SIEMPRE una cuenta de práctica / sandbox.  
> Nunca ejecutes código que no entiendas en una cuenta de producción.

---

## ✅ Requisitos previos

Antes de empezar, necesitas:

- Python 3.10+ instalado  
- Git instalado  
- VS Code o tu editor favorito  
- Una cuenta de AWS de práctica  
- Access Key y Secret Access Key personales (NO las compartas con nadie)  
- Haber visto:
  - Variables
  - Listas, tuplas y diccionarios
  - Condicionales
  - Funciones
  - Conceptos básicos de excepciones

---

## 🧰 Paso 1 — Hacer Fork y clonar el repositorio

El profesor Isen tendrá un repositorio base con el código inicial y los TODOs.

1. Ve al repositorio original del profesor en GitHub.
2. Haz clic en el botón Fork.
3. En tu cuenta aparecerá una copia del repo.
4. Clona tu fork a tu computadora:

```bash
git clone https://github.com/TU_USUARIO/NOMBRE_DEL_REPO.git
cd NOMBRE_DEL_REPO
```

---

## 🛠️ Paso 2 — Configurar el entorno de trabajo

Dentro de la carpeta del proyecto:

1. (Opcional pero recomendado) Crear entorno virtual:

```bash
python -m venv .venv
# En Windows:
.venv\Scripts\activate
# En macOS / Linux:
source .venv/bin/activate
```

2. Instalar dependencias:

```bash
pip install -r requirements.txt
```

El archivo requirements.txt incluye al menos:

```txt
boto3
jmespath
python-dotenv
```

---

## 🔐 Paso 3 — Configurar tus credenciales de AWS

Tienes 3 opciones. Elige solo UNA.

### Opción A: aws configure (recomendada si tienes AWS CLI)

```bash
aws configure
```

Te pedirá:

- AWS Access Key ID  
- AWS Secret Access Key  
- Default region name (por ejemplo, us-east-1)  
- Default output format (json)

### Opción B: Variables de entorno (más avanzada)

```bash
export AWS_ACCESS_KEY_ID="TU_ACCESS_KEY"
export AWS_SECRET_ACCESS_KEY="TU_SECRET_KEY"
export AWS_DEFAULT_REGION="us-east-1"
```

### Opción C: Archivo .env (usando python-dotenv)

1. Crea un archivo llamado .env en la raíz del proyecto:

```env
AWS_ACCESS_KEY_ID=TU_ACCESS_KEY
AWS_SECRET_ACCESS_KEY=TU_SECRET_KEY
AWS_DEFAULT_REGION=us-east-1
```

2. Nunca subas tu .env a GitHub.  
   Asegúrate de que .gitignore contenga:

```gitignore
.env
```

---

## 🧱 Paso 4 — Estructura del proyecto

La estructura recomendada del proyecto es:

```txt
NOMBRE_DEL_REPO/
├─ src/
│  ├─ config.py
│  ├─ aws_client.py
│  ├─ instances_cli.py
│  └─ main.py
├─ requirements.txt
└─ README.md
```

### src/config.py
Responsable de leer variables de entorno y exponer la configuración.

```python
# src/config.py
from dotenv import load_dotenv
import os

load_dotenv()

AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")

def get_aws_credentials():
    '''
    Devuelve un diccionario con las credenciales de AWS.
    Si las variables no existen, lanza una excepción clara para el usuario.
    '''
    access_key = os.getenv("AWS_ACCESS_KEY_ID")
    secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")

    if not access_key or not secret_key:
        raise ValueError("No se encontraron las credenciales de AWS. Revisa tu archivo .env o variables de entorno.")

    return {
        "aws_access_key_id": access_key,
        "aws_secret_access_key": secret_key,
        "region_name": AWS_REGION,
    }
```

### src/aws_client.py
Crea y devuelve el cliente de AWS (por ejemplo, EC2).

```python
# src/aws_client.py
import boto3
from botocore.exceptions import BotoCoreError, NoCredentialsError
from .config import get_aws_credentials

def create_ec2_client():
    '''
    Crea un cliente de EC2 usando las credenciales de config.py.
    Maneja excepciones básicas para dar mensajes claros al usuario.
    '''
    try:
        creds = get_aws_credentials()
        client = boto3.client("ec2", **creds)
        return client
    except NoCredentialsError:
        print("Error: No se encontraron credenciales de AWS.")
        raise
    except BotoCoreError as e:
        print("Error al crear el cliente de EC2:", e)
        raise
```

### src/instances_cli.py
Aquí vivirán las funciones que interactúan con las instancias: listar, crear, detener, etc.

```python
# src/instances_cli.py
from botocore.exceptions import ClientError
import jmespath

def list_instances(ec2_client):
    '''
    Lista las instancias existentes y muestra información básica:
    - ID de instancia
    - Estado
    - Tipo
    - Zona de disponibilidad
    '''
    try:
        response = ec2_client.describe_instances()
        # Usamos JMESPath para extraer solo lo que nos interesa
        instances = jmespath.search(
            "Reservations[].Instances[][].{id: InstanceId, state: State.Name, type: InstanceType, az: Placement.AvailabilityZone}",
            response
        )
        print("Instancias encontradas:")
        for inst in instances:
            print(f"- {inst['id']} | {inst['state']} | {inst['type']} | {inst['az']}")
    except ClientError as e:
        print("Error al listar instancias:", e)

def create_instance(ec2_client):
    '''
    Crea una instancia simple (por ejemplo, Amazon Linux 2 t2.micro).
    Practicarás:
    - Lectura de input()
    - Validaciones básicas
    - Manejo de excepciones
    '''
    print("Creación de instancia")
    ami_id = input("Ingresa el AMI ID (ejemplo: ami-1234567890abcdef0): ").strip()
    instance_type = input("Ingresa el tipo de instancia (ejemplo: t2.micro): ").strip()

    if not ami_id or not instance_type:
        print("AMI ID y tipo de instancia son obligatorios.")
        return

    try:
        response = ec2_client.run_instances(
            ImageId=ami_id,
            InstanceType=instance_type,
            MinCount=1,
            MaxCount=1
        )
        instance_id = response["Instances"][0]["InstanceId"]
        print(f"Instancia creada con ID: {instance_id}")
    except ClientError as e:
        print("Error al crear la instancia:", e)

def stop_instance(ec2_client):
    '''
    Detiene una instancia existente a partir de su ID.
    Practicarás:
    - Validación de que el ID no esté vacío
    - Manejo de errores de AWS
    '''
    instance_id = input("Ingresa el ID de la instancia a detener: ").strip()
    if not instance_id:
        print("El ID de la instancia no puede estar vacío.")
        return

    try:
        ec2_client.stop_instances(InstanceIds=[instance_id])
        print(f"Solcitada detención de la instancia {instance_id}")
    except ClientError as e:
        print("Error al detener la instancia:", e)

# TODO: Implementar funciones similares:
# - start_instance(ec2_client)
# - reboot_instance(ec2_client)
# - terminate_instance(ec2_client)
# - filter_instances_by_state(ec2_client)
```

### src/main.py
La puerta de entrada de la aplicación.  
Mostrará un menú y llamará a las funciones de instances_cli.py.

```python
# src/main.py
from .aws_client import create_ec2_client
from .instances_cli import (
    list_instances,
    create_instance,
    stop_instance,
    # start_instance,
    # reboot_instance,
    # terminate_instance,
    # filter_instances_by_state,
)

def print_menu():
    print("\n=== Cloud Instance Manager ===")
    print("1. Listar instancias")
    print("2. Crear instancia")
    print("3. Detener instancia")
    print("4. Iniciar instancia (TODO)")
    print("5. Reiniciar instancia (TODO)")
    print("6. Terminar instancia (TODO)")
    print("7. Filtrar instancias por estado (TODO)")
    print("0. Salir")

def main():
    ec2_client = create_ec2_client()

    while True:
        print_menu()
        opcion = input("Selecciona una opción: ").strip()

        if opcion == "1":
            list_instances(ec2_client)
        elif opcion == "2":
            create_instance(ec2_client)
        elif opcion == "3":
            stop_instance(ec2_client)
        elif opcion == "0":
            print("Saliendo del administrador de instancias. ¡Hasta luego!")
            break
        else:
            print("Opción no válida. Intenta nuevamente.")

if __name__ == "__main__":
    main()
```

---

## 🧪 Ritmo de trabajo recomendado

### Fase 1 — Configuración
- Clonar repo  
- Crear entorno virtual  
- Instalar dependencias  
- Configurar credenciales  
- Probar que main.py al menos muestra el menú

### Fase 2 — Lectura y comprensión
- Entender config.py y aws_client.py  
- Dibujar en papel el flujo: main → aws_client → EC2

### Fase 3 — Implementación guiada
- Completar funciones simples (listar, crear, detener)  
- Agregar mensajes claros y validaciones

### Fase 4 — Manejo de errores
- Envolver llamadas críticas en try / except  
- Diferenciar errores de credenciales, permisos, parámetros inválidos

### Fase 5 — Filtros con JMESPath
- Practicar expresiones JMESPath para:
  - Mostrar solo instancias running
  - Mostrar solo IDs y estados
  - Filtrar por tipo de instancia

---

## 📦 Entrega del proyecto (Pull Request)

1. Asegúrate de que tu código corre sin errores:

```bash
python -m src.main
```

2. Guarda tus cambios:

```bash
git status
git add src/
git commit -m "Implemento Cloud Instance Manager básico"
```

3. Envía tus cambios a tu fork:

```bash
git push origin main
```

4. En GitHub:
   - Haz clic en Compare & Pull Request
   - Título sugerido:
     Entrega Proyecto 2 — Cloud Instance Manager
   - Describe qué partes completaste (listar, crear, detener, etc.)

5. Crea el Pull Request hacia el repositorio del profesor.

---

## 🎉 Logros esperados

Al finalizar este proyecto habrás practicado:

- Uso de estructuras de datos reales con respuestas de AWS  
- Diseño de una aplicación de línea de comandos  
- Organización de código en módulos y funciones  
- Manejo de errores y excepciones de AWS  
- Uso de credenciales de forma responsable  
- Filtros con JMESPath para extraer datos útiles  
- Flujo de trabajo profesional con GitHub + Pull Requests

¡Este proyecto se parece mucho a lo que harías en un equipo de DevOps o Cloud Engineering junior!
