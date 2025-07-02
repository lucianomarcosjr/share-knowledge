import os
import requests
import base64
import nacl.encoding
import nacl.public

## You will need install this package
## sudo pip3 install pynacl

def get_public_key(token, repo):
    url = f"https://api.github.com/repos/{repo}/actions/secrets/public-key"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error retrieving public key: {response.text}")
        return None

def encrypt_secret(secret_value, public_key):
    try:
        pk = nacl.public.PublicKey(public_key["key"], nacl.encoding.Base64Encoder())
        sealed_box = nacl.public.SealedBox(pk)
        encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
        return base64.b64encode(encrypted).decode("utf-8")
    except Exception as e:
        print(f"Encryption error: {e}")
        return None

def set_secret(token, repo, secret_name, secret_value, public_key):
    encrypted_value = encrypt_secret(secret_value, public_key)
    if not encrypted_value:
        print(f"Failed to encrypt '{secret_name}', skipping...")
        return

    url = f"https://api.github.com/repos/{repo}/actions/secrets/{secret_name}"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}"
    }
    data = {
        "encrypted_value": encrypted_value,
        "key_id": public_key["key_id"]
    }

    response = requests.put(url, headers=headers, json=data)

    if response.status_code in [201, 204]:
        print(f"Secret '{secret_name}' added successfully!")
    else:
        print(f"Error adding secret '{secret_name}': {response.text}")

def set_variable(token, repo, var_name, var_value):
    url = f"https://api.github.com/repos/{repo}/actions/variables/{var_name}"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}"
    }
    data = {
        "name": var_name,
        "value": var_value
    }

    response = requests.put(url, headers=headers, json=data)

    if response.status_code in [201, 204]:
        print(f"Variable '{var_name}' added successfully!")
    else:
        print(f"Error adding variable '{var_name}': {response.text}")

def interactive_input():
    items = {}
    while True:
        name = input("Enter name (or press ENTER to finish): ").strip()
        if not name:
            break
        value = input(f"Enter value for '{name}': ").strip()
        items[name] = value
    return items

def load_secrets_from_file(file_path):
    items = {}
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            for line in f:
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    name, value = line.split("=", 1)
                    items[name.strip()] = value.strip()
    else:
        print(f"File '{file_path}' not found.")
    return items

def main():
    print("GitHub Secrets/Variables Importer")

    github_token = input("Enter your GitHub Token: ").strip()
    repo_name = input("Enter repository name (e.g., owner/repo): ").strip()

    print("\nDo you want to add:")
    print("1 - Secrets")
    print("2 - Variables")

    item_type = None
    while item_type not in ("1", "2"):
        item_type = input("Option (1 or 2): ").strip()
        if item_type not in ("1", "2"):
            print("Invalid option. Please type 1 or 2.")

    if item_type == "1":
        public_key = get_public_key(github_token, repo_name)
        if not public_key:
            return

    print("\nHow would you like to add the data?")
    print("1 - Enter manually")
    print("2 - Load from a .secrets/.env file")

    choice = None
    while choice not in ("1", "2"):
        choice = input("Option (1 or 2): ").strip()
        if choice not in ("1", "2"):
            print("Invalid option. Please type 1 or 2.")

    if choice == "2":
        file_path = input("Enter the path to your file: ").strip()
        items = load_secrets_from_file(file_path)
    else:
        items = interactive_input()

    if not items:
        print("No data provided. Exiting...")
        return

    for name, value in items.items():
        if item_type == "1":
            set_secret(github_token, repo_name, name, value, public_key)
        else:
            set_variable(github_token, repo_name, name, value)

    print("All items have been added.")

if __name__ == "__main__":
    main()
