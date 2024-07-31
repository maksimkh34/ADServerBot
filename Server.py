import os.path
import subprocess
import time
import glob

import functional


class Server:
    port: int
    location = ''
    rcon_password = 1111
    ram = 2

    def __init__(self, location, port=25565):
        self.location = location
        self.port = port
        self.ram = int(open(f"{location}\\xmx").read())

    def start(self):
        if self.check_running():
            return "running"
        else:
            subprocess.Popen(f"javaw -Xmx{self.ram}G -jar server.jar nogui",
                             cwd=self.location, start_new_session=True)
            while not self.check_running():
                time.sleep(5)
            return "started"

    def stop(self):
        if self.check_running():
            functional.exec_rcon(self, "stop")
            while self.check_running():
                time.sleep(1)
                # functional.backup_if_needed(self)
            return "stopped"
        else:
            return "already_stopped"

    def check_running(self) -> bool:
        return functional.exec_rcon(self, "list").returncode == 1

    def exec(self, cmd: str):
        return functional.exec_rcon(self, cmd)

    def get_online_players(self):
        if not self.check_running():
            return ""
        return str(functional.exec_rcon(self, "list").stdout).split(":")[1].replace("\\r\\n'", "")

    # def get_latest_backup(self):
    #     if not os.path.isdir(f"{self.location}\\backups") or len(os.listdir(f"{self.location}\\backups")) == 0:
    #         try:
    #             os.mkdir(f"{self.location}\\backups")
    #         except FileExistsError:
    #             pass
    #         return None
    #     return max(glob.glob(f"{self.location}\\backups\\*.zip"), key=os.path.getctime)

    def set_property(self, pref_property, pref_value):
        buffer = open(f"{self.location}\\server.properties", "r").readlines()
        new_buffer = ""
        found = False
        for line in buffer:
            if line.split("=")[0] == pref_property:
                line = line.split("=")[0] + "=" + pref_value + "\n"
                new_buffer += line
                found = True
            else:
                new_buffer += line
        open(f"{self.location}\\server.properties", "w").write(new_buffer)
        return found

    def get_name(self):
        return open(f"{self.location}\\name", "r").read()

    def get_rcon_port(self):
        return open(f"{self.location}\\rcon-port", "r").read()
