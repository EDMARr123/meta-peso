r"""
Gera o painel "Meta Peso" (painel.html) a partir de dados.json.

Versão enxuta do Melhoria Salarial: digita o código do RCA e vê só a
tabela de Peso por categoria, com uma Meta Peso editável por categoria
(igual o Meta Posit do original, mas usando peso em vez de positivação) —
a diferença (kg que faltam pra bater a meta) fica salva por RCA no
localStorage do navegador.
"""

import base64
import json
import os

PASTA_BASE = os.path.dirname(os.path.abspath(__file__))
CAMINHO_DADOS = os.path.join(PASTA_BASE, "dados.json")
CAMINHO_SAIDA = os.path.join(PASTA_BASE, "painel.html")

PASTA_FOTOS_RCAS = os.path.join(PASTA_BASE, "..", "painel_pilares", "fotos_rcas")


def _fotos_rcas_json():
    fotos = {}
    if os.path.isdir(PASTA_FOTOS_RCAS):
        for nome_pasta_supervisor in os.listdir(PASTA_FOTOS_RCAS):
            pasta_supervisor = os.path.join(PASTA_FOTOS_RCAS, nome_pasta_supervisor)
            if not os.path.isdir(pasta_supervisor):
                continue
            for nome_arquivo in os.listdir(pasta_supervisor):
                nome, ext = os.path.splitext(nome_arquivo)
                if ext.lower() not in (".jpg", ".jpeg", ".png"):
                    continue
                tipo_mime = "image/png" if ext.lower() == ".png" else "image/jpeg"
                with open(os.path.join(pasta_supervisor, nome_arquivo), "rb") as f:
                    b64 = base64.b64encode(f.read()).decode("ascii")
                fotos[nome.upper().strip()] = f"data:{tipo_mime};base64,{b64}"
    return json.dumps(fotos, ensure_ascii=False)


_FOTOS_RCAS_JSON = _fotos_rcas_json()

TEMPLATE = r"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Meta Peso — Equipe GYN</title>
<style>
:root {
  --bg: #F2F4F0; --surface: #FFFFFF; --surface-2: #F7F8F5; --border: #E2E5DD;
  --ink: #1C231C; --ink-soft: #5B655A; --ink-faint: #8B948A;
  --good: #1D9A5D; --good-soft: #E4F5EC; --bad: #C23B3B; --bad-soft: #FBEAEA;
  --accent: #1F7A5C; --accent-soft: #E1F1EA;
  --shadow: 0 1px 2px rgba(20,25,20,0.05), 0 10px 24px -14px rgba(20,25,20,0.18);
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --bg: #12160F; --surface: #1B211A; --surface-2: #212820; --border: #303A2E;
    --ink: #E9EEE6; --ink-soft: #AEBAA9; --ink-faint: #7C887A;
    --good: #3FC17F; --good-soft: #123625; --bad: #E2685F; --bad-soft: #3A1D1B;
    --accent: #3FC17F; --accent-soft: #17301F;
    --shadow: 0 1px 2px rgba(0,0,0,0.35), 0 12px 28px -14px rgba(0,0,0,0.6);
  }
}
:root[data-theme="dark"] {
  --bg: #12160F; --surface: #1B211A; --surface-2: #212820; --border: #303A2E;
  --ink: #E9EEE6; --ink-soft: #AEBAA9; --ink-faint: #7C887A;
  --good: #3FC17F; --good-soft: #123625; --bad: #E2685F; --bad-soft: #3A1D1B;
  --accent: #3FC17F; --accent-soft: #17301F;
  --shadow: 0 1px 2px rgba(0,0,0,0.35), 0 12px 28px -14px rgba(0,0,0,0.6);
}
* { box-sizing: border-box; }
body { margin: 0; background: var(--bg); color: var(--ink); font-family: ui-sans-serif, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; -webkit-font-smoothing: antialiased; }
.wrap { max-width: 760px; margin: 0 auto; padding: 24px 20px 64px; }
header.top h1 { font-size: 22px; margin: 0 0 4px; }
header.top p { margin: 0 0 18px; color: var(--ink-soft); font-size: 13.5px; }

.panel { background: var(--surface); border: 1px solid var(--border); border-radius: 16px; box-shadow: var(--shadow); padding: 18px 20px; margin-bottom: 16px; }

.busca-row { display: flex; gap: 12px; align-items: flex-end; flex-wrap: wrap; }
.campo { display: flex; flex-direction: column; gap: 4px; }
.campo label { font-size: 11px; font-weight: 800; text-transform: uppercase; letter-spacing: .03em; color: var(--ink-faint); }
.campo input {
  font: inherit; font-size: 15px; font-weight: 700; padding: 8px 10px; border-radius: 9px;
  border: 1px solid var(--border); background: var(--surface-2); color: var(--ink);
  font-variant-numeric: tabular-nums;
}
#codigoInput { width: 110px; }
#nomeAtual { font-size: 15px; font-weight: 800; color: var(--accent); align-self: center; padding-bottom: 8px; }
.rota-atual { font-size: 12.5px; color: var(--ink-faint); align-self: center; padding-bottom: 8px; }

table.breakdown { width: 100%; border-collapse: collapse; font-size: 13px; margin-top: 6px; }
table.breakdown th { text-align: right; font-size: 10.5px; text-transform: uppercase; color: var(--ink-faint); font-weight: 800; padding: 6px 6px; border-bottom: 1px solid var(--border); }
table.breakdown th:first-child, table.breakdown td:first-child { text-align: left; }
table.breakdown td { text-align: right; padding: 6px 6px; font-variant-numeric: tabular-nums; font-weight: 700; border-bottom: 1px solid var(--border); }
table.breakdown tr:last-child td { border-bottom: none; }
table.breakdown td.dif-pos { color: var(--good); }
table.breakdown td.dif-bad { color: var(--bad); }
table.breakdown input.meta-peso-input {
  width: 64px; font: inherit; font-size: 12.5px; font-weight: 800; text-align: center;
  padding: 4px 4px; border-radius: 6px; border: 1px solid var(--border); background: var(--surface-2); color: var(--accent);
}
.btn-limpar {
  margin-top: 12px; background: var(--bad); color: #fff; border: none; border-radius: 10px;
  padding: 11px 20px; font: inherit; font-size: 13.5px; font-weight: 800; cursor: pointer; width: 100%;
}
.btn-limpar:hover { opacity: .9; }
.vazio { text-align: center; padding: 60px 20px; color: var(--ink-faint); font-size: 14px; }
.foot { text-align: center; color: var(--ink-faint); font-size: 12px; margin-top: 30px; }
</style>
</head>
<body>
<div class="wrap">
  <header class="top">
    <h1>Meta Peso</h1>
    <p>Digite o código do RCA pra ver o peso por categoria — defina a meta e veja quanto falta.</p>
  </header>

  <div class="panel">
    <div class="busca-row">
      <div class="campo">
        <label>Código do RCA</label>
        <input type="number" id="codigoInput" list="rcaList" placeholder="ex: 15">
        <datalist id="rcaList"></datalist>
      </div>
      <div id="avatarAtual" style="display:flex;align-self:center"></div>
      <div id="nomeAtual"></div>
      <div class="rota-atual" id="rotaAtual"></div>
    </div>
  </div>

  <div id="conteudo"></div>

  <p class="foot">Dados extraídos de RESULTADO.xlsm (via melhoria_salarial) · gerado automaticamente</p>
</div>

<script>
const DADOS = __DADOS_JSON__;
const FOTOS_RCAS = __FOTOS_RCAS_JSON__;
const RCAS_POR_CODIGO = Object.fromEntries(DADOS.rcas.map(r => [r.codigo, r]));

function normalizarNomeFoto(nome) { return nome.replace(/\s*-\s*$/, "").trim().toUpperCase(); }
function iniciais(nome) { return nome.split(/\s+/).filter(Boolean).slice(0, 2).map(p => p[0]).join("").toUpperCase(); }

const PALETA_AVATAR = ["#0E7C86", "#7A5CC7", "#C0672B", "#3D6FB4", "#1D9A5D", "#B4740A", "#B4406B"];
function corAvatar(nome) {
  let h = 0;
  for (const c of nome) h = (h * 31 + c.charCodeAt(0)) >>> 0;
  return PALETA_AVATAR[h % PALETA_AVATAR.length];
}
function avatarHtml(nome, foto, tamanho) {
  return foto
    ? `<img src="${foto}" alt="${nome}" style="width:${tamanho}px;height:${tamanho}px;object-fit:cover;border-radius:50%;flex:none;">`
    : `<div style="width:${tamanho}px;height:${tamanho}px;border-radius:50%;flex:none;background:${corAvatar(nome)};color:#fff;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:${Math.round(tamanho * 0.36)}px;">${iniciais(nome)}</div>`;
}

// type="text" (não number) pra não perder cursor/posição a cada tecla —
// aceita vírgula ou ponto, mostra sempre com vírgula.
function parseNum(str) {
  const v = parseFloat(String(str).replace(",", "."));
  return isNaN(v) ? 0 : v;
}
function fmtInput(v) { return String(v).replace(".", ","); }
function fmtPeso(v) { return Number(v).toLocaleString("pt-BR", { maximumFractionDigits: 2 }); }

// ---- Estado por RCA (Meta Peso de cada categoria) ----
function chaveEstado(codigo) { return "meta_peso_estado_v1_" + codigo; }

function estadoPadrao(rca) {
  const metasPeso = {};
  DADOS.constantes.ordem_categorias.forEach(chave => {
    // Sem meta pré-definida na origem — começa igual ao peso atual (diferença
    // zero), o Edmar ajusta pra cima conforme a meta real de cada categoria.
    metasPeso[chave] = rca ? rca.categorias[chave].peso : 0;
  });
  return { metasPeso };
}

function lerEstado(codigo) {
  const rca = RCAS_POR_CODIGO[codigo];
  const padrao = estadoPadrao(rca);
  try {
    const salvo = localStorage.getItem(chaveEstado(codigo));
    if (!salvo) return padrao;
    const parsed = JSON.parse(salvo);
    return { metasPeso: Object.assign({}, padrao.metasPeso, parsed.metasPeso || {}) };
  } catch (e) { return padrao; }
}

function salvarEstado(codigo, estado) {
  try { localStorage.setItem(chaveEstado(codigo), JSON.stringify(estado)); } catch (e) {}
}

function limparEstado(codigo) {
  try { localStorage.removeItem(chaveEstado(codigo)); } catch (e) {}
}

function montarConteudo(rca) {
  const estado = lerEstado(rca.codigo);
  const { labels_categoria, ordem_categorias } = DADOS.constantes;

  const linhas = ordem_categorias.map(chave => {
    const cat = rca.categorias[chave];
    const metaPeso = estado.metasPeso[chave];
    const diferenca = metaPeso - cat.peso;
    const bateu = diferenca <= 0;
    const classeDif = bateu ? "dif-pos" : "dif-bad";
    const textoDif = bateu ? "Bateu" : `Faltam ${fmtPeso(diferenca)} kg`;
    return `<tr>
      <td>${labels_categoria[chave]}</td>
      <td>${fmtPeso(cat.peso)} kg</td>
      <td><input type="text" inputmode="numeric" class="meta-peso-input" data-chave="${chave}" value="${fmtInput(metaPeso)}"> kg</td>
      <td>${cat.positivacao}</td>
      <td class="${classeDif}">${textoDif}</td>
    </tr>`;
  }).join("");

  return `
    <div class="panel">
      <table class="breakdown">
        <thead><tr><th>Categoria</th><th>Peso</th><th>Meta Peso</th><th>Positivação</th><th>Diferença</th></tr></thead>
        <tbody>${linhas}</tbody>
      </table>
      <button class="btn-limpar" id="btnLimpar">Limpar metas deste vendedor</button>
    </div>
  `;
}

function renderizarRca() {
  const codigo = parseInt(document.getElementById("codigoInput").value);
  const conteudo = document.getElementById("conteudo");
  const avatarAtual = document.getElementById("avatarAtual");
  const nomeAtual = document.getElementById("nomeAtual");
  const rotaAtual = document.getElementById("rotaAtual");

  const ativo = document.activeElement;
  const focoAntes = (ativo && conteudo.contains(ativo) && ativo.tagName === "INPUT")
    ? { chave: ativo.dataset.chave, inicio: ativo.selectionStart, fim: ativo.selectionEnd, valorBruto: ativo.value }
    : null;

  const rca = RCAS_POR_CODIGO[codigo];
  if (!rca) {
    avatarAtual.innerHTML = "";
    nomeAtual.textContent = "";
    rotaAtual.textContent = "";
    conteudo.innerHTML = codigo ? `<div class="vazio">RCA ${codigo} não encontrado.</div>` : `<div class="vazio">Digite um código de RCA acima pra começar.</div>`;
    return;
  }

  avatarAtual.innerHTML = avatarHtml(rca.nome, FOTOS_RCAS[normalizarNomeFoto(rca.nome)], 40);
  nomeAtual.textContent = rca.nome;
  rotaAtual.textContent = `RCA ${rca.codigo} · ${rca.rota}`;
  conteudo.innerHTML = montarConteudo(rca);

  if (focoAntes && focoAntes.chave) {
    const novo = conteudo.querySelector(`[data-chave="${focoAntes.chave}"]`);
    if (novo) {
      novo.value = focoAntes.valorBruto;
      novo.focus();
      try { novo.setSelectionRange(focoAntes.inicio, focoAntes.fim); } catch (e) {}
    }
  }
}

document.getElementById("conteudo").addEventListener("input", (e) => {
  if (e.target.classList.contains("meta-peso-input")) {
    const codigo = parseInt(document.getElementById("codigoInput").value);
    const estado = lerEstado(codigo);
    estado.metasPeso[e.target.dataset.chave] = parseNum(e.target.value);
    salvarEstado(codigo, estado);
    renderizarRca();
  }
});

document.getElementById("conteudo").addEventListener("click", (e) => {
  if (!e.target.closest("#btnLimpar")) return;
  const codigo = parseInt(document.getElementById("codigoInput").value);
  limparEstado(codigo);
  renderizarRca();
});

function montarDatalist() {
  const opts = DADOS.rcas
    .slice()
    .sort((a, b) => a.nome.localeCompare(b.nome))
    .map(r => `<option value="${r.codigo}">${r.nome} — RCA ${r.codigo}</option>`)
    .join("");
  document.getElementById("rcaList").innerHTML = opts;
}

document.getElementById("codigoInput").addEventListener("input", renderizarRca);

montarDatalist();
renderizarRca();
</script>
</body>
</html>
"""


def gerar_html(dados):
    html = TEMPLATE.replace("__DADOS_JSON__", json.dumps(dados, ensure_ascii=False))
    html = html.replace("__FOTOS_RCAS_JSON__", _FOTOS_RCAS_JSON)
    return html


def main():
    with open(CAMINHO_DADOS, "r", encoding="utf-8") as f:
        dados = json.load(f)

    html = gerar_html(dados)
    with open(CAMINHO_SAIDA, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Painel gerado em: {CAMINHO_SAIDA}")


if __name__ == "__main__":
    main()
