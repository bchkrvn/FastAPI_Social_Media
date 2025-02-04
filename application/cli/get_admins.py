from application.user.dao import UserDAO


async def get_admins():
    active_admins = await UserDAO.find_all(filters=dict(is_admin=True, is_active=True))
    not_active_admins = await UserDAO.find_all(filters=dict(is_admin=True, is_active=False))
    template = "ID={a.id}, {a.first_name} {a.last_name}, {a.email}"

    print("Список активных администраторов системы:")
    for a in active_admins:
        print(template.format(a=a))

    print("\nСписок заблокированных администраторов системы:")
    for a in not_active_admins:
        print(template.format(a=a))
