from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    model_config = SettingsConfigDict(
        # SettingsConfigDict: é um objeto do pydantic-settings que carrega as variáveis em um arquivo de configuração. Por exemplo, um .env.
        env_file='.env', env_file_encoding='utf-8'
        # Aqui definimos o caminho para o arquivo de configuração e o encoding dele.
    )

    DATABASE_URL: str
    # DATABASE_URL: Essa variável sera preenchida com o valor encontrado com o mesmo nome no arquivo .env.
