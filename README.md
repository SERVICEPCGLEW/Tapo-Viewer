# Tapo Viewer

Un visor ligero, flotante y minimalista para cámaras Tapo (y otras cámaras compatibles con RTSP), construido con Python, PyQt6 y VLC.

## Características Principales

- **Flotante y Minimalista**: Interfaz sin bordes, pensada para quedarse en una esquina de la pantalla sin estorbar.
- **Fijar por Encima (Always on Top)**: Un botón integrado de chincheta (📌) para mantener la cámara siempre visible por sobre otras ventanas.
- **Doble Clic para Expandir**: Alterna rápidamente entre la visualización en ventana pequeña (calidad 360p) y pantalla completa (calidad 2K) haciendo doble clic en el video.
- **Configuración Dinámica**: Ajusta la dirección IP de la cámara, tu usuario, contraseña y las rutas de los *streams* directamente desde la bandeja del sistema, sin tocar código.
- **Silencioso por Defecto**: El audio se silencia automáticamente para evitar ecos y ruidos de ambiente, ideal para monitoreo visual en la PC.
- **Ocultar y Mostrar**: Minimízalo completamente a la bandeja del sistema (System Tray) o configúralo para que se inicie automáticamente con Windows.

## Requisitos Previos

Para ejecutar la aplicación o compilarla, es **obligatorio** tener instalado:

- **VLC Media Player** (El motor de video utiliza las librerías nativas de VLC para conectarse al RTSP).
- **Python 3.x** (Solo si vas a correr o compilar el código fuente).

## Instalación Automática

Se incluye un script para facilitar la instalación del motor VLC y las librerías necesarias.

1. Clona o descarga este repositorio en tu PC.
2. Haz doble clic en el archivo `install_dependencies.bat`.
3. El script instalará automáticamente VLC usando `winget` y descargará las dependencias de Python listadas en `requirements.txt`.

## Uso

### A partir del código fuente
Puedes iniciar la aplicación directamente corriendo el script:
```bash
python main.py
```

### Versión Ejecutable (.exe)
Si prefieres generar un ejecutable `.exe` portátil que no requiera abrir la consola:

1. Ejecuta el archivo `build.bat`.
2. Espera a que termine el proceso de PyInstaller.
3. Busca tu aplicación lista en la carpeta `dist/Tapo Viewer.exe`.
4. (Opcional) Puedes copiar ese `.exe` a tu Escritorio o donde prefieras.

## Uso de la Aplicación

- **Mover la ventana**: Simplemente arrastra el video con el clic izquierdo del mouse para reubicarlo.
- **Redimensionar**: Usa la esquina inferior derecha (el pequeño triángulo blanco) para cambiar el tamaño a gusto.
- **Ocultar/Ajustes**: Busca el ícono negro de la cámara en la bandeja de iconos (cerca de la hora en Windows). Haz clic derecho para ver las opciones de configuración, ocultarlo o cerrarlo.
- **Conectar tu cámara**: Ve a "Configuración" (click derecho en el ícono del área de notificación) e introduce la IP local de tu cámara Tapo (ej. `192.168.1.41`) y las credenciales que creaste en la app móvil.

## Tecnologías Utilizadas
- **PyQt6**: Para la creación de la interfaz sin bordes y manejo de eventos.
- **python-vlc**: Como *wrapper* del motor libVLC para reproducir video de baja latencia con aceleración por hardware.
- **PyInstaller**: Para el empaquetado del software en un ejecutable autocontenido.
