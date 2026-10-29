*** Settings ***
Documentation       Alucinação: o assistente deve reconhecer quando a informação não está no regimento.
Resource            ../resources/dify_keywords.robot
Suite Setup         Verificar Disponibilidade Da API
Test Template       Executar Caso De Pergunta Unica
Test Tags           alucinacao


*** Test Cases ***
CT10 Valor da bolsa nao consta no regimento         CT10
CT11 Pergunta fora do contexto                      CT11
CT20 Numero de vagas nao fixado no regimento        CT20
CT21 Taxa de matricula nao consta no regimento      CT21
CT22 Linhas de pesquisa nao nomeadas                CT22
