# Monitor de Rede Local - Raspberry Pi

Atividade extra 2 de Nanocomputadores (Atitus - CC).
Aplicacao web que mostra a configuracao de rede da Raspberry e testa a comunicacao com o gateway, com outro equipamento da rede e com a internet.

## Integrantes

- Bruno Benetti
- Patrick M.
- Luiz Eduardo Tremea

## Arquivos

- `config.py` -> destinos que vao ser testados (trocar o `DESTINO_LOCAL` pelo ip certo)
- `rede.py` -> pega IP, mascara, gateway, DNS e faz os pings
- `app.py` -> servidor Flask
- `templates/` e `static/` -> pagina

## De onde vem cada informacao

| Informacao | Como pegamos |
|-----------|--------------|
| Gateway e interface | comando `ip route show default` |
| IP e mascara | `psutil.net_if_addrs()` |
| Estado da interface | `psutil.net_if_stats()` |
| Nome do wifi | comando `iwgetid -r` |
| DNS | arquivo `/etc/resolv.conf` |
| Testes | comando `ping -c 3 -W 2 <destino>` |

## Regra das cores

- **OK**: respondeu tudo e o tempo medio ficou abaixo de 100 ms
- **ATENCAO**: perdeu algum pacote ou passou de 100 ms
- **FALHA**: nao respondeu ou nao conseguiu resolver o nome

Se um destino cair o painel continua funcionando, so aquele destino fica vermelho.
A aplicacao so faz ping nos destinos configurados, nao faz varredura da rede.

## Como rodar

```bash
git clone <link do repositorio>
cd rasp-monitor-rede
python -m venv env
source env/bin/activate
pip install -r requirements.txt

sudo ufw allow 5000
python app.py
```

Abrir `http://IP_DA_RASP:5000` em outro computador da rede.
