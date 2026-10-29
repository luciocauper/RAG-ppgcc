*** Settings ***
Documentation       Correção factual: as respostas devem coincidir com o regimento (inclui caso de contradição).
Resource            ../resources/dify_keywords.robot
Suite Setup         Verificar Disponibilidade Da API
Test Template       Executar Caso De Pergunta Unica
Test Tags           factual


*** Test Cases ***
CT01 Nota minima para aprovacao                     CT01
CT02 Frequencia minima                              CT02
CT03 Creditos exigidos no doutorado                 CT03
CT04 Limite de orientandos por professor            CT04
CT05 Trancamento no primeiro semestre               CT05
CT06 Prorrogacao do doutorado                       CT06
CT07 Composicao da banca de doutorado               CT07
CT08 Duracao da apresentacao oral                   CT08
CT09 Contradicao no prazo de qualificacao           CT09
    [Tags]    contradicao
