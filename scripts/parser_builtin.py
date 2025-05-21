import requests
from bs4 import BeautifulSoup

# URL страницы с плагинами Ansible
base_url = 'https://docs.ansible.com/ansible/latest/collections/ansible/builtin/'

def get_plugin_blocks():
    response = requests.get(base_url)
    if response.status_code != 200:
        print(f"Failed to retrieve the page: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')

    # Находим все блоки с плагинами
    plugin_blocks = soup.find_all('div', class_='toctree-wrapper compound')
    return plugin_blocks

def get_plugin_links(block):
    links = []
    for link in block.find_all('a'):
        href = link.get('href')
        if href and href.startswith('../'):
            full_url = base_url + href.replace('../', '')
            links.append((link.text.strip(), full_url))
    return links

def check_requirements(plugin_url):
    response = requests.get(plugin_url)
    if response.status_code != 200:
        print(f"Failed to retrieve the plugin page: {plugin_url} with status code {response.status_code}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')

    # Ищем секцию с requirements
    requirements_section = soup.find('h2', string='Requirements')
    if requirements_section:
        # Получаем следующий элемент, который содержит список зависимостей
        requirements_list = requirements_section.find_next('ul')
        if requirements_list:
            requirements = [li.text for li in requirements_list.find_all('li')]
            return requirements
    return None

def main():
    response = requests.get(base_url)
    if response.status_code != 200:
        print(f"Failed to retrieve the main page: {response.status_code}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')

    # Находим все заголовки блоков плагинов
    blocks = soup.find_all('h2')
    
    for block in blocks:
        block_title = block.text.strip()
        print(f"{block_title} - ", end='')

        # Получаем ссылки на плагины в этом блоке
        plugin_links = get_plugin_links(block.find_next('div', class_='toctree-wrapper compound'))
        
        if not plugin_links:
            print("requirements none")
            continue

        for plugin_name, plugin_url in plugin_links:
            requirements = check_requirements(plugin_url)
            if requirements:
                print(f"{plugin_name} - requirements: {', '.join(requirements)}")
            else:
                print(f"{plugin_name} - requirements none")

if __name__ == "__main__":
    main()
