import os
import subprocess
import sys

# --- [ ðŸ›ï¸ OMEGA BINARY FACTORY v1.0 ] ---
# Autor: Antigravity Î© Swarm Controller
# Objetivo: Gerar o binÃ¡rio de execuÃ§Ã£o soberana diretamente no Drive D.

# ConfiguraÃ§Ãµes do Blueprint
DRIVE_D_NAME = "D:"
DRIVE_D_PATH = "D:\\"
PROJECT_DIR = r"C:\Users\janio\omega-acoustic-resonance"
SOURCE_FILE = os.path.join(PROJECT_DIR, "src", "daemon.py")
OUTPUT_NAME = "OMEGA_PORTAL_CORE"

def build():
    print(f"--- [ INICIANDO CONSTRUÃ‡ÃƒO SOBERANA NO DRIVE D: ] ---")
    
    # 1. ValidaÃ§Ã£o de Handshake FÃ­sico (Pendrive)
    if not os.path.exists(DRIVE_D_PATH):
        print(f"âŒ ERRO: DRIVE {DRIVE_D_NAME} (AIR-GAP) NÃƒO DETECTADO!")
        print("Por favor, reconecte o pendrive para iniciar a injeÃ§Ã£o do binÃ¡rio.")
        return

    # 2. Comando de Empacotamento
    # --onefile: Ãšnico binÃ¡rio
    # --noconsole: Sem terminal pop-up
    # --distpath: Destino final (Drive D)
    # --add-data: Inclui bibliotecas internas do 'src'
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--noconsole",
        f"--distpath={DRIVE_D_PATH}",
        f"--workpath={os.path.join(PROJECT_DIR, 'build')}",
        f"--specpath={PROJECT_DIR}",
        f"--name={OUTPUT_NAME}",
        f"--add-data=src;src",
        SOURCE_FILE
    ]
    
    print(f"Executando Build Deterministico: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=True)
        print(f"\n[ OK ] SUCESSO: O BINARIO SOBERANO '{OUTPUT_NAME}.exe' FOI INJETADO NO DRIVE D!")
    except Exception as e:
        print(f"[ ERRO ] ERRO NA CONSTRUCAO: {str(e).encode('ascii', 'ignore').decode('ascii')}")

if __name__ == "__main__":
    build()
