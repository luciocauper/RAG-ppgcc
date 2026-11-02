*** Settings ***
Documentation       Alucinação: o assistente deve reconhecer quando a informação não está no regimento.
Resource            ../resources/dify_keywords.robot
Suite Setup         Verificar Disponibilidade Da API
Test Tags           alucinacao


*** Test Cases ***
CT10 Valor da bolsa nao consta no regimento
    [Documentation]    Verifica se o assistente reconhece que o valor da bolsa não consta no regimento.
    [Tags]    CT10
    Given o caso de teste    CT10
    When a pergunta é enviada ao assistente
    Then a resposta deve atender aos critérios de aceitação

CT11 Pergunta fora do contexto
    [Documentation]    Verifica se o assistente recusa pergunta fora do escopo do regimento.
    [Tags]    CT11
    Given o caso de teste    CT11
    When a pergunta é enviada ao assistente
    Then a resposta deve atender aos critérios de aceitação

CT20 Numero de vagas nao fixado no regimento
    [Documentation]    Verifica se o assistente não inventa número de vagas e menciona o Colegiado.
    [Tags]    CT20
    Given o caso de teste    CT20
    When a pergunta é enviada ao assistente
    Then a resposta deve atender aos critérios de aceitação

CT21 Taxa de matricula nao consta no regimento
    [Documentation]    Verifica se o assistente reconhece que a taxa de matrícula não consta no regimento.
    [Tags]    CT21
    Given o caso de teste    CT21
    When a pergunta é enviada ao assistente
    Then a resposta deve atender aos critérios de aceitação

CT22 Linhas de pesquisa nao nomeadas
    [Documentation]    Verifica se o assistente cita a área de concentração e não inventa nomes de linhas.
    [Tags]    CT22
    Given o caso de teste    CT22
    When a pergunta é enviada ao assistente
    Then a resposta deve atender aos critérios de aceitação
