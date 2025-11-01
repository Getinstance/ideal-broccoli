# ideal-broccoli

Desafio: Criação de uma API Pública para Consulta de Livros

O nome do reposotório foi sugerido pelo próprio GitHub na criação do repositório.

Gostei da sugestão e assim ficou.

![image](./docs/ideal_broccoli.png)

## Instruções de instalação

### Requisitos minimos

- Python ^3.12 <https://www.python.org/downloads/>
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

| Variável | Descrição |
|---|---|
|*DATABASE_URL*| URL string de conexão com o postgress. (Outros bancos de dados são suportados, mas as libs de conexão devem ser instaladas.)|
|*LOG_FILE_ENABLED* | Indica se o arquivo de log deve ser gerado|
|*LOG_FILE_PATH* | Caminha relativo ou absoluto do arquivo de logs.|
|*LOG_LEVEL* | Se não indicado assume o padrão `INFO`|
|*MULTI_THREAD_SCRAPING* | Indica se o scrap deve ser executado em multi thread.|
|*SECRET_KEY* | Segredo/Salt do token JWT|
|*REFRESH_SECRET_KEY* | Segredo/Salt do refresh token JWT|
|*ALGORITHM* | Algoritimo utilizado no token|
|*ACCESS_TOKEN_EXPIRE_MINUTES* | Tempo de expiração do token|
|*REFRESH_ACCESS_TOKEN_EXPIRE_DAYS* | Tempo de expiração do regfresh token|

### Executar o postgres localmente

`docker run --name ideal-broccoli-db -e POSTGRES_DB=ideal_broccoli -e POSTGRES_PASSWORD=mysecretpassword -p 5432:5432 -d postgres`

### Iniciar o projeto

Estando na raiz do projeto:

`pip install -r requirements.txt` para a instalação das dependencias.

`uvicorn main:app --reload --host 0.0.0.0 --port 3000 --app-dir=src` para a execução do projeto.

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

## Pipeline de ingestão de dados de books.toscrap.com

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

#### 1.1 Autenticar usuário `/auth/login`

Autenticação básica de usuário e senha, retorna tanto o token de acesso quanto
o token refresh.

``` shell
# REQUEST
curl -X 'POST' \
  'https://ideal-broccoli-bd8g.onrender.com/api/v1/auth/login' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "username": "user@example.com",
  "password": "string"
}'

#RESPONSE
{
  "token_type": "bearer",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyQGV4YW1wbGUuY29tIiwiZXhwIjoxNzYxODcyMDI2LCJ0eXBlIjoiYmVhcmVyIn0.nope",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyQGV4YW1wbGUuY29tIiwiZXhwIjoxNzYzMDc5ODI2LCJ0eXBlIjoicmVmcmVzaCJ9.nope",
  "expires_in": 1763079826
}
```

#### 1.2 Registrar novo usuário `/auth/register`

Cadastra um novo usuário com acesso aos endpoints da aplicação.

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

#### 1.3 Refresh token `/auth/refresh`

Utilizado para obter um token de acesso baseado no token de longa duração fornecido
no `/login` .

``` shell
#REQUEST
curl -X 'POST' \
  'https://ideal-broccoli-bd8g.onrender.com/api/v1/auth/refresh' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyQGV4YW1wbGUuY29tIiwiZXhwIjoxNzYzMDc5ODI2LCJ0eXBlIjoicmVmcmVzaCJ9.aMck1ACugihwjE2f2Vhj-vMYdNnke_kVinofQF2vuus"
}'

#RESPONSE

Response body
{
  "token_type": "bearer",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyQGV4YW1wbGUuY29tIiwiZXhwIjoxNzYxODcyMTQ2LCJ0eXBlIjoiYmVhcmVyIn0.nope",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyQGV4YW1wbGUuY29tIiwiZXhwIjoxNzYzMDc5OTQ2LCJ0eXBlIjoicmVmcmVzaCJ9.nope",
  "expires_in": 1763079946
}
```

### 2 Livros

#### 2.2 Listagem de livros `/books`

Listagem paginada e sem filtros.

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

#### 2.3 Detalhe de livros `/books/{id}`

Dados de um livro por ID

#### 2.4 Busca de livros `/books/search`

Busca paginada de livros por parametros. (Titulo ou Categoria)

#### 2.5 Top Rated `/books/top-rated`

Lista de livros ordenado por avaliações melhores.

#### 2.6 Faixa de preço `/books/price-range`

Permite busca de livros baseado em um range de preços.

### 3 Categorias

#### 3.1 Lista de categorias `/categories`

Lista paginada de categorias.

``` shell
#REQUEST
curl -X 'GET' \
  'https://ideal-broccoli-bd8g.onrender.com/api/v1/categories/' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyQGV4YW1wbGUuY29tIiwiZXhwIjoxNzYxODczMzAyLCJ0eXBlIjoiYmVhcmVyIn0.nope'

#RESPONSE
[
  {
    "id": 229,
    "name": "Travel"
  },
  {
    "id": 230,
    "name": "Mystery"
  },
  {
    "id": 231,
    "name": "Historical Fiction"
  }
]
```

### 4 Raspagem

#### 4.1 Trigger scrap `/scrap/trigger`

Inicia o processo de scrapping de <https://books.toscrape.com/>

#### 4.2 Scrap Clean-up `/scrap/cleanup`

Endpoint utilitário para limpar os dados de livros.
(Uso acadêmico)

### 5 Estatísticas

#### 5.1 Geral `/statistics/overview`

Contadores gerais dos livros cadastrados.

``` shell
#REQUEST
curl -X 'GET' \
  'https://ideal-broccoli-bd8g.onrender.com/api/v1/stats/overview' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyQGV4YW1wbGUuY29tIiwiZXhwIjoxNzYxODczMzAyLCJ0eXBlIjoiYmVhcmVyIn0.nope'

#RESPONSE
{
  "total_books": 1000,
  "total_categories": 50,
  "average_price": 35.07,
  "average_rating": 2.92,
  "available_books": 798,
  "unavailable_books": 202
}
```

#### 5.2 Categorias `/statistics/categories`

Contadores gerais das categorias dos livros, ordenado por quantidade de livros.

``` shell
#REQUEST
curl -X 'GET' \
  'https://ideal-broccoli-bd8g.onrender.com/api/v1/stats/categories' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyQGV4YW1wbGUuY29tIiwiZXhwIjoxNzYxODczMzAyLCJ0eXBlIjoiYmVhcmVyIn0.nope'

#RESPONSE
[
  {
    "category_id": 242,
    "category_name": "Default",
    "total_books": 152,
    "average_price": 34.39269736842105,
    "average_rating": 2.835526315789474
  },
  {
    "category_id": 240,
    "category_name": "Nonfiction",
    "total_books": 110,
    "average_price": 34.26018181818182,
    "average_rating": 2.881818181818182
  },
  {
    "category_id": 232,
    "category_name": "Sequential Art",
    "total_books": 75,
    "average_price": 34.57226666666667,
    "average_rating": 2.973333333333333
  }
]
```
