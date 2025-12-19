from dataclasses import dataclass


@dataclass
class AuthModel:
    id: str
    token: str
