# Painel de Status da Raspberry Pi

Atividade extra 1 de Nanocomputadores (Atitus - CC).
Pagina web que mostra o estado da Raspberry: CPU, temperatura, memoria, disco, IP e tempo ligada.

## Integrantes

- Bruno Benetti
- Patrick M.
- Luiz Eduardo Tremea

## Como funciona

- `sistema.py` -> le as informacoes reais da Raspberry (usa `psutil`, o arquivo `/sys/class/thermal/thermal_zone0/temp` e alguns comandos do Linux)
- `app.py` -> servidor Flask com as rotas
- `templates/index.html` + `static/` -> pagina que mostra os dados

O JavaScript chama `/api/status` a cada 5 segundos (ou no botao) e atualiza a tela sem recarregar.
Se alguma informacao nao puder ser lida aparece "indisponivel" e o resto continua funcionando.

### Cores dos cards

| Item | Amarelo | Vermelho |
|------|---------|----------|
| CPU | 60% | 85% |
| Temperatura | 60 °C | 75 °C |
| Memoria | 70% | 90% |
| Disco | 75% | 90% |

## Rotas

- `/` -> painel
- `/api/status` -> dados em JSON
- `/api/historico` -> ultimas 20 leituras

## Como rodar na Raspberry

```bash
git clone https://github.com/EduTremea/Atividades-Extras-Raspberry.git
cd Atividades-Extras-Raspberry/atividade1-painel-status
python -m venv env
source env/bin/activate
pip install -r requirements.txt

sudo ufw allow 5000
python app.py
```

Depois e so abrir `http://IP_DA_RASP:5000` em outro computador da mesma rede.
