import os
import subprocess
import json
import yaml

def convert_manifest_to_galaxy(manifest_file, galaxy_file):
    # Чтение данных из MANIFEST.json
    with open(manifest_file, 'r') as f:
        manifest_data = json.load(f)

    # Извлечение информации из manifest_data
    collection_info = manifest_data.get("collection_info", {})
    
    galaxy_data = {
        'namespace': collection_info.get('namespace'),
        'name': collection_info.get('name'),
        'version': collection_info.get('version'),
        'authors': collection_info.get('authors', []),
        'readme': collection_info.get('readme'),
        'tags': collection_info.get('tags', []),
        'description': collection_info.get('description'),
    }

    # Создание словаря для лицензии и других метаданных
    collection_info_dict = {
        'repository': collection_info.get('repository'),
        'documentation': collection_info.get('documentation'),
        'homepage': collection_info.get('homepage'),
        'issues': collection_info.get('issues')
    }

    # Проверяем наличие license или license_file
    if 'license' in collection_info:
        collection_info_dict['license'] = collection_info.get('license')
    elif 'license_file' in collection_info:
        collection_info_dict['license'] = collection_info.get('license_file')

    # Добавляем информацию о лицензии и другие метаданные в galaxy_data
    galaxy_data.update(collection_info_dict)

    # Запись данных в galaxy.yml
    with open(galaxy_file, 'w') as f:
        yaml.dump(galaxy_data, f, default_flow_style=False, sort_keys=False)

def build_collection(collection_path):
    # Строим коллекцию
    print(f"Building collection: {collection_path}")
    try:
        subprocess.run(['ansible-galaxy', 'collection', 'build', '-c', collection_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error building collection {collection_path}: {e}")
        return False

    # Получаем имя tar файла
    collection_name = os.path.basename(collection_path)
    collection_tar = f"{collection_name}.tar.gz"

    # Публикуем коллекцию
def publish_collection(collection_path):
    galaxy_url = os.getenv('ANSIBLE_GALAXY_SERVER_GALAXY_URL')
    validated_token = os.getenv('ANSIBLE_GALAXY_SERVER_VALIDATED_TOKEN')

    if not galaxy_url or not validated_token:
        print("Не установлены необходимые переменные окружения.")
        sys.exit(1)

    command = [
        'ansible-galaxy', 
        'collection', 
        'publish', 
        collection_path, 
        '--server', galaxy_url, 
        '--api-key', validated_token
    ]

    try:
        subprocess.run(command, check=True)
        print(f"Коллекция {collection_path} успешно опубликована.")
    except subprocess.CalledProcessError as e:
        if "already exists" in str(e):
            print(f"Коллекция {collection_path} уже существует на Galaxy.")
        elif "namespace" in str(e):
            print(f"Namespace для {collection_path} не существует на Galaxy.")
        else:
            print(f"Ошибка при публикации коллекции {collection_path}: {e}")
        return False

    return True

def main():
    collections_dir = "/usr/share/ansible/collections/ansible_collections/"
    
    # Проходим по директориям коллекций
    for namespace in os.listdir(collections_dir):
        namespace_path = os.path.join(collections_dir, namespace)
        if os.path.isdir(namespace_path) and not namespace.endswith('.info'):
            for collection in os.listdir(namespace_path):
                collection_path = os.path.join(namespace_path, collection)
                if os.path.isdir(collection_path):
                    manifest_file = os.path.join(collection_path, 'MANIFEST.json')
                    galaxy_file = os.path.join(collection_path, 'galaxy.yml')

                    # Проверяем наличие MANIFEST.json
                    if os.path.exists(manifest_file):
                        convert_manifest_to_galaxy(manifest_file, galaxy_file)
                        
                        # Строим и публикуем коллекцию
                        success = build_collection(collection_path)
                        if not success:
                            print(f"Failed to process collection: {collection_path}")
                    else:
                        print(f"MANIFEST.json not found in {collection_path}")

if __name__ == "__main__":
    main()