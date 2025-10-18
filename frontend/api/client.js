import axios from 'axios';

// Asegúrate de que esta URL sea la correcta para tu emulador/dispositivo.
// Para Android Studio Emulator, normalmente es http://10.0.2.2:8000
// Para un dispositivo físico en la misma red, usa la IP de tu máquina.
const baseURL = 'http://127.0.0.1:8000';

const apiClient = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export default apiClient;