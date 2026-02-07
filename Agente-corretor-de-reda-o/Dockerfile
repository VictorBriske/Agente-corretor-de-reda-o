# Stage 1: Build do Angular
FROM node:20-alpine AS build

WORKDIR /app

# Copiar arquivos de dependências
COPY package.json package-lock.json ./

# Instalar dependências (incluindo dev para o build)
RUN npm ci

# Copiar código fonte
COPY . .

# Build de produção
RUN npm run build

# Stage 2: Servir com Nginx
FROM nginx:alpine

# Remover config padrão e usar a nossa
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copiar artefatos do build do stage anterior
COPY --from=build /app/dist/reda-corretor/browser /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
