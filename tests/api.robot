*** Settings ***
Documentation       Verificações básicas da API do Dify (pré-condição das demais suítes).
Resource            ../resources/dify_keywords.robot
Test Tags           api


*** Test Cases ***
API Disponivel Com Chave Valida
    Verificar Disponibilidade Da API

Resposta Contem Texto E Identificador De Conversa
    ${r}=    Enviar Pergunta    Olá, sobre o que você pode responder?    caso_id=API01
    Should Not Be Empty    ${r}[resposta]
    Should Not Be Empty    ${r}[conversation_id]

Resposta Traz Trechos Recuperados Da Base
    [Documentation]    Exige "Citations and Attributions" habilitado no app; sem isso o Ragas não recebe contextos.
    ${r}=    Enviar Pergunta    Qual é a nota mínima para aprovação em uma disciplina?    caso_id=API02
    Should Not Be Empty    ${r}[contextos]

Chave Invalida E Rejeitada
    ${status}=    Obter Status Da Requisicao    teste    api_key=app-chave-invalida
    Should Be Equal As Integers    ${status}    401
