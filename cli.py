from pathlib import Path

from dotenv import load_dotenv

from application.cli.base import MyCLI
from application.config import settings

if __name__ == "__main__":
    env_path = Path(".") / ".env"
    load_dotenv(dotenv_path=env_path)

    try:
        MyCLI().cmdloop()
    except Exception as e:
        if settings.DEBUG:
            raise e
        else:
            print("Приложение завершилось с ошибкой")
