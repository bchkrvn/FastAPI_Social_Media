from application.user.dao import UserDAO


async def activate_admin():
    while True:
        email = input("Введите email администратора, которого нужно разблокировать: ")
        filters = {
            "email": email,
            "is_admin": True,
        }
        admin = await UserDAO.find_one_or_none(filters=filters)

        if not admin:
            print(f"Администратор с почтой {email} не найден")
            continue

        if admin.is_active:
            print(f"Администратор с почтой {email} уже разблокирован")
            continue

        admin.is_active = True
        await UserDAO.update(admin)

        print(f"Администратор с почтой {email} успешно разблокирован")
        break
