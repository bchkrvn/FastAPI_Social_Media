import asyncio
import cmd

from application.cli.activate_admin import activate_admin
from application.cli.block_admin import block_admin
from application.cli.create_admin import AdminCreator
from application.cli.get_admins import get_admins


class MyCLI(cmd.Cmd):
    prompt = ">> "
    intro = "Cli-команды для приложения блога\nДля получения списка команд введите help"
    doc_header = "Список доступных команд (help <topic> для подробной информации)"

    def do_create_admin(self, line):
        """
        Создание администратора системы
        """
        self._async_to_sync(AdminCreator().create())

    def do_get_admins(self, line):
        """
        Получить список администраторов системы
        """
        self._async_to_sync(get_admins())

    def do_block_admin(self, line):
        """
        Блокировка администратора системы
        """
        self._async_to_sync(block_admin())

    def do_activate_admin(self, line):
        """
        Разблокировка администратора системы
        """
        self._async_to_sync(activate_admin())

    def _async_to_sync(self, coro):
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(coro)
        return result

    def do_quit(self, line):
        """Выход из приложения"""
        print("Выход из приложения")
        return True

    def postcmd(self, stop, line):
        print()
        return stop

    def default(self, line):
        print("Неизвестная команда. Для получения списка команд введите help")

    def do_help(self, arg):
        """
        Получить список доступных команд
        """
        print("Список доступных команд:\n")
        names = [n for n in self.get_names() if n.startswith("do_")]
        for n in names:
            doc = getattr(self, f"{n}").__doc__
            print(f"* {n[3:]} - {doc}")
