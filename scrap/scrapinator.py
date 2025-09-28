from bs4 import BeautifulSoup
import requests

base_url = 'https://books.toscrape.com/'
rates = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}

#Método para extrair dados de livros.
def extract_book_data(article):
    title = article.h3.a['title']
    price = float(article.find('p', class_='price_color').text.replace('£', ''))
    rating = rates[article.p['class'][1]]  # Pegando a segunda classe que indica a avaliação
    return {
        'title': title,
        'price': price,
        'rating': rating
    }

#Método para extrair as categorias
def extract_categories(category_anchor):
    category_name = category_anchor.text.strip()
    category_link = base_url + category_anchor['href']
    return { 'name': category_name, 'link': category_link , 'books' : [] }

#Método para extrair a proxima página
def extract_next_page(soup, category_link):
    next_button = soup.find('li', class_='next')
    if next_button:
        next_page_link = next_button.a['href']
        last_slash_index = category_link.rfind('/')
        return category_link[:last_slash_index+1] + next_page_link ## Substitui a parte final da URL pela nova página
    return None

def extract_from_books_to_scrape():
    # Fazendo uma requisição HTTP para a página desejada
    print(f'Acessando {base_url}')
    response = requests.get(base_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extraindo todas as categorias e links
    anchors = soup.find('ul', class_='nav-list').find_all('a')
    categories = [extract_categories(anchor) for anchor in anchors if anchor.text.strip() != 'Books']

    print(f'{len(categories)} categorias encontradas.')

    # Extraindo todos os elementos <article> com a classe 'product_pod' de cada uma das categorias
    for category in categories:
        print(f"Extraindo livros da categoria: {category['name']}")
        while category['link']:
            print(f"  Acessando página: {category['link']}")
            soup = BeautifulSoup(requests.get(category['link']).content, 'html.parser')
            articles = soup.find_all('article', class_='product_pod')
            books = [extract_book_data(article) for article in articles]
            category['books'] += books
            category['link'] = extract_next_page(soup, category['link'])
            print(f"  {len(books)} livros extraídos para a categoria {category['name']}.")

    # Iterando sobre os artigos e extraindo os dados.
    [print(category) for category in categories]

    return categories

if __name__ == "__main__":
    extract_from_books_to_scrape()
