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
            "thread-spawn": self._thread_spawn,
            "scan": self._scan,
            "ping": self._ping,
            "raw": self._raw,
            "man": self._man,
            "find": self._find,
            "echo": self._echo,
            "ip-lookup": self._ip_lookup,
            "decrypt": self._decrypt,
            "proc-kill": self._proc_kill,
            "vc-status": self._vc_status,
            "log-read": self._log_read,
            "vc-purge-logs": self._vc_purge_logs,
            "firewall-set": self._firewall_set,
            "vc-spoof": self._vc_spoof,
            "fragment-synthesize": self._fragment_synthesize,
            "extract": self._extract,
            "share": self._share,
            "vc-sync": self._vc_sync,
            "vc-relay": self._vc_relay,
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
                elif component == 'nic':
                    output += f"  - Effect: {next_tier_data['speed']} Mbps\n"
                elif component == 'ssd':
                    output += f"  - Effect: {next_tier_data['size']} GB\n"
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

    def _thread_spawn(self, args):
        if not args:
            return "thread-spawn: missing module name"

        module_name = args[0]
        max_threads = self.player.vc_state.get_max_threads()

        # For now, we'll just simulate the check
        if max_threads > 1:
            return f"Successfully spawned thread for module '{module_name}'."
        else:
            return "Upgrade your RAM to spawn more threads."

    def _scan(self, args):
        if not args:
            return "scan: missing target IP"

        target_ip = args[0]
        nic_tier = self.player.vc_state.nic_tier
        speed = UPGRADE_DATA['nic'][nic_tier]['speed']

        # Base delay of 5 seconds, reduced by NIC speed
        delay = max(0.5, 5 - (speed / 100))

        print(f"Scanning {target_ip} (ETA: {delay:.2f}s)...")
        time.sleep(delay)

        # Return a sample result
        return "Scan complete. Open ports: 22 (SSH), 80 (HTTP), 443 (HTTPS)"

    def _ping(self, args):
        if not args:
            return "ping: missing target IP"

        target_ip = args[0]
        return f"Pong from {target_ip}!"

    def _raw(self, args):
        if self.player.check_kmap("raw") == "LOCKED":
            return "raw: command not found"

        if len(args) < 2:
            return "raw: missing target IP and data packet"

        target_ip = args[0]
        data_packet = args[1]

        return f"Successfully sent raw packet to {target_ip}."

    def _man(self, args):
        if not args:
            return "man: missing command name"

        command = args[0]
        if self.player.check_kmap(command) in ["LOCKED", "HIDDEN"]:
            return f"man: command not found: {command}"

        man_pages = {
            "scan": "scan [ip_address]: Performs network discovery and port enumeration.",
            "ping": "ping [ip_address]: Tests basic network connectivity.",
            "raw": "raw [ip_address] [data_packet]: Sends a custom, low-level data packet.",
            "man": "man [command]: Displays the manual page for a command.",
            "shop": "shop: Displays the hardware upgrade shop.",
            "buy": "buy [component]: Buys the next tier of a hardware component.",
            "hashcrack": "hashcrack [hash]: Cracks a password hash.",
            "thread-spawn": "thread-spawn [module]: Executes a module in a separate thread.",
            "ls": "ls: Lists files in the current directory.",
            "cat": "cat [file]: Displays the contents of a file.",
            "set-theme": "set-theme [theme]: Sets the terminal theme.",
            "set-prompt": "set-prompt [prompt]: Sets the terminal prompt.",
            "mine-hash": "mine-hash [hours]: Starts passive hash mining.",
            "status": "status: Displays the status of passive mining.",
        }

        if len(args) > 1 and args[0] == "-a":
            return "\n".join(man_pages.keys())

        return man_pages.get(command, f"man: no manual entry for {command}")

    def _find(self, args):
        if not args:
            return "find: missing file pattern"

        pattern = args[0]
        import glob
        return "\n".join(glob.glob(pattern, recursive=True))

    def _echo(self, args):
        if not args:
            return ""

        text = args[0]
        if len(args) > 2 and args[1] == ">":
            filepath = args[2]
            try:
                with open(filepath, 'w') as f:
                    f.write(text)
                return ""
            except IOError as e:
                return f"echo: {e}"
        return text

    def _ip_lookup(self, args):
        if not args:
            return "ip-lookup: missing domain name"

        domain = args[0]
        # Simulate a DNS lookup
        import random
        return f"10.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}"

    def _decrypt(self, args):
        if len(args) < 2:
            return "decrypt: missing file and key"

        return "File decrypted successfully."

    def _proc_kill(self, args):
        if not args:
            return "proc-kill: missing process ID"

        return "Process killed."

    def _vc_status(self, args):
        cpu_load = random.uniform(10, 90)
        ram_usage = random.uniform(20, 80)
        return f"VC Status: CPU Load: {cpu_load:.2f}%, RAM Usage: {ram_usage:.2f}%"

    def _log_read(self, args):
        if len(args) < 2:
            return "log-read: missing target IP and log file"

        return "Log file content."

    def _vc_purge_logs(self, args):
        if self.player.check_kmap("vc-purge-logs") == "LOCKED":
            return "vc-purge-logs: command not found"
        return "Logs purged."

    def _firewall_set(self, args):
        if not args:
            return "firewall-set: missing rule"
        return "Firewall rule set."

    def _vc_spoof(self, args):
        if self.player.check_kmap("vc-spoof") == "LOCKED":
            return "vc-spoof: command not found"
        return "IP address spoofed."

    def _fragment_synthesize(self, args):
        if self.player.check_kmap("fragment-synthesize") == "LOCKED":
            return "fragment-synthesize: command not found"
        return "Fragments synthesized."

    def _extract(self, args):
        if len(args) < 2:
            return "extract: missing pattern and file"
        return "Data extracted."

    def _share(self, args):
        if len(args) < 2:
            return "share: missing item and teammate"
        return "Item shared."

    def _vc_sync(self, args):
        if self.player.check_kmap("vc-sync") == "LOCKED":
            return "vc-sync: command not found"
        return "VCs synced."

    def _vc_relay(self, args):
        if self.player.check_kmap("vc-relay") == "LOCKED":
            return "vc-relay: command not found"
        return "VC relay active."
