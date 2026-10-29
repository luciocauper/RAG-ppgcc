*** Settings ***
Documentation       Contexto conversacional: perguntas dependentes de turnos anteriores (mesmo conversation_id).
Resource            ../resources/dify_keywords.robot
Suite Setup         Verificar Disponibilidade Da API
Test Template       Executar Caso Conversacional
Test Tags           conversa


*** Test Cases ***
CT16 Nota minima referida ao doutorado              CT16
CT28 Elipse doutorado para mestrado                 CT28
CT29 Anafora sobre membros da banca                 CT29
CT30 Troca de nivel na duracao da apresentacao      CT30
