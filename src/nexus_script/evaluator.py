from .ast import (
    Program,
    SetStatement,
    ExpressionStatement,
    Identifier,
    StringLiteral,
    NumberLiteral,
    CallExpression,
    NewExpression,
)
from datetime import datetime, timedelta
from ..upgrade_data import UPGRADE_DATA
import time

class Evaluator:
    def __init__(self, player, themes):
        self.player = player
        self.themes = themes
        self.environment = {}
        self.builtins = {
            "ls": self._ls,
            "cat": self._cat,
            "set-theme": self._set_theme,
            "set-prompt": self._set_prompt,
            "mine-hash": self._mine_hash,
            "status": self._status,
            "shop": self._shop,
            "buy": self._buy,
            "hashcrack": self._hashcrack,
        }

    def eval(self, node):
        if isinstance(node, Program):
            return self.eval_statements(node.statements)
        elif isinstance(node, ExpressionStatement):
            return self.eval(node.expression)
        elif isinstance(node, SetStatement):
            value = self.eval(node.value)
            self.environment[node.name.value] = value
            return value
        elif isinstance(node, Identifier):
            if node.value in self.builtins:
                return self.builtins[node.value]
            return self.environment.get(node.value, None)
        elif isinstance(node, StringLiteral):
            return node.value
        elif isinstance(node, NumberLiteral):
            return node.value
        elif isinstance(node, CallExpression):
            func = self.eval(node.function)
            if not callable(func):
                return f"Error: {node.function.value} is not a function"
            args = [self.eval(arg) for arg in node.arguments]
            return func(args)
        elif isinstance(node, NewExpression):
            # Simplified for now
            return None
        return None

    def eval_statements(self, statements):
        result = None
        for statement in statements:
            result = self.eval(statement)
        return result

    def _ls(self, args):
        # TODO: Implement ls
        pass

    def _cat(self, args):
        # TODO: Implement cat
        pass

    def _set_theme(self, args):
        if not args:
            return "set-theme: missing operand"
        theme_name = args[0]
        if theme_name not in self.themes:
            return f"set-theme: unknown theme '{theme_name}'"
        self.player.vc_state.theme = theme_name
        return f"Theme set to '{theme_name}'."

    def _set_prompt(self, args):
        if not args:
            return "set-prompt: missing operand"
        self.player.vc_state.prompt_format = args[0]
        return "Prompt format updated."

    def _mine_hash(self, args):
        if not args:
            return "mine-hash: missing operand"
        try:
            duration_hours = int(args[0])
            self.player.vc_state.passive_mining_end_time = datetime.now() + timedelta(hours=duration_hours)
            return f"Passive hash mining started for {duration_hours} hours."
        except (ValueError, IndexError):
            return "mine-hash: invalid duration"

    def _status(self, args):
        if self.player.vc_state.passive_mining_end_time:
            if datetime.now() < self.player.vc_state.passive_mining_end_time:
                remaining = self.player.vc_state.passive_mining_end_time - datetime.now()
                return f"Passive mining in progress. Time remaining: {remaining}"
            else:
                return "Passive mining complete. Run 'status' again to collect."
        return "No passive mining in progress."

    def _shop(self, args):
        output = "--- Hardware Shop ---\n"
        for component, tiers in UPGRADE_DATA.items():
            current_tier = getattr(self.player.vc_state, f"{component}_tier")
            output += f"\n{component.upper()} (Current Tier: {current_tier})\n"
            if current_tier < max(tiers.keys()):
                next_tier_data = tiers[current_tier + 1]
                output += f"  - Next Tier: {current_tier + 1}\n"
                output += f"  - Cost: {next_tier_data['cost']} C\n"
                if component == 'cpu':
                    output += f"  - Effect: {next_tier_data['effect'] * 100}% speed\n"
                elif component == 'ram':
                    output += f"  - Effect: {next_tier_data['max_threads']} max threads\n"
            else:
                output += "  - Max tier reached.\n"
        return output

    def _buy(self, args):
        if not args:
            return "buy: missing component"

        component = args[0]
        if component not in UPGRADE_DATA:
            return f"buy: unknown component '{component}'"

        current_tier = getattr(self.player.vc_state, f"{component}_tier")
        if current_tier >= max(UPGRADE_DATA[component].keys()):
            return f"buy: {component} is already at max tier."

        next_tier = current_tier + 1
        cost = UPGRADE_DATA[component][next_tier]['cost']

        if self.player.vc_state.credits < cost:
            return f"buy: insufficient credits. Need {cost} C."

        self.player.vc_state.credits -= cost
        setattr(self.player.vc_state, f"{component}_tier", next_tier)

        return f"Successfully purchased {component.upper()} Tier {next_tier}."

    def _hashcrack(self, args):
        if not self.player.is_vip:
            cpu_tier = self.player.vc_state.cpu_tier
            speed_multiplier = UPGRADE_DATA['cpu'][cpu_tier]['effect']
            delay = 5 * speed_multiplier
            print(f"Cracking hash (standard algorithm)... ETA: {delay:.2f}s")
            time.sleep(delay)
        else:
            print("Cracking hash (quantum core)...")
        return "password123"
