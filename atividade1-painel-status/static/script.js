let timer = null;

// devolve a classe de cor de acordo com o valor
function nivel(valor, limiteAtencao, limitePerigo) {
    if (valor === null) return "";
    if (valor >= limitePerigo) return "perigo";
    if (valor >= limiteAtencao) return "atencao";
    return "ok";
}

function mostrar(id, texto) {
    // se nao veio o dado mostra "indisponivel"
    document.getElementById(id).textContent = (texto === null || texto === undefined) ? "indisponivel" : texto;
}

function pintarCard(id, classe) {
    const card = document.getElementById(id);
    card.classList.remove("ok", "atencao", "perigo");
    if (classe) card.classList.add(classe);
}

async function atualizar() {
    try {
        const resposta = await fetch("/api/status");
        const dados = await resposta.json();

        mostrar("hostname", dados.hostname);
        mostrar("sistema", dados.sistema);
        mostrar("ip", dados.ip);
        mostrar("uptime", dados.uptime);
        mostrar("cpu", dados.cpu !== null ? dados.cpu + " %" : null);
        mostrar("temperatura", dados.temperatura !== null ? dados.temperatura + " °C" : null);

        if (dados.memoria) {
            mostrar("memoria", dados.memoria.percentual + " %");
            mostrar("memoria-detalhe", dados.memoria.usada_mb + " / " + dados.memoria.total_mb + " MB");
        } else {
            mostrar("memoria", null);
        }

        if (dados.disco) {
            mostrar("disco", dados.disco.percentual + " %");
            mostrar("disco-detalhe", dados.disco.usado_gb + " / " + dados.disco.total_gb + " GB");
        } else {
            mostrar("disco", null);
        }

        pintarCard("card-cpu", nivel(dados.cpu, 60, 85));
        pintarCard("card-temp", nivel(dados.temperatura, 60, 75));
        pintarCard("card-mem", nivel(dados.memoria ? dados.memoria.percentual : null, 70, 90));
        pintarCard("card-disco", nivel(dados.disco ? dados.disco.percentual : null, 75, 90));

        document.getElementById("atualizado").textContent = "Ultima atualizacao: " + dados.atualizado_em;
        document.getElementById("erro").textContent = "";

        carregarHistorico();
    } catch (e) {
        document.getElementById("erro").textContent = "Nao foi possivel buscar os dados da Raspberry.";
    }
}

async function carregarHistorico() {
    const resposta = await fetch("/api/historico");
    const lista = await resposta.json();
    const tbody = document.getElementById("tabela-historico");
    tbody.innerHTML = "";

    // mais recente primeiro
    lista.slice().reverse().forEach(item => {
        const linha = document.createElement("tr");
        linha.innerHTML =
            "<td>" + item.horario + "</td>" +
            "<td>" + (item.cpu ?? "-") + " %</td>" +
            "<td>" + (item.temperatura ?? "-") + " °C</td>" +
            "<td>" + (item.memoria ?? "-") + " %</td>";
        tbody.appendChild(linha);
    });
}

function ligarAuto() {
    if (document.getElementById("auto").checked) {
        timer = setInterval(atualizar, 5000);
    } else {
        clearInterval(timer);
    }
}

document.getElementById("btn-atualizar").addEventListener("click", atualizar);
document.getElementById("auto").addEventListener("change", ligarAuto);

atualizar();
ligarAuto();
