import re

def ler_gramatica(caminho_arquivo):
    with open(caminho_arquivo, "r", encoding="utf-8") as file:
        linhas = [linha.strip() for linha in file if linha.strip()]

    gramatica = {
        "variaveis": set(),
        "alfabeto": set(),
        "inicial": "",
        "producoes": {}
    }

    lendo_regras = False

    for linha in linhas:
        # Variáveis
        if linha.startswith("Variaveis"):
            conteudo = extrair_conteudo_chaves(linha)
            gramatica["variaveis"] = set(conteudo)

        # Alfabeto
        elif linha.startswith("Alfabeto"):
            conteudo = extrair_conteudo_chaves(linha)
            gramatica["alfabeto"] = set(conteudo)

        # Inicial
        elif linha.startswith("Inicial"):
            gramatica["inicial"] = linha.split("=")[1].strip()

        # Início das regras
        elif linha.startswith("Regras"):
            lendo_regras = True

        # Produções
        elif lendo_regras:
            variavel, producao = parse_producao(linha)

            if variavel not in gramatica["producoes"]:
                gramatica["producoes"][variavel] = []

            gramatica["producoes"][variavel].append(producao)

    return gramatica


def extrair_conteudo_chaves(linha):
    match = re.search(r"\{(.+?)\}", linha)
    if not match:
        return []

    conteudo = match.group(1)
    return [item.strip() for item in conteudo.split(",")]


def parse_producao(linha):
    esquerda, direita = linha.split("->")
    esquerda = esquerda.strip()
    direita = direita.strip()

    # Trata epsilon (&)
    if direita == "&":
        direita = "ε"

    return esquerda, direita
