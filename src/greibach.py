from copy import deepcopy
from chomsky import *
from simplificacao import remover_inuteis
# ============================================================
# 5 - FORMA NORMAL DE GREIBACH
# ============================================================
def forma_normal_greibach(G):
    # PASSO 0: Garantir que está na Forma Normal de Chomsky
    # Se você já rodou a FNC antes, isso apenas garante.
    # É CRUCIAL que a gramática esteja em FNC para este algoritmo funcionar bem.
    G = forma_normal_chomsky(G)
    
    print("\n### FORMA NORMAL DE GREIBACH ###")
    
    # ---------------------------------------------------------
    # 1. RENOMEAÇÃO DE VARIÁVEIS (A1, A2, ..., An)
    # ---------------------------------------------------------
    # O algoritmo exige uma ordenação. Vamos mapear os nomes originais para A_i.
    
    variaveis_ordenadas = sorted(list(G["variaveis"]))
    mapa_original_para_Ai = {}
    mapa_Ai_para_original = {}
    
    novas_producoes = {}
    
    for i, var in enumerate(variaveis_ordenadas):
        nome_Ai = f"A_{i+1}"
        mapa_original_para_Ai[var] = nome_Ai
        mapa_Ai_para_original[nome_Ai] = var
    
    # Converte as produções para usar os novos nomes A_i
    for var in variaveis_ordenadas:
        novo_nome = mapa_original_para_Ai[var]
        regras = []
        for r in G["producoes"][var]:
            nova_regra = []
            for simbolo in r:
                if simbolo in G["variaveis"]:
                    nova_regra.append(mapa_original_para_Ai[simbolo])
                else:
                    nova_regra.append(simbolo)
            regras.append(nova_regra)
        novas_producoes[novo_nome] = regras

    # Atualiza a gramática para usar apenas A_i temporariamente
    G["variaveis"] = set(novas_producoes.keys())
    G["producoes"] = novas_producoes
    G["inicial"] = mapa_original_para_Ai[G["inicial"]]
    
    # Lista ordenada para iterar: ['A_1', 'A_2', ..., 'A_n']
    lista_A = [f"A_{i+1}" for i in range(len(variaveis_ordenadas))]

    print("-> Variáveis renomeadas para ordenação (A_1 ... A_n)")

    # ---------------------------------------------------------
    # 2. ELIMINAÇÃO DE RECURSÃO À ESQUERDA E ORDENAÇÃO
    # ---------------------------------------------------------
    # Objetivo: Transformar regras para que se Ai -> Aj..., então j > i
    
    # Iteramos sobre as variáveis Ai
    for i in range(len(lista_A)):
        Ai = lista_A[i]
        
        # Para cada j < i
        for j in range(i):
            Aj = lista_A[j]
            
            # Verifica se existe produção Ai -> Aj gamma
            novas_regras_Ai = []
            for regra in G["producoes"][Ai]:
                if regra[0] == Aj:
                    # SUBSTITUIÇÃO: Ai -> Aj gamma vira Ai -> (corpo de Aj) gamma
                    gamma = regra[1:]
                    for regra_Aj in G["producoes"][Aj]:
                        novas_regras_Ai.append(regra_Aj + gamma)
                else:
                    novas_regras_Ai.append(regra)
            
            G["producoes"][Ai] = novas_regras_Ai
        
        # Elimina recursão imediata (Ai -> Ai gamma)
        eliminar_recursao_imediata(G, Ai)

    # ---------------------------------------------------------
    # 3. SUBSTITUIÇÃO REVERSA (BACK-SUBSTITUTION)
    # ---------------------------------------------------------
    # Agora que An começa com terminais, substituímos em An-1, etc.
    # Iteramos de n-1 até 0 (de trás para frente)
    
    print("-> Realizando substituição reversa...")
    
    for i in range(len(lista_A) - 2, -1, -1):
        Ai = lista_A[i]
        
        novas_regras = []
        for regra in G["producoes"][Ai]:
            primeiro_simbolo = regra[0]
            
            # Se o primeiro símbolo é uma variável (Aj), sabemos que j > i
            # Devemos substituir para garantir que comece com terminal
            if primeiro_simbolo in G["variaveis"]:
                Aj = primeiro_simbolo
                gamma = regra[1:]
                
                # Pega as produções de Aj (que já estão na forma correta ou quase)
                for regra_Aj in G["producoes"][Aj]:
                    novas_regras.append(regra_Aj + gamma)
            else:
                # Já começa com terminal
                novas_regras.append(regra)
        
        G["producoes"][Ai] = novas_regras

    # ---------------------------------------------------------
    # 4. LIMPEZA DOS Z (Variáveis auxiliares da recursão)
    # ---------------------------------------------------------
    # As variáveis Z criadas na recursão também precisam ter seus corpos
    # iniciados por terminais. Elas dependem das variáveis originais.
    # Como as originais já foram corrigidas, basta fazer uma passada nelas.
    
    vars_z = [v for v in G["variaveis"] if v.startswith("Z_")]
    for z in vars_z:
        novas_regras_z = []
        for regra in G["producoes"][z]:
            primeiro = regra[0]
            if primeiro in G["variaveis"] and not primeiro.startswith("Z_"):
                 # Substitui pela regra da variável (que agora já começa com terminal)
                 gamma = regra[1:]
                 for regra_sub in G["producoes"][primeiro]:
                     novas_regras_z.append(regra_sub + gamma)
            else:
                novas_regras_z.append(regra)
        G["producoes"][z] = novas_regras_z
    
    imprimir_gramatica(G, "Forma Normal de Greibach Final")
    remover_inuteis(G)
    return G


# ============================================================
# AUXILIAR: ELIMINAR RECURSÃO IMEDIATA
# ============================================================
def eliminar_recursao_imediata(G, Ai):
    regras = G["producoes"][Ai]
    recursivas = [] # Ai -> Ai alpha
    nao_recursivas = [] # Ai -> beta
    
    for r in regras:
        if r[0] == Ai:
            recursivas.append(r[1:]) # Guarda o alpha
        else:
            nao_recursivas.append(r) # Guarda o beta
            
    # Se não tem recursão, retorna
    if not recursivas:
        return

    # Cria nova variável Z_i
    Zi = f"Z_{Ai}"
    G["variaveis"].add(Zi)
    
    # Novas regras para Ai:
    # Ai -> beta | beta Z_i
    novas_Ai = []
    for beta in nao_recursivas:
        novas_Ai.append(beta)
        novas_Ai.append(beta + [Zi])
    
    G["producoes"][Ai] = novas_Ai
    
    # Regras para Z_i:
    # Z_i -> alpha | alpha Z_i
    regras_Zi = []
    for alpha in recursivas:
        regras_Zi.append(alpha)
        regras_Zi.append(alpha + [Zi])
        
    G["producoes"][Zi] = regras_Zi