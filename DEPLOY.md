# Deploy em produção (VPS + domínio)

Este guia descreve como subir o **Socratis** (frontend Angular + API FastAPI) em uma VPS usando Docker.

## Por que Docker?

- **Reproduzível**: mesmo ambiente em qualquer servidor.
- **Isolado**: não polui a VPS com Node/Python globais.
- **Um comando**: `docker compose up -d` sobe frontend + API.
- **Fácil atualização**: novo build → nova imagem → recriar containers.

## Pré-requisitos na VPS

- **Docker** e **Docker Compose** instalados.
- **Domínio** apontando para o IP da VPS (registro A ou CNAME).
- (Opcional) **Nginx reverso** na frente (para HTTPS com Let's Encrypt); ver seção SSL abaixo.

## 1. Preparar o servidor

```bash
# Instalar Docker (exemplo para Ubuntu/Debian)
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
# Fazer logout e login para o grupo docker valer
```

## 2. Enviar o projeto para a VPS

No seu PC (na pasta do projeto):

```bash
# Opção A: Git (recomendado)
git push origin main
# Na VPS:
git clone <url-do-seu-repositorio> aplicada
cd aplicada
```

Ou use **rsync**/SFTP para copiar a pasta `aplicada` (incluindo `Agente-corretor-de-reda-o`) para a VPS.

## 3. Arquivo `.env` na VPS

Na **raiz do projeto** (pasta `aplicada`), crie um arquivo `.env` com as variáveis de produção:

```env
# Obrigatório: chave secreta forte (gere com: openssl rand -hex 32)
SECRET_KEY=sua-chave-secreta-muito-segura-aqui

# API da OpenAI (ou outro LLM que use)
OPENAI_API_KEY=sk-...

# Opcional: em produção, se quiser permitir CORS de outro domínio
# ALLOWED_ORIGINS=https://seudominio.com,https://www.seudominio.com

# Banco (se usar PostgreSQL em produção no futuro)
# DATABASE_URL=postgresql://user:senha@db:5432/socratis
```

**Importante:** nunca commite o `.env` no Git. Ele já deve estar no `.gitignore`.

## 4. Subir a aplicação

Na VPS, na pasta do projeto (onde está o `docker-compose.prod.yml`):

```bash
# Build das imagens (API + frontend) e subir em background
docker compose -f docker-compose.prod.yml build --no-cache
docker compose -f docker-compose.prod.yml up -d
```

Verificar se os containers estão rodando:

```bash
docker compose -f docker-compose.prod.yml ps
```

- **web** (Nginx + frontend): porta **80**.
- **api** (FastAPI): exposta apenas na rede interna; o Nginx faz proxy de `/api` para ela.

Acesse no navegador: `http://IP-DA-VPS` ou `http://seudominio.com`.

## 5. Apontar o domínio

No painel do seu provedor de DNS:

- Crie um registro **A** apontando seu domínio (ex: `socratis.seudominio.com`) para o **IP da VPS**.

Depois de propagar, acesse `http://seudominio.com`.

## 6. HTTPS (SSL) com Let's Encrypt (recomendado)

Para usar **HTTPS**, coloque um Nginx (ou Caddy) **na própria VPS**, fora do Docker, fazendo reverso para o container na porta 80 (ou use um container com Nginx + Certbot).

Exemplo mínimo com Nginx na VPS + Certbot:

```bash
# Instalar nginx e certbot (Ubuntu/Debian)
sudo apt update
sudo apt install -y nginx certbot python3-certbot-nginx

# Obter certificado (substitua seudominio.com)
sudo certbot --nginx -d seudominio.com

# Configurar proxy para o Docker (exemplo de site em /etc/nginx/sites-available/socratis)
# server {
#     listen 80;
#     server_name seudominio.com;
#     location / {
#         proxy_pass http://127.0.0.1:80;
#         proxy_set_header Host $host;
#         proxy_set_header X-Forwarded-For $remote_addr;
#         proxy_set_header X-Forwarded-Proto $scheme;
#     }
# }
```

Como o Docker já está usando a porta 80 no host, você pode:

- **Opção A:** Expor o container `web` em outra porta (ex: 8080) e no Nginx da VPS fazer `proxy_pass http://127.0.0.1:8080` e usar o Certbot no Nginx da VPS.
- **Opção B:** Usar um único Nginx na VPS na porta 80/443 e dentro dele fazer proxy para `api:8000` e servir o frontend (copiando os arquivos do build para a VPS). Assim o Docker só roda a API.

Para manter o setup atual (tudo no Docker), o mais simples é expor o `web` na porta **8080** e no Nginx da VPS:

- escutar 80/443;
- usar Certbot para SSL;
- fazer `proxy_pass http://127.0.0.1:8080` para o container.

No `docker-compose.prod.yml`, altere:

```yaml
ports:
  - "8080:80"
```

Assim o Nginx da VPS pode usar 80/443 e encaminhar para 8080.

## 7. Atualizar a aplicação

Depois de alterar código (frontend ou API):

```bash
# Na VPS, na pasta do projeto
git pull   # se usar Git

# Rebuild e recriar containers
docker compose -f docker-compose.prod.yml build --no-cache
docker compose -f docker-compose.prod.yml up -d
```

## 8. Logs e troubleshooting

```bash
# Logs dos dois serviços
docker compose -f docker-compose.prod.yml logs -f

# Só da API
docker compose -f docker-compose.prod.yml logs -f api

# Só do frontend (Nginx)
docker compose -f docker-compose.prod.yml logs -f web
```

Se a API retornar 502, confira se o container `api` está rodando e se o Nginx consegue resolver o nome `api` (rede interna do Compose).

## Resumo dos arquivos de deploy

| Arquivo | Função |
|--------|--------|
| `docker-compose.prod.yml` | Orquestra **api** (FastAPI) e **web** (Angular + Nginx). |
| `Dockerfile` (raiz) | Imagem da API Python. |
| `Agente-corretor-de-reda-o/Dockerfile` | Build do Angular e Nginx servindo estáticos. |
| `Agente-corretor-de-reda-o/nginx.conf` | Nginx: servir SPA e proxy `/api` para o container `api`. |
| `.env` | Variáveis de produção (SECRET_KEY, OPENAI_API_KEY, etc.). |

Com isso você sobe a aplicação inteira em produção na VPS com Docker.
