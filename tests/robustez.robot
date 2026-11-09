*** Settings ***
Documentation       Robustez: variações de escrita e paráfrases devem levar à mesma resposta.
Resource            ../resources/dify_keywords.robot
Suite Setup         Verificar Disponibilidade Da API
Test Tags           robustez


*** Test Cases ***
CT12 Pergunta com erros ortograficos
    [Documentation]    Verifica se o assistente responde corretamente apesar de erros ortográficos na pergunta.
    [Tags]    CT12
    Given o caso de teste    CT12
    When a pergunta é enviada ao assistente
    Then a resposta deve atender aos critérios de aceitação

CT13 Parafrase sobre frequencia
    [Documentation]    Verifica se o assistente relaciona "faltar mais de um quarto" ao limite de 75% (Art. 36).
    [Tags]    CT13
    Given o caso de teste    CT13
    When a pergunta é enviada ao assistente
    Then a resposta deve atender aos critérios de aceitação

CT23 Divergencia 48 quarenta no documento
    [Documentation]    Verifica se o assistente responde 48 créditos apesar da divergência "48 (quarenta)" no Art. 31b.
    [Tags]    CT23    contradicao
    Given o caso de teste    CT23
    When a pergunta é enviada ao assistente
    Then a resposta deve atender aos critérios de aceitação

CT24 Linguagem informal sobre creditos do mestrado
    [Documentation]    Verifica se o assistente informa 24 créditos do mestrado mesmo em linguagem informal.
    [Tags]    CT24
    Given o caso de teste    CT24
    When a pergunta é enviada ao assistente
    Then a resposta deve atender aos critérios de aceitação

CT25 Parafrase sobre prazo maximo do mestrado
    [Documentation]    Verifica se o assistente informa 24 meses como duração máxima do mestrado em paráfrase.
    [Tags]    CT25
    Given o caso de teste    CT25
    When a pergunta é enviada ao assistente
    Then a resposta deve atender aos critérios de aceitação
