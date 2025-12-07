from collections import defaultdict
from itertools import combinations
import sys

EPSILON = "&"  # palavra vazia


class Grammar:
    """
    Representação simples de uma Gramática Livre de Contexto.
    Não-terminais: strings (ex: 'S', 'A', 'B')
    Terminais: strings (ex: 'a', 'b')
    Produções: dict A -> conjunto de tuplas (símbolos na RHS)
    """

    def __init__(self):
        self.nonterminals = set()
        self.terminals = set()
        self.start_symbol = None
        self.productions = defaultdict(set)  # A -> set of rhs tuples

    @staticmethod
    def from_file(path: str) -> "Grammar":
        """
        Lê uma gramática de um arquivo .txt.
        Formato esperado (um por linha, comentários opcionais):

            # comentário
            S -> A B | a
            A -> a A | &
            B -> b

        - '&' representa ε (palavra vazia).
        - Símbolos são separados por espaço.
        """
        g = Grammar()
        temp_prods = []
        nonterms_order = []

        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                if line.startswith("#") or line.startswith("//") or line.startswith(";"):
                    continue
                if "->" not in line:
                    # linha não reconhecida como produção, ignore
                    continue

                lhs, rhs_all = line.split("->", 1)
                lhs = lhs.strip()

                if lhs not in g.nonterminals:
                    g.nonterminals.add(lhs)
                    nonterms_order.append(lhs)

                alternatives = rhs_all.split("|")
                for alt in alternatives:
                    alt = alt.strip()
                    if not alt or alt == EPSILON:
                        rhs = (EPSILON,)
                    else:
                        rhs = tuple(alt.split())
                    temp_prods.append((lhs, rhs))

        if not nonterms_order:
            raise ValueError("Nenhuma produção encontrada no arquivo.")

        # símbolo inicial: se existir 'S', usa; senão o primeiro LHS encontrado
        if "S" in g.nonterminals:
            g.start_symbol = "S"
        else:
            g.start_symbol = nonterms_order[0]

        # descobre os terminais a partir dos símbolos que NÃO aparecem à esquerda
        symbols_rhs = set()
        for lhs, rhs in temp_prods:
            for sym in rhs:
                if sym != EPSILON:
                    symbols_rhs.add(sym)

        g.terminals = symbols_rhs - g.nonterminals

        for lhs, rhs in temp_prods:
            g.productions[lhs].add(rhs)

        return g

    def copy(self) -> "Grammar":
        new = Grammar()
        new.nonterminals = set(self.nonterminals)
        new.terminals = set(self.terminals)
        new.start_symbol = self.start_symbol
        for A, rhs_set in self.productions.items():
            new.productions[A] = set(rhs_set)
        return new

    def to_text(self) -> str:
        """
        Converte a gramática para um texto legível para salvar no log.
        """
        lines = []
        lines.append("Não-terminais: " + ", ".join(sorted(self.nonterminals)))
        lines.append("Terminais: " + ", ".join(sorted(self.terminals)))
        lines.append(f"Símbolo inicial: {self.start_symbol}")
        lines.append("Produções:")
        for A in sorted(self.nonterminals):
            if A not in self.productions or not self.productions[A]:
                continue
            rhs_list = []
            for rhs in sorted(self.productions[A]):
                if len(rhs) == 1 and rhs[0] == EPSILON:
                    rhs_list.append(EPSILON)
                else:
                    rhs_list.append(" ".join(rhs))
            lines.append(f"  {A} -> " + " | ".join(rhs_list))
        return "\n".join(lines)


class Normalizer:
    """
    Responsável por aplicar as transformações de normalização na GLC
    e registrar cada passo em um arquivo de log.
    """

    def __init__(self, grammar: Grammar, log_file):
        self.g = grammar
        self.log = log_file
        self.counter = 1  # contador para criar novos não-terminais

    def fresh_nonterminal(self, prefix="X") -> str:
        """
        Gera um novo símbolo não-terminal que não colide com nenhum já existente.
        """
        while True:
            name = f"{prefix}{self.counter}"
            self.counter += 1
            if name not in self.g.nonterminals and name not in self.g.terminals:
                return name

    def log_initial(self):
        self.log.write("=== Gramática inicial (como lida do arquivo) ===\n")
        self.log.write(self.g.to_text() + "\n\n")

    def _recompute_terminals(self):
        """
        Recalcula o conjunto de terminais com base nas produções atuais.
        """
        g = self.g
        symbols_rhs = set()
        for rhs_set in g.productions.values():
            for rhs in rhs_set:
                for sym in rhs:
                    if sym != EPSILON:
                        symbols_rhs.add(sym)
        g.terminals = symbols_rhs - g.nonterminals

    # ------------------------------------------------------------------
    # 1) Remoção de produções-λ (epsilon)
    # ------------------------------------------------------------------
    def remove_epsilon(self):
        self.log.write("=== Remoção de produções-λ (ε) ===\n")
        self.log.write("Gramática antes da remoção de λ:\n")
        self.log.write(self.g.to_text() + "\n\n")

        g = self.g

        # 1. Encontrar variáveis anuláveis (nullable)
        nullable = set()
        for A, rhs_set in g.productions.items():
            for rhs in rhs_set:
                if len(rhs) == 1 and rhs[0] == EPSILON:
                    nullable.add(A)
                    break

        changed = True
        while changed:
            changed = False
            for A, rhs_set in g.productions.items():
                if A in nullable:
                    continue
                for rhs in rhs_set:
                    # se todos os símbolos de rhs são anuláveis, então A é anulável
                    if all((sym in nullable) for sym in rhs):
                        nullable.add(A)
                        changed = True
                        break

        # 2. Construir novas produções sem ε (exceto possivelmente no novo símbolo inicial)
        new_productions = defaultdict(set)

        for A, rhs_set in g.productions.items():
            for rhs in rhs_set:
                # não copiamos produções A -> ε diretamente
                if len(rhs) == 1 and rhs[0] == EPSILON:
                    continue

                # manter a produção original
                new_productions[A].add(rhs)

                # Gera produções extras removendo variáveis anuláveis da RHS
                positions = [i for i, sym in enumerate(rhs) if sym in nullable]
                for r in range(1, len(positions) + 1):
                    for subset in combinations(positions, r):
                        new_rhs = tuple(sym for i, sym in enumerate(rhs) if i not in subset)
                        if len(new_rhs) == 0:
                            # não adicionar ε aqui, só vamos permitir ε no novo símbolo inicial
                            continue
                        new_productions[A].add(new_rhs)

        g.productions = new_productions

        # 3. Se o símbolo inicial é anulável, criar novo símbolo inicial S0 -> S | ε
        if g.start_symbol in nullable:
            new_start = self.fresh_nonterminal("S0")
            g.nonterminals.add(new_start)
            g.productions[new_start].add((g.start_symbol,))
            g.productions[new_start].add((EPSILON,))
            g.start_symbol = new_start

        self._recompute_terminals()

        self.log.write("Gramática depois da remoção de λ:\n")
        self.log.write(self.g.to_text() + "\n\n")

    # ------------------------------------------------------------------
    # 2) Remoção de produções unitárias A -> B
    # ------------------------------------------------------------------
    def remove_unit(self):
        self.log.write("=== Remoção de produções unitárias (A -> B) ===\n")
        self.log.write("Gramática antes da remoção de unitárias:\n")
        self.log.write(self.g.to_text() + "\n\n")

        g = self.g
        N = list(g.nonterminals)

        # unit[A] = {B | A =>* B por produções unitárias}
        unit = {A: set([A]) for A in N}

        changed = True
        while changed:
            changed = False
            for A in N:
                for B in list(unit[A]):
                    for rhs in g.productions.get(B, []):
                        if len(rhs) == 1 and rhs[0] in g.nonterminals:
                            C = rhs[0]
                            if C not in unit[A]:
                                unit[A].add(C)
                                changed = True

        new_productions = defaultdict(set)
        for A in N:
            for B in unit[A]:
                for rhs in g.productions.get(B, []):
                    # descarta produções unitárias
                    if len(rhs) == 1 and rhs[0] in g.nonterminals:
                        continue
                    new_productions[A].add(rhs)

        g.productions = new_productions
        self._recompute_terminals()

        self.log.write("Gramática depois da remoção de unitárias:\n")
        self.log.write(self.g.to_text() + "\n\n")

    # ------------------------------------------------------------------
    # 3) Remoção de símbolos inúteis (não geradores / inalcançáveis)
    # ------------------------------------------------------------------
    def remove_useless(self):
        self.log.write("=== Remoção de símbolos inúteis (não geradores / inalcançáveis) ===\n")
        self.log.write("Gramática antes da remoção de inúteis:\n")
        self.log.write(self.g.to_text() + "\n\n")

        g = self.g

        # 1. Símbolos geradores (que geram alguma palavra de terminais)
        productive = set()
        changed = True
        while changed:
            changed = False
            for A, rhs_set in g.productions.items():
                if A in productive:
                    continue
                for rhs in rhs_set:
                    ok = True
                    for sym in rhs:
                        if sym in g.nonterminals and sym not in productive:
                            ok = False
                            break
                    if ok:
                        productive.add(A)
                        changed = True
                        break

        orig_prods = g.productions
        g.nonterminals = g.nonterminals & productive
        new_prods = defaultdict(set)
        for A in g.nonterminals:
            for rhs in orig_prods.get(A, []):
                if all((sym not in g.nonterminals) or (sym in g.nonterminals) for sym in rhs):
                    new_prods[A].add(rhs)
        g.productions = new_prods

        # 2. Símbolos alcançáveis a partir do símbolo inicial
        if g.start_symbol not in g.nonterminals:
            self.log.write("Aviso: símbolo inicial não é produtivo; gramática ficou vazia.\n\n")
            return

        reachable = set([g.start_symbol])
        queue = [g.start_symbol]

        while queue:
            A = queue.pop(0)
            for rhs in g.productions.get(A, []):
                for sym in rhs:
                    if sym in g.nonterminals and sym not in reachable:
                        reachable.add(sym)
                        queue.append(sym)

        g.nonterminals = g.nonterminals & reachable
        orig_prods2 = g.productions
        new_prods2 = defaultdict(set)
        for A in g.nonterminals:
            for rhs in orig_prods2.get(A, []):
                if all((sym not in g.nonterminals) or (sym in g.nonterminals) for sym in rhs):
                    new_prods2[A].add(rhs)
        g.productions = new_prods2

        self._recompute_terminals()

        self.log.write("Gramática depois da remoção de inúteis:\n")
        self.log.write(self.g.to_text() + "\n\n")

    # ------------------------------------------------------------------
    # 4) Conversão estrutural para Forma Normal de Chomsky (FNC/CNF)
    # ------------------------------------------------------------------
    def to_cnf(self):
        self.log.write("=== Conversão para Forma Normal de Chomsky (FNC / CNF) ===\n")
        self.log.write("Gramática antes da FNC:\n")
        self.log.write(self.g.to_text() + "\n\n")

        g = self.g

        # Substituir terminais em produções longas por variáveis auxiliares
        new_prods = defaultdict(set)
        terminal_map = {}  # terminal -> novo não-terminal

        for A, rhs_set in g.productions.items():
            for rhs in rhs_set:
                # mantém produções S -> ε
                if len(rhs) == 1 and rhs[0] == EPSILON:
                    new_prods[A].add(rhs)
                    continue

                if len(rhs) == 1:
                    # A -> a (ou algum caso atípico que sobrou)
                    new_prods[A].add(rhs)
                    continue

                # produção com comprimento >= 2
                new_rhs = []
                for sym in rhs:
                    if sym in g.terminals:
                        if sym not in terminal_map:
                            T_sym = self.fresh_nonterminal("T_" + sym)
                            terminal_map[sym] = T_sym
                            g.nonterminals.add(T_sym)
                        new_rhs.append(terminal_map[sym])
                    else:
                        new_rhs.append(sym)
                new_prods[A].add(tuple(new_rhs))

        # adicionar produções T_a -> a
        for term, var in terminal_map.items():
            new_prods[var].add((term,))

        g.productions = new_prods

        # Quebrar produções com mais de 2 símbolos em produções binárias
        new_prods2 = defaultdict(set)
        for A, rhs_set in g.productions.items():
            for rhs in rhs_set:
                if len(rhs) <= 2:
                    new_prods2[A].add(rhs)
                else:
                    symbols = list(rhs)
                    current_left = A
                    while len(symbols) > 2:
                        X1 = symbols.pop(0)
                        new_var = self.fresh_nonterminal("X")
                        g.nonterminals.add(new_var)
                        new_prods2[current_left].add((X1, new_var))
                        current_left = new_var
                    # último par
                    new_prods2[current_left].add(tuple(symbols))

        g.productions = new_prods2
        self._recompute_terminals()

        self.log.write("Gramática depois de colocada em FNC:\n")
        self.log.write(self.g.to_text() + "\n\n")

    # ------------------------------------------------------------------
    # 5) Conversão para Forma Normal de Greibach (FNG/GNF)
    # ------------------------------------------------------------------
    def to_greibach(self):
        self.log.write("=== Conversão para Forma Normal de Greibach (FNG / GNF) ===\n")
        self.log.write("Gramática antes da FNG (já em FNC):\n")
        self.log.write(self.g.to_text() + "\n\n")

        g = self.g

        # ordem dos não-terminais: símbolo inicial primeiro
        order = [g.start_symbol] + [A for A in sorted(g.nonterminals) if A != g.start_symbol]

        # Passo: para cada Ai, eliminar produções Ai -> Aj γ com j < i
        i = 0
        while i < len(order):
            Ai = order[i]
            rhs_set = g.productions.get(Ai, set())
            changed = True
            while changed:
                changed = False
                new_rhs_set = set()
                for rhs in rhs_set:
                    if len(rhs) > 0 and rhs[0] in g.nonterminals:
                        Aj = rhs[0]
                        if Aj in order:
                            j = order.index(Aj)
                        else:
                            j = None
                        if j is not None and j < i:
                            # substituir Aj pela "corpo" de suas produções
                            gamma = rhs[1:]
                            for delta in g.productions.get(Aj, []):
                                # ignorar ε-produções (não deveriam existir nesta fase)
                                if len(delta) == 1 and delta[0] == EPSILON:
                                    # Aj => ε: some Aj
                                    if gamma:
                                        new_rhs_set.add(gamma)
                                    elif Ai == g.start_symbol:
                                        new_rhs_set.add((EPSILON,))
                                    continue
                                new_rhs_set.add(delta + gamma)
                            changed = True
                        else:
                            new_rhs_set.add(rhs)
                    else:
                        new_rhs_set.add(rhs)
                rhs_set = new_rhs_set
            g.productions[Ai] = rhs_set

            # Eliminar recursão à esquerda imediata em Ai
            alphas = []  # Ai -> Ai α
            betas = []   # Ai -> β (β não começa com Ai)
            for rhs in g.productions.get(Ai, []):
                if len(rhs) > 0 and rhs[0] == Ai:
                    alphas.append(rhs[1:])
                else:
                    betas.append(rhs)

            if alphas:
                # esquema clássico: introduz variável Z
                Z = self.fresh_nonterminal("Z_" + Ai)
                g.nonterminals.add(Z)
                order.append(Z)

                new_prods_Ai = set()
                prods_Z = set()

                # A -> β | β Z
                for beta in betas:
                    new_prods_Ai.add(beta)
                    new_prods_Ai.add(beta + (Z,))

                # Z -> α | α Z
                for alpha in alphas:
                    prods_Z.add(alpha)
                    prods_Z.add(alpha + (Z,))

                g.productions[Ai] = new_prods_Ai
                g.productions[Z] = prods_Z

            i += 1

        self.log.write("Após eliminar Ai->Aj com j<i e recursão à esquerda:\n")
        self.log.write(self.g.to_text() + "\n\n")

        # Passo final: garantir que toda produção começa com terminal
        changed = True
        while changed:
            changed = False
            for A in list(g.nonterminals):
                rhs_set = g.productions.get(A, set())
                new_rhs_set = set()
                for rhs in rhs_set:
                    if len(rhs) == 0:
                        continue
                    first = rhs[0]
                    if first in g.nonterminals:
                        changed = True
                        resto = rhs[1:]
                        for delta in g.productions.get(first, []):
                            # ignorar ε-produções
                            if len(delta) == 1 and delta[0] == EPSILON:
                                if resto:
                                    new_rhs_set.add(resto)
                                elif A == g.start_symbol:
                                    new_rhs_set.add((EPSILON,))
                                continue
                            new_rhs_set.add(delta + resto)
                    else:
                        new_rhs_set.add(rhs)
                g.productions[A] = new_rhs_set

        self._recompute_terminals()

        self.log.write("Gramática final em Forma Normal de Greibach:\n")
        self.log.write(self.g.to_text() + "\n\n")


def main():
    if len(sys.argv) >= 3:
        input_path = sys.argv[1]
        output_path = sys.argv[2]
    else:
        input_path = input("Informe o caminho do arquivo de entrada (.txt): ").strip()
        output_path = input("Informe o caminho do arquivo de saída de log (.txt): ").strip()
        if not output_path:
            output_path = "saida_normalizacao.txt"

    grammar = Grammar.from_file(input_path)

    with open(output_path, "w", encoding="utf-8") as log:
        normalizer = Normalizer(grammar, log)
        normalizer.log_initial()

        print("Escolha a opção de normalização:")
        print("  1 - Apenas remover produções-λ (ε)")
        print("  2 - Converter totalmente para Forma Normal de Greibach (FNG)")
        option = input("Opção (1/2): ").strip()

        log.write("Opção de normalização escolhida: " + option + "\n\n")

        if option == "1":
            normalizer.remove_epsilon()
            log.write("=== Fim: gramática após remoção de λ ===\n")
            log.write(normalizer.g.to_text() + "\n")
        else:
            # pipeline completa até FNG: λ, unitárias, inúteis, FNC e FNG
            normalizer.remove_epsilon()
            normalizer.remove_unit()
            normalizer.remove_useless()
            normalizer.to_cnf()
            normalizer.to_greibach()
            log.write("=== Fim: gramática em Forma Normal de Greibach ===\n")
            log.write(normalizer.g.to_text() + "\n")

    print(f"Normalização concluída. Veja o log em: {output_path}")


if __name__ == "__main__":
    main()
