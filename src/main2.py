from utils import ler_gramatica
from simplificacao import simplificar_gramatica
from chomsky import *
#G = ler_gramatica("GLC_completa.txt")
#G = ler_gramatica("gramatica2.txt")
G = ler_gramatica("gramatica4.txt")

G_simplificada = simplificar_gramatica(G)

gramatica_fnc = forma_normal_chomsky(G_simplificada)
