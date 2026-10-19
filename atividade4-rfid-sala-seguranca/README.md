# Sala de Seguranca com RFID

Atividade de Nanocomputadores (Atitus - CC).
Controle de acesso a sala de um projeto sob NDA usando a Raspberry Pi e o leitor RFID MFRC522.

## Integrantes

- Bruno Benetti
- Patrick M.
- Luiz Eduardo Tremea

## Arquivos

- `rfid_sala.py` -> versao base da atividade (LEDs + relatorio na tela)
- `rfid_sala_bonus.py` -> versao com o bonus (buzzer com som diferente pra cada caso + arquivo `.csv`)

## Ligacoes (modo BOARD)

| MFRC522 | Raspberry |
|---------|-----------|
| SDA | 24 (GPIO8) |
| SCK | 23 (GPIO11) |
| MOSI | 19 (GPIO10) |
| MISO | 21 (GPIO9) |
| IRQ | - |
| GND | 6 |
| RST | 22 (GPIO25) |
| 3,3V | 1 (3,3V) |

| Componente | Pino |
|------------|------|
| LED verde | 11 (GPIO17) |
| LED vermelho | 13 (GPIO27) |
| Buzzer (so no bonus) | 12 (GPIO18) |

Os LEDs vao com resistor e o outro lado no GND.

## Como rodar

Ativar o SPI: `sudo raspi-config` -> Interfacing Options -> SPI -> Enable (as vezes precisa reiniciar).

```bash
cd Atividades-Extras-Raspberry/atividade4-rfid-sala-seguranca
python -m venv env
source env/bin/activate
pip install -r requirements.txt

python rfid_sala.py        # versao base
python rfid_sala_bonus.py  # versao com bonus
```

Antes de usar, trocar os IDs de exemplo no dicionario `COLABORADORES` pelos IDs dos crachas. E so passar o cracha no leitor que o ID aparece na tela junto com "Identificação não encontrada!".

## Como funciona

- Tag com acesso, primeira vez no dia: "Bem-vindo, {nome}" e LED verde por 5 s
- Tag com acesso, ja entrou hoje: "Bem-vindo de volta, {nome}" e LED verde por 5 s
- Tag cadastrada sem acesso: "Você não tem acesso a este projeto, {nome}" e LED vermelho por 5 s
- Tag que nao esta cadastrada: "Identificação não encontrada!" e 10 piscadas do vermelho

A primeira leitura do cracha registra a entrada e a seguinte registra a saida, sempre alternando. O mesmo cartao e ignorado por 3 s depois de cada leitura pra nao contar duas vezes.

Ao apertar Ctrl+C sai o relatorio com o tempo de cada colaborador na sala, as tentativas de quem nao tem acesso (nome e quantidade) e o numero de tentativas de invasao. Quem ainda estava na sala tem o tempo fechado na hora do relatorio.

## Bonus

Sons do buzzer:

- Entrada/saida autorizada: dois bipes curtos e agudos
- Acesso negado: um bipe grave e longo
- Invasao: sirene alternando agudo e grave junto com as piscadas

Com piezo passivo cada caso tem um tom diferente. Com piezo ativo a frequencia e sempre a mesma, mas o padrao dos bipes muda.

No Ctrl+C tambem e gerado o arquivo `acessos_AAAAMMDD_HHMMSS.csv`, com uma linha por evento:

| Coluna | Conteudo |
|--------|----------|
| data_hora | `AAAA-MM-DD HH:MM:SS` |
| tag_id | ID do cracha |
| nome | nome do colaborador (vazio em invasao) |
| evento | `entrada`, `saida`, `saida_encerramento`, `acesso_negado` ou `invasao` |
| duracao_segundos | tempo na sala (so nas saidas) |

Pra abrir no Pandas:

```python
import pandas as pd
df = pd.read_csv("acessos_20261019_203140.csv", parse_dates=["data_hora"])
```
