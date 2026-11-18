# Ideya API

API para descobrir sugestões de lazer em Luanda com base no orçamento por
pessoa. Os locais e os respetivos dados são obtidos do Airtable; a opção
“Surpreenda-me” usa o Google Gemini para escolher entre os resultados válidos.

## Requisitos

- Python 3.11 ou superior
- Poetry
- Credenciais e uma base Airtable com uma tabela `Locais`
- Chave da API Google Gemini para o endpoint “Surpreenda-me”

## Instalação e execução

```bash
poetry install
cp .env.example .env
# Preencher as credenciais no ficheiro .env
poetry run uvicorn app.main:app --reload
```

O health check está disponível em `GET /health`; a documentação interativa
fica em `/docs`.

## Endpoints

- `GET /locais`: lista locais validados.
- `POST /criar-ideya`: devolve locais dentro do orçamento e dos filtros.
- `POST /surpreenda-me`: escolhe um local candidato e devolve uma justificação.

Os pedidos `POST` recebem `orcamento_total` e `num_pessoas`, podendo também
incluir `zona` e `categoria`. O orçamento máximo por pessoa é calculado por
divisão inteira.