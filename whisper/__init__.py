#https://minecraft.fandom.com/zh/wiki/%E5%91%BD%E4%BB%A4/tell
#https://minecraft.fandom.com/zh/wiki/%E5%91%BD%E4%BB%A4/team
#https://minecraft.fandom.com/zh/wiki/%E5%91%BD%E4%BB%A4/tellraw
from mcdreforged.api.all import *

CmdTree = {                 #command tree structure
    'cmd': '!!whisper',
    'then': ['list', 'del', 'delmum']
}

Groups = []                 #all the groups
Trigger = {'default': '!!w'}

def on_load(server: PluginServerInterface, prev_module):
    server.register_help_message('!!whisper', server.rtr('whisper.help_message'), permission = 1)

def on_user_info(server: PluginServerInterface, info: Info):            #processed command & trigger strings
    global CmdTree
    global Groups
    global Trigger

    if info.content.startswith(CmdTree['cmd']):
        info.cancel_send_to_server()
        ctx = info.content.split(' ', 2)[1]
        sth = info.content.split(' ', 2)[2].split()

        if info.content == CmdTree['cmd']:
            server.reply(info, RText(translate(server, 'whisper.cmd.help')))

        elif ctx in CmdTree['then']:
            if ctx == CmdTree['then'][0]:
                list_groups(server, info)

            if ctx == CmdTree['then'][1]:
                del_groups(server, info, sth)

            if ctx == CmdTree['then'][2]:
                del_player(server, info, sth)
        else:
            add_player(server, info, ctx, sth)
        
    if info.content.startswith(Trigger['default']):
        info.cancel_send_to_server()
        grp = 'MCDR_whisper_' + info.player + '_' + info.content.split(' ', 2)[1]
        if grp not in Groups:
            return
        server.execute('execute as ' + info.player + ' at ' + info.player + ' run tell ' + grp + ' ' + info.content.split(' ', 2)[2])

def on_player_left(server: PluginServerInterface, name: str):
    global Groups

    for i in range(len(Groups)):
        if Groups[i].split('_')[1] == name:
            server.execute('team remove ' + Groups[i])
            del Groups[i]


def translate(server: PluginServerInterface, key: str, *args, **kwargs) -> RTextMCDRTranslation:
    return server.rtr(key, *args, **kwargs)


def add_player(server: PluginServerInterface, info: Info, group: str, nameList: list):
    global Groups
    grp = 'MCDR_whisper_' + info.player + '_' + group
    if grp not in Groups:
        Groups.append(grp)
        server.execute('team add ' + grp)                                           #/team add
        server.execute('team join ' + grp + ' ' + info.player)

    for i in range(len(nameList)):
        server.execute('team join ' + grp + ' ' + nameList[i])                      #/team join

def del_player(server: PluginServerInterface, info: Info, nameList: list):
    for i in range(len(nameList)):
        server.execute('team leave ' + nameList[i])                                 #/team leave

def list_groups(server: PluginServerInterface, info: Info):
    global Groups

    for i in range(len(Groups)):
        if Groups[i].split('_')[1] == info.player:
            server.execute('team list ' + Groups[i])                                #/team list

def del_groups(server: PluginServerInterface, info: Info, group: list):
    global Groups

    for i in range(len(group)):
        Groups.remove('MCDR_whisper_' + info.player + '_' + group[i])
        server.execute('team remove ' + 'MCDR_whisper_' + info.player + '_' + group[i]) #/team remove
