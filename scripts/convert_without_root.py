import os
import json
import yaml
import shutil

# Функция для преобразования MANIFEST.json в galaxy.yml
def convert_manifest_to_galaxy(manifest_file, galaxy_file):
    # Чтение данных из MANIFEST.json
    with open(manifest_file, 'r', encoding='utf-8') as f:
        manifest_data = json.load(f)

    # Извлечение информации для galaxy.yml
    collection_info = manifest_data.get("collection_info", {})
    
    galaxy_data = {
        "namespace": collection_info.get("namespace"),
        "name": collection_info.get("name"),
        "version": collection_info.get("version"),
        "authors": collection_info.get("authors", []),
        "readme": collection_info.get("readme"),
        "tags": collection_info.get("tags", []),
        "description": collection_info.get("description"),
        "license": collection_info.get("license", []),
        "license_file": collection_info.get("license_file"),
        "dependencies": collection_info.get("dependencies", {}),
        "repository": collection_info.get("repository"),
        "documentation": collection_info.get("documentation"),
        "homepage": collection_info.get("homepage"),
        "issues": collection_info.get("issues")
    }

    # Запись данных в galaxy.yml
    with open(galaxy_file, 'w', encoding='utf-8') as f:
        yaml.dump(galaxy_data, f, default_flow_style=False, allow_unicode=True)

# Функция для обработки коллекций
def process_collections(collections_dir):
    temp_dir = "/tmp/ansible_collections"
    
    # Создаем временную директорию
    os.makedirs(temp_dir, exist_ok=True)

    # Проходим по директориям коллекций
    for namespace in os.listdir(collections_dir):
        namespace_path = os.path.join(collections_dir, namespace)
        if os.path.isdir(namespace_path) and not namespace.endswith('.info'):
            for collection in os.listdir(namespace_path):
                collection_path = os.path.join(namespace_path, collection)
                manifest_file = os.path.join(collection_path, 'MANIFEST.json')

                if os.path.isdir(collection_path) and os.path.isfile(manifest_file):
                    # Копируем коллекцию в /tmp
                    dest_collection_path = os.path.join(temp_dir, namespace, collection)
                    os.makedirs(os.path.dirname(dest_collection_path), exist_ok=True)
                    shutil.copytree(collection_path, dest_collection_path)

                    # Создаем galaxy.yml в скопированной директории
                    galaxy_file = os.path.join(dest_collection_path, 'galaxy.yml')
                    try:
                        convert_manifest_to_galaxy(manifest_file, galaxy_file)
                        print(f"Successfully processed collection: {dest_collection_path}")
                    except Exception as e:
                        print(f"Failed to process collection {dest_collection_path}: {e}")

# Пример использования
if __name__ == "__main__":
    collections_dir = "/usr/share/ansible/collections/ansible_collections/"
    process_collections(collections_dir)
