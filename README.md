# ideal-broccoli

Fase 1 - FIAP

[TOC]

## Instruções de instalação

### Requisitos minimos

- Python ^3.12
- Docker ou PostgresSQL

### .env inicial

``` shell
DATABASE_URL='postgresql+psycopg://postgres:mysecretpassword@localhost:5432/ideal_broccoli'
LOG_FILE_ENABLED=false
LOG_FILE_PATH='app.log'
LOG_LEVEL='DEBUG'
MULTI_THREAD_SCRAPING=true
SECRET_KEY=segredo_secreto_muito_secreto
REFRESH_SECRET_KEY=segredo_secreto_muito_mais_secreto
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_ACCESS_TOKEN_EXPIRE_DAYS=14
```

DATABASE_URL => URL string de conexão com o postgress.
Outros bancos de dados são suportados, mas as libs de conexão devem ser instaladas.

LOG_FILE_ENABLED => Indica se o arquivo de log deve ser gerado
LOG_FILE_PATH => Caminha relativo ou absoluto do arquivo de logs.
LOG_LEVEL => Se não indicado assume o padrão `INFO`
MULTI_THREAD_SCRAPING => Indica se o scrap deve ser executado em multi thread.
SECRET_KEY => Segredo/Salt do token JWT
REFRESH_SECRET_KEY => Segredo/Salt do refresh token JWT
ALGORITHM => Algoritimo utilizado no token
ACCESS_TOKEN_EXPIRE_MINUTES => Tempo de expiração do token
REFRESH_ACCESS_TOKEN_EXPIRE_DAYS => Tempo de expiração do regfresh token

### Executar o postgres localmente

`docker run --name ideal-broccoli-db -e POSTGRES_DB=ideal_broccoli -e POSTGRES_PASSWORD=mysecretpassword -p 5432:5432 -d postgres`

### Iniciar o projeto

Estando na raiz do projeto:

`uvicorn main:app --reload --host 0.0.0.0 --port 3000 --app-dir=src`

O projeto funciona como uma API Rest stateless.

Acesse [localhost:3000](http://localhost:3000/docs) após a execução.

## Estrutura do Projeto

Os diretórios de dominios são dividios em 3 arquivos:

- router (Rotas do FastAPI)
- models (Modelos da API e Banco de Dados)
- business, que leva o mesmo nome do dominio.

``` text
├── docs (Recursos utilizados na documentação)
├── notebooks (Notebooks criados durante os testes/desenvolvimentos)
└── src (Código da API, separados por dominios, rotas, negocios e modelos)
    ├── auth (Autenticação JWT)
    ├── books (Livros)
    ├── categories (Categorias)
    ├── core (Comum\Base para os outros dominios)
    ├── database (Setup do banco de dados)
    ├── machine_learning (Dados de treinamento e Machine Learning)
    ├── scrap (Lógica do Scrap e API)
    └── stats (Estatísticas gerais)
```

## Diagrama Entidade Relacionamento

``` mermaid
erDiagram
    categories {
        INT id PK
        VARCHAR name
        TIMESTAMP created_at
    }

    books {
        INT id PK
        VARCHAR title
        FLOAT price
        INT rating
        BOOLEAN available
        VARCHAR image_url
        INT category_id FK
        TIMESTAMP created_at
    }

    users {
        INT id PK
        VARCHAR username
        VARCHAR hashed_password
        TIMESTAMP created_at
    }

    categories ||--o{ books : "has"
```

## Pipeline de ingestão de dados

![image](./docs/scrapinator.png)

## Diagrama de sequência da pipeline de scrap

``` mermaid
sequenceDiagram
    participant Main
    participant Scraper as extract_from_books_to_scrape()
    participant Requests
    participant WebServer as books.toscrape.com
    participant BeautifulSoup
    participant CategoryProcessor as process_category()
    participant DataExtractors as extract_..._data()

    Main->>+Scraper: Start scraping
    Scraper->>+Requests: GET base_url
    Requests->>+WebServer: HTTP GET /
    WebServer-->>-Requests: HTML Response (Main Page)
    Requests-->>-Scraper: Return Response

    Scraper->>+BeautifulSoup: Parse HTML
    BeautifulSoup-->>-Scraper: Soup Object

    Scraper->>+DataExtractors: extract_categories(anchor)
    DataExtractors-->>-Scraper: List of Categories

    Note over Scraper: For each category (sequentially or in parallel)...
    Scraper->>+CategoryProcessor: process_category(category)

    loop For each page in category
        CategoryProcessor->>+Requests: GET category['link']
        Requests->>+WebServer: HTTP GET /catalogue/category/.../index.html
        WebServer-->>-Requests: HTML Response (Category Page)
        Requests-->>-CategoryProcessor: Return Response

        CategoryProcessor->>+BeautifulSoup: Parse HTML
        BeautifulSoup-->>-CategoryProcessor: Soup Object

        Note over CategoryProcessor: For each book article on page...
        CategoryProcessor->>+DataExtractors: extract_book_data(article)
        DataExtractors-->>-CategoryProcessor: Book Data (dict)

        CategoryProcessor->>+DataExtractors: extract_next_page(soup)
        DataExtractors-->>-CategoryProcessor: Next Page URL or None
    end

    CategoryProcessor-->>-Scraper: Return Category with Books
    Scraper-->>-Main: Return All Scraped Data
```

## API e seus usos

Acesse a documentação publicada em: [ideal-broccoli Swagger UI](https://ideal-broccoli-bd8g.onrender.com/docs)

![image](./docs/swagger.png)

### 1. Fluxo de autenticação

#### 1.1 Registrar novo usuário

``` shell
# REQUEST
curl -X 'POST' \
  'https://ideal-broccoli-bd8g.onrender.com/api/v1/auth/register' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "username": "user@example.com",
  "password": "string"
}'

#RESPONSE
{
  "message": "User registered successfully"
}
```

#### 1.2 Autenticar usuário

``` shell
#REQUEST
curl -X 'POST' \
  'https://ideal-broccoli-bd8g.onrender.com/api/v1/auth/login' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "username": "user@example.com",
  "password": "string"
}'

#RESPONSE

Response body
Download
{
  "token_type": "bearer",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyQGV4YW1wbGUuY29tIiwiZXhwIjoxNzYxNzc5OTUwLCJ0eXBlIjoiYmVhcmVyIn0.nope",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyQGV4YW1wbGUuY29tIiwiZXhwIjoxNzYyOTg3NzUwLCJ0eXBlIjoicmVmcmVzaCJ9.nope",
  "expires_in": 1762987750
}
```

### 2 Livros

#### 2.2 Listagem de livros

``` shell
#REQUEST
curl -X 'GET' \
  'https://ideal-broccoli-bd8g.onrender.com/api/v1/books/?page=1&limit=2' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyQGV4YW1wbGUuY29tIiwiZXhwIjoxNzYxNzc5OTUwLCJ0eXBlIjoiYmVhcmVyIn0.nope'

#RESPONSE
[
  {
    "id": 4825,
    "title": "It's Only the Himalayas",
    "price": 45.17,
    "rating": 2,
    "available": true,
    "image_url": "https://books.toscrape.com/media/cache/27/a5/27a53d0bb95bdd88288eaf66c9230d7e.jpg",
    "category": {
      "id": 229,
      "name": "Travel"
    }
  },
  {
    "id": 4826,
    "title": "Full Moon over Noah’s Ark: An Odyssey to Mount Ararat and Beyond",
    "price": 49.43,
    "rating": 4,
    "available": true,
    "image_url": "https://books.toscrape.com/media/cache/57/77/57770cac1628f4407636635f4b85e88c.jpg",
    "category": {
      "id": 229,
      "name": "Travel"
    }
  }
]
```
