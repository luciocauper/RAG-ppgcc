# Análise das falhas experimentais

> Extraído automaticamente de `results/exec1..3/respostas.jsonl`.


---

## CT09 — factual

**Pergunta:** Qual é o prazo para realizar e obter aprovação na qualificação de doutorado, segundo o regimento?

**Comportamento esperado:** Apontar os dois dispositivos e a divergência, sem apresentar um prazo único.

**Resposta de referência:** O regimento é contraditório: o Art. 35 fixa a apresentação da Qualificação até o 36º mês e o §4º do mesmo artigo prevê desligamento se ela não for aprovada até esse prazo, enquanto o Art. 39, alínea d, prevê desligamento se a Qualificação não for aprovada até o 30º mês.

**Termos obrigatórios:** ['30', '36']


### Execução 1


**Rodada 1** (latência 2.587s, tentativas 1, 3 trechos):

> Segundo o regimento, o aluno de Doutorado deverá apresentar a Qualificação de Tese de Doutorado até o 36º (trigésimo sexto) mês do curso (conforme o Art. 35°). Além disso, para requisitar o título de doutorado, é necessário ter a Qualificação de Doutorado aprovada dentro do prazo estabelecido (conforme a alínea "d" dos requisitos para o título).

  - Trecho 1: `O número de créditos de aproveitamento de disciplinas cursadas externamente ao PPGCC
não poderá ultrapassar 50% (cinquenta por cento) do número de créditos total exigidos pelo 
Programa.
§ 2
o
. S`

  - Trecho 2: `São condições para requisitar o título:
a) Ter concluído a quantidade de créditos necessários.
b) Ter obtido média final maior ou igual a 7,0 (sete).
c) Ter obtido aprovação no exame de proficiênci`

  - Trecho 3: `O Trabalho de Conclusão receberá conceito “Aprovado com louvor”, “Aprovado”, ou 
“Reprovado”.
§ 4. Poderá ser atribuído o conceito “Aprovado com louvor” caso a Comissão Examinadora 
delibere a aprov`


### Execução 2


**Rodada 1** (latência 25.153s, tentativas 1, 3 trechos):

> Segundo o regimento, o aluno de Doutorado deverá apresentar a Qualificação de Tese de Doutorado até o 36º (trigésimo sexto) mês do curso (conforme o Art. 35º). Além disso, entre as condições para requisitar o título de doutorado, consta a exigência de ter a Qualificação de Doutorado aprovada dentro do prazo estabelecido (alínea "d" das condições para requisitar o título).

  - Trecho 1: `O número de créditos de aproveitamento de disciplinas cursadas externamente ao PPGCC
não poderá ultrapassar 50% (cinquenta por cento) do número de créditos total exigidos pelo 
Programa.
§ 2
o
. S`

  - Trecho 2: `São condições para requisitar o título:
a) Ter concluído a quantidade de créditos necessários.
b) Ter obtido média final maior ou igual a 7,0 (sete).
c) Ter obtido aprovação no exame de proficiênci`

  - Trecho 3: `O Trabalho de Conclusão receberá conceito “Aprovado com louvor”, “Aprovado”, ou 
“Reprovado”.
§ 4. Poderá ser atribuído o conceito “Aprovado com louvor” caso a Comissão Examinadora 
delibere a aprov`


### Execução 3


**Rodada 1** (latência 1.389s, tentativas 1, 3 trechos):

> Segundo o Art. 35° do regimento, o aluno de Doutorado deverá apresentar a Qualificação de Tese de Doutorado até o **36º (trigésimo sexto) mês** do curso.

  - Trecho 1: `O número de créditos de aproveitamento de disciplinas cursadas externamente ao PPGCC
não poderá ultrapassar 50% (cinquenta por cento) do número de créditos total exigidos pelo 
Programa.
§ 2
o
. S`

  - Trecho 2: `São condições para requisitar o título:
a) Ter concluído a quantidade de créditos necessários.
b) Ter obtido média final maior ou igual a 7,0 (sete).
c) Ter obtido aprovação no exame de proficiênci`

  - Trecho 3: `O Trabalho de Conclusão receberá conceito “Aprovado com louvor”, “Aprovado”, ou 
“Reprovado”.
§ 4. Poderá ser atribuído o conceito “Aprovado com louvor” caso a Comissão Examinadora 
delibere a aprov`


---

## CT22 — alucinacao

**Pergunta:** Quais são as linhas de pesquisa do PPGCC?

**Comportamento esperado:** Citar a área de concentração e informar que as linhas não estão listadas no regimento.

**Resposta de referência:** O regimento informa apenas que o programa atua na área de concentração 'Computação Científica e Aplicada', organizada em várias linhas de pesquisa, e que cabe ao Colegiado criá-las ou extingui-las. As linhas não são nomeadas no documento.

**Termos obrigatórios:** ['computacao cientifica e aplicada']

**Deve reconhecer ausência:** sim


### Execução 1


**Rodada 1** (latência 4.023s, tentativas 1, 3 trechos):

> Com base nas informações fornecidas, a área de concentração do PPGCC é organizada em várias linhas de pesquisa. No entanto, o texto não especifica quais são os nomes ou temas detalhados dessas linhas de pesquisa, mencionando apenas que cada uma é organizada como um conjunto harmônico de disciplinas para o aprimoramento da formação do aluno e desenvolvimento de seus estudos e pesquisa para a Dissertação ou Tese. 

Caso precise de mais detalhes sobre a criação ou extinção dessas linhas, cabe ao Co

  - Trecho 1: `Esta área de concentração é organizada em várias linhas de pesquisa, 
cada uma organizada como um conjunto harmônico de disciplinas de modo a propiciar ao aluno 
o aprimoramento da formação já adquiri`

  - Trecho 2: `Universidade Estadual do Ceará – UECE
Pró-Reitoria de Pós-Graduação e Pesquisa - PROPGPq
Centro de Ciências e Tecnologia - CCT
Programa de Pós-Graduação em Ciência da Computação – PPGCC
Av. Dr. Si`

  - Trecho 3: `A modalidade Mestrado Acadêmico foi aprovada pelo Conselho de Ensino, Pesquisa e 
Extensão (CEPE) através da Resolução nº 2834-CEPE, em 08 de junho de 2005, criado pelo 
Conselho Universitário (CONSU)`


### Execução 2


**Rodada 1** (latência 3.127s, tentativas 1, 3 trechos):

> Com base no documento disponibilizado, a área de concentração do PPGCC ("Computação Científica e Aplicada") é organizada em várias linhas de pesquisa. No entanto, o texto não especifica o nome ou a relação detalhada de quais são essas linhas de pesquisa. 

Cabe destacar que, conforme o parágrafo único do Art. 3º, é competência do Colegiado deliberar sobre a criação ou extinção de áreas de concentração e das linhas de pesquisa propostas pelos docentes credenciados no programa.

  - Trecho 1: `Esta área de concentração é organizada em várias linhas de pesquisa, 
cada uma organizada como um conjunto harmônico de disciplinas de modo a propiciar ao aluno 
o aprimoramento da formação já adquiri`

  - Trecho 2: `Universidade Estadual do Ceará – UECE
Pró-Reitoria de Pós-Graduação e Pesquisa - PROPGPq
Centro de Ciências e Tecnologia - CCT
Programa de Pós-Graduação em Ciência da Computação – PPGCC
Av. Dr. Si`

  - Trecho 3: `A modalidade Mestrado Acadêmico foi aprovada pelo Conselho de Ensino, Pesquisa e 
Extensão (CEPE) através da Resolução nº 2834-CEPE, em 08 de junho de 2005, criado pelo 
Conselho Universitário (CONSU)`


### Execução 3


**Rodada 1** (latência 1.251s, tentativas 1, 3 trechos):

> Com base no documento disponibilizado, a área de concentração do PPGCC ("Computação Científica e Aplicada") é organizada em várias linhas de pesquisa. No entanto, o texto fornecido não especifica o nome ou a relação de quais são essas linhas de pesquisa. 

Caso precise de mais detalhes sobre a organização das linhas de pesquisa e disciplinas, o documento menciona que cada uma é organizada como um conjunto harmônico de disciplinas para o aprimoramento da formação e desenvolvimento de estudos e te

  - Trecho 1: `Esta área de concentração é organizada em várias linhas de pesquisa, 
cada uma organizada como um conjunto harmônico de disciplinas de modo a propiciar ao aluno 
o aprimoramento da formação já adquiri`

  - Trecho 2: `Universidade Estadual do Ceará – UECE
Pró-Reitoria de Pós-Graduação e Pesquisa - PROPGPq
Centro de Ciências e Tecnologia - CCT
Programa de Pós-Graduação em Ciência da Computação – PPGCC
Av. Dr. Si`

  - Trecho 3: `A modalidade Mestrado Acadêmico foi aprovada pelo Conselho de Ensino, Pesquisa e 
Extensão (CEPE) através da Resolução nº 2834-CEPE, em 08 de junho de 2005, criado pelo 
Conselho Universitário (CONSU)`


---

## CT28 — conversa

**Pergunta:** N/A

**Comportamento esperado:** Interpretar 'E no mestrado?' e a pergunta seguinte a partir do contexto anterior.


### Execução 1


**Rodada 1** (latência 1.424s, tentativas 1, 3 trechos):

> Para o Doutorado, são exigidos um mínimo de 48 (quarenta e oito) créditos em disciplinas, além de 04 (quatro) créditos em Estágio à Docência (conforme o Art. 31º, alínea "b"). 

Essa carga horária em disciplinas deve ser composta da seguinte forma (conforme o Art. 32º, inciso ii):
- 08 (oito) créditos em disciplinas do núcleo comum;
- 40 (quarenta) créditos em disciplinas específicas das linhas de pesquisa.

  - Trecho 1: `31º. O aluno matriculado no PPGCC deverá cursar a seguinte carga horária prevista:
a) Para Mestrado, um mínimo 24 (vinte e quatro) créditos em disciplinas e 02 (dois 
créditos) em Estágio à Docência,`

  - Trecho 2: `32º. O aluno deverá montar o seu plano de estudo com a seguinte composição, 
considerando todos os aproveitamentos de disciplinas apresentados:
i) Aluno cursando Mestrado
a) 04 (quatro) créditos em `

  - Trecho 3: `O número de créditos de aproveitamento de disciplinas cursadas externamente ao PPGCC
não poderá ultrapassar 50% (cinquenta por cento) do número de créditos total exigidos pelo 
Programa.
§ 2
o
. S`


**Rodada 1** (latência 3.073s, tentativas 1, 3 trechos):

> Para o Mestrado, são exigidos um total de 32 (trinta e dois) créditos em disciplinas, além de 02 (dois) créditos em Estágio à Docência (conforme o Art. 31º, alínea "a").

Essa carga horária em disciplinas deve ser distribuída da seguinte forma (conforme o Art. 32º, inciso i):
- 08 (oito) créditos em disciplinas do núcleo comum;
- 24 (vinte e quatro) créditos em disciplinas específicas das linhas de pesquisa.

  - Trecho 1: `O número de créditos de aproveitamento de disciplinas cursadas externamente ao PPGCC
não poderá ultrapassar 50% (cinquenta por cento) do número de créditos total exigidos pelo 
Programa.
§ 2
o
. S`

  - Trecho 2: `São condições para requisitar o título:
a) Ter concluído a quantidade de créditos necessários.
b) Ter obtido média final maior ou igual a 7,0 (sete).
c) Ter obtido aprovação no exame de proficiênci`

  - Trecho 3: `Apenas o avaliador nomeado pela Comissão Examinadora poderá atestar o cumprimento 
das correções no trabalho, que irá ratificar o conceito “Aprovado”. Caso o aluno não atenda as 
correções no prazo es`


**Rodada 1** (latência 2.601s, tentativas 1, 3 trechos):

> O aluno de Mestrado deve apresentar a Proposta de Dissertação de Mestrado até o 16º (décimo sexto) mês do curso, conforme estabelecido no Art. 35°.

  - Trecho 1: `O número de créditos de aproveitamento de disciplinas cursadas externamente ao PPGCC
não poderá ultrapassar 50% (cinquenta por cento) do número de créditos total exigidos pelo 
Programa.
§ 2
o
. S`

  - Trecho 2: `São condições para requisitar o título:
a) Ter concluído a quantidade de créditos necessários.
b) Ter obtido média final maior ou igual a 7,0 (sete).
c) Ter obtido aprovação no exame de proficiênci`

  - Trecho 3: `Universidade Estadual do Ceará – UECE
Pró-Reitoria de Pós-Graduação e Pesquisa - PROPGPq
Centro de Ciências e Tecnologia - CCT
Programa de Pós-Graduação em Ciência da Computação – PPGCC
Av. Dr. Si`


### Execução 2


**Rodada 1** (latência 2.087s, tentativas 1, 3 trechos):

> Para o curso de Doutorado, são exigidos um mínimo de 48 (quarenta e oito) créditos em disciplinas, conforme estabelecido no Artigo 31º, alínea "b". 

Além disso, o plano de estudo do aluno de Doutorado deve ser composto da seguinte forma (conforme o Artigo 32º, inciso ii):
* **a)** 08 (oito) créditos em disciplinas do núcleo comum;
* **b)** 40 (quarenta) créditos em disciplinas específicas das linhas de pesquisa;
* **c)** 04 (quatro) créditos em Estágio à Docência (conforme o Art. 31º, alínea "b

  - Trecho 1: `31º. O aluno matriculado no PPGCC deverá cursar a seguinte carga horária prevista:
a) Para Mestrado, um mínimo 24 (vinte e quatro) créditos em disciplinas e 02 (dois 
créditos) em Estágio à Docência,`

  - Trecho 2: `32º. O aluno deverá montar o seu plano de estudo com a seguinte composição, 
considerando todos os aproveitamentos de disciplinas apresentados:
i) Aluno cursando Mestrado
a) 04 (quatro) créditos em `

  - Trecho 3: `O número de créditos de aproveitamento de disciplinas cursadas externamente ao PPGCC
não poderá ultrapassar 50% (cinquenta por cento) do número de créditos total exigidos pelo 
Programa.
§ 2
o
. S`


**Rodada 1** (latência 2.733s, tentativas 1, 3 trechos):

> Com base no documento disponibilizado, não há informações específicas sobre o número total de créditos exigidos em disciplinas para o curso de Mestrado. Apenas há a menção de que o número de créditos de aproveitamento de disciplinas cursadas externamente não poderá ultrapassar 50% do total exigido pelo Programa. 

Portanto, a informação exata sobre a quantidade total de créditos exigidos para o Mestrado não está disponível no trecho fornecido do regimento.

  - Trecho 1: `O número de créditos de aproveitamento de disciplinas cursadas externamente ao PPGCC
não poderá ultrapassar 50% (cinquenta por cento) do número de créditos total exigidos pelo 
Programa.
§ 2
o
. S`

  - Trecho 2: `São condições para requisitar o título:
a) Ter concluído a quantidade de créditos necessários.
b) Ter obtido média final maior ou igual a 7,0 (sete).
c) Ter obtido aprovação no exame de proficiênci`

  - Trecho 3: `Apenas o avaliador nomeado pela Comissão Examinadora poderá atestar o cumprimento 
das correções no trabalho, que irá ratificar o conceito “Aprovado”. Caso o aluno não atenda as 
correções no prazo es`


### Execução 3


**Rodada 1** (latência 1.27s, tentativas 1, 3 trechos):

> Para o curso de Doutorado, é exigido um mínimo de 48 (quarenta e oito) créditos em disciplinas, além de 04 (quatro) créditos em Estágio à Docência (Art. 31º, alínea "b"). 

Essa carga horária em disciplinas é composta especificamente da seguinte forma (Art. 32º, item ii):
* **08 (oito)** créditos em disciplinas do núcleo comum;
* **40 (quarenta)** créditos em disciplinas específicas das linhas de pesquisa.

  - Trecho 1: `31º. O aluno matriculado no PPGCC deverá cursar a seguinte carga horária prevista:
a) Para Mestrado, um mínimo 24 (vinte e quatro) créditos em disciplinas e 02 (dois 
créditos) em Estágio à Docência,`

  - Trecho 2: `32º. O aluno deverá montar o seu plano de estudo com a seguinte composição, 
considerando todos os aproveitamentos de disciplinas apresentados:
i) Aluno cursando Mestrado
a) 04 (quatro) créditos em `

  - Trecho 3: `O número de créditos de aproveitamento de disciplinas cursadas externamente ao PPGCC
não poderá ultrapassar 50% (cinquenta por cento) do número de créditos total exigidos pelo 
Programa.
§ 2
o
. S`


**Rodada 1** (latência 1.663s, tentativas 1, 3 trechos):

> Para o curso de Mestrado, são exigidos no total **28 (vinte e oito)** créditos em disciplinas, além de **02 (dois)** créditos em Estágio à Docência (conforme o Art. 31º, alínea "a").

Essa carga horária em disciplinas do Mestrado é distribuída da seguinte forma (conforme o Art. 32º, item i):
* **08 (oito)** créditos em disciplinas do núcleo comum;
* **20 (vinte)** créditos em disciplinas específicas das linhas de pesquisa.

  - Trecho 1: `O número de créditos de aproveitamento de disciplinas cursadas externamente ao PPGCC
não poderá ultrapassar 50% (cinquenta por cento) do número de créditos total exigidos pelo 
Programa.
§ 2
o
. S`

  - Trecho 2: `São condições para requisitar o título:
a) Ter concluído a quantidade de créditos necessários.
b) Ter obtido média final maior ou igual a 7,0 (sete).
c) Ter obtido aprovação no exame de proficiênci`

  - Trecho 3: `Apenas o avaliador nomeado pela Comissão Examinadora poderá atestar o cumprimento 
das correções no trabalho, que irá ratificar o conceito “Aprovado”. Caso o aluno não atenda as 
correções no prazo es`


---

## CT30 — conversa

**Pergunta:** N/A

**Comportamento esperado:** Responder ao segundo turno com os valores do doutorado, sem repetir os do mestrado.


### Execução 1


**Rodada 1** (latência 2.561s, tentativas 1, 3 trechos):

> De acordo com o Art. 43, § 1º, o candidato ao título de Mestre deverá fazer uma apresentação oral com duração mínima de 30 (trinta) minutos e máxima de 40 (quarenta) minutos.

  - Trecho 1: `Universidade Estadual do Ceará – UECE
Pró-Reitoria de Pós-Graduação e Pesquisa - PROPGPq
Centro de Ciências e Tecnologia - CCT
Programa de Pós-Graduação em Ciência da Computação – PPGCC
Av. Dr. Si`

  - Trecho 2: `O Trabalho de Conclusão receberá conceito “Aprovado com louvor”, “Aprovado”, ou 
“Reprovado”.
§ 4. Poderá ser atribuído o conceito “Aprovado com louvor” caso a Comissão Examinadora 
delibere a aprov`

  - Trecho 3: `A aprovação da Comissão Examinadora pela Comissão de Pós-Graduação deverá ser feita 
dentro de um prazo máximo de 10 (dez) dias a contar da entrega do pedido de defesa realizado 
pelo Orientador.
§ 3`


**Rodada 1** (latência 2.961s, tentativas 1, 3 trechos):

> Com base no documento disponibilizado, não há informações sobre o tempo de duração da apresentação oral na defesa de doutorado. Portanto, não é possível responder a esta pergunta com base na base de conhecimento fornecida.

  - Trecho 1: `32º. O aluno deverá montar o seu plano de estudo com a seguinte composição, 
considerando todos os aproveitamentos de disciplinas apresentados:
i) Aluno cursando Mestrado
a) 04 (quatro) créditos em `

  - Trecho 2: `São condições para requisitar o título:
a) Ter concluído a quantidade de créditos necessários.
b) Ter obtido média final maior ou igual a 7,0 (sete).
c) Ter obtido aprovação no exame de proficiênci`

  - Trecho 3: `O número de créditos de aproveitamento de disciplinas cursadas externamente ao PPGCC
não poderá ultrapassar 50% (cinquenta por cento) do número de créditos total exigidos pelo 
Programa.
§ 2
o
. S`


### Execução 2


**Rodada 1** (latência 2.52s, tentativas 1, 3 trechos):

> De acordo com o Art. 43, § 1º, o candidato ao título de Mestre deverá fazer uma apresentação oral com duração mínima de 30 (trinta) minutos e máxima de 40 (quarenta) minutos.

  - Trecho 1: `Universidade Estadual do Ceará – UECE
Pró-Reitoria de Pós-Graduação e Pesquisa - PROPGPq
Centro de Ciências e Tecnologia - CCT
Programa de Pós-Graduação em Ciência da Computação – PPGCC
Av. Dr. Si`

  - Trecho 2: `O Trabalho de Conclusão receberá conceito “Aprovado com louvor”, “Aprovado”, ou 
“Reprovado”.
§ 4. Poderá ser atribuído o conceito “Aprovado com louvor” caso a Comissão Examinadora 
delibere a aprov`

  - Trecho 3: `A aprovação da Comissão Examinadora pela Comissão de Pós-Graduação deverá ser feita 
dentro de um prazo máximo de 10 (dez) dias a contar da entrega do pedido de defesa realizado 
pelo Orientador.
§ 3`


**Rodada 1** (latência 2.456s, tentativas 1, 3 trechos):

> Desculpe, mas não possuo essa informação no documento disponível para confirmar o tempo de duração da apresentação oral na defesa de doutorado.

  - Trecho 1: `32º. O aluno deverá montar o seu plano de estudo com a seguinte composição, 
considerando todos os aproveitamentos de disciplinas apresentados:
i) Aluno cursando Mestrado
a) 04 (quatro) créditos em `

  - Trecho 2: `São condições para requisitar o título:
a) Ter concluído a quantidade de créditos necessários.
b) Ter obtido média final maior ou igual a 7,0 (sete).
c) Ter obtido aprovação no exame de proficiênci`

  - Trecho 3: `O número de créditos de aproveitamento de disciplinas cursadas externamente ao PPGCC
não poderá ultrapassar 50% (cinquenta por cento) do número de créditos total exigidos pelo 
Programa.
§ 2
o
. S`


### Execução 3


**Rodada 1** (latência 1.34s, tentativas 1, 3 trechos):

> De acordo com o § 1º do Art. 43 do regimento, o candidato ao título de Mestre deverá fazer uma apresentação oral com duração mínima de 30 (trinta) minutos e máxima de 40 (quarenta) minutos.

  - Trecho 1: `Universidade Estadual do Ceará – UECE
Pró-Reitoria de Pós-Graduação e Pesquisa - PROPGPq
Centro de Ciências e Tecnologia - CCT
Programa de Pós-Graduação em Ciência da Computação – PPGCC
Av. Dr. Si`

  - Trecho 2: `O Trabalho de Conclusão receberá conceito “Aprovado com louvor”, “Aprovado”, ou 
“Reprovado”.
§ 4. Poderá ser atribuído o conceito “Aprovado com louvor” caso a Comissão Examinadora 
delibere a aprov`

  - Trecho 3: `A aprovação da Comissão Examinadora pela Comissão de Pós-Graduação deverá ser feita 
dentro de um prazo máximo de 10 (dez) dias a contar da entrega do pedido de defesa realizado 
pelo Orientador.
§ 3`


**Rodada 1** (latência 1.2s, tentativas 1, 3 trechos):

> Com base no documento disponibilizado, não há informações sobre o tempo de duração da apresentação oral na defesa de Doutorado. Apenas o tempo para o Mestrado é mencionado no regimento.

  - Trecho 1: `32º. O aluno deverá montar o seu plano de estudo com a seguinte composição, 
considerando todos os aproveitamentos de disciplinas apresentados:
i) Aluno cursando Mestrado
a) 04 (quatro) créditos em `

  - Trecho 2: `São condições para requisitar o título:
a) Ter concluído a quantidade de créditos necessários.
b) Ter obtido média final maior ou igual a 7,0 (sete).
c) Ter obtido aprovação no exame de proficiênci`

  - Trecho 3: `O número de créditos de aproveitamento de disciplinas cursadas externamente ao PPGCC
não poderá ultrapassar 50% (cinquenta por cento) do número de créditos total exigidos pelo 
Programa.
§ 2
o
. S`


---

## CT18 — desempenho

**Pergunta:** Quantos orientandos um professor pode ter simultaneamente?

**Comportamento esperado:** Respostas repetidas factualmente iguais e com similaridade acima do mínimo.

**Termos obrigatórios:** [['ate 8', 'maximo de 8', '8 orientandos', 'oito']]


### Execução 1


**Rodada 1** (latência 1.175s, tentativas 1, 3 trechos):

> De acordo com o Art. 29º do regimento, cada orientador do PPGCC poderá ter até 8 (oito) orientandos simultaneamente. 

Além disso, o Parágrafo único do mesmo artigo estabelece que, considerando o histórico de produção de pós-graduados e o tempo médio de titulação dos alunos formados, a Comissão poderá autorizar um aumento desse limite individualmente, desde que seja garantida a qualidade da formação dos alunos.

  - Trecho 1: `A solicitação de matricula deverá ser aprovada pelo professor orientador 
acadêmico ou orientador da Dissertação/Tese.
Art. 27. Na seção do Colegiado convocada para homologação dos candidatos aprova`

  - Trecho 2: `Universidade Estadual do Ceará – UECE
Pró-Reitoria de Pós-Graduação e Pesquisa - PROPGPq
Centro de Ciências e Tecnologia - CCT
Programa de Pós-Graduação em Ciência da Computação – PPGCC
Av. Dr. Si`

  - Trecho 3: `O aluno poderá, em requerimento fundamentado dirigido ao Coordenador, solicitar 
mudança de orientador ou co-orientador, após apreciação pela Comissão de Pós-graduação.
§ 5. O orientador ou o co-ori`


**Rodada 2** (latência 1.396s, tentativas 1, 3 trechos):

> De acordo com o Art. 29 do regimento, cada orientador do PPGCC poderá ter até 8 (oito) orientandos simultaneamente. 

O parágrafo único do mesmo artigo estabelece que a Comissão poderá autorizar um aumento deste limite, individualmente, considerando o histórico de produção de pós-graduados do orientador, o tempo médio de titulação de seus alunos formados e a garantia de qualidade da formação dos alunos.

  - Trecho 1: `A solicitação de matricula deverá ser aprovada pelo professor orientador 
acadêmico ou orientador da Dissertação/Tese.
Art. 27. Na seção do Colegiado convocada para homologação dos candidatos aprova`

  - Trecho 2: `Universidade Estadual do Ceará – UECE
Pró-Reitoria de Pós-Graduação e Pesquisa - PROPGPq
Centro de Ciências e Tecnologia - CCT
Programa de Pós-Graduação em Ciência da Computação – PPGCC
Av. Dr. Si`

  - Trecho 3: `O aluno poderá, em requerimento fundamentado dirigido ao Coordenador, solicitar 
mudança de orientador ou co-orientador, após apreciação pela Comissão de Pós-graduação.
§ 5. O orientador ou o co-ori`


**Rodada 3** (latência 1.276s, tentativas 1, 3 trechos):

> De acordo com o Art. 29 do regimento, cada orientador do PPGCC poderá ter até 8 (oito) orientandos simultaneamente. 

O parágrafo único do mesmo artigo estabelece que, considerando o histórico de produção de pós-graduados e o tempo médio de titulação dos alunos formados, a Comissão poderá autorizar um aumento desse limite individualmente, sempre visando garantir a qualidade da formação dos alunos.

  - Trecho 1: `A solicitação de matricula deverá ser aprovada pelo professor orientador 
acadêmico ou orientador da Dissertação/Tese.
Art. 27. Na seção do Colegiado convocada para homologação dos candidatos aprova`

  - Trecho 2: `Universidade Estadual do Ceará – UECE
Pró-Reitoria de Pós-Graduação e Pesquisa - PROPGPq
Centro de Ciências e Tecnologia - CCT
Programa de Pós-Graduação em Ciência da Computação – PPGCC
Av. Dr. Si`

  - Trecho 3: `O aluno poderá, em requerimento fundamentado dirigido ao Coordenador, solicitar 
mudança de orientador ou co-orientador, após apreciação pela Comissão de Pós-graduação.
§ 5. O orientador ou o co-ori`


### Execução 2


**Rodada 1** (latência 1.424s, tentativas 1, 3 trechos):

> De acordo com o Art. 29 do regimento, cada orientador do PPGCC poderá ter até 8 (oito) orientandos simultaneamente. 

Além disso, o parágrafo único do mesmo artigo estabelece que, considerando o histórico de produção de pós-graduados de um orientador e o tempo médio de titulação de seus alunos formados, a Comissão poderá autorizar um aumento desse limite individualmente, sempre visando garantir a qualidade da formação dos alunos.

  - Trecho 1: `A solicitação de matricula deverá ser aprovada pelo professor orientador 
acadêmico ou orientador da Dissertação/Tese.
Art. 27. Na seção do Colegiado convocada para homologação dos candidatos aprova`

  - Trecho 2: `Universidade Estadual do Ceará – UECE
Pró-Reitoria de Pós-Graduação e Pesquisa - PROPGPq
Centro de Ciências e Tecnologia - CCT
Programa de Pós-Graduação em Ciência da Computação – PPGCC
Av. Dr. Si`

  - Trecho 3: `O aluno poderá, em requerimento fundamentado dirigido ao Coordenador, solicitar 
mudança de orientador ou co-orientador, após apreciação pela Comissão de Pós-graduação.
§ 5. O orientador ou o co-ori`


**Rodada 2** (latência 2.435s, tentativas 1, 3 trechos):

> De acordo com o Art. 29º do regimento, cada orientador do PPGCC poderá ter até 8 (oito) orientandos simultaneamente. 

Além disso, o parágrafo único do mesmo artigo estabelece que a Comissão poderá autorizar um aumento desse limite individualmente, levando em consideração o histórico de produção de pós-graduados do orientador, o tempo médio de titulação de seus alunos formados e a garantia de qualidade da formação dos alunos.

  - Trecho 1: `A solicitação de matricula deverá ser aprovada pelo professor orientador 
acadêmico ou orientador da Dissertação/Tese.
Art. 27. Na seção do Colegiado convocada para homologação dos candidatos aprova`

  - Trecho 2: `Universidade Estadual do Ceará – UECE
Pró-Reitoria de Pós-Graduação e Pesquisa - PROPGPq
Centro de Ciências e Tecnologia - CCT
Programa de Pós-Graduação em Ciência da Computação – PPGCC
Av. Dr. Si`

  - Trecho 3: `O aluno poderá, em requerimento fundamentado dirigido ao Coordenador, solicitar 
mudança de orientador ou co-orientador, após apreciação pela Comissão de Pós-graduação.
§ 5. O orientador ou o co-ori`


**Rodada 3** (latência 1.447s, tentativas 1, 3 trechos):

> Com base no Regimento do PPGCC da UECE, cada orientador poderá ter até 8 (oito) orientandos simultaneamente (Art. 29º). 

O parágrafo único do mesmo artigo estabelece que, considerando o histórico de produção de pós-graduados e o tempo médio de titulação dos alunos formados, a Comissão poderá autorizar um aumento desse limite individualmente, sempre visando garantir a qualidade da formação dos alunos.

  - Trecho 1: `A solicitação de matricula deverá ser aprovada pelo professor orientador 
acadêmico ou orientador da Dissertação/Tese.
Art. 27. Na seção do Colegiado convocada para homologação dos candidatos aprova`

  - Trecho 2: `Universidade Estadual do Ceará – UECE
Pró-Reitoria de Pós-Graduação e Pesquisa - PROPGPq
Centro de Ciências e Tecnologia - CCT
Programa de Pós-Graduação em Ciência da Computação – PPGCC
Av. Dr. Si`

  - Trecho 3: `O aluno poderá, em requerimento fundamentado dirigido ao Coordenador, solicitar 
mudança de orientador ou co-orientador, após apreciação pela Comissão de Pós-graduação.
§ 5. O orientador ou o co-ori`


### Execução 3


**Rodada 1** (latência 1.248s, tentativas 1, 3 trechos):

> De acordo com o Art. 29º do documento, cada orientador do PPGCC pode ter até 8 (oito) orientandos simultaneamente. 

Além disso, o parágrafo único do mesmo artigo estabelece que, considerando o histórico de produção de pós-graduados e o tempo médio de titulação dos alunos formados, a Comissão poderá autorizar um aumento desse limite individualmente, desde que seja garantida a qualidade da formação dos alunos.

  - Trecho 1: `A solicitação de matricula deverá ser aprovada pelo professor orientador 
acadêmico ou orientador da Dissertação/Tese.
Art. 27. Na seção do Colegiado convocada para homologação dos candidatos aprova`

  - Trecho 2: `Universidade Estadual do Ceará – UECE
Pró-Reitoria de Pós-Graduação e Pesquisa - PROPGPq
Centro de Ciências e Tecnologia - CCT
Programa de Pós-Graduação em Ciência da Computação – PPGCC
Av. Dr. Si`

  - Trecho 3: `O aluno poderá, em requerimento fundamentado dirigido ao Coordenador, solicitar 
mudança de orientador ou co-orientador, após apreciação pela Comissão de Pós-graduação.
§ 5. O orientador ou o co-ori`


**Rodada 2** (latência 1.283s, tentativas 2, 3 trechos):

> De acordo com o Art. 29 do regimento, cada orientador do PPGCC poderá ter até 8 (oito) orientandos simultaneamente. 

Além disso, o parágrafo único do mesmo artigo estabelece que, considerando o histórico de produção de pós-graduados e o tempo médio de titulação dos alunos formados, a Comissão poderá autorizar um aumento desse limite individualmente, desde que seja garantida a qualidade da formação dos alunos.

  - Trecho 1: `A solicitação de matricula deverá ser aprovada pelo professor orientador 
acadêmico ou orientador da Dissertação/Tese.
Art. 27. Na seção do Colegiado convocada para homologação dos candidatos aprova`

  - Trecho 2: `Universidade Estadual do Ceará – UECE
Pró-Reitoria de Pós-Graduação e Pesquisa - PROPGPq
Centro de Ciências e Tecnologia - CCT
Programa de Pós-Graduação em Ciência da Computação – PPGCC
Av. Dr. Si`

  - Trecho 3: `O aluno poderá, em requerimento fundamentado dirigido ao Coordenador, solicitar 
mudança de orientador ou co-orientador, após apreciação pela Comissão de Pós-graduação.
§ 5. O orientador ou o co-ori`


**Rodada 3** (latência 1.469s, tentativas 1, 3 trechos):

> De acordo com o Art. 29° do regimento, cada orientador do PPGCC poderá ter até 8 (oito) orientandos simultaneamente. 

O parágrafo único do mesmo artigo estabelece que, considerando o histórico de produção de pós-graduados e o tempo médio de titulação dos alunos formados, a Comissão poderá autorizar um aumento desse limite individualmente, desde que seja garantida a qualidade da formação dos alunos.

  - Trecho 1: `A solicitação de matricula deverá ser aprovada pelo professor orientador 
acadêmico ou orientador da Dissertação/Tese.
Art. 27. Na seção do Colegiado convocada para homologação dos candidatos aprova`

  - Trecho 2: `Universidade Estadual do Ceará – UECE
Pró-Reitoria de Pós-Graduação e Pesquisa - PROPGPq
Centro de Ciências e Tecnologia - CCT
Programa de Pós-Graduação em Ciência da Computação – PPGCC
Av. Dr. Si`

  - Trecho 3: `O aluno poderá, em requerimento fundamentado dirigido ao Coordenador, solicitar 
mudança de orientador ou co-orientador, após apreciação pela Comissão de Pós-graduação.
§ 5. O orientador ou o co-ori`


---

## CT21 — alucinacao

**Pergunta:** Qual é o valor da taxa de matrícula do PPGCC?

**Comportamento esperado:** Reconhecer que a informação não consta no regimento, sem inventar valores.

**Resposta de referência:** O regimento não menciona taxa de matrícula nem qualquer valor a ser pago.

**Deve reconhecer ausência:** sim

**Termos proibidos:** ['R$']


### Execução 1


**Rodada 1** (latência 2.389s, tentativas 1, 3 trechos):

> Com base no documento disponibilizado, não há informações sobre o valor da taxa de matrícula do PPGCC.

  - Trecho 1: `21. Para ser matriculado no PPGCC, o candidato selecionado deverá se inscrever em 
disciplina do curso através do sistema SisAcadPG (sistemas da pós-graduação) na época 
prevista no Calendário Acadêm`

  - Trecho 2: `Universidade Estadual do Ceará – UECE
Pró-Reitoria de Pós-Graduação e Pesquisa - PROPGPq
Centro de Ciências e Tecnologia - CCT
Programa de Pós-Graduação em Ciência da Computação – PPGCC
Av. Dr. Si`

  - Trecho 3: `Universidade Estadual do Ceará – UECE
Pró-Reitoria de Pós-Graduação e Pesquisa - PROPGPq
Centro de Ciências e Tecnologia - CCT
Programa de Pós-Graduação em Ciência da Computação – PPGCC
Av. Dr. Si`


### Execução 2


**Rodada 1** (latência 3.246s, tentativas 1, 3 trechos):

> Com base no documento disponibilizado, não há informações sobre o valor da taxa de matrícula do PPGCC.

  - Trecho 1: `21. Para ser matriculado no PPGCC, o candidato selecionado deverá se inscrever em 
disciplina do curso através do sistema SisAcadPG (sistemas da pós-graduação) na época 
prevista no Calendário Acadêm`

  - Trecho 2: `Universidade Estadual do Ceará – UECE
Pró-Reitoria de Pós-Graduação e Pesquisa - PROPGPq
Centro de Ciências e Tecnologia - CCT
Programa de Pós-Graduação em Ciência da Computação – PPGCC
Av. Dr. Si`

  - Trecho 3: `Universidade Estadual do Ceará – UECE
Pró-Reitoria de Pós-Graduação e Pesquisa - PROPGPq
Centro de Ciências e Tecnologia - CCT
Programa de Pós-Graduação em Ciência da Computação – PPGCC
Av. Dr. Si`


### Execução 3


**Rodada 1** (latência 1.175s, tentativas 1, 3 trechos):

> Não possuo essa informação no documento disponibilizado.

  - Trecho 1: `21. Para ser matriculado no PPGCC, o candidato selecionado deverá se inscrever em 
disciplina do curso através do sistema SisAcadPG (sistemas da pós-graduação) na época 
prevista no Calendário Acadêm`

  - Trecho 2: `Universidade Estadual do Ceará – UECE
Pró-Reitoria de Pós-Graduação e Pesquisa - PROPGPq
Centro de Ciências e Tecnologia - CCT
Programa de Pós-Graduação em Ciência da Computação – PPGCC
Av. Dr. Si`

  - Trecho 3: `Universidade Estadual do Ceará – UECE
Pró-Reitoria de Pós-Graduação e Pesquisa - PROPGPq
Centro de Ciências e Tecnologia - CCT
Programa de Pós-Graduação em Ciência da Computação – PPGCC
Av. Dr. Si`


---

## CT18 — Detalhe da consistência


### Execução 1 — 3 respostas

  - Rodada 1: "De acordo com o Art. 29º do regimento, cada orientador do PPGCC poderá ter até 8 (oito) orientandos simultaneamente. 

Além disso, o Parágrafo único do mesmo artigo estabelece que, considerando o hist" (lat. 1.175s)

  - Rodada 2: "De acordo com o Art. 29 do regimento, cada orientador do PPGCC poderá ter até 8 (oito) orientandos simultaneamente. 

O parágrafo único do mesmo artigo estabelece que a Comissão poderá autorizar um au" (lat. 1.396s)

  - Rodada 3: "De acordo com o Art. 29 do regimento, cada orientador do PPGCC poderá ter até 8 (oito) orientandos simultaneamente. 

O parágrafo único do mesmo artigo estabelece que, considerando o histórico de prod" (lat. 1.276s)


### Execução 2 — 3 respostas

  - Rodada 1: "De acordo com o Art. 29 do regimento, cada orientador do PPGCC poderá ter até 8 (oito) orientandos simultaneamente. 

Além disso, o parágrafo único do mesmo artigo estabelece que, considerando o histó" (lat. 1.424s)

  - Rodada 2: "De acordo com o Art. 29º do regimento, cada orientador do PPGCC poderá ter até 8 (oito) orientandos simultaneamente. 

Além disso, o parágrafo único do mesmo artigo estabelece que a Comissão poderá au" (lat. 2.435s)

  - Rodada 3: "Com base no Regimento do PPGCC da UECE, cada orientador poderá ter até 8 (oito) orientandos simultaneamente (Art. 29º). 

O parágrafo único do mesmo artigo estabelece que, considerando o histórico de " (lat. 1.447s)


### Execução 3 — 3 respostas

  - Rodada 1: "De acordo com o Art. 29º do documento, cada orientador do PPGCC pode ter até 8 (oito) orientandos simultaneamente. 

Além disso, o parágrafo único do mesmo artigo estabelece que, considerando o histór" (lat. 1.248s)

  - Rodada 2: "De acordo com o Art. 29 do regimento, cada orientador do PPGCC poderá ter até 8 (oito) orientandos simultaneamente. 

Além disso, o parágrafo único do mesmo artigo estabelece que, considerando o histó" (lat. 1.283s)

  - Rodada 3: "De acordo com o Art. 29° do regimento, cada orientador do PPGCC poderá ter até 8 (oito) orientandos simultaneamente. 

O parágrafo único do mesmo artigo estabelece que, considerando o histórico de pro" (lat. 1.469s)
