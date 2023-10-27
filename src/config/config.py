from pydantic import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Arcade API"
    secret_key: str
    jwt_algorithm: str
    access_token_expire_minutes: int
    development: bool
    production: bool
    auth_server_url: str
    route_prefix: str


    class Config:
        env_file = "src/config/.env"

settings = Settings()