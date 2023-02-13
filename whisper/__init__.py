from mcdreforged.api.all import *

import os
import json

Groups = {}         #{'lightberryshdo': {'lightberryshdo', 'myfriend', 'theotherplayer'}}, The players can receive your msg.
Trigger = '**'      #trigger strings

def on_load(server: PluginServerInterface, prev_module):
    global Groups
    global Trigger
    with open(os.path.join(server.get_data_folder(), 'save.json'), 'r', encoding='utf-8') as saveFl:
        save = json.load(saveFl)
        keys = list(save['save'].keys())
        for i in range(len(keys)):
            groups = set(save['save'][keys[i]])
            save['save'][keys[i]] = groups
        Groups = save['save']
        Trigger = save['trigger']

    server.register_help_message('!!whisper', server.rtr('whisper.help_message'), permission = 1)
    cmdTree = SimpleCommandBuilder()

    cmdTree.command('!!whisper', lambda src: src.reply(translate(server, 'whisper.cmd.help', Trigger)))
    cmdTree.command('!!whisper <player>', lambda src, ctx: add_player(server, getPlayerName(src.is_player, src.player), ctx['player']))
    cmdTree.command('!!whisper list', lambda src: list_group(server, getPlayerName(src.is_player, src.player)))
    cmdTree.command('!!whisper clear', lambda src: del_group(server, getPlayerName(src.is_player, src.player)))
    cmdTree.command('!!whisper delmum <player>', lambda src, ctx: del_player(server, getPlayerName(src.is_player, src.player), ctx['player']))
    cmdTree.command('!!whisper cp <name>', lambda src, ctx: copy(server, getPlayerName(src.is_player, src.player), ctx['name']))

    cmdTree.arg('name', Text)
    cmdTree.arg('player', GreedyText)

    cmdTree.register(server)

def on_user_info(server: PluginServerInterface, info: Info):
    global Groups
    global Trigger
    if info.content.startswith(Trigger):
        info.cancel_send_to_server()
        '''if info.player not in Groups[info.player]:
            server.reply(info, RText(translate(server, 'whisper.error.playerNotInGroups'), RColor.red))
            return'''
        msg = RText(translate(server, 'whisper.info.whisper', RText(info.player, RColor.green)), RColor.gold) + info.content[len(Trigger):]
        for i in range(len(Groups[info.player])):
            player = list(Groups[info.player])
            server.tell(player[i], msg)

def on_unload(server: PluginServerInterface):
    with open(os.path.join(server.get_data_folder(), 'save.json'), 'w', encoding='utf-8') as saveFl:
        keys = list(Groups.keys())
        for i in range(len(keys)):
            groups = list(Groups[keys[i]])
            Groups[keys[i]] = groups
        save = {'save': Groups, 'trigger': Trigger}
        json.dump(save, saveFl, ensure_ascii=False, indent=4)


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

def copy(server: PluginServerInterface, player: str, targetPlayer: str):
    global Groups
    players = Groups[targetPlayer]
    Groups[player].update(list(players))
    server.tell(player, RText(translate(server, 'whisper.info.copy'), RColor.gray))
