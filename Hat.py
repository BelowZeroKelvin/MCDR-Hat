# coding: utf-8
import json

blacklist = [
    'minecraft:leather_chestplate', 'minecraft:leather_leggings', 'minecraft:leather_boots',
    'minecraft:chainmail_chestplate', 'minecraft:chainmail_leggings', 'minecraft:chainmail_boots',
    'minecraft:iron_chestplate', 'minecraft:iron_leggings', 'minecraft:iron_boots',
    'minecraft:diamond_chestplate', 'minecraft:diamond_leggings', 'minecraft:diamond_boots',
    'minecraft:elytra'
]


class Inventory():
    def __init__(self, server, player):
        self.PlayerInfoAPI = server.get_plugin_instance('PlayerInfoAPI')
        self.server = server
        self.player = player

    def get_slot(self, slot):
        info = self.PlayerInfoAPI.getPlayerInfo(
            self.server, self.player, 'Inventory')
        slotinfo = [i for i in info if i['Slot'] == slot]
        if not len(slotinfo):
            return None
        else:
            return self.slot_item_decode(slotinfo[0])

    def selected_slot(self):
        return self.PlayerInfoAPI.getPlayerInfo(self.server, self.player,
                                                'SelectedItemSlot')

    def set_slot(self, slot, item):
        self.server.execute(
            self.pack_repitem(self.player, self.slot_name(slot), item))

    def del_slot(self, slot):
        self.server.execute(
            self.pack_repitem(self.player, self.slot_name(slot),
                              self.item_air()))

    def swap_slot(self, slot1, slot2):
        item1 = self.get_slot(slot1)
        item2 = self.get_slot(slot2)
        if not item1 and not item2:
            return
        elif not item1:
            self.del_slot(slot2)
            self.set_slot(slot1, item2)
        elif not item2:
            self.del_slot(slot1)
            self.set_slot(slot2, item1)
        else:
            self.set_slot(slot2, item1)
            self.set_slot(slot1, item2)

    @staticmethod
    def slot_item_decode(info):
        count = info['Count']
        id = info['id']
        tag = json.dumps(info['tag']) if 'tag' in info else ''
        return {'count': count, 'id': id, 'tag': tag}

    @staticmethod
    def slot_name(slot):
        slots = {a: 'hotbar.' + str(a) for a in range(9)}
        slots1 = {a: 'inventory.' + str(a - 9) for a in range(9, 35)}
        slots2 = {
            100: 'armor.feet',
            101: 'armor.legs',
            102: 'armor.chest',
            103: 'armor.head',
            -106: 'weapon.offhand'
        }
        slots.update(slots1)
        slots.update(slots2)
        return slots[slot]

    @staticmethod
    def pack_repitem(player, slot, item):
        return 'replaceitem entity ' + player + ' ' + slot + ' ' + item[
            'id'] + item['tag'] + ' ' + str(item['count'])

    @staticmethod
    def item_air():
        return {'id': 'minecraft:air', 'count': 1, 'tag': ''}


def on_info(server, info):
    if info.is_player and info.content == '!!hat':
        inventory = Inventory(server, info.player)
        selected = inventory.selected_slot()
        if inventory.get_slot(selected)['id'] in blacklist:
            server.tell(info.player, '§7[Hat]该物品不能戴在头上！')
            return
        inventory.swap_slot(selected, 103)
