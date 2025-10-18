# Hermes Frontend (SACI Project)

Este es el frontend de la aplicación Hermes, desarrollado con React Native y Expo.

## Requisitos Previos

- Node.js (v18 o superior)
- npm o yarn
- Expo Go app en tu dispositivo móvil (iOS o Android) o un emulador de Android Studio / Xcode.

## Instalación

1.  **Navega al directorio del frontend:**
    ```bash
    cd frontend
    ```

2.  **Instala las dependencias:**
    ```bash
    npm install
    ```

## Ejecución

1.  **Inicia el servidor de desarrollo de Expo:**
    ```bash
    npm start
    ```
    O también puedes usar:
    ```bash
    npx expo start
    ```

2.  **Abre la aplicación:**
    -   Se abrirá una pestaña en tu navegador con el Metro Bundler.
    -   Escanea el código QR que aparece con la aplicación Expo Go en tu teléfono.
    -   Alternativamente, puedes presionar `a` para abrir en un emulador de Android o `i` para un simulador de iOS (si tienes Xcode).

## Conexión con el Backend

El cliente de la API (en `api/client.js`) está configurado por defecto para conectarse a `http://127.0.0.1:8000`.

-   **Si usas un emulador de Android**, cambia esta URL a `http://10.0.2.2:8000`.
-   **Si usas un dispositivo físico**, asegúrate de que esté en la misma red Wi-Fi que tu computadora y cambia la URL a la dirección IP de tu máquina (ej. `http://192.168.1.100:8000`).