*** Settings ***
Documentation       Keywords compartilhadas pelas suítes de teste do Assistente PPGCC/UECE (Dify + RAG).
...                 Organizadas em padrão BDD (Given/When/Then) para separar comportamento de implementação.
Library             Collections
Library             ../libraries/dify_client.py
Library             ../libraries/rag_evaluator.py


*** Keywords ***
# --- Pergunta única (factualidade, alucinação, robustez, segurança) ---

o caso de teste
    [Documentation]    Carrega um caso do golden dataset e prepara as variáveis do teste.
    [Arguments]    ${id}
    Set Test Variable    ${caso_id}    ${id}
    ${caso}=    Obter Caso    ${id}
    Set Test Variable    ${caso}

a pergunta é enviada ao assistente
    [Documentation]    Envia a pergunta do caso em uma conversa nova e registra a resposta.
    ${r}=    Enviar Pergunta    ${caso}[pergunta]    caso_id=${caso_id}
    Set Test Variable    ${resultado}    ${r}

a resposta deve atender aos critérios de aceitação
    [Documentation]    Aplica os critérios determinísticos do caso à resposta obtida.
    Validar Caso    ${caso}    ${resultado}[resposta]

# --- Caso conversacional (vários turnos, mesmo conversation_id) ---

o caso conversacional
    [Documentation]    Carrega um caso conversacional e inicia uma conversa vazia.
    [Arguments]    ${id}
    Set Test Variable    ${caso_id}    ${id}
    ${caso}=    Obter Caso    ${id}
    Set Test Variable    ${caso}
    Set Test Variable    ${conversation_id}    ${EMPTY}

o turno é enviado ao assistente
    [Documentation]    Envia um turno na conversa atual e registra a resposta para validação.
    [Arguments]    ${turno}
    ${r}=    Enviar Pergunta    ${turno}[pergunta]    ${conversation_id}    caso_id=${caso_id}
    Set Test Variable    ${conversation_id}    ${r}[conversation_id]
    Set Test Variable    ${resposta_turno}    ${r}[resposta]
    Set Test Variable    ${turno_atual}    ${turno}

a resposta do turno deve atender aos critérios
    [Documentation]    Aplica os critérios do turno atual (não pula mesmo sem critérios).
    Validar Caso    ${turno_atual}    ${resposta_turno}    pular_sem_criterios=${False}

# --- Desempenho ---

a pergunta é repetida
    [Documentation]    Envia a pergunta do caso N vezes, cada uma em conversa nova.
    [Arguments]    ${repeticoes}
    ${resultados}=    Create List
    FOR    ${i}    IN RANGE    1    ${repeticoes} + 1
        ${r}=    Enviar Pergunta    ${caso}[pergunta]    caso_id=${caso_id}    rodada=${i}
        Append To List    ${resultados}    ${r}
    END
    Set Test Variable    ${resultados}

a latência máxima deve estar dentro do limite
    [Documentation]    Verifica se todas as latências ficam abaixo do limite (em segundos).
    [Arguments]    ${limite_s}
    Validar Latencia    ${resultados}    ${limite_s}

cada resposta deve atender aos critérios do caso
    [Documentation]    Valida cada resposta individualmente, continuando em caso de falha.
    FOR    ${r}    IN    @{resultados}
        Run Keyword And Continue On Failure    Validar Caso    ${caso}    ${r}[resposta]
    END

a similaridade entre respostas deve estar acima do mínimo
    [Documentation]    Verifica similaridade lexical média entre as respostas repetidas.
    [Arguments]    ${minimo}
    Validar Consistencia    ${resultados}    ${minimo}

uma entrada extensa é enviada
    [Documentation]    Envia a pergunta do caso precedida de muito preenchimento, sem exigir sucesso.
    ${preenchimento}=    Evaluate    "Considere o regimento do programa. " * ${caso}[repeticoes_preenchimento]
    ${status}=    Obter Status Da Requisicao    ${preenchimento}${caso}[pergunta]
    Set Test Variable    ${status_http}    ${status}

o servidor não deve retornar erro 5xx
    [Documentation]    Aceita 2xx e 4xx, mas rejeita erros de servidor (5xx).
    Should Be True    ${status_http} < 500    Servidor retornou erro ${status_http} para entrada extensa

# --- API ---

que a API está acessível
    [Documentation]    Verifica se a API do Dify responde e a chave é válida.
    Verificar Disponibilidade Da API

uma pergunta de saudação é enviada ao assistente
    [Documentation]    Envia uma pergunta simples e registra o resultado.
    ${r}=    Enviar Pergunta    Olá, sobre o que você pode responder?    caso_id=API01
    Set Test Variable    ${resultado}    ${r}

a resposta deve conter texto e identificador de conversa
    [Documentation]    A resposta deve ter conteúdo e um conversation_id não vazio.
    Should Not Be Empty    ${resultado}[resposta]
    Should Not Be Empty    ${resultado}[conversation_id]

uma pergunta factual é enviada ao assistente
    [Documentation]    Envia uma pergunta que exige recuperação da base de conhecimento.
    ${r}=    Enviar Pergunta    Qual é a nota mínima para aprovação em uma disciplina?    caso_id=API02
    Set Test Variable    ${resultado}    ${r}

a resposta deve trazer trechos recuperados da base
    [Documentation]    Exige "Citations and Attributions" habilitado no app; sem isso o Ragas não recebe contextos.
    Should Not Be Empty    ${resultado}[contextos]

uma pergunta é enviada com chave inválida
    [Documentation]    Tenta enviar uma pergunta com uma chave de API falsa.
    ${status}=    Obter Status Da Requisicao    teste    api_key=app-chave-invalida
    Set Test Variable    ${status_http}    ${status}

o status HTTP deve ser
    [Documentation]    Verifica se o status HTTP retornado corresponde ao esperado.
    [Arguments]    ${esperado}
    Should Be Equal As Integers    ${status_http}    ${esperado}
