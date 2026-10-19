import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
from datetime import datetime
import csv
import time

# Pinos no modo BOARD. O RFID usa os pinos padrao da biblioteca (24, 23, 19, 21, 22)
LED_VERDE = 11     # GPIO17
LED_VERMELHO = 13  # GPIO27
BUZZER = 12        # GPIO18 (piezo)

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
GPIO.setup(BUZZER, GPIO.OUT, initial=GPIO.LOW)

leitor = SimpleMFRC522()
buzzer = GPIO.PWM(BUZZER, 1000)

dentro_da_sala = {}      # tag -> horario de entrada
tempo_na_sala = {}       # (nome, data) -> segundos acumulados
entrou_hoje = set()      # (tag, data) de quem ja entrou no dia
tentativas_negadas = {}  # nome -> quantidade
invasoes = 0
ultima_leitura = {}      # tag -> horario, evita ler o mesmo cartao varias vezes seguidas
eventos = []             # linhas que vao para o CSV


# ---------- Sons ----------

def tocar(frequencia, duracao):
    buzzer.ChangeFrequency(frequencia)
    buzzer.start(50)
    time.sleep(duracao)
    buzzer.stop()


def som_autorizado():
    # Dois bipes agudos e curtos
    tocar(2000, 0.1)
    time.sleep(0.05)
    tocar(2500, 0.1)


def som_negado():
    # Um bipe grave e longo
    tocar(400, 0.8)


def som_invasao_e_pisca():
    # Sirene alternando agudo/grave junto com as 10 piscadas do vermelho
    for i in range(10):
        GPIO.output(LED_VERMELHO, GPIO.HIGH)
        tocar(1800 if i % 2 == 0 else 900, 0.2)
        GPIO.output(LED_VERMELHO, GPIO.LOW)
        time.sleep(0.2)


# ---------- Auxiliares ----------

def acender(led, segundos):
    GPIO.output(led, GPIO.HIGH)
    time.sleep(segundos)
    GPIO.output(led, GPIO.LOW)


def formatar(segundos):
    segundos = int(segundos)
    return f"{segundos // 3600:02d}:{segundos % 3600 // 60:02d}:{segundos % 60:02d}"


def somar_tempo(nome, entrada, saida):
    chave = (nome, entrada.strftime("%d/%m/%Y"))
    tempo_na_sala[chave] = tempo_na_sala.get(chave, 0) + (saida - entrada).total_seconds()


def registrar(momento, tag, nome, evento, duracao=""):
    eventos.append({
        "data_hora": momento.strftime("%Y-%m-%d %H:%M:%S"),
        "tag_id": tag,
        "nome": nome,
        "evento": evento,
        "duracao_segundos": duracao,
    })


# ---------- Logica principal ----------

def tratar_tag(tag):
    global invasoes
    agora = datetime.now()
    hoje = agora.strftime("%d/%m/%Y")

    # Tag que nao esta no cadastro: possivel invasao
    if tag not in COLABORADORES:
        invasoes += 1
        print(f"Identificação não encontrada! (ID {tag})")
        registrar(agora, tag, "", "invasao")
        som_invasao_e_pisca()
        return

    nome = COLABORADORES[tag]["nome"]

    # Cadastrado mas sem permissao para o projeto
    if not COLABORADORES[tag]["acesso"]:
        tentativas_negadas[nome] = tentativas_negadas.get(nome, 0) + 1
        print(f"Você não tem acesso a este projeto, {nome}")
        registrar(agora, tag, nome, "acesso_negado")
        GPIO.output(LED_VERMELHO, GPIO.HIGH)
        som_negado()
        time.sleep(4.2)  # completa os 5 segundos com o som
        GPIO.output(LED_VERMELHO, GPIO.LOW)
        return

    # Se ja esta na sala, essa leitura e a saida
    if tag in dentro_da_sala:
        entrada = dentro_da_sala.pop(tag)
        duracao = (agora - entrada).total_seconds()
        somar_tempo(nome, entrada, agora)
        print(f"Saída registrada: {nome} às {agora:%H:%M:%S} (ficou {formatar(duracao)})")
        registrar(agora, tag, nome, "saida", int(duracao))
        GPIO.output(LED_VERDE, GPIO.HIGH)
        som_autorizado()
        time.sleep(4.75)
        GPIO.output(LED_VERDE, GPIO.LOW)
        return

    # Entrada
    if (tag, hoje) in entrou_hoje:
        print(f"Bem-vindo de volta, {nome}")
    else:
        print(f"Bem-vindo, {nome}")
        entrou_hoje.add((tag, hoje))
    dentro_da_sala[tag] = agora
    print(f"Entrada registrada às {agora:%H:%M:%S}")
    registrar(agora, tag, nome, "entrada")
    GPIO.output(LED_VERDE, GPIO.HIGH)
    som_autorizado()
    time.sleep(4.75)
    GPIO.output(LED_VERDE, GPIO.LOW)


def relatorio():
    agora = datetime.now()
    # Fecha o tempo de quem ainda estava na sala
    for tag, entrada in dentro_da_sala.items():
        nome = COLABORADORES[tag]["nome"]
        duracao = (agora - entrada).total_seconds()
        somar_tempo(nome, entrada, agora)
        registrar(agora, tag, nome, "saida_encerramento", int(duracao))

    linha = "+" + "-" * 22 + "+" + "-" * 12 + "+" + "-" * 10 + "+"
    print("\n" + "=" * 46)
    print(f"{'RELATÓRIO DE ACESSOS':^46}")
    print("=" * 46)

    print("\nTempo de permanência na sala")
    print(linha)
    print(f"| {'Colaborador':<20} | {'Data':<10} | {'Tempo':<8} |")
    print(linha)
    for (nome, data), segundos in tempo_na_sala.items():
        print(f"| {nome:<20} | {data:<10} | {formatar(segundos):<8} |")
    if not tempo_na_sala:
        print(f"| {'Nenhum acesso registrado':<44} |")
    print(linha)

    print("\nTentativas de acesso não autorizado")
    for nome, qtd in tentativas_negadas.items():
        print(f"  {nome}: {qtd} tentativa(s)")
    if not tentativas_negadas:
        print("  Nenhuma")

    print(f"\nTentativas de invasão (tag desconhecida): {invasoes}")

    # CSV com todos os eventos, separado por virgula e com cabecalho
    arquivo = f"acessos_{agora:%Y%m%d_%H%M%S}.csv"
    with open(arquivo, "w", newline="", encoding="utf-8") as f:
        campos = ["data_hora", "tag_id", "nome", "evento", "duracao_segundos"]
        escritor = csv.DictWriter(f, fieldnames=campos)
        escritor.writeheader()
        escritor.writerows(eventos)
    print(f"\nArquivo gerado: {arquivo}")
    print("=" * 46)


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
    buzzer.stop()
    GPIO.cleanup()
