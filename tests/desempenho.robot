*** Settings ***
Documentation       Desempenho e estabilidade: latência, variabilidade entre repetições e entradas extensas.
Resource            ../resources/dify_keywords.robot
Suite Setup         Verificar Disponibilidade Da API
Test Tags           desempenho


*** Test Cases ***
CT17 Latencia dentro do limite
    [Documentation]    Todas as repetições devem ter latência abaixo do limite configurado.
    [Tags]    CT17
    Given o caso de teste    CT17
    When a pergunta é repetida    %{REPETICOES_CONSISTENCIA=3}
    Then a latência máxima deve estar dentro do limite    %{LIMITE_LATENCIA_S=30}

CT18 Consistencia entre repeticoes
    [Documentation]    Respostas repetidas devem ser factualmente corretas e lexicalmente similares.
    [Tags]    CT18
    Given o caso de teste    CT18
    When a pergunta é repetida    %{REPETICOES_CONSISTENCIA=3}
    Then cada resposta deve atender aos critérios do caso
    And a similaridade entre respostas deve estar acima do mínimo    %{LIMITE_SIMILARIDADE_CONSISTENCIA=0.5}

CT19 Entrada extensa tratada sem erro de servidor
    [Documentation]    Uma entrada muito longa deve ser tratada sem erro 5xx (responder ou rejeitar com 4xx).
    [Tags]    CT19
    Given o caso de teste    CT19
    When uma entrada extensa é enviada
    Then o servidor não deve retornar erro 5xx
