*** Settings ***
Documentation       Desempenho e estabilidade: latência, variabilidade entre repetições e entradas extensas.
Resource            ../resources/dify_keywords.robot
Suite Setup         Verificar Disponibilidade Da API
Test Tags           desempenho


*** Test Cases ***
CT17 Latencia dentro do limite
    ${resultados}=    Repetir Pergunta Do Caso    CT17    %{REPETICOES_CONSISTENCIA=3}
    Validar Latencia    ${resultados}    %{LIMITE_LATENCIA_S=30}

CT18 Consistencia entre repeticoes
    ${caso}=    Obter Caso    CT18
    ${resultados}=    Repetir Pergunta Do Caso    CT18    %{REPETICOES_CONSISTENCIA=3}
    FOR    ${r}    IN    @{resultados}
        Run Keyword And Continue On Failure    Validar Caso    ${caso}    ${r}[resposta]
    END
    Validar Consistencia    ${resultados}    %{LIMITE_SIMILARIDADE_CONSISTENCIA=0.5}

CT19 Entrada extensa tratada sem erro de servidor
    ${caso}=    Obter Caso    CT19
    ${preenchimento}=    Evaluate    "Considere o regimento do programa. " * ${caso}[repeticoes_preenchimento]
    ${status}=    Obter Status Da Requisicao    ${preenchimento}${caso}[pergunta]
    Should Be True    ${status} < 500    Servidor retornou erro ${status} para entrada extensa
