#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module for automatic building and publishing of Ansible collections to the Ansible Galaxy server.
The program checks for necessary environment variables, builds a collection, and publishes it.
"""

import glob
import json
import os
import subprocess
import sys
from typing import List

import yaml

ANSIBLE_GALAXY_SERVER_VALIDATED_TOKEN = os.getenv("ANSIBLE_GALAXY_SERVER_VALIDATED_TOKEN")
ANSIBLE_GALAXY_SERVER_GALAXY_URL = os.getenv("ANSIBLE_GALAXY_SERVER_GALAXY_URL")

def check_env() -> List[str]:
    """
    Checks for the presence of required environment variables.

    :return: A list of missing environment variables.
    """
    required_envs = ["ANSIBLE_GALAXY_SERVER_VALIDATED_TOKEN", "ANSIBLE_GALAXY_SERVER_GALAXY_URL"]
    return [env for env in required_envs if not globals()[env]]


def convert_manifest_to_galaxy(manifest_file: str, galaxy_file: str) -> None:
    """
    Converts data from the MANIFEST.json file into the galaxy.yml format.

    :param manifest_file: Path to the MANIFEST.json file.
    :param galaxy_file: Path to the galaxy.yml file.
    """
    with open(manifest_file, 'r') as f:
        manifest_data = json.load(f)

    galaxy_data = manifest_data.get("collection_info", {})

    if "aacertified" in galaxy_data.get("tags", []):
        galaxy_data['publish_url'] = "/api/galaxy/content/aa-certified/"
    else:
        galaxy_data['publish_url'] = "/api/galaxy/content/validated/"

    if galaxy_data.get("license_file", ""):
        galaxy_data.pop("license", None)
    else:
        galaxy_data.pop("license_file", None)

    with open(galaxy_file, 'w') as f:
        yaml.dump(galaxy_data, f, default_flow_style=False, sort_keys=False)


def build_collection(base_path: str, collection_path: str) -> str:
    """
    Builds an Ansible collection using ansible-galaxy.

    :param base_path: Base path to the collection.
    :param collection_path: Path to a specific collection relative to the base path.
    :return: The name of the built archive (.tar.gz).
    """
    collection_dir = os.path.join(base_path, collection_path)

    print(f"Building collection: {collection_dir}")

    try:
        with open(os.devnull, 'wb') as devnull:
            subprocess.run(['ansible-galaxy', 'collection', 'build', '-c', collection_dir],
                           check=True,
                           stdout=devnull,
                           stderr=devnull,
                           text=True)
    except subprocess.CalledProcessError as e:
        print(f"Error building collection {collection_dir}: {e}")
        return ""

    namespace, collection = collection_path.split('/')
    tarball_pattern = f"{namespace}-{collection}-*.tar.gz"
    tarballs = glob.glob(tarball_pattern)

    if not tarballs:
        print(f"Could not find built collection matching pattern: {tarball_pattern}")
        return ""

    return os.path.basename(tarballs[0])

def get_publish_url(galaxy_file: str, galaxy_url: str) -> str:
    """
    Generates a URL for publishing the collection based on data from the galaxy.yml file. 
    
    :param galaxy_file: The path to the galaxy.yml file. 
    :param galaxy_url: The base URL of the Ansible Galaxy server. 
    :return: The full URL for publishing the collection.
    """
    if galaxy_url.startswith("http://") or galaxy_url.startswith("https://"):
        publish_url = galaxy_url
    else:
        publish_url = f"https://{galaxy_url}"

    with open(galaxy_file, 'r') as f:
        galaxy_data = yaml.safe_load(f)
        publish_url += galaxy_data['publish_url']

    return publish_url

def publish_collection(collection_tar: str, publish_url: str) -> None:
    """
    Publishes a collection to the Ansible Galaxy server.

    :param collection_tar: Name of the archived collection file.
    :param publish_url: URL for publication on the Ansible Galaxy server.
    """
    validated_token = ANSIBLE_GALAXY_SERVER_VALIDATED_TOKEN

    command = [
        'ansible-galaxy',
        'collection',
        'publish',
        collection_tar,
        '--server', publish_url,
        '--api-key', validated_token,
        '--ignore-certs'
    ]

    try:
        subprocess.run(command, check=True, capture_output=True)
        print(f"Collection {collection_tar} successfully published.")

    except subprocess.CalledProcessError as e:
        if "already exists" in str(e.stderr):
            print(f"Collection {collection_tar} already exists on Galaxy.")

        elif "Namespace" in str(e.stderr):
            print(f"Namespace for {collection_tar} does not exist on Galaxy.")

        else:
            print(f"Error publishing collection {collection_tar}: {e}")


def main() -> None:
    """
    Main entry point of the program.
    Performs the building and publishing of Ansible collections.

    Usage:
    python script.py --collection <namespace>.<collection>  # Publish a single collection
    python script.py --namespace <namespace>                # Publish all collections within a given namespace
    python script.py --all                                  # Publish all available collections
    """
    collections_dir = "/usr/share/ansible/collections/ansible_collections/"

    missing_envs = check_env()
    if missing_envs:
        print(f"The following required environment variables are missing: {', '.join(missing_envs)}")
        sys.exit(1)

    if len(sys.argv) < 2:
        print("Usage:")
        print("python script.py --collection <namespace>.<collection>  # Publish a single collection")
        print("python script.py --namespace <namespace>                # Publish all collections within a given namespace")
        print("python script.py --all                                  # Publish all available collections")
        sys.exit(1)
    
    if sys.argv[1] == "--collection":
        if len(sys.argv) == 3:
            target_collection = sys.argv[2]

            parts = target_collection.split(".")
            if len(parts) != 2:
                print("Incorrect collection format. Expected: <namespace>.<collection>")
                sys.exit(1)

            namespace, collection = parts

            collection_path = os.path.join(namespace, collection)

            full_collection_path = os.path.join(collections_dir, collection_path)
            if not os.path.exists(full_collection_path):
                print(f"Collection path '{full_collection_path}' does not exist.")
                sys.exit(1)

            manifest_file = os.path.join(full_collection_path, 'MANIFEST.json')
            galaxy_file = os.path.join(full_collection_path, 'galaxy.yml')

            if os.path.exists(manifest_file):
                convert_manifest_to_galaxy(manifest_file, galaxy_file)
                collection_tar = build_collection(
                    base_path=collections_dir,
                    collection_path=collection_path
                )

                if collection_tar:
                    publish_url = get_publish_url(galaxy_file, ANSIBLE_GALAXY_SERVER_GALAXY_URL)
                    publish_collection(collection_tar, publish_url)

            else:
                print(f"MANIFEST.json file is missing for {full_collection_path}")
                sys.exit(0)

        else:
            print("Usage: --collection <namespace>.<collection>")
            sys.exit(1)

    elif sys.argv[1] == "--namespace":
        if len(sys.argv) == 3:
            target_namespace = sys.argv[2]
            namespace_path = os.path.join(collections_dir, target_namespace)
            if os.path.exists(namespace_path):

                for collection in os.listdir(namespace_path):
                    collection_path = os.path.join(namespace_path, collection)

                    if os.path.isdir(collection_path):
                        manifest_file = os.path.join(collection_path, 'MANIFEST.json')
                        galaxy_file = os.path.join(collection_path, 'galaxy.yml')

                        if os.path.exists(manifest_file):
                            convert_manifest_to_galaxy(manifest_file, galaxy_file)
                            collection_tar = build_collection(
                                base_path=collections_dir,
                                collection_path=os.path.join(target_namespace, collection)
                            )

                            if collection_tar:
                                publish_url = get_publish_url(galaxy_file, ANSIBLE_GALAXY_SERVER_GALAXY_URL)
                                publish_collection(collection_tar, publish_url)
                        else:
                            print(f"MANIFEST.json file is missing for {collection_path}")
            else:
                print(f"Namespace directory '{target_namespace}' does not exist.")
                sys.exit(1)
        else:
            print("Usage: --namespace <namespace>")
            sys.exit(1)

    elif sys.argv[1] == "--all":
        for namespace in os.listdir(collections_dir):
            namespace_path = os.path.join(collections_dir, namespace)
            if os.path.isdir(namespace_path) and not namespace.endswith('.info'):

                for collection in os.listdir(namespace_path):
                    collection_path = os.path.join(namespace_path, collection)

                    if os.path.isdir(collection_path):
                        manifest_file = os.path.join(collection_path, 'MANIFEST.json')
                        galaxy_file = os.path.join(collection_path, 'galaxy.yml')

                        if os.path.exists(manifest_file):
                            convert_manifest_to_galaxy(manifest_file, galaxy_file)
                            collection_tar = build_collection(
                                base_path=collections_dir,
                                collection_path=os.path.join(namespace, collection)
                            )

                            if collection_tar:
                                publish_url = get_publish_url(galaxy_file, ANSIBLE_GALAXY_SERVER_GALAXY_URL)
                                publish_collection(collection_tar, publish_url)
                    else:
                        print(f"MANIFEST.json file is missing for {collection_path}")
    else:
        print(f"Unknown option: {sys.argv[1]}. Use one of the supported options:")
        print("--collection <namespace>.<collection>  # Publish a single collection")
        print("--namespace <namespace>                # Publish all collections within a given namespace")
        print("--all                                  # Publish all available collections")
        sys.exit(1)

if __name__ == "__main__":
    main()