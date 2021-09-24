import jwt


def encode(
    exp, payload: dict, secret_key
) -> str:
    payload['exp'] = exp
    token = jwt.encode(
        payload, secret_key, algorithm='HS256'
    ).decode("utf-8")
    return token


def decode(
    token: str, secret_key
) -> dict:
    return jwt.decode(token, secret_key)
