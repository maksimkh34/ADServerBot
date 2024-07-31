import datetime
import subprocess

import static
from Server import Server
from datetime import datetime


def exec_rcon(server: Server, cmd: str):
    return subprocess.run(f"X:\\rcon\\mcrcon.exe -p {server.rcon_password} -H 26.19.145.4 -P "
                          f"{server.get_rcon_port()} \"{cmd}\"", capture_output=True)


def get_server_by_name(name: str, pool: []) -> Server:
    for server in pool:
        if server.get_name() == name:
            return server


# def backup_if_needed(server: Server):
#     latest = server.get_latest_backup()
#     if not ((latest.split("-")[2] == datetime.today().strftime(static.date_format) and
#              datetime.timedelta(hours=latest.split("-")[3].split(".")[0], minutes=latest.split("-")[3].split(".")[1]) -
#              datetime.timedelta(hours=datetime.today().hours, minutes=datetime.today().minutes)
#              < datetime.timedelta(hours=1))):
#         pass  # backup


def restore(server: Server, backup_name: str):
    pass


def role(user_roles: [], role_id: int) -> bool:
    for _role in user_roles:
        if _role.id == role_id:
            return True
    return False
