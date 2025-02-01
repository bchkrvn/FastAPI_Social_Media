import asyncio
import cmd

from application.cli.create_admin import AdminCreator


class MyCLI(cmd.Cmd):
    prompt = ">> "
    intro = "Cli-команды для приложения блога\nДля получения списка команд введите help"
    doc_header = "Список доступных команд (help <topic> для подробной информации)"

    def do_create_admin(self, line):
        """
        Создание администратора системы
        """
        asyncio.run(AdminCreator().create())

    def do_quit(self, line):
        """Выход из приложения"""
        print("Выход из приложения")
        return True

    def postcmd(self, stop, line):
        print()
        return stop
