# ESPECIFICAÇÃO FUNCIONAL E TÉCNICA — SISTEMA DE MONITORAMENTO DOS PARÂMETROS MÍNIMOS DAS OUVIDORIAS DE SERVIÇOS PENAIS

## 1. Finalidade deste arquivo

Este documento deve orientar integralmente a IA responsável pelo desenvolvimento do sistema local de monitoramento dos parâmetros mínimos das Ouvidorias de Serviços Penais.

A aplicação deverá ser simples, local, rastreável, de baixa manutenção e compatível com o uso da planilha `DADOS.xlsx` como fonte principal de dados.

Não criar outra base de dados principal. Não migrar os dados para SQLite, PostgreSQL, Supabase ou outro banco sem autorização expressa. O arquivo `DADOS.xlsx` deve permanecer como fonte tabular persistente e auditável do sistema.

O sistema deverá permitir:

1. visualizar a situação consolidada das Unidades Federativas;
2. abrir a avaliação detalhada de cada UF/unidade de avaliação;
3. visualizar as respostas originalmente registradas no diagnóstico;
4. editar a avaliação de cada pergunta;
5. registrar e editar evidências por pergunta;
6. anexar documentos comprobatórios a cada pergunta;
7. armazenar os anexos dentro do próprio workspace do projeto;
8. recalcular automaticamente as pontuações;
9. apresentar a classificação final;
10. gerar relatórios gerais;
11. gerar relatórios individuais por UF/unidade avaliada;
12. disponibilizar uma página institucional de “Metodologia”, com o texto constante deste documento;
13. preservar histórico mínimo das alterações;
14. fazer backup seguro do arquivo `DADOS.xlsx` antes de qualquer gravação.

---

# 2. Regra central do desenvolvimento

Priorizar, nesta ordem:

1. integridade do `DADOS.xlsx`;
2. rastreabilidade das alterações;
3. simplicidade;
4. manutenção por terceiros;
5. segurança dos documentos anexados;
6. boa experiência de uso;
7. compatibilidade com Windows e OneDrive;
8. baixo número de dependências;
9. ausência de arquitetura desnecessariamente complexa.

Não transformar o projeto em um sistema corporativo de grande porte.

Não criar microserviços.

Não criar frontend e backend em repositórios separados.

Não utilizar React, Next.js, Vue, Angular ou outro framework SPA sem necessidade concreta.

Não utilizar Docker como requisito para execução local.

Não utilizar SQLite no MVP.

Não criar serviço externo de armazenamento de documentos.

Não enviar arquivos ou dados para nuvem por API.

O sistema será executado localmente no workspace do projeto.

---

# 3. Estrutura atual do workspace

Considerar como raiz do projeto a pasta atualmente denominada:

`PARAMETROS MINIMOS`

O arquivo principal de dados já se encontra nessa pasta e deve ser tratado como:

`DADOS.xlsx`

O sistema deve procurar esse arquivo por caminho relativo à raiz do projeto.

Nunca gravar no código um caminho absoluto do OneDrive, nome de usuário do Windows ou caminho específico da máquina.

Exemplo esperado:

```text
PARAMETROS MINIMOS/
├── DADOS.xlsx
├── app.py
├── requirements.txt
├── src/
├── templates/
├── static/
├── ANEXOS/
├── BACKUPS/
├── EXPORTACOES/
└── tests/
```

Caso a extensão esteja oculta no Windows, o código deve continuar tratando o arquivo como `DADOS.xlsx`.

Se `DADOS.xlsx` não existir, a aplicação deve encerrar a inicialização com mensagem clara e não criar uma planilha vazia automaticamente.

---

# 4. Stack técnica recomendada

## 4.1. Backend

Utilizar:

- Python 3.12 ou versão estável compatível;
- FastAPI;
- Uvicorn;
- OpenPyXL;
- Jinja2;
- python-multipart;
- filelock;
- ReportLab.

Arquivo `requirements.txt` enxuto:

```text
fastapi
uvicorn[standard]
jinja2
python-multipart
openpyxl
filelock
reportlab
```

Não acrescentar bibliotecas sem necessidade.

## 4.2. Frontend

Utilizar:

- HTML semântico;
- CSS próprio;
- JavaScript vanilla;
- templates Jinja2.

Não exigir build de frontend.

Não exigir Node.js para executar a aplicação.

A aplicação deve iniciar com comando equivalente a:

```bash
uvicorn app:app --host 127.0.0.1 --port 8000 --reload
```

Em produção local, o `--reload` pode ser removido.

O bind padrão deve ser somente em `127.0.0.1`. Não expor o sistema na rede local sem configuração expressa.

---

# 5. Procedimento obrigatório antes de alterar arquivos

Antes de qualquer alteração no repositório, executar somente:

```bash
git branch --show-current
git status --short
git status -sb
```

Se houver intenção de fazer commit ou push, executar também:

```bash
git fetch origin
git status -sb
```

Não utilizar:

```bash
git reset --hard
git clean
```

Não alterar arquivos fora do escopo deste sistema.

Não alterar `.env`, credenciais, dados publicados ou outros projetos.

Não criar `implementation_plan.md`, `task.md`, `walkthrough.md` ou documentos auxiliares não solicitados.

Este arquivo é a especificação principal.

---

# 6. `DADOS.xlsx` como fonte de verdade

## 6.1. Princípio

A planilha `DADOS.xlsx` é a base principal.

A aplicação deve ler e gravar nela.

Não duplicar a base inteira em outro formato.

A aplicação deve preservar:

- nomes das abas;
- conteúdos;
- fórmulas;
- estilos;
- validações;
- dados de diagnóstico;
- fundamentações;
- pontuações;
- linhas específicas do Espírito Santo;
- observações já existentes.

## 6.2. Abas existentes

A planilha contém, no mínimo:

```text
00_Metodologia
01_Institucionalização
02_Autonomia
03_Imparcialidade
04_Acessibilidade
05_Transparência
06_Integração Tec
07_Maturidade
08_Resumo
```

A IA deve confirmar esses nomes ao abrir o arquivo.

Se algum nome estiver diferente, não inventar correspondência silenciosamente. Registrar erro claro.

## 6.3. Não depender de letras fixas de coluna

A aplicação NÃO deve depender apenas de posições como `C`, `D`, `X`, `AJ`.

As colunas podem mudar no futuro.

Identificar as colunas pelos cabeçalhos e pelos códigos das perguntas.

Exemplos:

```text
M1-11
M3-56
M3-57
M1-12
M4-67
M4-68
```

O parser deve procurar os códigos nos cabeçalhos da linha de perguntas.

Para cada pergunta das abas de pontuação-base, a estrutura lógica atual é:

```text
Pergunta/status
Resposta do diagnóstico
Fundamentação na IN nº 75/2026
Pontos
```

A aplicação deve detectar essa estrutura.

## 6.4. Linhas especiais

A aplicação deve preservar duas unidades de avaliação para o Espírito Santo:

```text
ES — Espírito Santo — Polícia Penal
ES — Espírito Santo — SEJUS/ES
```

Elas não podem ser mescladas.

Devem aparecer separadamente:

- no dashboard;
- na página de detalhe;
- nos filtros;
- nos relatórios;
- nos anexos;
- na auditoria.

Para fins internos, utilizar chaves estáveis:

```text
ES_PP
ES_SEJUS
```

Para as demais UFs, utilizar a própria sigla:

```text
AC
AL
AP
...
RO
SC
...
```

A planilha atual já está consolidada para RO e SC com a resposta mais recente. O sistema não deve tentar reconstruir o histórico das respostas antigas a partir de outra planilha.

---

# 7. Identificação única de pergunta

Alguns códigos de perguntas aparecem em mais de uma dimensão.

Exemplo: uma mesma resposta do diagnóstico pode ser utilizada para aferir aspectos distintos.

Portanto, nunca usar apenas o código `M4-67` como chave primária.

Utilizar uma chave de ocorrência:

```text
<aba>:<codigo>
```

Exemplos:

```text
02_Autonomia:M4-67
06_Integração Tec:M4-67
03_Imparcialidade:M2-37
06_Integração Tec:M2-37
```

Os anexos, evidências e registros de auditoria devem ser vinculados à ocorrência específica da pergunta.

---

# 8. Abas auxiliares permitidas no próprio `DADOS.xlsx`

Para viabilizar evidências por pergunta, anexos e auditoria sem depender de banco externo, a aplicação pode criar, caso ainda não existam, três abas auxiliares.

Usar exatamente:

```text
DB_EVIDENCIAS
DB_ANEXOS
DB_AUDITORIA
```

Podem permanecer ocultas no Excel, desde que sejam facilmente reexibíveis e não sejam protegidas por senha.

## 8.1. `DB_EVIDENCIAS`

Uma linha por unidade de avaliação + ocorrência de pergunta.

Colunas:

```text
id
entity_key
uf
unidade_label
sheet_name
dimension_name
item_name
question_code
occurrence_key
evidence_text
updated_at
```

Na primeira inicialização, se a aba ainda não existir, criar os registros correspondentes às perguntas avaliadas.

Como a matriz atual registra como evidência documental:

`Doc. SEI 37070578`

usar esse texto como evidência inicial de cada pergunta quando ainda não existir evidência individualizada.

Não apagar o conteúdo já existente das colunas `Evidências / observações` das abas principais.

## 8.2. `DB_ANEXOS`

Uma linha por arquivo anexado.

Colunas:

```text
id
entity_key
uf
unidade_label
sheet_name
dimension_name
item_name
question_code
occurrence_key
original_filename
stored_filename
relative_path
mime_type
size_bytes
sha256
uploaded_at
active
notes
```

`active` deve aceitar `TRUE/FALSE`.

Não apagar fisicamente um arquivo a partir da interface comum. A ação “remover” deve apenas desvincular o arquivo, marcando `active = FALSE`.

## 8.3. `DB_AUDITORIA`

Registrar alterações relevantes.

Colunas:

```text
id
timestamp
entity_key
sheet_name
question_code
occurrence_key
field
old_value
new_value
action
```

A auditoria deve registrar, no mínimo:

- mudança de status de avaliação;
- alteração de evidência;
- correção manual da resposta do diagnóstico;
- inclusão de anexo;
- desvinculação de anexo.

Não é necessário implementar autenticação de usuários no MVP.

---

# 9. Gravação segura no Excel

O arquivo está em workspace sincronizado com OneDrive. Isso exige cuidado.

## 9.1. Lock

Utilizar `filelock` com arquivo local, por exemplo:

```text
.dados.lock
```

Toda gravação deve adquirir o lock.

## 9.2. Backup

Antes de qualquer alteração persistente em `DADOS.xlsx`, criar cópia em:

```text
BACKUPS/
```

Formato:

```text
DADOS_2026-09-22_143012.xlsx
```

Manter backups cronológicos.

Não sobrescrever backup existente.

## 9.3. Escrita atômica

Fluxo obrigatório:

1. adquirir lock;
2. criar backup;
3. carregar `DADOS.xlsx`;
4. aplicar alteração;
5. salvar em arquivo temporário;
6. reabrir o arquivo temporário para validar que é um XLSX legível;
7. substituir `DADOS.xlsx`;
8. liberar lock.

Nunca editar o arquivo de forma parcial.

## 9.4. Arquivo aberto no Excel

Se o arquivo estiver bloqueado pelo Excel/OneDrive e não puder ser gravado, retornar ao usuário:

> Não foi possível salvar porque `DADOS.xlsx` está aberto ou bloqueado por outro processo. Feche a planilha no Excel e tente novamente.

Não criar outro `DADOS (1).xlsx`.

---

# 10. Armazenamento dos documentos anexos

Criar pasta:

```text
ANEXOS/
```

Estrutura:

```text
ANEXOS/
└── <entity_key>/
    └── <sheet_slug>/
        └── <question_code>/
            └── <uuid>__<nome_sanitizado>
```

Exemplo:

```text
ANEXOS/
└── ES_PP/
    └── 02_autonomia/
        └── M3-56/
            └── 8bb5...__portaria_123_2026.pdf
```

Nunca salvar caminho absoluto na planilha.

Salvar somente caminho relativo ao workspace:

```text
ANEXOS/ES_PP/02_autonomia/M3-56/8bb5...__portaria_123_2026.pdf
```

## 10.1. Extensões permitidas

Inicialmente:

```text
.pdf
.docx
.xlsx
.xls
.csv
.png
.jpg
.jpeg
.txt
```

Não permitir executáveis.

Não executar conteúdo de arquivo anexado.

## 10.2. Tamanho

Limite padrão:

`25 MB por arquivo`

Se ultrapassar, rejeitar com mensagem clara.

## 10.3. Nome

Preservar o nome original na coluna `original_filename`.

No disco, utilizar:

```text
UUID + "__" + nome sanitizado
```

Remover caracteres inválidos de Windows.

Impedir path traversal (`../` etc.).

## 10.4. Hash

Calcular SHA-256 e registrar em `DB_ANEXOS`.

---

# 11. Regras de edição

## 11.1. Resposta do diagnóstico

A coluna “Resposta do diagnóstico” representa informação histórica declarada pela UF.

No frontend, ela deve aparecer em modo somente leitura por padrão.

Disponibilizar ação discreta:

`Corrigir resposta do diagnóstico`

Ao acioná-la:

1. exibir confirmação;
2. permitir edição;
3. registrar valor anterior e novo em `DB_AUDITORIA`;
4. salvar no mesmo local da planilha.

Não alterar respostas do diagnóstico automaticamente.

## 11.2. Avaliação

A avaliação deve ser editável normalmente.

Valores das dimensões ordinárias:

```text
Atende
Parcial
Não atende
Sem evidência
```

A pontuação é calculada automaticamente.

Regra geral:

```text
Atende = 100% do peso da pergunta
Parcial = 50% do peso da pergunta
Não atende = 0
Sem evidência = 0
```

## 11.3. Bônus

Valores:

```text
Sim
Não
Sem evidência
```

`Sim` concede o bônus previsto para a pergunta.

Os demais concedem zero.

## 11.4. Evidência

Cada pergunta deve ter campo próprio:

`Evidência / observação`

Valor inicial:

`Doc. SEI 37070578`

O campo deve aceitar texto livre.

Abaixo ou ao lado do campo devem aparecer os documentos anexados.

---

# 12. Sistema de pontuação

## 12.1. Pontuação-base

A pontuação-base total é de:

`100 pontos`

Distribuição:

| Dimensão | Peso |
|---|---:|
| 01 — Institucionalização | 15 |
| 02 — Autonomia técnica e funcional | 15 |
| 03 — Imparcialidade, sigilo e proteção | 15 |
| 04 — Acessibilidade e atendimento humanizado | 15 |
| 05 — Transparência e publicidade | 15 |
| 06 — Integração tecnológica | 25 |
| **TOTAL** | **100** |

A maior ponderação da integração tecnológica é opção metodológica da ONASP para esta ferramenta de monitoramento. Não apresentar esse peso como determinação da IN nº 75/2026.

## 12.2. Institucionalização — 15 pontos

### Item 1 — Instituição formal da Ouvidoria de Serviços Penais

- `M1-11 — Existe ato normativo específico que cria a Ouvidoria de Serviços Penais ou núcleo especializado?`
- Peso: `15 pontos`
- Fundamento: `art. 6º, caput, da IN nº 75/2026`.

Regra especial:

- com ato: unidade instituída e 15 pontos;
- sem ato: 0 ponto e classificação institucional “Não instituída”;
- sem evidência: situação não comprovada.

A institucionalização é simultaneamente pontuável e requisito de entrada.

Uma unidade sem ato de instituição não deve ser classificada como unidade instituída com baixa/parcial/satisfatória/elevada aderência.

## 12.3. Autonomia técnica e funcional — 15 pontos

### Item 1 — Garantia normativa de autonomia técnica/funcional

- `M3-56 — Vinculação institucional da Ouvidoria de Serviços Penais` — `3 pontos`
- `M3-57 — Existência e designação do(a) Ouvidor(a) de Serviços Penais` — `3 pontos`

### Item 2 — Condições institucionais de atuação sem interferência indevida

- `M1-12 — Conteúdo do ato de criação da Ouvidoria de Serviços Penais` — `3 pontos`
- `M4-67 — Fluxo de trabalho interno da Ouvidoria de Serviços Penais` — `3 pontos`
- `M4-68 — Prazos e qualidade da resposta às manifestações` — `3 pontos`

Total: `15 pontos`.

## 12.4. Imparcialidade, sigilo e proteção — 15 pontos

### Item 1 — Proteção da identidade do denunciante/manifestante

- `M4-66 — Registro, protocolo e classificação das manifestações` — `4 pontos`
- `M4-69 — Tratamento de denúncias graves e sensíveis` — `4 pontos`

### Item 2 — Confidencialidade e sigilo das informações

- `M2-37 — Recursos específicos de segurança da informação` — `4 pontos`
- `M3-63 — Compromisso de sigilo da equipe` — `3 pontos`

Total: `15 pontos`.

## 12.5. Acessibilidade e atendimento humanizado — 15 pontos

### Item 1 — Canais institucionais acessíveis

- `M2-41 — E-mail institucional exclusivo` — `2 pontos`
- `M2-43 — Linha telefônica funcional de uso restrito` — `2 pontos`
- `M2-45 — Sistemas ou canais eletrônicos utilizados` — `2 pontos`
- `M2-47 — Endereço postal próprio ou referência clara` — `2 pontos`

### Item 2 — Condições de atendimento reservado e acessível

- `M2-16 — Espaço físico da Ouvidoria` — `3 pontos`

### Item 3 — Alcance dos públicos dos serviços penais

- `M1-13 — Públicos atendidos no plano normativo` — `2 pontos`
- `M4-64 — Públicos atendidos na prática` — `2 pontos`

Total: `15 pontos`.

## 12.6. Transparência e publicidade — 15 pontos

### Item 1 — Visibilidade institucional e divulgação dos canais e atribuições

- `M2-35 — Placas e cartazes da Ouvidoria` — `5 pontos`
- `M1-12 — Conteúdo do ato de criação da Ouvidoria de Serviços Penais` — `5 pontos`

### Item 2 — Publicidade das ações e atividades

- `M4-71 — Monitoramento, relatórios e recomendações` — `5 pontos`

Total: `15 pontos`.

## 12.7. Integração tecnológica — 25 pontos

### Item 1 — Canal eletrônico e solução para registro e gestão das manifestações

- `M2-45 — Sistemas ou canais eletrônicos utilizados para registro e gestão` — `5 pontos`

### Item 2 — Protocolo, rastreabilidade e acompanhamento

- `M4-66 — Registro, protocolo e classificação das manifestações` — `3 pontos`
- `M4-67 — Fluxo de trabalho interno da Ouvidoria` — `3 pontos`

### Item 3 — Sigilo, autenticação e controle de acesso

- `M2-37 — Recursos específicos de segurança da informação` — `4 pontos`

### Item 4 — Computadores e acesso à internet

- `M2-17 — Quantidade atualmente disponível de computadores com acesso à internet` — `4 pontos`

### Item 5 — Impressoras e scanners

- `M2-19 — Impressoras multifuncionais atualmente disponíveis` — `2 pontos`
- `M2-21 — Scanners atualmente disponíveis` — `2 pontos`

### Item 6 — Aparelhos de telefone celular

- `M2-27 — Smartphones atualmente disponíveis` — `2 pontos`

Total: `25 pontos`.

---

# 13. Maturidade / bônus

O bônus máximo disponível é:

`10 pontos`

Itens:

| Critério | Pergunta | Bônus |
|---|---|---:|
| Uso do Fala.BR | M2-46 | +3 |
| Mandato fixo do Ouvidor | M0-08 | +1 |
| Dedicação exclusiva da equipe | M3-60 | +1 |
| Qualificação/perfil preferencial do Ouvidor | M3-58 | +1 |
| WhatsApp institucional | M2-50 | +1 |
| Outros canais eletrônicos institucionais | M2-49 | +1 |
| Materiais adicionais de divulgação e educação em direitos | M2-36 | +2 |
| **TOTAL POSSÍVEL** |  | **+10** |

O bônus não cria nota superior a 100.

Fórmula:

```text
bônus_aplicado = min(bônus_disponível, 100 - nota_base)
nota_final = min(100, nota_base + bônus_aplicado)
```

Exemplo:

```text
nota_base = 96
bônus_disponível = 8
bônus_aplicado = 4
nota_final = 100
```

---

# 14. Trava por dimensão essencial zerada

Para unidade formalmente instituída, se qualquer uma das seguintes dimensões estiver totalmente zerada:

- Autonomia;
- Imparcialidade;
- Acessibilidade;
- Transparência;
- Integração tecnológica;

a classificação deve ser:

`Instituída — aderência insuficiente (dimensão essencial zerada)`

O bônus não elimina essa trava.

---

# 15. Faixas de classificação

Somente para unidades formalmente instituídas e sem dimensão essencial zerada:

| Nota final | Classificação |
|---|---|
| menor que 50 | Instituída — baixa aderência |
| de 50 até abaixo de 70 | Instituída — aderência parcial |
| de 70 até abaixo de 90 | Instituída — aderência satisfatória |
| de 90 a 100 | Instituída — elevada aderência |

Essas faixas são metodologia de monitoramento da ONASP.

Não afirmar que as faixas constam da IN nº 75/2026.

---

# 16. Página inicial / Dashboard

Rota:

```text
/
```

Título:

`Parâmetros Mínimos das Ouvidorias de Serviços Penais`

Subtítulo:

`Monitoramento de aderência à IN GABSEC/SENAPPEN/MJSP nº 75/2026`

## 16.1. Cards superiores

Exibir:

- Unidades de avaliação;
- Instituídas;
- Não instituídas;
- Sem evidência institucional;
- Aderência elevada;
- Aderência satisfatória;
- Aderência parcial;
- Baixa/insuficiente aderência.

Usar “Unidades de avaliação”, e não simplesmente “UFs”, porque o Espírito Santo possui duas unidades avaliadas separadamente.

## 16.2. Tabela principal

Colunas:

```text
UF
Unidade avaliada
Institucionalização
Autonomia
Imparcialidade
Acessibilidade
Transparência
Integração tecnológica
Nota-base
Bônus aplicado
Nota final
Classificação
Ações
```

Ação:

`Abrir avaliação`

Filtros:

- UF;
- situação institucional;
- classificação;
- faixa de nota;
- texto livre.

Permitir ordenação por nota final.

Não ocultar unidades sem avaliação preenchida.

---

# 17. Página de detalhe da UF/unidade

Rota sugerida:

```text
/unidades/{entity_key}
```

Exemplos:

```text
/unidades/AC
/unidades/ES_PP
/unidades/ES_SEJUS
```

## 17.1. Cabeçalho

Exibir:

- sigla;
- nome da unidade avaliada;
- situação institucional;
- nota-base;
- bônus disponível;
- bônus aplicado;
- nota final;
- classificação.

## 17.2. Navegação interna

Utilizar abas ou acordeões:

```text
Institucionalização
Autonomia
Imparcialidade
Acessibilidade
Transparência
Integração tecnológica
Maturidade / bônus
```

## 17.3. Card de cada pergunta

Cada pergunta deve aparecer como um bloco individual.

Exibir, nesta ordem:

1. código da pergunta;
2. título da pergunta;
3. item da metodologia;
4. peso máximo;
5. fundamentação normativa;
6. resposta do diagnóstico;
7. critério de pontuação;
8. seletor de avaliação;
9. pontuação obtida;
10. campo “Evidência / observação”;
11. documentos anexados;
12. botão “Anexar documento”.

Layout conceitual:

```text
┌──────────────────────────────────────────────────────────────┐
│ M3-56 — Vinculação institucional                           │
│ Item 1 — Garantia normativa de autonomia                   │
│ Peso máximo: 3 pts                                         │
├──────────────────────────────────────────────────────────────┤
│ Resposta do diagnóstico                                    │
│ [texto original da UF]                                     │
├──────────────────────────────────────────────────────────────┤
│ Avaliação: [Atende ▼]        Pontuação: 3 / 3              │
├──────────────────────────────────────────────────────────────┤
│ Evidência / observação                                     │
│ [Doc. SEI 37070578 ...]                                    │
│                                                             │
│ Documentos:                                                 │
│ 📄 Portaria_123_2026.pdf   [Abrir] [Baixar] [Desvincular]  │
│                                                             │
│ [ + Anexar documento ]                                     │
└──────────────────────────────────────────────────────────────┘
```

Salvar alterações sem recarregar a página inteira, quando possível.

Exibir confirmação visual discreta:

`Alteração salva.`

Em erro:

`Não foi possível salvar. Nenhuma alteração foi gravada.`

---

# 18. Página Metodologia

Rota:

```text
/metodologia
```

O frontend deve utilizar como conteúdo-base o texto abaixo.

Não reduzir a página a um resumo curto.

Ela é parte institucional do sistema e deve permitir que qualquer usuário compreenda:

- de onde veio a avaliação;
- qual a relação com o Pena Justa;
- qual a relação com a IN nº 75/2026;
- de onde vieram os dados;
- como funcionam as dimensões;
- por que existem pesos;
- como funciona a classificação;
- como são tratadas evidências e documentos.

---

# 19. TEXTO DA PÁGINA “METODOLOGIA”

## Metodologia de Monitoramento dos Parâmetros Mínimos das Ouvidorias de Serviços Penais

### 1. Apresentação

Este sistema foi desenvolvido para apoiar o monitoramento da institucionalização, da estruturação e das condições de funcionamento das Ouvidorias de Serviços Penais dos Estados e do Distrito Federal.

A ferramenta articula três componentes principais: as metas e diretrizes do Plano Nacional Pena Justa relacionadas às ouvidorias de serviços penais; os parâmetros mínimos estabelecidos pela Instrução Normativa GABSEC/SENAPPEN/MJSP nº 75, de 8 de abril de 2026; e as informações produzidas no diagnóstico nacional realizado pela Ouvidoria Nacional de Serviços Penais — ONASP junto às Unidades Federativas.

O objetivo não é substituir a análise técnica nem declarar, de forma automática, a regularidade jurídica de uma Ouvidoria. A finalidade é organizar evidências, permitir comparação padronizada entre as unidades avaliadas, acompanhar a evolução da política pública e identificar de forma objetiva os pontos que demandam fortalecimento institucional.

### 2. Relação com o Plano Nacional Pena Justa

O fortalecimento das ouvidorias de serviços penais integra a agenda de implementação do Plano Nacional Pena Justa.

A matriz de implementação do Plano contém previsões diretamente relacionadas à atuação da ONASP e à estruturação das ouvidorias estaduais de serviços penais, especialmente:

**Indicador 2.4.2.1.1.1 — Elaboração de parâmetros para a criação de ouvidorias estaduais autônomas dos serviços penais.**

Esse indicador corresponde à etapa de definição de referência técnica nacional para orientar a criação e a estruturação das ouvidorias de serviços penais.

**Indicador 2.4.2.1.2.1 — Estabelecimento de ouvidorias estaduais criadas, seguindo os parâmetros.**

Esse indicador avança da definição dos parâmetros para sua implementação, permitindo acompanhar a criação e a estruturação das Ouvidorias de Serviços Penais conforme o referencial estabelecido.

A lógica do monitoramento adotado neste sistema decorre dessa sequência: primeiro se definem parâmetros objetivos; depois se verifica, de forma estruturada e documentada, o nível de institucionalização e de aderência das unidades estaduais e distrital.

A metodologia também se relaciona ao objetivo de fortalecer canais efetivos de manifestação, transparência, participação social, proteção de informações sensíveis, tratamento de denúncias e capacidade institucional das Ouvidorias de Serviços Penais.

### 3. Processo de construção do referencial

A construção do referencial de monitoramento não decorreu exclusivamente da publicação de uma norma.

O processo foi precedido por atividades de diagnóstico, identificação de assimetrias federativas e levantamento das condições materiais, tecnológicas, normativas e operacionais das Ouvidorias de Serviços Penais.

Ao longo de 2025, a ONASP sistematizou necessidades relacionadas ao funcionamento das ouvidorias, identificando a importância de definir parâmetros mínimos e de estruturar ações federais capazes de apoiar os Estados e o Distrito Federal.

Em janeiro de 2026, foi realizado diagnóstico nacional junto às Unidades Federativas, com levantamento estruturado de informações sobre institucionalização, organização administrativa, infraestrutura, tecnologia, canais de atendimento, recursos humanos, fluxos de trabalho, segurança da informação, públicos atendidos e práticas de monitoramento.

As respostas do diagnóstico constituem a principal base factual utilizada nesta ferramenta.

Para assegurar rastreabilidade, as informações provenientes do diagnóstico encontram-se associadas à referência documental **Doc. SEI 37070578**, sem prejuízo da inclusão de documentos específicos adicionais para cada pergunta ou critério avaliado.

O sistema preserva a resposta originalmente prestada pela unidade federativa e a apresenta ao lado da avaliação técnica correspondente.

### 4. Instrução Normativa nº 75/2026

A Instrução Normativa GABSEC/SENAPPEN/MJSP nº 75, de 8 de abril de 2026, instituiu parâmetros para criação e estruturação das Ouvidorias de Serviços Penais.

A norma consta do Processo SEI nº 08016.027689/2025-19.

A Instrução Normativa estabelece referência mínima para formalização, composição e funcionamento inicial das Ouvidorias de Serviços Penais, observadas a autonomia dos entes federativos e as especificidades locais.

Entre os parâmetros estruturantes previstos na norma estão:

- autonomia técnica e funcional;
- imparcialidade e proteção da identidade;
- acessibilidade e atendimento humanizado;
- transparência e publicidade;
- integração tecnológica.

Além desses eixos, a norma estabelece que a criação da Ouvidoria de Serviços Penais deve ser formalizada por ato normativo específico, define elementos mínimos do ato, trata de infraestrutura, canais de atendimento, segurança da informação, composição da equipe, designação do Ouvidor, fluxos de tratamento das manifestações, registro, protocolo, relatórios e outras condições necessárias ao funcionamento da unidade.

A metodologia deste sistema transforma esses parâmetros normativos em critérios de monitoramento, utilizando perguntas do diagnóstico capazes de fornecer evidência objetiva sobre cada aspecto.

A pontuação, os pesos e as faixas de classificação utilizados pelo sistema são instrumentos metodológicos de monitoramento da ONASP. Eles não integram o texto da Instrução Normativa e não devem ser interpretados como sanção, certificação jurídica ou requisito criado pela própria norma.

### 5. Estrutura da avaliação

Para fins de monitoramento, o sistema utiliza seis dimensões de pontuação-base.

Cinco delas correspondem diretamente aos principais eixos estruturantes previstos no art. 4º da Instrução Normativa nº 75/2026.

A institucionalização foi segregada como dimensão própria porque a existência de ato normativo específico constitui condição antecedente para a própria existência formal da Ouvidoria de Serviços Penais, nos termos do art. 6º da norma.

As dimensões são:

1. Institucionalização;
2. Autonomia técnica e funcional;
3. Imparcialidade, sigilo e proteção;
4. Acessibilidade e atendimento humanizado;
5. Transparência e publicidade;
6. Integração tecnológica.

A pontuação-base máxima é de 100 pontos.

### 6. Pesos das dimensões

A metodologia atribui o mesmo peso de 15 pontos às dimensões institucionais de institucionalização, autonomia, imparcialidade, acessibilidade e transparência.

A dimensão de integração tecnológica recebe peso de 25 pontos.

A distribuição é:

| Dimensão | Pontuação máxima |
|---|---:|
| Institucionalização | 15 |
| Autonomia técnica e funcional | 15 |
| Imparcialidade, sigilo e proteção | 15 |
| Acessibilidade e atendimento humanizado | 15 |
| Transparência e publicidade | 15 |
| Integração tecnológica | 25 |
| **Total** | **100** |

A maior ponderação da integração tecnológica é uma opção metodológica do monitoramento, adotada em razão do papel transversal da tecnologia para o registro, o protocolo, a rastreabilidade, a proteção da informação, o acompanhamento das manifestações e o funcionamento dos canais institucionais.

Essa ponderação não significa que a Instrução Normativa estabeleça hierarquia jurídica entre os parâmetros.

### 7. Institucionalização

A institucionalização corresponde à existência de ato normativo específico que cria ou institui a Ouvidoria de Serviços Penais ou núcleo especializado.

Esse critério vale 15 pontos.

Além de produzir pontuação, funciona como requisito de entrada da avaliação.

Quando não existe ato de instituição, a unidade deve ser apresentada como **“Não instituída”**.

Nessa situação, a existência de estrutura física, equipamentos, canais ou boas práticas não substitui a formalização institucional exigida pela norma.

A finalidade dessa regra é separar duas perguntas distintas:

- a Ouvidoria existe formalmente?
- se existe, em que medida sua estrutura e funcionamento aderem aos parâmetros avaliados?

### 8. Autonomia técnica e funcional

A dimensão de autonomia avalia a posição institucional da Ouvidoria, a existência e designação formal do Ouvidor e as condições normativas e operacionais necessárias para atuação sem interferência indevida.

São consideradas informações sobre:

- vinculação institucional;
- designação do Ouvidor;
- conteúdo do ato de criação;
- fluxo interno de trabalho;
- prazos e qualidade das respostas.

A dimensão vale até 15 pontos.

### 9. Imparcialidade, sigilo e proteção

Essa dimensão avalia as condições destinadas à proteção da identidade do manifestante, ao tratamento de denúncias graves ou sensíveis e à preservação do sigilo das informações.

São observados:

- registro, protocolo e classificação das manifestações;
- tratamento de denúncias graves e sensíveis;
- recursos de segurança da informação;
- compromisso de sigilo da equipe.

A dimensão vale até 15 pontos.

### 10. Acessibilidade e atendimento humanizado

A acessibilidade é avaliada considerando a existência de canais institucionais, condições adequadas de atendimento e capacidade de alcançar os públicos relacionados aos serviços penais.

São considerados:

- e-mail institucional exclusivo;
- linha telefônica funcional;
- canais eletrônicos;
- endereço postal;
- espaço físico;
- públicos previstos normativamente;
- públicos efetivamente atendidos.

A dimensão vale até 15 pontos.

### 11. Transparência e publicidade

Essa dimensão busca verificar se a Ouvidoria possui mecanismos de visibilidade institucional, divulgação de seus canais e atribuições e produção de informações sobre suas atividades.

São considerados:

- placas e cartazes;
- definição das competências da Ouvidoria no ato normativo;
- monitoramento, relatórios e recomendações.

A dimensão vale até 15 pontos.

A ferramenta deve registrar que alguns elementos de transparência previstos na IN podem demandar verificação documental adicional, especialmente quando a resposta do diagnóstico não comprovar integralmente a publicação ou atualização das informações em portal institucional.

### 12. Integração tecnológica

A integração tecnológica recebe peso máximo de 25 pontos.

São avaliados:

- sistema ou canal eletrônico para registro e gestão;
- protocolo;
- rastreabilidade;
- acompanhamento do fluxo;
- segurança da informação;
- autenticação e controle de acesso;
- disponibilidade de computadores;
- impressoras multifuncionais;
- scanners;
- smartphones.

A opção por peso superior decorre da função transversal desses recursos no funcionamento cotidiano da Ouvidoria e na capacidade de manter registros seguros, rastreáveis e acessíveis.

Alguns recursos, como impressora multifuncional e aparelho celular institucional, aparecem na IN como recursos recomendados. Sua utilização na pontuação decorre da metodologia de monitoramento e deve ser interpretada nesse contexto.

### 13. Critérios de pontuação das perguntas

Para os critérios ordinários, utilizam-se quatro estados:

**Atende:** a evidência demonstra atendimento suficiente ao critério. A pergunta recebe 100% de sua pontuação.

**Parcial:** existe atendimento incompleto, limitado ou intermediário. A pergunta recebe 50% da pontuação.

**Não atende:** a evidência demonstra ausência do requisito. A pontuação é zero.

**Sem evidência:** não há informação suficiente para concluir pelo atendimento. A pontuação é zero.

A condição “Sem evidência” não deve ser convertida automaticamente em “Não atende”, pois ausência de documentação e ausência material do requisito são situações distintas.

### 14. Bônus de maturidade

Além dos 100 pontos-base, o sistema reconhece algumas características adicionais de maturidade institucional.

O bônus máximo disponível é de 10 pontos:

- uso do Fala.BR: até 3 pontos;
- mandato fixo do Ouvidor: 1 ponto;
- dedicação exclusiva da equipe: 1 ponto;
- qualificação ou perfil preferencial do Ouvidor: 1 ponto;
- WhatsApp institucional: 1 ponto;
- outros canais eletrônicos institucionais: 1 ponto;
- materiais adicionais de divulgação e educação em direitos: 2 pontos.

O bônus é compensatório.

Ele somente pode preencher a diferença entre a nota-base e 100.

Assim, uma unidade que possua 96 pontos-base e 8 pontos de bônus disponíveis receberá apenas 4 pontos de bônus aplicado, alcançando nota final 100.

O bônus não permite nota superior a 100.

O bônus também não corrige a ausência completa de uma dimensão essencial.

### 15. Trava de dimensão essencial zerada

A metodologia considera que uma Ouvidoria formalmente instituída não deve ser classificada como satisfatória ou elevada se uma dimensão essencial estiver completamente ausente.

Por isso, quando Autonomia, Imparcialidade, Acessibilidade, Transparência ou Integração Tecnológica obtiver pontuação igual a zero, a classificação será:

**Instituída — aderência insuficiente (dimensão essencial zerada).**

Essa regra busca evitar que desempenho elevado em algumas áreas compense integralmente a inexistência de uma dimensão estrutural da Ouvidoria.

### 16. Classificação da aderência

Para unidades formalmente instituídas e sem dimensão essencial zerada, a nota final é classificada da seguinte forma:

- abaixo de 50 pontos: **Instituída — baixa aderência**;
- de 50 até abaixo de 70 pontos: **Instituída — aderência parcial**;
- de 70 até abaixo de 90 pontos: **Instituída — aderência satisfatória**;
- de 90 a 100 pontos: **Instituída — elevada aderência**.

As faixas são instrumento gerencial da metodologia.

Elas não constituem classificação prevista textualmente na IN nº 75/2026.

### 17. Evidências e rastreabilidade

Toda avaliação deve ser sustentada por evidência.

O sistema apresenta, para cada pergunta:

- resposta do diagnóstico;
- fundamento normativo;
- avaliação atribuída;
- evidência textual;
- documentos anexados.

A referência **Doc. SEI 37070578** identifica a fonte documental geral das respostas utilizadas na matriz atual.

Sempre que houver documento mais específico — por exemplo, portaria, decreto, resolução, ato de designação, relatório, print de sistema, página institucional ou outro documento comprobatório — ele poderá ser anexado diretamente à pergunta correspondente.

A inclusão de documentos específicos fortalece a rastreabilidade e permite revisar a avaliação sem depender da memória do avaliador.

### 18. Atualização da avaliação

O monitoramento deve ser compreendido como processo contínuo.

A situação de uma Ouvidoria pode mudar com:

- publicação de novo ato normativo;
- alteração da vinculação institucional;
- designação de novo Ouvidor;
- implantação de sistemas;
- criação de canais;
- aquisição de equipamentos;
- formalização de fluxos;
- capacitação da equipe;
- produção de relatórios;
- adoção de mecanismos de segurança.

Por isso, o sistema deve permitir atualizar a avaliação preservando registros suficientes para identificar o que foi alterado.

### 19. Limites da metodologia

A pontuação não substitui análise jurídica.

A pontuação não certifica conformidade integral com toda a legislação aplicável.

A pontuação não transforma recomendação da IN em obrigação jurídica.

A pontuação não deve ser utilizada isoladamente para responsabilização.

A ferramenta é um instrumento de governança, monitoramento, priorização, planejamento e acompanhamento da Política de Fortalecimento das Ouvidorias de Serviços Penais.

---

# 20. Página de Relatórios

Rota:

```text
/relatorios
```

Exibir dois blocos:

## 20.1. Relatório geral

Filtros opcionais:

- todas as unidades;
- apenas instituídas;
- apenas não instituídas;
- classificação;
- faixa de nota.

Botões:

```text
Gerar PDF
Gerar XLSX
```

## 20.2. Relatório individual

Selecionar:

```text
UF / unidade avaliada
```

No ES, apresentar separadamente:

```text
Espírito Santo — Polícia Penal
Espírito Santo — SEJUS/ES
```

Botões:

```text
Gerar PDF
Gerar XLSX
```

---

# 21. Conteúdo do relatório geral

O PDF geral deve conter:

## Capa/cabeçalho

```text
MINISTÉRIO DA JUSTIÇA E SEGURANÇA PÚBLICA
SECRETARIA NACIONAL DE POLÍTICAS PENAIS
OUVIDORIA NACIONAL DE SERVIÇOS PENAIS

MONITORAMENTO DOS PARÂMETROS MÍNIMOS
DAS OUVIDORIAS DE SERVIÇOS PENAIS
```

Informar:

- data e hora de geração;
- referência à IN nº 75/2026;
- metodologia ONASP;
- arquivo de dados utilizado.

## Síntese

Exibir:

- total de unidades avaliadas;
- instituídas;
- não instituídas;
- sem evidência;
- quantidade por faixa de aderência.

## Quadro consolidado

Colunas:

```text
UF
Unidade
Institucionalização
Autonomia
Imparcialidade
Acessibilidade
Transparência
Integração tecnológica
Nota-base
Bônus
Nota final
Classificação
```

## Nota metodológica final

Utilizar:

> As pontuações, pesos e faixas de classificação constituem metodologia de monitoramento da ONASP e não integram o texto da Instrução Normativa GABSEC/SENAPPEN/MJSP nº 75/2026. A avaliação deve ser interpretada em conjunto com as evidências registradas no sistema.

---

# 22. Conteúdo do relatório individual

O relatório individual deve ser suficientemente detalhado para instruir análise técnica.

## 22.1. Identificação

Exibir:

```text
UF
Unidade avaliada
Situação institucional
Data de emissão
```

## 22.2. Resultado

Exibir tabela:

```text
Institucionalização
Autonomia
Imparcialidade
Acessibilidade
Transparência
Integração tecnológica
Nota-base
Bônus disponível
Bônus aplicado
Nota final
Classificação
```

## 22.3. Detalhamento por dimensão

Para cada pergunta:

```text
Código:
Pergunta:
Item:
Resposta do diagnóstico:
Fundamentação:
Avaliação:
Pontuação:
Evidência / observação:
Documentos anexados:
```

Listar os nomes dos documentos ativos.

Não embutir o conteúdo integral dos anexos no PDF.

## 22.4. Nota metodológica

Incluir ao final a mesma ressalva de que a pontuação é metodologia ONASP.

---

# 23. Exportação XLSX

A exportação não deve simplesmente entregar o `DADOS.xlsx` inteiro.

## Geral

Gerar arquivo:

```text
EXPORTACOES/relatorio_geral_YYYYMMDD_HHMMSS.xlsx
```

Com abas:

```text
Resumo
Resultados por unidade
Metodologia resumida
```

## Individual

Gerar:

```text
EXPORTACOES/relatorio_<entity_key>_YYYYMMDD_HHMMSS.xlsx
```

Com abas:

```text
Resumo
Avaliação detalhada
Anexos
```

Os relatórios são derivados.

Nunca usar o arquivo exportado como nova fonte de dados.

---

# 24. API interna

Mesmo utilizando templates server-side, manter endpoints organizados.

## Leitura

```text
GET /api/health
GET /api/resumo
GET /api/unidades
GET /api/unidades/{entity_key}
GET /api/unidades/{entity_key}/avaliacoes
GET /api/unidades/{entity_key}/avaliacoes/{occurrence_key}/anexos
```

## Alterações

```text
PATCH /api/unidades/{entity_key}/avaliacoes/{occurrence_key}
POST  /api/unidades/{entity_key}/avaliacoes/{occurrence_key}/anexos
POST  /api/anexos/{attachment_id}/desvincular
```

## Relatórios

```text
GET /api/relatorios/geral.pdf
GET /api/relatorios/geral.xlsx
GET /api/relatorios/{entity_key}.pdf
GET /api/relatorios/{entity_key}.xlsx
```

Não permitir atualização em massa sem confirmação explícita.

---

# 25. Contrato do PATCH de avaliação

Exemplo:

```json
{
  "status": "Atende",
  "evidence_text": "Doc. SEI 37070578; Portaria nº 123/2026",
  "observation": ""
}
```

A aplicação deve:

1. validar `entity_key`;
2. validar `occurrence_key`;
3. validar valor de status;
4. calcular pontuação;
5. registrar auditoria;
6. fazer backup;
7. gravar no Excel;
8. recalcular totais;
9. retornar dados atualizados.

Resposta:

```json
{
  "ok": true,
  "entity_key": "AC",
  "occurrence_key": "02_Autonomia:M3-56",
  "score": 3,
  "dimension_score": 12,
  "base_score": 78,
  "bonus_available": 4,
  "bonus_applied": 4,
  "final_score": 82,
  "classification": "Instituída — aderência satisfatória"
}
```

Valores acima são apenas exemplo de formato; não usar como dados reais.

---

# 26. Serviço de planilha

Criar módulo dedicado, por exemplo:

```text
src/workbook_service.py
```

Responsabilidades:

- localizar `DADOS.xlsx`;
- abrir workbook;
- mapear abas;
- mapear perguntas;
- mapear entidades;
- ler status;
- ler resposta do diagnóstico;
- ler fundamento;
- ler peso;
- ler pontuação;
- ler totais;
- gravar status;
- corrigir resposta quando autorizado;
- gerenciar abas auxiliares;
- recalcular fórmulas necessárias;
- validar consistência;
- salvar com backup e lock.

Não espalhar chamadas OpenPyXL pelos routers.

---

# 27. Motor de pontuação

Criar:

```text
src/scoring.py
```

A lógica de pontuação deve existir em código de maneira explícita e testável.

Não depender apenas do Excel para calcular.

A aplicação deve recalcular a nota para exibição no frontend.

O Excel também deve permanecer coerente.

Fonte de pesos:

preferencialmente uma configuração única em código, conferida contra a aba `00_Metodologia`.

Criar estrutura equivalente a:

```python
BASE_WEIGHTS = {
    "01_Institucionalização": 15,
    "02_Autonomia": 15,
    "03_Imparcialidade": 15,
    "04_Acessibilidade": 15,
    "05_Transparência": 15,
    "06_Integração Tec": 25,
}
```

E mapa de perguntas.

Se houver divergência entre configuração e planilha, registrar erro de consistência.

Não corrigir silenciosamente.

---

# 28. Serviço de anexos

Criar:

```text
src/attachments.py
```

Responsabilidades:

- validar extensão;
- validar tamanho;
- sanitizar nome;
- calcular SHA-256;
- gerar UUID;
- criar diretório;
- salvar;
- registrar `DB_ANEXOS`;
- listar arquivos;
- desvincular;
- fornecer download seguro.

Não permitir acesso arbitrário a arquivo por caminho informado pelo usuário.

Downloads devem usar apenas `attachment_id` existente em `DB_ANEXOS`.

---

# 29. Serviço de relatórios

Criar:

```text
src/reports.py
```

Responsabilidades:

- carregar dados consolidados;
- gerar PDF geral;
- gerar PDF individual;
- gerar XLSX geral;
- gerar XLSX individual;
- salvar em `EXPORTACOES`;
- retornar arquivo para download.

Usar ReportLab para PDF.

Manter visual institucional simples.

Evitar elementos gráficos decorativos desnecessários.

---

# 30. Interface visual

Utilizar identidade sóbria e compatível com a matriz.

Cores-base sugeridas:

```text
Azul escuro: #17365D
Azul:        #1F4E78
Azul claro:  #D9EAF7
Cinza claro: #F2F2F2
Verde claro: #E2F0D9
Amarelo:     #FFF2CC
Vermelho:    #F4CCCC
```

## Regras de UX

- navegação lateral ou superior simples;
- dashboard como página inicial;
- não usar excesso de cards;
- texto legível;
- status com texto, não apenas cor;
- tabelas com cabeçalho fixo quando útil;
- filtros claros;
- botões com verbo;
- confirmação antes de desvincular anexo;
- erros próximos ao campo relacionado;
- suporte a teclado;
- labels associados aos inputs;
- contraste adequado;
- responsividade mínima para notebook e monitor;
- evitar interfaces excessivamente densas.

---

# 31. Menu principal

Itens:

```text
Visão Geral
Unidades Federativas
Relatórios
Metodologia
```

Opcional:

```text
Auditoria
```

A auditoria pode ficar disponível apenas por rota administrativa simples no MVP.

---

# 32. Página “Unidades Federativas”

Rota:

```text
/unidades
```

Mostrar cards compactos ou tabela.

Preferir tabela para permitir comparação.

Campos:

```text
UF
Unidade
Situação
Nota final
Classificação
Última alteração
Abrir
```

ES deve aparecer em duas linhas.

---

# 33. Segurança

O sistema manipula documentos administrativos.

Mesmo sendo local:

- não executar uploads;
- não aceitar path externo;
- não renderizar HTML bruto vindo do Excel;
- escapar todo conteúdo apresentado;
- validar nomes e IDs;
- não permitir `../`;
- não expor pasta `ANEXOS` diretamente pelo servidor;
- servir anexos por endpoint controlado;
- não armazenar senhas;
- não usar chave de API;
- não publicar o servidor externamente por padrão.

Se futuramente houver acesso em rede, autenticação deverá ser implementada antes da exposição.

---

# 34. Integridade documental

A resposta do diagnóstico, a avaliação e a evidência são campos conceitualmente distintos.

Nunca misturar:

**Resposta do diagnóstico**
= declaração registrada pela UF.

**Avaliação**
= interpretação técnica do critério.

**Evidência**
= documento ou referência usada para sustentar a avaliação.

**Fundamentação**
= dispositivo da IN nº 75/2026 relacionado ao critério.

A interface deve deixar essa distinção visualmente clara.

---

# 35. Não automatizar interpretação substantiva

O sistema pode calcular pontos.

O sistema NÃO deve decidir sozinho que determinada resposta significa “Atende”, “Parcial” ou “Não atende”, salvo regra determinística expressamente aprovada.

No MVP, a decisão de avaliação deve permanecer humana.

É permitido futuramente criar botão:

`Sugerir avaliação`

mas somente mediante nova autorização e sem salvar automaticamente.

---

# 36. Tratamento do Espírito Santo

Não agregar as duas respostas do ES.

A aplicação deve tratar:

```text
ES_PP
ES_SEJUS
```

como unidades de avaliação diferentes.

No relatório geral, ambas devem aparecer.

Nos cálculos de quantidade:

- “Unidades de avaliação” conta ambas;
- “UFs representadas” pode contar ES apenas uma vez, se essa métrica for exibida.

Não calcular média do ES automaticamente.

---

# 37. Estado sem resposta suficiente

Se houver campo sem resposta:

exibir:

`Sem resposta no diagnóstico`

Não preencher com dado presumido.

Não usar resposta de outra UF.

Não usar informação da internet automaticamente.

---

# 38. Atualização das fórmulas do Excel

OpenPyXL não calcula fórmulas como o Excel.

Portanto:

- a aplicação deve calcular os resultados em Python para exibição imediata;
- ao gravar status, deve manter ou atualizar as fórmulas compatíveis existentes;
- deve gravar os valores de entrada corretos;
- os totais apresentados no frontend não podem depender de o Excel ter sido aberto após a alteração.

Ao gerar relatórios, utilizar o motor Python de pontuação, não o cache de fórmula do Excel.

---

# 39. Controle de consistência na inicialização

Ao iniciar, validar:

1. `DADOS.xlsx` existe;
2. as nove abas principais existem;
3. há registros das unidades;
4. ES possui duas unidades de avaliação distintas;
5. as perguntas configuradas existem;
6. os pesos das dimensões somam 100;
7. os bônus somam 10;
8. não há `entity_key` duplicada;
9. os caminhos registrados em `DB_ANEXOS` permanecem dentro de `ANEXOS`;
10. o arquivo pode ser aberto sem corrupção.

Exibir erro claro no terminal e em página de erro se a validação falhar.

---

# 40. Testes mínimos obrigatórios

Criar testes objetivos.

## 40.1. Pontuação

Testar:

- Atende = 100%;
- Parcial = 50%;
- Não atende = 0;
- Sem evidência = 0;
- soma das dimensões = 100;
- bônus máximo = 10;
- nota final nunca > 100.

## 40.2. Institucionalização

Testar:

- sem ato = Não instituída;
- bônus não transforma unidade não instituída em instituída.

## 40.3. Trava

Testar:

- uma dimensão essencial igual a zero gera “aderência insuficiente”.

## 40.4. ES

Testar:

- `ES_PP` existe;
- `ES_SEJUS` existe;
- são independentes;
- anexo de uma não aparece na outra.

## 40.5. Anexos

Testar:

- arquivo permitido;
- extensão proibida;
- path traversal;
- hash;
- metadados;
- desvinculação sem exclusão física.

## 40.6. Persistência

Em cópia temporária de `DADOS.xlsx`:

- editar um status;
- salvar;
- reabrir;
- confirmar que o valor persiste;
- confirmar que backup foi criado.

Nunca usar o `DADOS.xlsx` real em teste automatizado destrutivo.

---

# 41. Critérios de aceite

O desenvolvimento somente pode ser considerado concluído quando:

- [ ] a aplicação inicia localmente;
- [ ] lê `DADOS.xlsx`;
- [ ] não exige banco externo;
- [ ] dashboard apresenta todas as unidades;
- [ ] ES aparece duas vezes, corretamente identificado;
- [ ] cada pergunta mostra resposta do diagnóstico;
- [ ] cada pergunta mostra fundamento normativo;
- [ ] cada pergunta permite editar o status;
- [ ] pontuação é recalculada;
- [ ] cada pergunta possui evidência individual;
- [ ] evidência inicial pode conter `Doc. SEI 37070578`;
- [ ] cada pergunta permite anexar múltiplos documentos;
- [ ] anexos ficam em `ANEXOS/`;
- [ ] metadados ficam em `DB_ANEXOS`;
- [ ] alterações relevantes ficam em `DB_AUDITORIA`;
- [ ] há backup antes de gravar;
- [ ] há relatório geral PDF;
- [ ] há relatório geral XLSX;
- [ ] há relatório individual PDF;
- [ ] há relatório individual XLSX;
- [ ] página Metodologia está implementada com o conteúdo deste arquivo;
- [ ] classificação final obedece às regras;
- [ ] bônus não ultrapassa 100;
- [ ] dimensão zerada aplica a trava;
- [ ] unidade não instituída não recebe classificação normal de aderência;
- [ ] testes mínimos passam.

---

# 42. Sequência recomendada de implementação

Executar de forma incremental.

## Etapa 1 — leitura segura

- criar estrutura mínima;
- localizar `DADOS.xlsx`;
- mapear abas e entidades;
- exibir `/api/health`;
- exibir lista de unidades.

Não editar a planilha ainda.

## Etapa 2 — dashboard e detalhe

- dashboard;
- página da unidade;
- leitura de perguntas;
- resposta do diagnóstico;
- fundamentos;
- pontos atuais.

## Etapa 3 — gravação

- lock;
- backup;
- atualização de status;
- motor Python de pontuação;
- auditoria.

## Etapa 4 — evidências

- criar `DB_EVIDENCIAS`;
- inicializar `Doc. SEI 37070578`;
- editar evidência por pergunta.

## Etapa 5 — anexos

- criar `ANEXOS`;
- criar `DB_ANEXOS`;
- upload;
- listagem;
- download;
- desvinculação.

## Etapa 6 — relatórios

- individual;
- geral;
- PDF;
- XLSX.

## Etapa 7 — metodologia e acabamento

- implementar texto integral;
- filtros;
- responsividade;
- mensagens de erro;
- testes.

Não tentar fazer todas as etapas simultaneamente antes de validar a leitura da planilha.

---

# 43. Arquivos esperados

Estrutura sugerida:

```text
PARAMETROS MINIMOS/
├── DADOS.xlsx
├── app.py
├── requirements.txt
├── README.md
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── workbook_service.py
│   ├── scoring.py
│   ├── attachments.py
│   ├── reports.py
│   └── schemas.py
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   ├── units.html
│   ├── unit_detail.html
│   ├── reports.html
│   ├── methodology.html
│   └── error.html
├── static/
│   ├── app.css
│   └── app.js
├── ANEXOS/
├── BACKUPS/
├── EXPORTACOES/
└── tests/
    ├── test_scoring.py
    ├── test_workbook.py
    └── test_attachments.py
```

Manter quantidade pequena de arquivos.

Não criar camadas abstratas desnecessárias.

---

# 44. README mínimo do sistema

O `README.md` do repositório deve conter apenas o necessário para execução:

```text
# Parâmetros Mínimos — ONASP

## Requisitos
Python 3.12+

## Instalação
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

## Execução
uvicorn app:app --host 127.0.0.1 --port 8000

Acesse:
http://127.0.0.1:8000

## Dados
O arquivo DADOS.xlsx deve permanecer na raiz do projeto.

Antes de editar pelo Excel, encerre a aplicação.
Antes de editar pelo sistema, feche o arquivo no Excel.
```

---

# 45. Referências institucionais que devem orientar o conteúdo

Utilizar como referências do projeto:

1. Plano Nacional Pena Justa e respectiva matriz de implementação;
2. indicador `2.4.2.1.1.1` — elaboração de parâmetros para a criação de ouvidorias estaduais autônomas dos serviços penais;
3. indicador `2.4.2.1.2.1` — estabelecimento de ouvidorias estaduais criadas seguindo os parâmetros;
4. Instrução Normativa GABSEC/SENAPPEN/MJSP nº 75, de 8 de abril de 2026;
5. Processo SEI nº `08016.027689/2025-19`;
6. diagnóstico nacional das Ouvidorias de Serviços Penais;
7. `Doc. SEI 37070578` como referência documental das respostas consolidadas na matriz;
8. documentos técnicos da ONASP relacionados à Política de Fortalecimento das Ouvidorias de Serviços Penais e ao PROFOR/ONASP.

Não utilizar versões preliminares antigas da IN como fundamento vigente quando houver a IN nº 75/2026.

---

# 46. Regras finais para a IA executora

1. Ler este arquivo antes de começar.
2. Não replanejar a metodologia.
3. Não alterar pesos sem autorização.
4. Não retirar perguntas.
5. Não unir as duas avaliações do ES.
6. Não substituir `DADOS.xlsx` por outro banco.
7. Não apagar anexos fisicamente pela interface.
8. Não alterar resposta histórica do diagnóstico sem ação explícita.
9. Não inventar fundamento normativo.
10. Não modificar fórmulas ou estrutura além do necessário.
11. Criar backup antes de cada escrita.
12. Implementar primeiro leitura, depois gravação.
13. Utilizar paths relativos.
14. Manter o sistema local.
15. Manter interface institucional e objetiva.
16. Não criar dependências desnecessárias.
17. Não fazer commit ou push sem solicitação.
18. Não publicar o sistema.
19. Não executar rotinas destrutivas.
20. Ao final, informar objetivamente:
    - arquivos criados;
    - arquivos alterados;
    - testes executados;
    - resultado dos testes;
    - riscos remanescentes;
    - forma de rollback.

---

# 47. Resultado esperado

O resultado final deve ser uma aplicação local simples na qual o usuário consiga:

1. abrir o sistema pelo navegador;
2. visualizar todas as unidades avaliadas;
3. identificar rapidamente a situação de cada uma;
4. entrar em uma UF;
5. visualizar cada pergunta e a resposta do diagnóstico;
6. avaliar o critério;
7. registrar evidência;
8. anexar documentos comprobatórios;
9. consultar a fundamentação normativa;
10. visualizar a pontuação atualizada imediatamente;
11. gerar relatório individual;
12. gerar relatório geral;
13. consultar a metodologia completa;
14. manter todos os dados e documentos dentro do workspace;
15. continuar conseguindo abrir `DADOS.xlsx` diretamente no Excel para auditoria e conferência.

A solução deve funcionar como camada de visualização, edição, rastreabilidade e relatório sobre a matriz existente, sem perder a simplicidade e a auditabilidade da planilha como fonte principal de dados.
