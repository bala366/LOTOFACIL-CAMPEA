# LOTOFÁCIL CAMPEÃO V4 — ANDROID

Aplicativo Android Java, com trevo branco em fundo roxo e geração de PDF **exatamente 2 páginas**.

## Motor
Portado do `LOTOFACIL_CAMPEAO_V3_WINDOWS.py` (motor V2): 300 duplas; score = frequência histórica percentual + 0,5×últimos 100 + últimos 20; limites históricos 3%-97% para primos, Fibonacci, borda, miolo, pares e soma; repetidas 8, 9 ou 10; rejeita jogos idênticos aos sorteios anteriores; otimiza conjuntos de 10 com 35 reinícios e até 22 trocas, usando os últimos 200 sorteios e pesos 6→1, 7→3, 8→10, 9→35, 10→120; extrai 5 duplas disjuntas por emparelhamento ótimo.

**Nota importante:** o gerador aleatório nativo Java não é o mesmo do Python. Portanto, embora a fórmula e a busca tenham sido portadas, **não se garante que o conjunto escolhido seja numericamente idêntico ao Windows**. Os resultados são reproduzíveis dentro desta versão Android com o mesmo histórico. Não garante prêmio.

## Como compilar no GitHub
1. Criar repositório em https://github.com/new
2. Enviar **o conteúdo desta pasta**, inclusive `.github/workflows/android-apk.yml`, à raiz do repositório.
3. Abrir **Actions > Gerar APK Lotofacil Campeao V4 > Run workflow**.
4. Baixar o artefato `LOTOFACIL_CAMPEAO_V4_APK` e instalar o APK.

## Como usar
1. Abrir o TXT/CSV do histórico com o seletor do Android (Downloads). Links de rodapé são ignorados.
2. Analisar 300 duplas. A busca pode demorar, dependendo do celular.
3. Escolher um dos 5 conjuntos candidatos.
4. Conferir 10 falhas, 15 para jogar, filtros e histórico.
5. Salvar o PDF de 2 páginas no local escolhido (por exemplo, Downloads).

O Android usa o seletor de arquivos do sistema, sem exigir permissão de acesso a todos os arquivos.

## Arquivo de referência
`referencia/LOTOFACIL_CAMPEAO_V3_WINDOWS.py` preserva o motor Python original para comparação. O aplicativo compila e roda com Java nativo (sem Python).
