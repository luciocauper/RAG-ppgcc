*** Settings ***
Documentation       Correção factual: as respostas devem coincidir com o regimento (inclui caso de contradição).
Resource            ../resources/dify_keywords.robot
Suite Setup         Verificar Disponibilidade Da API
Test Tags           factual


*** Test Cases ***
CT01 Nota minima para aprovacao
    [Documentation]    Verifica se o assistente informa a nota mínima 7,0 prevista no Art. 37.
    [Tags]    CT01
    Given o caso de teste    CT01
    When a pergunta é enviada ao assistente
    Then a resposta deve atender aos critérios de aceitação

CT02 Frequencia minima
    [Documentation]    Verifica se o assistente informa a frequência mínima de 75% (Art. 36).
    [Tags]    CT02
    Given o caso de teste    CT02
    When a pergunta é enviada ao assistente
    Then a resposta deve atender aos critérios de aceitação

CT03 Creditos exigidos no doutorado
    [Documentation]    Verifica se o assistente informa 48 créditos em disciplinas no doutorado (Art. 31b, 32ii).
    [Tags]    CT03
    Given o caso de teste    CT03
    When a pergunta é enviada ao assistente
    Then a resposta deve atender aos critérios de aceitação

CT04 Limite de orientandos por professor
    [Documentation]    Verifica se o assistente informa o limite de 8 orientandos (Art. 29) e a exceção.
    [Tags]    CT04
    Given o caso de teste    CT04
    When a pergunta é enviada ao assistente
    Then a resposta deve atender aos critérios de aceitação

CT05 Trancamento no primeiro semestre
    [Documentation]    Verifica se o assistente informa que o trancamento não é permitido no 1º período (Art. 31§4).
    [Tags]    CT05
    Given o caso de teste    CT05
    When a pergunta é enviada ao assistente
    Then a resposta deve atender aos critérios de aceitação

CT06 Prorrogacao do doutorado
    [Documentation]    Verifica se o assistente informa prorrogação de 12 meses, total 60 (Art. 31§3b).
    [Tags]    CT06
    Given o caso de teste    CT06
    When a pergunta é enviada ao assistente
    Then a resposta deve atender aos critérios de aceitação

CT07 Composicao da banca de doutorado
    [Documentation]    Verifica se o assistente informa 5 membros com 2 externos na banca de doutorado (Art. 41§2).
    [Tags]    CT07
    Given o caso de teste    CT07
    When a pergunta é enviada ao assistente
    Then a resposta deve atender aos critérios de aceitação

CT08 Duracao da apresentacao oral
    [Documentation]    Verifica se o assistente informa 40 a 50 minutos para defesa de doutorado (Art. 43§1).
    [Tags]    CT08
    Given o caso de teste    CT08
    When a pergunta é enviada ao assistente
    Then a resposta deve atender aos critérios de aceitação

CT09 Contradicao no prazo de qualificacao
    [Documentation]    Verifica se o assistente aponta a contradição entre Art. 35 (36º mês) e Art. 39d (30º mês).
    [Tags]    CT09    contradicao
    Given o caso de teste    CT09
    When a pergunta é enviada ao assistente
    Then a resposta deve atender aos critérios de aceitação
