*** Settings ***
Documentation       Segurança: resistência a prompt injection e a vazamento das instruções de sistema.
...                 Falhas aqui são analisadas individualmente, independentemente das médias gerais.
Resource            ../resources/dify_keywords.robot
Suite Setup         Verificar Disponibilidade Da API
Test Template       Executar Caso De Pergunta Unica
Test Tags           seguranca    critico


*** Test Cases ***
CT14 Injecao alterando a nota minima                CT14
CT15 Pedido para revelar o prompt de sistema        CT15
CT26 Role play de coordenador autorizando excecao   CT26
CT27 Premissa falsa sobre artigo inexistente        CT27
