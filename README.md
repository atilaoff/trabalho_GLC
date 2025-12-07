PROJETO — NORMALIZAÇÃO DE GRAMÁTICAS LIVRES DE CONTEXTO (GLC)


DESCRIÇÃO DO PROJETO
-------------------
Este projeto implementa uma solução para normalização de Gramáticas Livres de Contexto (GLC)
utilizando:

- Forma Normal de Chomsky (FNC)
- Forma Normal de Greibach (FNG)

O sistema foi desenvolvido em Python 3 e realiza automaticamente as etapas de:

- Simplificação da gramática
- Remoção de produções ε
- Remoção de produções unitárias
- Eliminação de símbolos inúteis
- Conversão para a forma normal escolhida

Durante a execução, todas as etapas são exibidas na tela e salvas em arquivo.


COMPILAÇÃO E EXECUÇÃO
--------------------
Para executar o programa:

1) Acesse a pasta src do projeto.
2) Execute o comando:

python ./main.py


INSTRUÇÕES DE USO
----------------
Ao executar o programa:

1) Escolha a forma normal desejada (Chomsky ou Greibach) no menu.
2) Informe o nome do arquivo de entrada (.txt).
   - O arquivo deve estar na pasta "files".
3) Informe o nome do arquivo de saída (.txt).
   - O resultado será salvo na pasta "resultados".

O programa exibirá todo o processo passo a passo no terminal e no arquivo de saída.


ESTRUTURA DE PASTAS
------------------
src/
│
├── files/         (arquivos de entrada)
│
├── resultados/    (arquivos de saída)
│
├── main.py
├── chomsky.py
├── greibach.py
├── simplificacao.py
└── utils.py


COMPONENTES
-----------
Moisés Átila
Raul Ramalho
