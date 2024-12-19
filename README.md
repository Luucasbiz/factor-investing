Aplicando Factor Investing nas Ações Brasileiras

Esta estratégia busca identificar ações com alto potencial, utilizando fatores fundamentais para avaliar o valor e a rentabilidade das empresas, com foco em ações subavaliadas e eficientes. 

Indicadores Utilizados 

- EV/EBIT: Mede o valor pago pelo mercado por cada unidade de lucro ajustada pela dívida, destacando ações subavaliadas.

- ROIC: Avalia o retorno sobre o capital investido, refletindo a eficiência da empresa em gerar lucros.

Processo de Coleta e Análise de Dados 

Os dados são obtidos por web scraping no site Fundamentus e passam por três etapas principais:

- Coleta e Limpeza: O script coleta os dados, remove símbolos e ajusta os valores para o formato numérico.

- Filtro de Liquidez: Considera apenas ações com liquidez mínima de R$ 1 milhão nos últimos dois meses.

- Classificação e Seleção: Classifica as ações com base nos indicadores EV/EBIT (ordem crescente) e ROIC (ordem decrescente), selecionando as 10 ações mais bem classificadas.

Execução de Ordens no MetaTrader 5 (MT5) 

Além da seleção das ações, o sistema envia ordens de compra para o MetaTrader 5 (MT5) com as seguintes etapas:

- Verifica se o mercado de ações está aberto.

- Solicita as credenciais de login no MT5.

- Exige aceitação de um termo de responsabilidade.

- Envia ordens de compra com o volume definido pelo usuário.

Como Utilizar 

- Clone o repositório para seu ambiente local.

- Instale as dependências necessárias.

- Configure suas credenciais de login no MetaTrader 5 (MT5).

- Execute o script principal para iniciar o processo.

Referência

Para entender mais sobre a aplicação de fatores em estratégias de investimento, consulte este artigo na ScienceDirect:

Link: https://www.sciencedirect.com/science/article/abs/pii/S0304405X14002323  
