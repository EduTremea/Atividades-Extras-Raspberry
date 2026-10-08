# Funcoes que pegam a configuracao de rede da Raspberry e fazem os testes de ping

import socket
import subprocess
from datetime import datetime

import psutil

import config


def agora():
    return datetime.now().strftime("%d/%m/%Y %H:%M:%S")


def rota_padrao():
    # o comando "ip route show default" devolve algo assim:
    # default via 192.168.1.1 dev wlan0 proto dhcp src 192.168.1.111 metric 600
    try:
        saida = subprocess.check_output(["ip", "route", "show", "default"], text=True)
        partes = saida.split()
        gateway = partes[partes.index("via") + 1]
        interface = partes[partes.index("dev") + 1]
        return gateway, interface
    except Exception:
        return None, None


def dados_interface(interface):
    ip = None
    mascara = None
    ligada = None

    try:
        for endereco in psutil.net_if_addrs().get(interface, []):
            if endereco.family == socket.AF_INET:  # so ipv4
                ip = endereco.address
                mascara = endereco.netmask
    except Exception:
        pass

    try:
        ligada = psutil.net_if_stats()[interface].isup
    except Exception:
        pass

    return ip, mascara, ligada


def tipo_conexao(interface):
    if interface is None:
        return None
    if interface.startswith("wlan"):
        return "Wi-Fi"
    if interface.startswith("eth") or interface.startswith("en"):
        return "Cabeada"
    return "Outro"


def nome_wifi():
    # iwgetid -r mostra o nome da rede wifi conectada
    try:
        nome = subprocess.check_output(["iwgetid", "-r"], text=True).strip()
        return nome or None
    except Exception:
        return None


def servidores_dns():
    dns = []
    try:
        with open("/etc/resolv.conf") as arquivo:
            for linha in arquivo:
                if linha.startswith("nameserver"):
                    dns.append(linha.split()[1])
    except Exception:
        pass
    return dns


def info_rede():
    gateway, interface = rota_padrao()
    ip, mascara, ligada = dados_interface(interface) if interface else (None, None, None)

    if ligada is None:
        estado = None
    else:
        estado = "Conectada" if ligada else "Desconectada"

    return {
        "hostname": socket.gethostname(),
        "interface": interface,
        "tipo": tipo_conexao(interface),
        "wifi": nome_wifi() if interface and interface.startswith("wlan") else None,
        "estado": estado,
        "ip": ip,
        "mascara": mascara,
        "gateway": gateway,
        "dns": servidores_dns(),
        "verificado_em": agora(),
    }


def fazer_ping(destino, descricao):
    resultado = {
        "destino": destino,
        "descricao": descricao,
        "status": "falha",
        "tempo_ms": None,
        "perda": None,
        "testado_em": agora(),
        "mensagem": "",
    }

    if not destino:
        resultado["mensagem"] = "Destino nao encontrado"
        return resultado

    try:
        # -c = quantidade de pacotes, -W = espera no maximo 2s por resposta
        processo = subprocess.run(
            ["ping", "-c", str(config.QUANTIDADE_PINGS), "-W", "2", destino],
            capture_output=True, text=True, timeout=15
        )
    except subprocess.TimeoutExpired:
        resultado["mensagem"] = "Demorou demais para responder"
        return resultado
    except Exception as erro:
        resultado["mensagem"] = "Erro ao executar o ping: " + str(erro)
        return resultado

    saida = processo.stdout

    # pega a perda de pacotes. linha: "3 packets transmitted, 3 received, 0% packet loss"
    for linha in saida.splitlines():
        if "packet loss" in linha:
            for pedaco in linha.split(","):
                if "packet loss" in pedaco:
                    resultado["perda"] = float(pedaco.strip().split("%")[0])

        # tempo medio. linha: "rtt min/avg/max/mdev = 1.1/2.2/3.3/0.4 ms"
        if linha.startswith("rtt") or linha.startswith("round-trip"):
            valores = linha.split("=")[1].strip().split("/")
            resultado["tempo_ms"] = float(valores[1])

    if processo.returncode != 0 or resultado["perda"] == 100:
        if "unknown host" in processo.stderr.lower() or "name or service" in processo.stderr.lower():
            resultado["mensagem"] = "Nao conseguiu resolver o nome (DNS)"
        else:
            resultado["mensagem"] = "Sem resposta"
        resultado["status"] = "falha"
    elif resultado["perda"] and resultado["perda"] > 0:
        resultado["status"] = "atencao"
        resultado["mensagem"] = "Perdeu alguns pacotes"
    elif resultado["tempo_ms"] is not None and resultado["tempo_ms"] > config.LIMITE_ATENCAO_MS:
        resultado["status"] = "atencao"
        resultado["mensagem"] = "Resposta lenta"
    else:
        resultado["status"] = "ok"
        resultado["mensagem"] = "Respondendo normalmente"

    return resultado


def testar_destinos(gateway):
    testes = []
    testes.append(fazer_ping(gateway, "Gateway (roteador)"))
    testes.append(fazer_ping(config.DESTINO_LOCAL, "Equipamento da rede local"))
    for destino in config.DESTINOS_EXTERNOS:
        testes.append(fazer_ping(destino, "Externo"))
    return testes
