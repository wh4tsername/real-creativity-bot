import os


def get_token():
    token_path = os.environ.get('TOKEN')
    if token_path is None:
        print("No token provided")
        exit(123)

    with open(token_path, 'r') as f:
        return f.read().strip()
