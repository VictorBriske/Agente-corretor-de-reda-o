-- Migrations para Mentor de Escrita IA
-- Database: info_aplicada
-- Execute: psql -U postgres -d info_aplicada -f migrations.sql

-- Criar tabela de usuários
CREATE TABLE IF NOT EXISTS usuarios (
    id VARCHAR(36) PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    nome VARCHAR(100) NOT NULL,
    senha_hash VARCHAR(255) NOT NULL,
    plano VARCHAR(20) DEFAULT 'free' NOT NULL,
    correcoes_realizadas_hoje INTEGER DEFAULT 0,
    limite_diario INTEGER DEFAULT 5,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_usuarios_email ON usuarios(email);

-- Criar tabela de redações
CREATE TABLE IF NOT EXISTS redacoes (
    id VARCHAR(36) PRIMARY KEY,
    usuario_id VARCHAR(36) NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    titulo VARCHAR(200) NOT NULL,
    texto TEXT NOT NULL,
    tema VARCHAR(500) NOT NULL,
    tipo VARCHAR(20) DEFAULT 'dissertativa',
    status VARCHAR(20) DEFAULT 'pendente',
    data_submissao TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Criar tabela de análises
CREATE TABLE IF NOT EXISTS analises (
    id VARCHAR(36) PRIMARY KEY,
    redacao_id VARCHAR(36) NOT NULL UNIQUE REFERENCES redacoes(id) ON DELETE CASCADE,
    plano_usuario VARCHAR(20) NOT NULL,
    tempo_processamento FLOAT,
    tokens_utilizados INTEGER,
    analise_gramatical JSONB NOT NULL,
    analise_logica JSONB,
    analise_estrutural JSONB,
    repertorio_sociocultural JSONB,
    reescritas_comparativas JSONB,
    modo_socratico JSONB,
    avaliacao_final JSONB NOT NULL,
    fuga_ao_tema JSONB,
    aderencia_tema FLOAT,
    palavras_chave_usadas JSONB,
    data_analise TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Criar tabela de versões do Alembic
CREATE TABLE IF NOT EXISTS alembic_version (
    version_num VARCHAR(32) NOT NULL PRIMARY KEY
);

-- Inserir versão atual da migration
INSERT INTO alembic_version (version_num) 
VALUES ('93bb7a299a8b')
ON CONFLICT (version_num) DO NOTHING;

-- Mensagem de sucesso
SELECT 'Migrations aplicadas com sucesso!' as mensagem;
SELECT 'Tabelas criadas:' as info;
SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;

