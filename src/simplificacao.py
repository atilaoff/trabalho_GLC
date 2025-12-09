from copy import deepcopy


# impressão da gramática

def imprimir_gramatica(G, titulo=""):
    print("\n" + "="*40)
    print(titulo)
    print("="*40)
    # Converte sets para lista ordenada para visualização limpa
    print("Variáveis:", sorted(list(G["variaveis"])))
    print("Alfabeto:", sorted(list(G["alfabeto"])))
    print("Inicial:", G["inicial"])
    print("Produções:")

    
    # ordena alfabeticamente
    ordem_variaveis = sorted(list(G["producoes"].keys()))

    # se o símbolo inicial estiver na lista, move para o topo
    inicial = G["inicial"]
    if inicial in ordem_variaveis:
        ordem_variaveis.remove(inicial) # Tira de onde estava (ex: posição 3)
        ordem_variaveis.insert(0, inicial) # Coloca na posição 0

    # itera sobre lista ordenada personalizada
    for v in ordem_variaveis:
        regras_formatadas = []
        
        for r in G["producoes"][v]:
            # verifica tipo:
            if isinstance(r, list):
                # Se for lista ['A', 'B'], junta com espaço -> "A B"
                regras_formatadas.append(" ".join(r))
            else:
                # Se for string "AB", mantém "AB"
                regras_formatadas.append(r)
        
        # Junta todas as regras com " | "
        linha = " | ".join(regras_formatadas)
        print(f"{v} -> {linha}")
        
    print("="*40 + "\n")



# Remove epsilon-produções

def remover_epsilon(G):
    G = deepcopy(G)
    
    print("\n### REMOÇÃO DE ε-PRODUÇÕES ###")

    anulaveis = set()

    # Encontrar variáveis anuláveis
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

    # Gerar novas produções
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

    # Caso variável inicial seja anulável
    if G["inicial"] in anulaveis:
        novas_producoes[G["inicial"]].append("ε")

    G["producoes"] = novas_producoes

    return G



# Remove produções unitárias

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

    return G


# Remove simbolos inúteis

def remover_inuteis(G):
    G = deepcopy(G)

    print("\n### REMOÇÃO DE SÍMBOLOS INÚTEIS ###")

    variaveis = G["variaveis"]
    terminais = G["alfabeto"]

    # Encontra variáveis geradores
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
        print("⚠ Nenhuma variável geradora encontrada Abortando remoção para evitar perda da gramática.")
        return G

    # Remove não geradores
    G["variaveis"] = G["variaveis"] & geradores
    G["producoes"] = {A: G["producoes"][A] for A in G["variaveis"]}

    # Encontra variáveis alcançáveis
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

   
    # remove não alcançáveis
    
    G["variaveis"] = G["variaveis"] & alcan
    G["producoes"] = {A: G["producoes"][A] for A in G["variaveis"]}

    return G



# Função simplificação principal

def simplificar_gramatica(G):
    imprimir_gramatica(G, "Gramática Original")

    G = remover_epsilon(G)
    imprimir_gramatica(G, "Após remoção de ε-produções")
    G = remover_unitarias(G)
    imprimir_gramatica(G, "Após remoção de produções unitárias")
    G = remover_inuteis(G)
    imprimir_gramatica(G, "Após remoção de símbolos inúteis")

    imprimir_gramatica(G, "Gramática Simplificada Final")
    return G
