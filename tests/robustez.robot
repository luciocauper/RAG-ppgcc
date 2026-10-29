*** Settings ***
Documentation       Robustez: variações de escrita e paráfrases devem levar à mesma resposta.
Resource            ../resources/dify_keywords.robot
Suite Setup         Verificar Disponibilidade Da API
Test Template       Executar Caso De Pergunta Unica
Test Tags           robustez


*** Test Cases ***
CT12 Pergunta com erros ortograficos                CT12
CT13 Parafrase sobre frequencia                     CT13
CT23 Divergencia 48 quarenta no documento           CT23
    [Tags]    contradicao
CT24 Linguagem informal sobre creditos do mestrado   CT24
CT25 Parafrase sobre prazo maximo do mestrado        CT25
