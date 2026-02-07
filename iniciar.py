"""Script para iniciar o servidor"""
import sys
import subprocess

if __name__ == "__main__":
    print("Iniciando servidor Mentor de Escrita IA...")
    print("API: http://localhost:8000")
    print("Docs: http://localhost:8000/docs")
    print("")
    print("Pressione Ctrl+C para parar o servidor")
    print("")
    
    # Usar subprocess para garantir que funciona
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn",
            "app.main:app",
            "--reload",
            "--host", "0.0.0.0",
            "--port", "8000"
        ])
    except KeyboardInterrupt:
        print("\n\nServidor encerrado.")
        sys.exit(0)

