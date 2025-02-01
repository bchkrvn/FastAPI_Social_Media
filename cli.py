from pathlib import Path

from dotenv import load_dotenv

from application.cli.base import MyCLI

if __name__ == "__main__":
    env_path = Path(".") / ".env"
    load_dotenv(dotenv_path=env_path)
    try:
        MyCLI().cmdloop()
    except Exception:
        print("Приложение завершилось с ошибкой")
