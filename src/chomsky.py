from copy import deepcopy
from simplificacao import imprimir_gramatica

def forma_normal_chomsky(G):
    G = deepcopy(G)
    print("\n### FORMA NORMAL DE CHOMSKY ###")
    
    # Padronização (String -> Lista)
    # converte produções de string "ABC" para lista ["A", "B", "C"]
    # necessário para nomes de variáveis compostos (ex: X_ab)
    for var, regras in G["producoes"].items():
        novas_regras = []
        for r in regras:
            # se já for lista, mantém, se for string, converte
            if isinstance(r, str):
                # caso especial: epsilon
                if r == "ε": 
                    novas_regras.append(["ε"])
                else:
                    novas_regras.append(list(r))
            else:
                novas_regras.append(r)
        G["producoes"][var] = novas_regras

    # dicionário para reaproveitar variáveis criadas
    # chave: tupla do corpo da produção (ex: ('A', 'B')), Valor: nome da variável
    cache_producoes = {}
    
    # contador para garantir nomes únicos se necessário
    contador_var = 1

    # isolar terminais
    # regra: Se o corpo tem comprimento >= 2, terminais devem virar variáveis.
    # Ex: A -> aB vira A -> V_a B e V_a -> a
    
    print("-> Isolando terminais...")
    
    # iteramos sobre uma cópia das chaves para poder modificar o dicionário
    variaveis_originais = list(G["producoes"].keys())
    
    for var in variaveis_originais:
        regras = G["producoes"][var]
        novas_regras = []
        
        for r in regras:
            # se tamanho < 2, não precisa fazer nada (ex: A -> a ou A -> B)
            if len(r) < 2:
                novas_regras.append(r)
                continue
            
            nova_regra = []
            for simbolo in r:
                # se é terminal (está no alfabeto), cria variável para ele
                if simbolo in G["alfabeto"]:
                    chave_terminal = tuple([simbolo])
                    
                    if chave_terminal in cache_producoes:
                        nome_var_terminal = cache_producoes[chave_terminal]
                    else:
                        # cria nome da variável (ex: T_a)
                        nome_var_terminal = f"T_{simbolo}"
                        cache_producoes[chave_terminal] = nome_var_terminal
                        
                        # adiciona na gramática
                        G["variaveis"].add(nome_var_terminal)
                        if nome_var_terminal not in G["producoes"]:
                            G["producoes"][nome_var_terminal] = []
                        G["producoes"][nome_var_terminal].append([simbolo])
                    
                    nova_regra.append(nome_var_terminal)
                else:
                    # É variável, mantém
                    nova_regra.append(simbolo)
            
            novas_regras.append(nova_regra)
        G["producoes"][var] = novas_regras

    # binarização (Reduzir tamanho das produções)
    # Regra: A -> ABC vira A -> X_AB C e X_AB -> AB
    
    print("-> Binarizando produções longas...")
    
    mudou = True
    while mudou:
        mudou = False
        # coletamos todas as variáveis atuais
        variaveis_atuais = list(G["producoes"].keys())
        
        for var in variaveis_atuais:
            regras = G["producoes"][var]
            novas_regras = []
            
            for r in regras:
                # se tamanho <= 2, está ok
                if len(r) <= 2:
                    novas_regras.append(r)
                    continue
                
                mudou = True # encontramos regra longa, o loop vai rodar de novo
                
                # pega os 2 primeiros símbolos
                primeiro = r[0]
                segundo = r[1]
                restante = r[2:]
                
                par = (primeiro, segundo)
                
                # verifica se já criamos uma variável para esse par
                if par in cache_producoes:
                    nova_var = cache_producoes[par]
                else:
                    # cria nome seguindo seu padrão: X_AB (concatenação simples se curto)
                    # limpa caracteres estranhos para o nome não quebrar
                    p1_clean = primeiro.replace("T_", "")
                    p2_clean = segundo.replace("T_", "")
                    nova_var = f"X_{p1_clean}{p2_clean}"
                    
                    # garante unicidade caso o nome já exista (colisão)
                    if nova_var in G["variaveis"]:
                        nova_var = f"X_{contador_var}"
                        contador_var += 1

                    cache_producoes[par] = nova_var
                    G["variaveis"].add(nova_var)
                    
                    # cria a nova produção: X_AB -> A B
                    G["producoes"][nova_var] = [[primeiro, segundo]]

                # atualiza a regra original: A -> X_AB C ...
                nova_regra_original = [nova_var] + restante
                novas_regras.append(nova_regra_original)
            
            G["producoes"][var] = novas_regras

    # imprime usando função 
    imprimir_gramatica(G, "Forma Normal de Chomsky Final")
    return G


