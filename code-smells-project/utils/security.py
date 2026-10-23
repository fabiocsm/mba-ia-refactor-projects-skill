from werkzeug.security import check_password_hash, generate_password_hash


def hash_password(senha):
    return generate_password_hash(senha)


def verify_password(senha, senha_hash):
    return check_password_hash(senha_hash, senha)
