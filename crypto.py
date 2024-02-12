import json
from jwcrypto import jwk, jwe


def convert_dict_to_json_str(data: dict) -> str:
    return json.dumps(data)


def convert_dict_to_json_bytes(data: dict) -> bytes:
    return convert_dict_to_json_str(data).encode("utf-8")


def encrypt_bytes_with_key(payload: bytes, public_key: dict):
    # reading key
    public_key = jwk.JWK(**public_key)

    # encrypting
    protected_header = {
        "alg": "RSA-OAEP-256",
        "enc": "A256GCM",
        "typ": "JWE",
        "kid": public_key.thumbprint(),
        "zip": "DEF",
        "cty": "application/json"
    }

    jwe_token = jwe.JWE(payload, recipient=public_key, protected=protected_header)
    return jwe_token.serialize(compact=True)


def encrypt_dict_with_key(payload: dict, key: dict):
    return encrypt_bytes_with_key(convert_dict_to_json_bytes(payload), key)
