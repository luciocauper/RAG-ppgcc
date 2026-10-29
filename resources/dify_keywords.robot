*** Settings ***
Documentation       Keywords compartilhadas pelas suítes de teste do Assistente PPGCC/UECE (Dify + RAG).
Library             Collections
Library             ../libraries/dify_client.py
Library             ../libraries/rag_evaluator.py


*** Keywords ***
Executar Caso De Pergunta Unica
    [Documentation]    Envia a pergunta do caso em uma conversa nova e aplica os critérios do dataset.
    [Arguments]    ${caso_id}
    ${caso}=    Obter Caso    ${caso_id}
    ${r}=    Enviar Pergunta    ${caso}[pergunta]    caso_id=${caso_id}
    Validar Caso    ${caso}    ${r}[resposta]

Executar Caso Conversacional
    [Documentation]    Envia os turnos do caso na mesma conversa, validando cada resposta.
    [Arguments]    ${caso_id}
    ${caso}=    Obter Caso    ${caso_id}
    ${conversa}=    Set Variable    ${EMPTY}
    FOR    ${turno}    IN    @{caso}[turnos]
        ${r}=    Enviar Pergunta    ${turno}[pergunta]    ${conversa}    caso_id=${caso_id}
        ${conversa}=    Set Variable    ${r}[conversation_id]
        Validar Caso    ${turno}    ${r}[resposta]    pular_sem_criterios=${False}
    END

Repetir Pergunta Do Caso
    [Documentation]    Envia a pergunta do caso N vezes, cada uma em conversa nova, e retorna os resultados.
    [Arguments]    ${caso_id}    ${repeticoes}
    ${caso}=    Obter Caso    ${caso_id}
    ${resultados}=    Create List
    FOR    ${i}    IN RANGE    1    ${repeticoes} + 1
        ${r}=    Enviar Pergunta    ${caso}[pergunta]    caso_id=${caso_id}    rodada=${i}
        Append To List    ${resultados}    ${r}
    END
    RETURN    ${resultados}
