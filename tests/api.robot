*** Settings ***
Documentation       Verificações básicas da API do Dify (pré-condição das demais suítes).
...                 Esta suíte também funciona como smoke test automatizado do ambiente.
Resource            ../resources/dify_keywords.robot
Test Tags           api


*** Test Cases ***
API Disponivel Com Chave Valida
    [Documentation]    Verifica se a API do Dify responde e a chave de aplicação é aceita.
    [Tags]    smoke
    Given que a API está acessível

Resposta Contem Texto E Identificador De Conversa
    [Documentation]    Uma pergunta simples deve devolver resposta e identificador de conversa.
    When uma pergunta de saudação é enviada ao assistente
    Then a resposta deve conter texto e identificador de conversa

Resposta Traz Trechos Recuperados Da Base
    [Documentation]    Exige "Citations and Attributions" habilitado no app; sem isso o Ragas não recebe contextos.
    When uma pergunta factual é enviada ao assistente
    Then a resposta deve trazer trechos recuperados da base

Chave Invalida E Rejeitada
    [Documentation]    Uma chave de API inválida deve ser rejeitada com HTTP 401.
    When uma pergunta é enviada com chave inválida
    Then o status HTTP deve ser    401
