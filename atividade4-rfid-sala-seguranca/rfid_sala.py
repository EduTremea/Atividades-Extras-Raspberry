import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
from datetime import datetime
import time

# Pinos no modo BOARD. O RFID usa os pinos padrao da biblioteca (24, 23, 19, 21, 22)
LED_VERDE = 11     # GPIO17
LED_VERMELHO = 13  # GPIO27

# Cadastro: troque os IDs pelos das suas tags (rode o programa e veja o ID impresso)
COLABORADORES = {
    111111111111: {"nome": "Luiz", "acesso": True},
    222222222222: {"nome": "Bruno", "acesso": True},
    333333333333: {"nome": "Patrick", "acesso": False},
}

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(LED_VERDE, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(LED_VERMELHO, GPIO.OUT, initial=GPIO.LOW)

leitor = SimpleMFRC522()

dentro_da_sala = {}   # tag -> horario de entrada
tempo_na_sala = {}    # (nome, data) -> segundos acumulados
entrou_hoje = set()   # (tag, data) de quem ja entrou no dia
tentativas_negadas = {}  # nome -> quantidade
invasoes = 0
ultima_leitura = {}   # tag -> horario, evita ler o mesmo cartao varias vezes seguidas


def acender(led, segundos):
    GPIO.output(led, GPIO.HIGH)
    time.sleep(segundos)
    GPIO.output(led, GPIO.LOW)


def piscar(led, vezes):
    for _ in range(vezes):
        GPIO.output(led, GPIO.HIGH)
        time.sleep(0.2)
        GPIO.output(led, GPIO.LOW)
        time.sleep(0.2)


def formatar(segundos):
    segundos = int(segundos)
    return f"{segundos // 3600:02d}:{segundos % 3600 // 60:02d}:{segundos % 60:02d}"


def somar_tempo(nome, entrada, saida):
    chave = (nome, entrada.strftime("%d/%m/%Y"))
    tempo_na_sala[chave] = tempo_na_sala.get(chave, 0) + (saida - entrada).total_seconds()


def tratar_tag(tag):
    global invasoes
    agora = datetime.now()
    hoje = agora.strftime("%d/%m/%Y")

    # Tag que nao esta no cadastro: possivel invasao
    if tag not in COLABORADORES:
        invasoes += 1
        print(f"Identificação não encontrada! (ID {tag})")
        piscar(LED_VERMELHO, 10)
        return

    nome = COLABORADORES[tag]["nome"]

    # Cadastrado mas sem permissao para o projeto
    if not COLABORADORES[tag]["acesso"]:
        tentativas_negadas[nome] = tentativas_negadas.get(nome, 0) + 1
        print(f"Você não tem acesso a este projeto, {nome}")
        acender(LED_VERMELHO, 5)
        return

    # Se ja esta na sala, essa leitura e a saida
    if tag in dentro_da_sala:
        entrada = dentro_da_sala.pop(tag)
        somar_tempo(nome, entrada, agora)
        print(f"Saída registrada: {nome} às {agora:%H:%M:%S} (ficou {formatar((agora - entrada).total_seconds())})")
        acender(LED_VERDE, 5)
        return

    # Entrada
    if (tag, hoje) in entrou_hoje:
        print(f"Bem-vindo de volta, {nome}")
    else:
        print(f"Bem-vindo, {nome}")
        entrou_hoje.add((tag, hoje))
    dentro_da_sala[tag] = agora
    print(f"Entrada registrada às {agora:%H:%M:%S}")
    acender(LED_VERDE, 5)


def relatorio():
    agora = datetime.now()
    # Fecha o tempo de quem ainda estava na sala
    for tag, entrada in dentro_da_sala.items():
        somar_tempo(COLABORADORES[tag]["nome"], entrada, agora)

    print("\n========== RELATÓRIO ==========")
    print("\nTempo na sala:")
    if tempo_na_sala:
        for (nome, data), segundos in tempo_na_sala.items():
            print(f"  {nome} ({data}): {formatar(segundos)}")
    else:
        print("  Nenhum acesso registrado")

    print("\nTentativas de acesso não autorizado:")
    if tentativas_negadas:
        for nome, qtd in tentativas_negadas.items():
            print(f"  {nome}: {qtd} tentativa(s)")
    else:
        print("  Nenhuma")

    print(f"\nTentativas de invasão (tag desconhecida): {invasoes}")
    print("===============================")


try:
    print("Aproxime o crachá do leitor...")
    while True:
        tag = leitor.read_id_no_block()
        if tag is not None:
            # Ignora o mesmo cartao se ele foi lido ha menos de 3 segundos
            if time.time() - ultima_leitura.get(tag, 0) > 3:
                tratar_tag(tag)
                print("\nAproxime o crachá do leitor...")
            ultima_leitura[tag] = time.time()
        time.sleep(0.1)

except KeyboardInterrupt:
    relatorio()
finally:
    GPIO.cleanup()
