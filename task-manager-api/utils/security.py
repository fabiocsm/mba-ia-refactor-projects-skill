from werkzeug.security import check_password_hash, generate_password_hash


def hash_password(raw_password):
    return generate_password_hash(raw_password)


def verify_password(raw_password, stored_hash):
    return check_password_hash(stored_hash, raw_password)
