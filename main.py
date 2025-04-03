import os
import sys
import subprocess
import random
import string
import requests
import json
from cryptography.fernet import Fernet

def ensure_installed(packages):
    """Ensure required packages are installed."""
    for package in packages:
        try:
            __import__(package)
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# List of required packages (excluding 'json' since it's built-in)
required_packages = ["requests", "cryptography"]
ensure_installed(required_packages)

# Encryption key management
def generate_key():
    """Generate a new encryption key."""
    return Fernet.generate_key()

def load_key():
    """Load the encryption key from a file."""
    try:
        with open("secret.key", "rb") as key_file:
            return key_file.read()
    except FileNotFoundError:
        key = generate_key()
        save_key(key)
        return key

def save_key(key):
    """Save the encryption key to a file."""
    with open("secret.key", "wb") as key_file:
        key_file.write(key)

# Encryption functions
def encrypt_password(password):
    """Encrypt a password using Fernet encryption."""
    key = load_key()
    fernet = Fernet(key)
    return fernet.encrypt(password.encode()).decode()

def decrypt_password(encrypted_password):
    """Decrypt an encrypted password."""
    key = load_key()
    fernet = Fernet(key)
    return fernet.decrypt(encrypted_password.encode()).decode()

# Password storage
passwords_file = 'passwords_v2.json'
last_passwords = []

def load_passwords():
    """Load and decrypt stored passwords from file."""
    global last_passwords
    try:
        with open(passwords_file, 'r') as f:
            encrypted_passwords = json.load(f)
            last_passwords = [decrypt_password(pwd) for pwd in encrypted_passwords]
    except (FileNotFoundError, json.JSONDecodeError):
        last_passwords = []

def save_passwords():
    """Encrypt and save passwords to file."""
    with open(passwords_file, 'w') as f:
        encrypted_passwords = [encrypt_password(pwd) for pwd in last_passwords]
        json.dump(encrypted_passwords, f, indent=4)

def import_passwords(file_path):
    """Import passwords from a text file."""
    global last_passwords
    try:
        with open(file_path, 'r') as file:
            for line in file:
                passwords = line.strip().split()
                last_passwords.extend(passwords)
        save_passwords()
        print(f"Successfully imported passwords from '{file_path}'.")
    except Exception as e:
        print(f"Error importing passwords: {e}")

def clear_screen():
    """Clear the console screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def get_random_word():
    """Fetch a random word from an API."""
    try:
        response = requests.get("https://random-word-api.herokuapp.com/word")
        return response.json()[0]
    except:
        return "randomword"

def replace_with_number(word):
    """Replace letters with numbers for a stronger password."""
    replacements = {'o': '0', 'l': '1', 'e': '3', 'a': '4', 's': '$'}
    return ''.join(replacements.get(char.lower(), char) for char in word)

def capitalize_random(word):
    """Randomly capitalize letters in a word."""
    word = list(word)
    for _ in range(len(word) // 2):
        idx = random.randint(0, len(word) - 1)
        word[idx] = word[idx].upper()
    return ''.join(word)

def generate_customizable_password(length, include_numbers=True, include_symbols=False, random_capitalization=True):
    """Generate a customizable password."""
    keyword = get_random_word()[:length]

    if include_numbers:
        keyword = replace_with_number(keyword)

    if random_capitalization:
        keyword = capitalize_random(keyword)

    extra_chars = ""
    if include_numbers:
        extra_chars += ''.join(random.choice(string.digits) for _ in range(4))
    if include_symbols:
        extra_chars += ''.join(random.choice(string.punctuation) for _ in range(2))

    password = keyword + extra_chars
    last_passwords.append(password)
    save_passwords()
    return password

def generate_impossible_password():
    """Generate a very strong password."""
    password = ''.join(random.choice(string.ascii_letters + string.digits + string.punctuation) for _ in range(30))
    last_passwords.append(password)
    save_passwords()
    return password

def export_passwords_json(file_path):
    """Export decrypted passwords to JSON file."""
    if not last_passwords:
        print("No passwords to export.")
        return

    base_file_path = file_path
    counter = 1
    while os.path.exists(file_path):
        file_path = f"{base_file_path[:-5]}_{counter}.json"
        counter += 1

    try:
        with open(file_path, 'w') as file:
            json.dump(last_passwords, file, indent=4)
        print(f"Exported passwords to '{file_path}'.")
    except Exception as e:
        print(f"Error exporting passwords: {e}")

def export_passwords_raw(file_path):
    """Export passwords as raw text."""
    try:
        with open(file_path, 'w') as file:
            file.writelines(f"{pwd}\n" for pwd in last_passwords)
        print(f"Exported passwords to '{file_path}'.")
    except Exception as e:
        print(f"Error exporting passwords: {e}")

def main():
    """Main function to run the password generator."""
    load_passwords()
    print("Welcome to the Password Generator!")
    
    while True:
        clear_screen()
        print(" COPYRIGHT - VOIDIC STUDIOS\n")
        print("1. Generate Custom Password")
        print("2. Generate Impossible Password")
        print("3. Show Last Password" if last_passwords else "")
        print("4. View All Saved Passwords")
        print("5. Import Passwords from File")
        print("6. Export Passwords as JSON")
        print("7. Export Passwords as Raw Text")
        print("8. Exit")

        option = input("\nEnter your choice: ")

        if option == '1':
            length = int(input("Password length: "))
            include_numbers = input("Include numbers? (y/n): ").lower() == 'y'
            include_symbols = input("Include symbols? (y/n): ").lower() == 'y'
            random_capitalization = input("Random capitalization? (y/n): ").lower() == 'y'
            password = generate_customizable_password(length, include_numbers, include_symbols, random_capitalization)
            print("Generated password:", password)

        elif option == '2':
            print("Generated impossible password:", generate_impossible_password())

        elif option == '3' and last_passwords:
            print("Last generated password:", last_passwords[-1])

        elif option == '4':
            print("\nAll saved passwords:")
            for idx, pwd in enumerate(last_passwords, start=1):
                print(f"{idx}. {pwd}")

        elif option == '5':
            import_passwords(input("Enter file path to import from: "))

        elif option == '6':
            export_passwords_json("passwords_export.json")

        elif option == '7':
            export_passwords_raw("passwords_export.txt")

        elif option == '8':
            print("Exiting...")
            break

        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
