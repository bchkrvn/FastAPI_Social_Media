from application.user.dao import UserDAO


async def block_admin():
    while True:
        email = input("Введите email администратора, которого нужно заблокировать: ")
        filters = {
            "email": email,
            "is_admin": True,
        }
        admin = await UserDAO.find_one_or_none(filters=filters)

        if not admin:
            print(f"Администратор с почтой {email} не найден")
            continue

        if not admin.is_active:
            print(f"Администратор с почтой {email} уже заблокирован")
            continue

        admin.is_active = False
        await UserDAO.update(admin)

        print(f"Администратор с почтой {email} успешно заблокирован")
        break
