from copy import deepcopy

# ============================================================
# IMPRESSÃO DA GRAMÁTICA
# ============================================================
def imprimir_gramatica(G, titulo=""):
    print("\n" + "="*40)
    print(titulo)
    print("="*40)
    print("Variáveis:", G["variaveis"])
    print("Alfabeto:", G["alfabeto"])
    print("Inicial:", G["inicial"])
    print("Produções:")
    for v in sorted(G["producoes"]):
        regras = " | ".join(G["producoes"][v])
        print(f"{v} -> {regras}")
    print("="*40 + "\n")


# ============================================================
# 1 - REMOÇÃO DE ε-PRODUÇÕES
# ============================================================
def remover_epsilon(G):
    G = deepcopy(G)
    
    print("\n### REMOÇÃO DE ε-PRODUÇÕES ###")

    anulaveis = set()

    # PASSO 1: Encontrar variáveis anuláveis
    mudou = True
    while mudou:
        mudou = False
        for var, regras in G["producoes"].items():
            for r in regras:
                if r == "ε" or all(simbolo in anulaveis for simbolo in r):
                    if var not in anulaveis:
                        anulaveis.add(var)
                        mudou = True

    print("Variáveis anuláveis:", anulaveis)

    # PASSO 2: Gerar novas produções
    novas_producoes = {}

    for var, regras in G["producoes"].items():
        novas = set()

        for r in regras:
            if r == "ε":
                continue

            posicoes = [i for i, s in enumerate(r) if s in anulaveis]
            total = len(posicoes)
            n = 1 << total

            for i in range(n):
                nova = list(r)
                for j in range(total):
                    if (i >> j) & 1:
                        nova[posicoes[j]] = ""
                resultado = "".join(nova)
                if resultado != "":
                    novas.add(resultado)

        novas_producoes[var] = list(novas)

    # PASSO 3: Caso variável inicial seja anulável
    if G["inicial"] in anulaveis:
        novas_producoes[G["inicial"]].append("ε")

    G["producoes"] = novas_producoes

    imprimir_gramatica(G, "Após remoção de ε-produções")
    return G


# ============================================================
# 2 - REMOÇÃO DE PRODUÇÕES UNITÁRIAS
# ============================================================
def remover_unitarias(G):
    G = deepcopy(G)

    print("\n### REMOÇÃO DE PRODUÇÕES UNITÁRIAS ###")

    unitarios = {}

    # Monta grafo de unitários
    for A in G["variaveis"]:
        unitarios[A] = set()

    for A, regras in G["producoes"].items():
        for r in regras:
            if len(r) == 1 and r in G["variaveis"]:
                unitarios[A].add(r)

    # Fechamento transitivo
    mudou = True
    while mudou:
        mudou = False
        for A in unitarios:
            for B in list(unitarios[A]):
                for C in unitarios[B]:
                    if C not in unitarios[A]:
                        unitarios[A].add(C)
                        mudou = True

    novas = {}

    # Copia produções não unitárias
    for A in G["variaveis"]:
        novas[A] = []

        for r in G["producoes"].get(A, []):
            if not (len(r) == 1 and r in G["variaveis"]):
                novas[A].append(r)

        # Puxa produções dos alcançáveis
        for B in unitarios[A]:
            for r in G["producoes"].get(B, []):
                if not (len(r) == 1 and r in G["variaveis"]):
                    if r not in novas[A]:
                        novas[A].append(r)

    G["producoes"] = novas

    imprimir_gramatica(G, "Após remoção de produções unitárias")
    return G


# ============================================================
# 3 - ELIMINAÇÃO DE SÍMBOLOS INÚTEIS
# ============================================================

def remover_inuteis(G):
    G = deepcopy(G)

    print("\n### REMOÇÃO DE SÍMBOLOS INÚTEIS ###")

    variaveis = G["variaveis"]
    terminais = G["alfabeto"]

    # =========================================================
    # PASSO 1 - ENCONTRAR VARIÁVEIS GERADORAS
    # =========================================================
    geradores = set()
    mudou = True

    while mudou:
        mudou = False
        for A, regras in G["producoes"].items():
            for r in regras:
                valida = True
                for s in r:
                    # símbolo inválido
                    if s not in variaveis and s not in terminais:
                        valida = False
                        break

                    # variável que ainda não gera
                    if s in variaveis and s not in geradores:
                        valida = False
                        break

                if valida:
                    if A not in geradores:
                        geradores.add(A)
                        mudou = True

    print("Variáveis geradoras:", geradores)

    # Proteção contra destruição total
    if not geradores:
        print("⚠ Nenhuma variável geradora encontrada! Abortando remoção para evitar perda da gramática.")
        return G

    # =========================================================
    # REMOVE NÃO-GERADORES
    # =========================================================
    G["variaveis"] = G["variaveis"] & geradores
    G["producoes"] = {A: G["producoes"][A] for A in G["variaveis"]}

    # =========================================================
    # PASSO 2 - ENCONTRAR VARIÁVEIS ALCANÇÁVEIS
    # =========================================================
    alcan = set()
    fila = [G["inicial"]]

    while fila:
        A = fila.pop(0)
        if A not in alcan:
            alcan.add(A)

            for r in G["producoes"].get(A, []):
                for s in r:
                    if s in G["variaveis"] and s not in alcan:
                        fila.append(s)

    print("Variáveis alcançáveis:", alcan)

    # Protege símbolo inicial
    if G["inicial"] not in alcan:
        print("⚠ Símbolo inicial não alcançável. Abortando remoção.")
        return G

    # =========================================================
    # REMOVE NÃO-ALCANÇÁVEIS
    # =========================================================
    G["variaveis"] = G["variaveis"] & alcan
    G["producoes"] = {A: G["producoes"][A] for A in G["variaveis"]}

    imprimir_gramatica(G, "Após remoção de símbolos inúteis")
    return G


# ============================================================
# FUNÇÃO PRINCIPAL DE SIMPLIFICAÇÃO
# ============================================================
def simplificar_gramatica(G):
    imprimir_gramatica(G, "Gramática Original")

    G = remover_epsilon(G)
    G = remover_unitarias(G)
    G = remover_inuteis(G)

    imprimir_gramatica(G, "Gramática Simplificada Final")
    return G
