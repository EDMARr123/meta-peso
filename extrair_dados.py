r"""
Extrai os dados do painel "Meta Peso" a partir do dados.json que o projeto
melhoria_salarial já gera (mesma fonte, RESULTADO.xlsm) — não lê a
planilha direto, só reaproveita peso/positivação por categoria de cada
RCA. Rodar DEPOIS de melhoria_salarial/extrair_dados.py.
"""

import json
import os

PASTA_BASE = os.path.dirname(os.path.abspath(__file__))
CAMINHO_SAIDA = os.path.join(PASTA_BASE, "dados.json")
CAMINHO_MELHORIA_SALARIAL = os.path.join(PASTA_BASE, "..", "melhoria_salarial", "dados.json")


def extrair():
    with open(CAMINHO_MELHORIA_SALARIAL, "r", encoding="utf-8") as f:
        origem = json.load(f)

    rcas = []
    for r in origem["rcas"]:
        categorias = {
            chave: {"peso": info["peso"], "positivacao": info["positivacao"]}
            for chave, info in r["categorias"].items()
        }
        rcas.append({
            "codigo": r["codigo"],
            "nome": r["nome"],
            "rota": r["rota"],
            "supervisor": r["supervisor"],
            "categorias": categorias,
            # Meta de positivação por categoria configurada no Painel
            # Performance (melhoria_salarial) — ponto de partida antes de
            # qualquer edição ao vivo (essa vem do localStorage no navegador).
            "meta_posit_departamento": r.get("meta_posit_departamento", {}),
        })

    constantes = {
        "labels_categoria": origem["constantes"]["labels_categoria"],
        "ordem_categorias": origem["constantes"]["ordem_categorias"],
        "metas_categoria_padrao": origem["constantes"]["metas_categoria_padrao"],
    }
    return rcas, constantes


def main():
    rcas, constantes = extrair()
    saida = {"rcas": rcas, "constantes": constantes}
    with open(CAMINHO_SAIDA, "w", encoding="utf-8") as f:
        json.dump(saida, f, ensure_ascii=False, indent=2)
    print(f"{len(rcas)} RCAs extraídos. Salvo em: {CAMINHO_SAIDA}")


if __name__ == "__main__":
    main()
