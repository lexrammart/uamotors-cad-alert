<p align="center">
  <a href="https://uamotors.github.io/">
    <img src="assets/1.completo.svg" width="400" alt="UAMOTORS Logo">
  </a>
</p>

# UAMOTORS CAD Alert Monitor

*English documentation below.*

Monitor silencioso en segundo plano para archivos de ensamblaje de SolidWorks.

**[Visita el sitio web del equipo UAMOTORS](https://uamotors.github.io/)**

Esta aplicación monitorea en tiempo real los archivos de ensamblaje de SolidWorks dentro del directorio de Google Drive del equipo y envía actualizaciones de estado (quién está editando qué) a un canal de Discord de forma automática.

## Descarga e Instalación

1. Ve a la sección de **[Releases](../../releases/latest)** en el lado derecho de este repositorio.
2. Descarga la versión más reciente ubicada bajo la sección **Assets** (el archivo se llama `UAMOTORS CAD ALERT.exe`).
3. Ejecuta el archivo descargado.

**Aviso sobre Windows SmartScreen (Pantalla Azul):**
Como esta es una aplicación interna del equipo y no tiene un certificado comercial, Windows mostrará una pantalla azul indicando "Windows protegió su PC". Para continuar con la instalación:
* Haz clic en el texto **"Más información"**.
* Aparecerá un nuevo botón en la parte inferior derecha. Haz clic en **"Ejecutar de todas formas"**.

4. Al abrirse, ingresa tu correo institucional para vincular tu equipo.
5. El sistema se instalará automáticamente en segundo plano y se ejecutará solo cada vez que enciendas tu computadora. No necesitas volver a abrir el archivo manualmente.

## Características ⚙️

* **Motor C# (.NET 8):** Alto rendimiento y muy bajo consumo de memoria RAM.
* **Actualizaciones OTA:** Descarga e instala nuevas versiones automáticamente en segundo plano.
* **Auto-Arranque:** Se ancla de forma segura al Registro de Windows (Run Key) sin necesidad de permisos de administrador.

---

# English Documentation

A silent, background monitor for SolidWorks assemblies.

This application monitors SolidWorks assembly files within a local or cloud-synced directory and sends real-time status updates to a Discord webhook.

## Download & Installation

1. Go to the **[Releases](../../releases/latest)** section on the right side of this repository.
2. Download the latest release under the **Assets** section (the file is named `UAMOTORS CAD ALERT.exe`).
3. Run the downloaded executable.

**Windows SmartScreen Bypass:**
Since this is an internal tool without a commercial certificate, Windows will display a blue warning screen saying "Windows protected your PC". To bypass this:
* Click on **"More info"**.
* Click on the **"Run anyway"** button that appears.

4. Once the app opens, enter your institutional email to link your device.
5. The system will automatically install itself in the background and configure Windows to run it on startup. You do not need to manually open the file again.

## Core Features ⚙️

* **C# (.NET 8) Engine:** High performance and minimal memory footprint.
* **OTA Updates:** Automatically downloads and applies new updates in the background.
* **Auto-Start Integration:** Safely hooks into the Windows Registry Run Key without requiring administrator privileges.
