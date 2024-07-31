import datetime
import os
import pathlib
import shutil
import subprocess

import discord

import data_import
import functional
import static
from discord.ext import commands, tasks

import token
from Server import Server

intents = discord.Intents().all()
bot = commands.Bot(command_prefix='>', intents=intents)

users = {}

rename_all_bool = True

Servers_pool = []
try:
    for server in data_import.import_data("servers", ";"):
        Servers_pool.append(Server(server[0], int(server[1])))
except:
    pass


@bot.command()
async def rename_all(ctx, *args):
    await ctx.send(static.emoji__poshalko * 5)
    guild = bot.get_guild(1130566885382029472)
    for member in guild.members:
        if member.id in [968115196327518289, 715148417789198398, 1172551712456847490]:
            continue
        print(f"Renaming {member.global_name} to {users[member.id]}")
        await member.edit(nick=users[member.id])


@bot.command()
async def rename_switch(ctx):
    global rename_all_bool
    rename_all_bool = not rename_all_bool

@bot.command()
async def reset_nicks(ctx):
    guild = bot.get_guild(1130566885382029472)
    for member in guild.members:
        if member.id in [968115196327518289, 715148417789198398, 1172551712456847490]:
            continue
        print(f"Resetting {member.global_name} ({member.name})...")
        await member.edit(nick=None)
    print("Done. ")


@bot.command()
async def get_emoji_ids(ctx, *args):
    i = 1
    emojis = []
    for emoji in args:
        emojis.append(emoji.split(":")[2].replace(">", ""))
        i += 1

    for i in range(len(emojis)):
        await ctx.send(f"{args[i]}: \\{args[i]}")


@bot.command()
async def start(ctx, server_name):
    current_server = functional.get_server_by_name(server_name, Servers_pool)
    if current_server is not None:
        await ctx.send(f"Запускается `{server_name}`... " + static.emoji__like)
        result = current_server.start()
        if result == "running":
            await ctx.send("Сервер и так запущен " + static.emoji__che)
            return
        elif result == "started":
            await ctx.send(f"`{server_name}` запущен! " + static.emoji__dogovorilis)
        else:
            await ctx.send(f"`Ошибка запуска сервера. <@968115196327518289>`")
    else:
        await ctx.send(f"Сервер с таким именем не найден! " + static.emoji__porposche)


@bot.command()
async def stop(ctx, server_name):
    if functional.role(ctx.author.roles, static.bot_adm_role_id):
        current_server = functional.get_server_by_name(server_name, Servers_pool)
        if current_server is None:
            await ctx.send(f"Сервер с таким именем не найден! " + static.emoji__porposche)
        else:
            result = current_server.stop()
            if result == "already_stopped":
                await ctx.send(f"`{server_name}` и так остановлен! " + static.emoji__laugh)
                return
            elif result == "stopped":
                await ctx.send(f"`{server_name}` остановлен! " + static.emoji__za_compom)
            else:
                await ctx.send(f"`Ошибка запуска сервера. <@968115196327518289>`")
    else:
        await ctx.send(f"{static.emoji__poshalko}")


@bot.command()
async def rename_db(ctx):
    guild = bot.get_guild(1130566885382029472)
    i = 1
    for member in guild.members:
        if member.id in [968115196327518289, 715148417789198398, 1172551712456847490]:
            continue
        users[member.id] = "OGUZOK #" + str(i)
        i += 1


@bot.command()
async def set_property(ctx, *args):
    for role in ctx.author.roles:
        if role.id == static.bot_adm_role_id:
            try:
                current_server = functional.get_server_by_name(args[0], Servers_pool)
                if current_server.check_running():
                    await ctx.send("Сначала остановите сервер! " + static.emoji__laugh)
                    return
                if current_server.set_property(args[1], args[2]):
                    await ctx.send(f"Серверу `{args[0]}` было присвоено: `{args[1]}={args[2]}`")
                else:
                    await ctx.send(f"`{args[1]}` не найдено! ")
            except IndexError:
                await ctx.send("Неверно заданы параметры. ")
            return
    await ctx.send(f"{static.emoji__poshalko}")


@bot.command()
async def exec_server(ctx, *args):
    for role in ctx.author.roles:
        if role.id == static.bot_adm_role_id:
            try:
                current_server = functional.get_server_by_name(args[0], Servers_pool)
                cmd = ' '.join(args[1:])
                result = current_server.exec(cmd)
                if result.returncode == 1:
                    await ctx.send('Выполнено `' + cmd + '`: `' +
                                   str(result.stdout).replace("b'", "")
                                   .replace(" \\r\\n'", "") + '`')
                else:
                    await ctx.send('Ошибка выполнения `' + cmd + '`: `' +
                                   str(result.stderr).replace("b'", "")
                                   .replace(" \\r\\n'", "") + '`')
            except IndexError:
                await ctx.send("Неверно заданы параметры. ")
            return
    await ctx.send(f"{static.emoji__poshalko}")


@bot.command()
async def create_new_server(ctx, *args):
    if len(args) != 5:
        await ctx.send("Неверно заданы параметры. ")
        return
    for role in ctx.author.roles:
        if role.id == static.bot_adm_role_id:
            if functional.get_server_by_name(args[0], Servers_pool) is not None:
                await ctx.send(f"Сервер с именем `{args[0]}` уже существует! ")
                return
            path = args[1]
            try:
                if len(os.listdir(path)) != 0:
                    await ctx.send("Папка с сервером не пуста. ")
                    return
            except FileNotFoundError:
                pass
            try:
                pathlib.Path(path).mkdir(parents=True)
            except FileExistsError:
                pass
            if not args[2].isdigit():
                await ctx.send("Неверный порт. ")
                return
            if not args[3].isdigit():
                await ctx.send("Неверный порт RCON. ")
                return
            if not args[4].isdigit():
                await ctx.send("Неверное кол-во памяти. ")
                return

            await ctx.send(f"Создается: `{args[0]}`")

            shutil.copy(static.server_path, f"{path}\\server.jar")
            proc = subprocess.Popen(f"java -Xmx{args[4]}G -jar server.jar nogui",
                                    shell=True, cwd=path)
            proc.wait()
            os.remove(f"{path}\\eula.txt")
            open(f"{path}\\eula.txt", "w").write("eula=true")

            open(f"{path}\\xmx", "x").close()
            open(f"{path}\\name", "x").close()
            open(f"{path}\\rcon-port", "x").close()
            open(f"{path}\\xmx", "w").write(args[4])
            open(f"{path}\\name", "w").write(args[0])
            open(f"{path}\\rcon-port", "w").write(args[3])

            created_server = Server(path, args[2])
            Servers_pool.append(created_server)

            created_server.set_property("enable-rcon", "true")
            created_server.set_property("server-port", args[2])
            created_server.set_property("rcon.port", args[3])
            created_server.set_property("rcon.password", "1111")

            open("servers", "a").write(f"{created_server.location};{created_server.port}\n")

            await ctx.send("Сервер создан! " + static.emoji__like)
            return

    await ctx.send(f"{static.emoji__poshalko}")


@bot.command()
async def tag(ctx):
    await ctx.send("<@968115196327518289>")


@bot.command()
async def list_servers(ctx):
    msg = ""
    i = 1
    for server_i in Servers_pool:
        msg += f"{i}: `{server_i.get_name()}`, `port={server_i.port}`\n"
        i += 1
    if msg == "":
        msg = "Пусто! " + static.emoji__podveshen
    await ctx.send(msg)


@bot.command()
async def status(ctx, server_name):
    current_server = functional.get_server_by_name(server_name, Servers_pool)
    if current_server is not None:
        msg = ""
        msg += f"Имя сервера:\t`{server_name}`\n"
        msg += f"Статус сервера:\t`{'Онлайн!' if current_server.check_running() else 'Оффлайн'}`\n"
        msg += f"Игроки:\t`{'-' if (not current_server.check_running() or current_server.get_online_players() == '') else current_server.get_online_players()}`\n"
        msg += f"connect:\t`26.19.145.4:{current_server.port}`\n"

        await ctx.send(msg)
    else:
        await ctx.send(f"Сервер с таким именем не найден! " + static.emoji__porposche)


@bot.command()
async def remove_server(ctx, server_name):
    current_server = functional.get_server_by_name(server_name, Servers_pool)
    if current_server.check_running():
        await ctx.send("Сервер запущен! ")
        return
    if current_server is not None:
        await ctx.send("Ожидание подтверждения... ")
        await tag(ctx)
        if ctx.author.id == static.my_id or input("Удалить сервер? ") in ["Y", 'y', "yes", "Yes", "Д", "д", "Да", "д"]:
            try:
                shutil.rmtree(current_server.location)
            except PermissionError:
                await ctx.send("Ошибка прав доступа к файлам")
                await tag(ctx)
            buffer = []
            for line in data_import.import_data("servers", ";"):
                buffer.append(line)
            for line in buffer:
                if line[0] == current_server.location:
                    buffer.remove(line)
            data_import.export_data("servers", buffer)
            await ctx.send("Сервер удален! " + static.emoji__dislike)
        else:
            await ctx.send("Удаление запрещено " + static.emoji__poshalko)
            await ctx.author.timeout(datetime.timedelta(minutes=5))

    else:
        await ctx.send(f"Сервер с таким именем не найден! " + static.emoji__porposche)


@bot.command()
async def info(ctx):
    msg = ""
    msg += "## Команды бота\n"
    msg += "### команды (ADM) требуют роли BotAdm\n"
    msg += "### все команды начинаются с '>'\n"

    msg += "`start [имя сервера]`:\tзапускает сервер с заданным именем\n"
    msg += "`stop [имя сервера]`:\tостанавливает сервер с заданным именем\n"
    msg += "`list_servers`:\tвыводит список серверов, зарегистрированных в боте\n"
    msg += "`status [имя сервера]`:\tвыводит информацию о сервере\n"
    msg += "`remove_server [имя сервера]`:\tудаляет сервер\n"
    msg += "`info`:\tвыводит это сообщение\n"
    msg += "`(ADM) set_property [имя сервера] [переменная] [значение]`:\tзадаёт значение в server.properties\n"
    msg += "Например:\t>set_property main difficulty hard\n"
    msg += "`(ADM) exec_server [имя сервера] [команда]`:\tвыполняет на сервере команду\n"
    msg += "Например:\t>exec_server main kick Fydzzziama\n"
    msg += ("`(ADM) create_new_server "
            "[имя сервера] [путь на диске] [порт сервера] [порт RCON] [кол-во памяти в Гб]`:\tсоздает новый сервер\n")
    msg += static.emoji__poshalko

    await ctx.send(msg)


@bot.event
async def on_voice_state_update(member, before, after):
    guild = bot.get_guild(1130566885382029472)


async def do_stuff():
    await rename_db(None)
    print("Oguzkov total: " + str(len(users)))


@bot.command()
async def my_command(ctx):
    await do_stuff()


@bot.event
async def on_ready():
    await do_stuff()


@bot.event
async def on_member_update(before, after):
    global rename_all_bool
    print(f"{before.nick} => {after.nick}")
    if after.nick is None or not after.nick.startswith("OGUZOK"):
        if not rename_all_bool:
            return
        await (bot.get_guild(1130566885382029472).get_channel(1130566886317367299)
               .send(f"<@{before.id}> ахуел! Ты не {after.nick}, ты {users[before.id]}! "))
        await before.edit(nick=users[after.id])


bot.run(token.bot_token)

# `
