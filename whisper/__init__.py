from mcdreforged.api.all import *

Groups = {}         #{'lightberryshdo': {'lightberryshdo', 'myfriend', 'theotherplayer'}}, The players can receive your msg.
Trigger = '**'      #trigger strings

def on_load(server: PluginServerInterface, prev_module):
    server.register_help_message('!!whisper', server.rtr('whisper.help_message'), permission = 1)
    cmdTree = SimpleCommandBuilder()

    cmdTree.command('!!whisper', lambda src: src.reply(RText(translate(server, 'whisper.cmd.help'), RColor.gray)))
    cmdTree.command('!!whisper <player>', lambda src, ctx: add_player(server, getPlayerName(src.is_player, src.player), ctx['player']))
    cmdTree.command('!!whisper list', lambda src: list_group(server, getPlayerName(src.is_player, src.player)))
    cmdTree.command('!!whisper clear', lambda src: del_group(server, getPlayerName(src.is_player, src.player)))
    cmdTree.command('!!whisper delmum <player>', lambda src, ctx: del_player(server, getPlayerName(src.is_player, src.player), ctx['player']))

    cmdTree.arg('player', GreedyText)

    cmdTree.register(server)

def on_user_info(server: PluginServerInterface, info: Info):
    global Groups
    global Trigger
    if info.content.startswith(Trigger):
        info.cancel_send_to_server()
        if info.player not in Groups[info.player]:
            server.reply(info, RText(translate(server, 'whisper.error.playerNotInGroups'), RColor.red))
            return
        msg = RText(translate(server, 'whisper.info.whisper', RText(info.player, RColor.green)), RColor.gold) + info.content[len(Trigger):]
        for i in range(len(Groups[info.player])):
            player = list(Groups[info.player])
            server.tell(player[i], msg)


def translate(server: PluginServerInterface, key: str, *args, **kwargs) -> RTextMCDRTranslation:
    return server.rtr(key, *args, **kwargs)

def getPlayerName(player: bool, playerName: str) -> str:
    if player:
        return playerName


def add_player(server: PluginServerInterface, player: str, names: str):
    global Groups
    if player not in Groups.keys():
        Groups.update({player: {player,}})
    nameList = names.split()
    Groups[player].update(nameList)
    server.tell(player, RText(translate(server, 'whisper.info.add', nameList), RColor.gray))

def del_player(server: PluginServerInterface, player: str, names: str):
    global Groups
    nameList = names.split()
    for i in range(len(nameList)):
        Groups[player].remove(nameList[i])
    server.tell(player, RText(translate(server, 'whisper.info.del', nameList), RColor.gray))

def list_group(server: PluginServerInterface, player: str):
    global Groups
    msg = list(Groups[player])
    server.tell(player, RText(translate(server, 'whisper.info.group'), RColor.blue))
    for i in range(len(msg)):
        server.tell(player, RText(msg[i], RColor.gray))

def del_group(server: PluginServerInterface, player: str):
    global Groups
    del Groups[player]
    server.tell(player, RText(translate(server, 'whisper.info.del_group'), RColor.gray))
