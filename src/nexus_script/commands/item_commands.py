from ...core.command import Command, CommandResult
from ...core.exceptions import CommandError

class InventoryCommand(Command):
    def __init__(self, player_service):
        super().__init__("inventory", "List items in inventory", "inventory")
        self.player_service = player_service

    def execute(self, player, args, context=None):
        if not player.inventory:
            return CommandResult(True, "Inventory is empty.")

        output = "--- Inventory ---\n"
        for item in player.inventory:
            output += f"[{item.type.name}] {item.name} ({item.rarity.name})\n"
            if hasattr(item, "description"):
                output += f"  {item.description}\n"
        return CommandResult(True, output)

class EquipCommand(Command):
    def __init__(self, player_service):
        super().__init__("equip", "Equip an item", "equip <item_name> <slot>")
        self.player_service = player_service

    def execute(self, player, args, context=None):
        if len(args) < 2:
            return CommandResult(False, "Usage: equip <item_name> <slot>")

        item_name = args[0]
        slot = args[1]

        # Find item by name (simple lookup)
        item_id = None
        for item in player.inventory:
            if item.name.lower() == item_name.lower():
                item_id = item.id
                break

        if not item_id:
            return CommandResult(False, f"Item '{item_name}' not found in inventory.")

        success, message = self.player_service.equip_item(player, item_id, slot)
        return CommandResult(success, message, animation_type="SUCCESS_UNLOCK" if success else "ERROR_SHAKE")

class UseCommand(Command):
    def __init__(self, player_service):
        super().__init__("use", "Use a consumable item", "use <item_name>")
        self.player_service = player_service

    def execute(self, player, args, context=None):
        if len(args) < 1:
            return CommandResult(False, "Usage: use <item_name>")

        item_name = args[0]
        item_id = None
        for item in player.inventory:
            if item.name.lower() == item_name.lower():
                item_id = item.id
                break

        if not item_id:
            return CommandResult(False, f"Item '{item_name}' not found.")

        success, message = self.player_service.use_item(player, item_id)
        return CommandResult(success, message, animation_type="SUCCESS_UNLOCK" if success else "ERROR_SHAKE")
