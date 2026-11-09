*** Settings ***
Documentation       Contexto conversacional: perguntas dependentes de turnos anteriores (mesmo conversation_id).
Resource            ../resources/dify_keywords.robot
Suite Setup         Verificar Disponibilidade Da API
Test Tags           conversa


*** Test Cases ***
CT16 Nota minima referida ao doutorado
    [Documentation]    Verifica se o 2º turno ("nessas disciplinas") usa o contexto do 1º (doutorado).
    [Tags]    CT16
    Given o caso conversacional    CT16
    FOR    ${turno}    IN    @{caso}[turnos]
        When o turno é enviado ao assistente    ${turno}
        Then a resposta do turno deve atender aos critérios
    END

CT28 Elipse doutorado para mestrado
    [Documentation]    Verifica interpretação de elipse ("E no mestrado?") e pergunta seguinte sobre qualificação.
    [Tags]    CT28
    Given o caso conversacional    CT28
    FOR    ${turno}    IN    @{caso}[turnos]
        When o turno é enviado ao assistente    ${turno}
        Then a resposta do turno deve atender aos critérios
    END

CT29 Anafora sobre membros da banca
    [Documentation]    Verifica interpretação de "deles" como referência aos membros da banca do turno anterior.
    [Tags]    CT29
    Given o caso conversacional    CT29
    FOR    ${turno}    IN    @{caso}[turnos]
        When o turno é enviado ao assistente    ${turno}
        Then a resposta do turno deve atender aos critérios
    END

CT30 Troca de nivel na duracao da apresentacao
    [Documentation]    Verifica se o 2º turno ("E no doutorado?") responde com os valores do doutorado, não do mestrado.
    [Tags]    CT30
    Given o caso conversacional    CT30
    FOR    ${turno}    IN    @{caso}[turnos]
        When o turno é enviado ao assistente    ${turno}
        Then a resposta do turno deve atender aos critérios
    END
