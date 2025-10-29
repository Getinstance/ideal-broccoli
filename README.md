# ideal-broccoli

Fase 1 - FIAP

## Executar o postgres localmente

`docker run --name ideal-broccoli-db -e POSTGRES_DB=ideal_broccoli -e POSTGRES_PASSWORD=mysecretpassword -p 5432:5432 -d postgres`

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
