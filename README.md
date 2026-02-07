# 📝 Mentor de Escrita IA - API

**Sistema Multiagentes para Correção Inteligente de Redações**

Uma API FastAPI avançada que funciona como um mentor evolutivo de escrita, indo muito além da simples correção gramatical. O sistema utiliza arquitetura multiagentes (inspirada em uma "banca examinadora") para análise profunda de redações com foco em estrutura lógica, argumentação e adequação ao tema (ENEM, concursos, vestibulares).

---

## 🎯 Visão Geral

### Por que é diferente?

A maioria dos corretores aponta apenas erros gramaticais. Este sistema:

- ✅ Analisa a **estrutura lógica** dos argumentos
- ✅ Detecta **falácias** e **contradições**
- ✅ Avalia **coesão textual** e uso de conectivos
- ✅ Verifica **repertório sociocultural**
- ✅ Gera **reescritas comparativas** (mostra como melhorar)
- ✅ Modo **Socrático** (ensina através de perguntas)
- ✅ Pontuação detalhada por **competências do ENEM**

---

## 🏗️ Arquitetura: Sistema Multiagentes "Banca Examinadora"

O texto passa por **4 agentes especializados**, cada um com expertise específica:

### 🔹 Agente 1: O Gramático (Free)
**Foco:** Ortografia, regência, crase, pontuação, vícios de linguagem

```
Entrada: Texto da redação
Saída: Lista de erros com regra + sugestão + nota
```

### 🔹 Agente 2: O Lógico (Premium)
**Foco:** Tese, argumentos, falácias lógicas, contradições

```
Entrada: Texto + tema
Saída: Análise da profundidade argumentativa + problemas lógicos
```

### 🔹 Agente 3: O Estruturalista (Premium)
**Foco:** Conectivos, coesão, estrutura dissertativo-argumentativa

```
Entrada: Texto
Saída: Análise de estrutura + uso de operadores argumentativos
```

### 🔹 Agente 4: O Avaliador (Híbrido)
**Foco:** Nota final + rubrica ENEM

```
Entrada: Texto + análises anteriores
Saída Free: Nota geral
Saída Premium: Nota por competência + gráfico de evolução
```

---

## 🚀 Instalação e Configuração

### Pré-requisitos

- Python 3.10+
- Conta OpenAI ou Google Gemini (para LLM)

### 1. Clone o repositório

```bash
git clone <seu-repositorio>
cd aplicada
```

### 2. Crie um ambiente virtual

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente

Copie o arquivo `env_example.txt` e renomeie para `.env`:

```bash
cp env_example.txt .env
```

Edite o `.env` e configure:

```env
# Escolha seu provider LLM
LLM_PROVIDER=openai  # ou "gemini"
LLM_MODEL=gpt-4o     # ou "gemini-1.5-pro"

# Adicione sua API Key
OPENAI_API_KEY=sk-...
# OU
GEMINI_API_KEY=...

# Segurança (MUDE!)
SECRET_KEY=sua-chave-super-secreta-aqui
```

### 5. Execute a API

```bash
# Modo desenvolvimento
uvicorn app.main:app --reload

# Ou usando Python
python -m app.main
```

A API estará disponível em: **http://localhost:8000**

Documentação interativa: **http://localhost:8000/docs**

---

## 📚 Documentação da API

### Autenticação

A API usa **JWT (JSON Web Tokens)** para autenticação.

#### 1. Cadastro

```http
POST /api/v1/usuarios/cadastro
Content-Type: application/json

{
  "email": "usuario@example.com",
  "nome": "João Silva",
  "senha": "senha123",
  "plano": "free"
}
```

**Resposta:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "usuario": {
    "id": "uuid",
    "email": "usuario@example.com",
    "nome": "João Silva",
    "plano": "free",
    "limite_diario": 5
  }
}
```

#### 2. Login

```http
POST /api/v1/usuarios/login
Content-Type: application/json

{
  "email": "usuario@example.com",
  "senha": "senha123"
}
```

#### 3. Obter perfil

```http
GET /api/v1/usuarios/me
Authorization: Bearer {token}
```

---

### Análise de Redações

#### Analisar uma redação

```http
POST /api/v1/analises/analisar
Authorization: Bearer {token}
Content-Type: application/json

{
  "titulo": "Os desafios da educação no Brasil",
  "texto": "A educação brasileira enfrenta...",
  "tema": "Desafios da educação no século XXI",
  "tipo": "enem",
  "referencias_esperadas": ["educação", "tecnologia", "desigualdade"]
}
```

**Resposta (Free):**
```json
{
  "redacao_id": "uuid",
  "plano_usuario": "free",
  "analise_gramatical": {
    "nota": 8.5,
    "total_erros": 3,
    "erros": [
      {
        "trecho": "trecho com erro",
        "tipo": "concordancia_verbal",
        "explicacao": "O sujeito está no plural...",
        "sugestao": "Os alunos precisam",
        "regra": "Concordância verbal"
      }
    ],
    "vicios_linguagem": [],
    "feedback_geral": "Boa redação com poucos erros..."
  },
  "fuga_ao_tema": false,
  "aderencia_tema": 85.5,
  "palavras_chave_usadas": ["educação", "tecnologia"],
  "avaliacao_final": {
    "nota_geral": 7.5,
    "nota_enem": 760,
    "feedback_geral": "Redação bem estruturada...",
    "pontos_fortes": ["argumentação clara"],
    "pontos_fracos": ["conclusão fraca"],
    "sugestoes_melhoria": ["fortaleça a proposta"]
  },
  "tempo_processamento": 12.5
}
```

**Resposta (Premium):** Inclui também:
- `analise_logica`: Análise profunda da argumentação
- `analise_estrutural`: Análise de coesão e estrutura
- `repertorio_sociocultural`: Análise de citações
- `reescritas_comparativas`: Exemplos de como melhorar
- `modo_socratico`: Perguntas para reflexão
- `competencias_enem`: Nota detalhada (0-200) para cada competência

#### Obter análise específica

```http
GET /api/v1/analises/{redacao_id}
Authorization: Bearer {token}
```

#### Listar análises

```http
GET /api/v1/analises?limite=10
Authorization: Bearer {token}
```

#### Ver evolução (Premium)

```http
GET /api/v1/analises/estatisticas/evolucao
Authorization: Bearer {token}
```

---

## 💎 Planos e Funcionalidades

| Funcionalidade | Free | Premium | B2B |
|---|:---:|:---:|:---:|
| Correção Gramatical | ✅ | ✅ | ✅ |
| Detecção de Fuga ao Tema | ✅ | ✅ | ✅ |
| Nota Geral | ✅ | ✅ | ✅ |
| Análise Lógica | ❌ | ✅ | ✅ |
| Análise Estrutural | ❌ | ✅ | ✅ |
| Repertório Sociocultural | ❌ | ✅ | ✅ |
| Reescrita Comparativa | ❌ | ✅ | ✅ |
| Modo Socrático | ❌ | ✅ | ✅ |
| Nota por Competência ENEM | ❌ | ✅ | ✅ |
| Gráfico de Evolução | ❌ | ✅ | ✅ |
| Limite Diário | 5 | 100 | Ilimitado |
| Painel do Professor | ❌ | ❌ | ✅ |

---

## 🛠️ Estrutura do Projeto

```
aplicada/
├── app/
│   ├── __init__.py
│   ├── main.py                    # Aplicação FastAPI principal
│   ├── config.py                  # Configurações
│   │
│   ├── agents/                    # Sistema Multiagentes
│   │   ├── __init__.py
│   │   ├── base_agent.py          # Classe base
│   │   ├── agente_gramatico.py    # Agente 1
│   │   ├── agente_logico.py       # Agente 2
│   │   ├── agente_estruturalista.py # Agente 3
│   │   ├── agente_avaliador.py    # Agente 4
│   │   ├── funcionalidades_premium.py
│   │   └── orquestrador.py        # Coordenador
│   │
│   ├── routers/                   # Endpoints
│   │   ├── __init__.py
│   │   ├── usuario.py             # Autenticação
│   │   ├── redacao.py             # Redações
│   │   └── analise.py             # Análises (core)
│   │
│   ├── schemas/                   # Modelos Pydantic
│   │   ├── __init__.py
│   │   ├── usuario.py
│   │   └── redacao.py
│   │
│   └── services/                  # Serviços
│       ├── __init__.py
│       ├── llm_service.py         # Integração com LLMs
│       └── auth_service.py        # Autenticação
│
├── requirements.txt               # Dependências
├── .gitignore
├── env_example.txt                # Exemplo de .env
└── README.md                      # Documentação
```

---

## 🧪 Testando a API

### Usando cURL

```bash
# 1. Cadastro
curl -X POST "http://localhost:8000/api/v1/usuarios/cadastro" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "teste@example.com",
    "nome": "Teste",
    "senha": "senha123",
    "plano": "premium"
  }'

# 2. Análise (usando o token recebido)
curl -X POST "http://localhost:8000/api/v1/analises/analisar" \
  -H "Authorization: Bearer SEU_TOKEN_AQUI" \
  -H "Content-Type: application/json" \
  -d '{
    "titulo": "Teste",
    "texto": "A educação é fundamental...",
    "tema": "Educação no Brasil",
    "tipo": "enem"
  }'
```

### Usando a documentação interativa

Acesse **http://localhost:8000/docs** para testar visualmente todos os endpoints.

---

## 🔧 Configuração Avançada

### Trocar de LLM (OpenAI ↔ Gemini)

Edite `.env`:

```env
# Para OpenAI
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o
OPENAI_API_KEY=sk-...

# Para Gemini
LLM_PROVIDER=gemini
LLM_MODEL=gemini-1.5-pro
GEMINI_API_KEY=...
```

### Ajustar temperatura e tokens

```env
LLM_TEMPERATURE=0.7    # 0-1 (menor = mais determinístico)
LLM_MAX_TOKENS=4000    # Máximo de tokens por resposta
```

### Limites por plano

```env
FREE_TIER_DAILY_LIMIT=5
PREMIUM_TIER_DAILY_LIMIT=100
```

---

## 📊 Exemplo de Fluxo Completo

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# 1. Cadastro
response = requests.post(f"{BASE_URL}/usuarios/cadastro", json={
    "email": "aluno@example.com",
    "nome": "Maria Silva",
    "senha": "senha123",
    "plano": "premium"
})
token = response.json()["access_token"]

# 2. Submeter redação
headers = {"Authorization": f"Bearer {token}"}
redacao = {
    "titulo": "Desafios da mobilidade urbana no Brasil",
    "texto": """
        A mobilidade urbana é um dos maiores desafios das grandes cidades brasileiras.
        Com o crescimento desordenado das metrópoles, o transporte público tornou-se
        insuficiente e de baixa qualidade, forçando milhões de pessoas a dependerem
        de carros particulares, o que agrava os congestionamentos.
        
        Portanto, é necessário investir em infraestrutura de transporte coletivo,
        como metrô e BRT, além de incentivar o uso de bicicletas através da criação
        de ciclovias integradas. Somente assim será possível garantir o direito
        de ir e vir com dignidade a todos os cidadãos.
    """,
    "tema": "Desafios da mobilidade urbana no Brasil contemporâneo",
    "tipo": "enem"
}

response = requests.post(
    f"{BASE_URL}/analises/analisar",
    headers=headers,
    json=redacao
)

analise = response.json()

# 3. Ver resultados
print(f"Nota Geral: {analise['avaliacao_final']['nota_geral']}")
print(f"Nota ENEM: {analise['avaliacao_final']['nota_enem']}")
print(f"Erros Gramaticais: {analise['analise_gramatical']['total_erros']}")
print(f"Fuga ao Tema: {analise['fuga_ao_tema']}")

# Premium: Ver análise lógica
if analise.get('analise_logica'):
    print(f"Tese identificada: {analise['analise_logica']['tese_identificada']}")
    print(f"Profundidade: {analise['analise_logica']['profundidade_argumentacao']}")
```

---

## 🚀 Próximos Passos / Roadmap

### Backend
- [ ] Implementar banco de dados real (PostgreSQL/MongoDB)
- [ ] Sistema de cache (Redis)
- [ ] Fila de processamento (Celery/RQ)
- [ ] Webhooks para notificações
- [ ] API de comparação com média nacional
- [ ] Sistema de templates de rubricas customizáveis

### Agentes
- [ ] Agente de detecção de plágio
- [ ] Agente de análise de originalidade
- [ ] Agente especializado em proposta de intervenção
- [ ] Suporte a mais tipos de texto (narrativo, descritivo)

### Funcionalidades
- [ ] Exportação de análise em PDF
- [ ] Histórico de versões de redação
- [ ] Comparativo entre versões
- [ ] Sistema de gamificação (badges, pontos)
- [ ] Integração com Google Classroom

### B2B
- [ ] Painel do professor
- [ ] Correção em lote
- [ ] Analytics da turma
- [ ] Sistema de turmas/escolas

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

---

## 💬 Suporte

Para dúvidas ou sugestões:
- Abra uma [Issue](link-do-repositorio/issues)
- Email: suporte@mentordeescrita.com (exemplo)

---

## 🙏 Agradecimentos

- OpenAI (GPT-4)
- Google (Gemini)
- FastAPI
- Comunidade Python

---

**Desenvolvido com ❤️ para estudantes brasileiros**

