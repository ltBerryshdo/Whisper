from mcdreforged.api.all import *

import os
import json

Groups = {}         #{'lightberryshdo': {'lightberryshdo', 'myfriend', 'otherplayer'}}, The players can receive your message.
Trigger = '**'      #trigger strings
ItemName = 'MCDRwhisper'

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
    cmdTree.command('!!whisper <player>', lambda src, ctx: add_player(server, getPlayerName(src), ctx['player']))
    cmdTree.command('!!whisper list', lambda src: list_group(server, getPlayerName(src)))
    cmdTree.command('!!whisper clear', lambda src: del_group(server, getPlayerName(src)))
    cmdTree.command('!!whisper delmum <player>', lambda src, ctx: del_player(server, getPlayerName(src), ctx['player']))
    cmdTree.command('!!whisper cp <name>', lambda src, ctx: copy(server, getPlayerName(src), ctx['name']))

    cmdTree.arg('name', Text)
    cmdTree.arg('player', GreedyText)

    cmdTree.register(server)

def on_user_info(server: PluginServerInterface, info: Info):
    if info.content == Trigger:
        info.cancel_send_to_server()
        '''if info.player not in Groups[info.player]:
            server.reply(info, RText(translate(server, 'whisper.error.playerNotInGroups'), RColor.red))
            return'''
        send_msg(server, info.player)

def on_unload(server: PluginServerInterface):
    with open(os.path.join(server.get_data_folder(), 'save.json'), 'w', encoding='utf-8') as saveFl:
        keys = list(Groups.keys())
        for i in range(len(keys)):
            groups = list(Groups[keys[i]])
            Groups[keys[i]] = groups
        save = {'save': Groups, 'trigger': Trigger}
        json.dump(save, saveFl, ensure_ascii=False, indent=4)

@new_thread('getCharInBook')
def send_msg(server: PluginServerInterface, player: str):
    api = server.get_plugin_instance('minecraft_data_api')

    slot_numbers = [0, 1, 2, 3, 4, 5, 6, 7, 8] #https://minecraft.fandom.com/zh/wiki/Player.dat%E6%A0%BC%E5%BC%8F?file=Items_slot_number.png
    slot: int
    for i in slot_numbers:
        data_path = 'Inventory['+ str(i) +'].id'
        item_id = api.get_player_info(player, data_path)
        if item_id == 'minecraft:writable_book':
            data_path = 'Inventory['+ str(i) +'].tag.display.Name'
            item_name_raw = api.get_player_info(player, data_path)
            item_name = api.convert_minecraft_json(item_name_raw)
            if (item_name != None) and (item_name['text'] == ItemName):
                slot = i
                break
    
    if slot != None:
        data_path = 'Inventory['+ str(slot) +'].tag.pages'
        message = api.get_player_info(player, data_path)

        msg = RText(translate(server, 'whisper.info.whisper', RText(player, RColor.green)), RColor.gold) + str(message[0])
        for i in range(len(Groups[player])):
            players = list(Groups[player])
            server.tell(players[i], msg)
        
        #clear data_path = 'data get entity lightberryshdo Inventory[0].tag.pages'


def translate(server: PluginServerInterface, key: str, *args, **kwargs) -> RTextMCDRTranslation:
    return server.rtr(key, *args, **kwargs)

def getPlayerName(source: CommandSource) -> str:
    if isinstance(source, PlayerCommandSource):
        return source.player


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
