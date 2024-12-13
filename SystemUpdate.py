import cv2
import mss
import numpy as np
import socket
import random
import time
import os
import subprocess
from flask import Flask, Response

# Configuração do servidor Flask
app = Flask(__name__)

# Função para capturar a tela continuamente
def capture_screen():
    with mss.mss() as sct:
        monitor = sct.monitors[1]  # Captura a tela inteira (monitor principal)
        while True:
            try:
                # Captura a tela
                frame = sct.grab(monitor)
                img = np.array(frame)  # Converte para array numpy
                img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)  # Converte BGRA para BGR
                _, jpeg = cv2.imencode('.jpg', img)  # Codifica como JPEG
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')

                # Intervalo aleatório entre capturas
                interval = random.randint(2, 8)
                time.sleep(interval)

                # Força o foco da janela do programa
                set_window_to_foreground()
            except:
                pass  # Suprime qualquer erro para evitar interrupções

# Rota para fornecer o stream de vídeo
@app.route('/video_feed')
def video_feed():
    return Response(capture_screen(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Página inicial para exibir o feed
@app.route('/')
def index():
    return f"""
    <html>
        <head>
            <title>Transmissão da Tela</title>
        </head>
        <body>
            <h1>Transmissão ao Vivo da Tela</h1>
            <p>Acesse este endereço em outros dispositivos: <b>http://{get_local_ip()}:8080/video_feed</b></p>
            <img src="/video_feed" style="width: 100%; height: auto;" />
        </body>
    </html>
    """

# Função para detectar o IP local
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

# Definir prioridade máxima do processo no Windows
def set_high_priority():
    if os.name == 'nt':  # Somente para Windows
        try:
            import win32process
            import win32api
            import win32con
            pid = os.getpid()  # Obtém o PID do processo atual
            handle = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, True, pid)
            win32process.SetPriorityClass(handle, win32process.REALTIME_PRIORITY_CLASS)
        except:
            pass  # Suprime erros silenciosamente

# Forçar o foco da janela no Windows
def set_window_to_foreground():
    if os.name == 'nt':  # Somente para Windows
        try:
            import win32gui
            import win32con
            import ctypes

            hwnd = ctypes.windll.kernel32.GetConsoleWindow()  # Obtém o handle da janela
            if hwnd:
                ctypes.windll.user32.ShowWindow(hwnd, win32con.SW_RESTORE)  # Restaura a janela
                ctypes.windll.user32.SetForegroundWindow(hwnd)  # Traz para frente
        except:
            pass  # Suprime erros silenciosamente

# Inicialização do servidor Flask
if __name__ == '__main__':
    # Define prioridade máxima no Windows
    if os.name == 'nt':
        set_high_priority()

    # Ocultar a janela do script (somente no Windows)
    if os.name == 'nt':
        import ctypes
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

    # Abrir o navegador automaticamente
    try:
        local_ip = get_local_ip()
        url = f"http://{local_ip}:8080"
        subprocess.Popen(['start', url], shell=True)
    except:
        pass  # Suprime qualquer erro ao tentar abrir o navegador

    # Iniciar o servidor Flask
    app.run(host='0.0.0.0', port=8080, debug=False)
