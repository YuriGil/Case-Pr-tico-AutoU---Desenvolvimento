import os
import sys
from pathlib import Path

if __name__ == "__main__":
    # Adiciona o diretório backend ao path
    backend_dir = Path(__file__).parent / "backend"
    sys.path.insert(0, str(backend_dir))
    
    # Verifica se requirements estão instalados
    try:
        import uvicorn
        from fastapi import FastAPI
    except ImportError:
        print("Instalando dependências...")
        os.system(f"{sys.executable} -m pip install -r {backend_dir}/requirements.txt")
    
    # Inicia o servidor
    os.chdir(backend_dir)
    os.system(f"{sys.executable} -m uvicorn app:app --reload --host 0.0.0.0 --port 8000")