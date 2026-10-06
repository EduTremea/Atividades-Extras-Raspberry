# Funcoes que pegam as informacoes da Raspberry
# cada funcao tem seu try/except, se uma falhar o resto do painel continua

import socket
import subprocess
import time
import platform
from datetime import datetime

import psutil


def pegar_hostname():
    try:
        return socket.gethostname()
    except Exception:
        return None


def pegar_ip():
    # truque: abre um socket UDP pra fora e ve qual ip a placa usou
    # (nao manda nenhum pacote de verdade)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        pass

    # se nao tiver internet tenta pelo comando hostname -I
    try:
        saida = subprocess.check_output(["hostname", "-I"], text=True)
        return saida.split()[0]
    except Exception:
        return None


def pegar_uptime():
    try:
        segundos = int(time.time() - psutil.boot_time())
    except Exception:
        return None

    dias = segundos // 86400
    horas = (segundos % 86400) // 3600
    minutos = (segundos % 3600) // 60
    return f"{dias}d {horas}h {minutos}min"


def pegar_cpu():
    try:
        return psutil.cpu_percent(interval=0.5)
    except Exception:
        return None


def pegar_temperatura():
    # na rasp a temperatura fica nesse arquivo, em milesimos de grau
    try:
        with open("/sys/class/thermal/thermal_zone0/temp") as arquivo:
            return round(int(arquivo.read()) / 1000, 1)
    except Exception:
        pass

    # segunda opcao: comando da propria raspberry
    try:
        saida = subprocess.check_output(["vcgencmd", "measure_temp"], text=True)
        # vem assim: temp=45.6'C
        return float(saida.replace("temp=", "").replace("'C", "").strip())
    except Exception:
        return None


def pegar_memoria():
    try:
        mem = psutil.virtual_memory()
        return {
            "total_mb": round(mem.total / 1024 / 1024),
            "usada_mb": round(mem.used / 1024 / 1024),
            "percentual": mem.percent,
        }
    except Exception:
        return None


def pegar_disco():
    try:
        disco = psutil.disk_usage("/")
        return {
            "total_gb": round(disco.total / 1024 ** 3, 1),
            "usado_gb": round(disco.used / 1024 ** 3, 1),
            "percentual": disco.percent,
        }
    except Exception:
        return None


def pegar_sistema_operacional():
    try:
        return f"{platform.system()} {platform.release()} ({platform.machine()})"
    except Exception:
        return None


def coletar_status():
    return {
        "hostname": pegar_hostname(),
        "ip": pegar_ip(),
        "uptime": pegar_uptime(),
        "cpu": pegar_cpu(),
        "temperatura": pegar_temperatura(),
        "memoria": pegar_memoria(),
        "disco": pegar_disco(),
        "sistema": pegar_sistema_operacional(),
        "atualizado_em": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
    }
