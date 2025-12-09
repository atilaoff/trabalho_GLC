import sys
from chomsky import *
from greibach import * 
from simplificacao import *
from utils import *
import os

class Logger(object):
    def __init__(self, nome_arquivo="../test_files/gramatica6.txt"):
        self.terminal = sys.stdout
        self.log = open(nome_arquivo, "w", encoding="utf-8")

    def write(self, message):
        self.terminal.write(message) # imprime na tela
        self.log.write(message)      # salva no arquivo

    def flush(self):
        # necessário para compatibilidade com o sistema
        self.terminal.flush()
        self.log.flush()



def menu():
    print("="*50)
    print("  NORMALIZAÇÃO DE GRAMÁTICAS")
    print("="*50)
    print("1 - Forma Normal de Chomsky (FNC)")
    print("2 - Forma Normal de Greibach (FNG)")
    print("0 - Sair")
    return input("\nEscolha uma opção: ")


def main():

    print("\n=== PROCESSADOR DE GRAMÁTICAS ===\n")

    opcao = menu()

    if opcao == "0":
        print("\nEncerrando...")
        return

    arquivo_entrada = input("\nDigite o caminho do arquivo da gramática (.txt): ").strip()
    arquivo_saida = input("\nDigite o nome do arquivo de saída (ex: resultado.txt): ").strip()

    caminho_entrada = os.path.join("../files/", arquivo_entrada)
    caminho_saida = os.path.join("../resultados/", arquivo_saida)

    print("\nLendo gramática...\n")

    gramatica = ler_gramatica(caminho_entrada)

    sys.stdout = Logger(caminho_saida)

    print("\n=== ETAPA 1: SIMPLIFICAÇÃO ===")
    gramatica = simplificar_gramatica(gramatica)

    if opcao == "1":
        print("\n=== CONVERSÃO PARA FORMA NORMAL DE CHOMSKY ===")
        gramatica = forma_normal_chomsky(gramatica)

    elif opcao == "2":
        print("\n=== CONVERSÃO PARA FORMA NORMAL DE GREIBACH ===")
        gramatica = forma_normal_greibach(gramatica)

    else:
        print("\nOpção inválida.")
        return

    print("\nProcesso concluído com sucesso!")


if __name__ == "__main__":
    main()