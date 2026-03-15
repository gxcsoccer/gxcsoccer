#!/usr/bin/env python3
"""Terminal Dungeon Crawler RPG for GitHub Profile README."""

import json
import os
import random
import sys
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path

REPO = "gxcsoccer/gxcsoccer"
GAME_DIR = Path(__file__).parent
XP_THRESHOLDS = [0, 20, 50, 100, 180, 300]

VALID_MOVES = {"NORTH", "SOUTH", "EAST", "WEST"}
VALID_COMBAT = {"ATTACK", "DEFEND", "RUN"}
VALID_SHOP = {"BUY1", "BUY2", "BUY3"}
VALID_OTHER = {"REST", "SEARCH", "RESET"}
VALID_COMMANDS = VALID_MOVES | VALID_COMBAT | VALID_SHOP | VALID_OTHER

# Emoji constants
E_PIN = "\U0001f4cd"
E_SKULL = "\U0001f480"
E_SWORD = "\u2694\ufe0f"
E_GREEN = "\U0001f49a"
E_CART = "\U0001f6d2"
E_CHECK = "\u2705"
E_SCROLL = "\U0001f4dc"
E_TROPHY = "\U0001f3c6"
E_CHART = "\U0001f4ca"
E_REFRESH = "\U0001f504"
E_SHIELD = "\U0001f6e1\ufe0f"
E_RUN = "\U0001f3c3"
E_UP = "\u2b06\ufe0f"
E_DOWN = "\u2b07\ufe0f"
E_LEFT = "\u2b05\ufe0f"
E_RIGHT = "\u27a1\ufe0f"
E_COIN = "\U0001f4b0"
E_ZAP = "\u26a1"
E_WAVE = "\U0001f44b"
E_STAR = "\u2b50"
E_DRAGON = "\U0001f409"
E_MAP = "\U0001f5fa\ufe0f"
E_CROSSED = "\u2694\ufe0f"
E_SPARKLE = "\u2728"
E_GAME = "\U0001f3ae"

# Action type to emoji
ACTION_EMOJI = {
    "NORTH": E_UP, "SOUTH": E_DOWN, "EAST": E_RIGHT, "WEST": E_LEFT,
    "ATTACK": E_SWORD, "DEFEND": E_SHIELD, "RUN": E_RUN,
    "ENCOUNTER": E_DRAGON, "VICTORY": E_TROPHY, "DEATH": E_SKULL,
    "TREASURE": E_STAR, "TRAP": E_ZAP, "REST": E_GREEN,
    "BUY": E_COIN, "RESPAWN": E_REFRESH, "RESET": E_REFRESH,
    "ENEMY": E_CROSSED, "START": E_SPARKLE,
}


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def hp_bar(current, maximum, length=10):
    filled = round(current / maximum * length) if maximum > 0 else 0
    filled = max(0, min(length, filled))
    return "\u2588" * filled + "\u2591" * (length - filled)


def issue_link(command, label):
    title = urllib.parse.quote(f"RPG:{command}", safe="")
    body = urllib.parse.quote(f"I chose **{command}**! Let the adventure continue!", safe="")
    return f"[{label}](https://github.com/{REPO}/issues/new?title={title}&body={body})"


def avatar(user, size=16):
    return f'<img src="https://github.com/{user}.png?size={size}" alt="" width="{size}">'


def user_link(user):
    return f"**[{user}](https://github.com/{user})**"


def now_str():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


class GameEngine:
    def __init__(self, state, world):
        self.state = state
        self.world = world
        self.player = state["player"]
        self.message = ""

    def current_room(self):
        return self.world["rooms"][self.player["position"]]

    def add_log(self, action, user, message):
        self.state["log"].append({"action": action, "user": user, "message": message})
        if len(self.state["log"]) > 5:
            self.state["log"] = self.state["log"][-5:]

    def add_history(self, action, user, message, issue_number=None):
        entry = {
            "turn": self.state["turn_count"],
            "time": now_str(),
            "action": action,
            "user": user,
            "message": message,
        }
        if issue_number:
            entry["issue"] = issue_number
        self.state["history"].append(entry)
        # Keep last 50 entries
        if len(self.state["history"]) > 50:
            self.state["history"] = self.state["history"][-50:]

    def add_contributor(self, user):
        contribs = self.state["contributors"]
        contribs[user] = contribs.get(user, 0) + 1

    def check_level_up(self):
        for i, threshold in enumerate(XP_THRESHOLDS):
            if i > self.player["level"] and self.player["xp"] >= threshold:
                self.player["level"] = i
                self.player["max_hp"] += 5
                self.player["atk"] += 2
                self.player["def"] += 1
                self.player["hp"] = self.player["max_hp"]
                self.message += f" Level up! Now level {i}!"

    def process(self, command, user, issue_number=None):
        if command == "RESET":
            self.reset()
            self.add_log("RESET", user, "The dungeon resets...")
            self.add_history("RESET", user, "Reset the dungeon", issue_number)
            return

        if not self.player["alive"]:
            self.respawn()
            self.add_log("RESPAWN", user, "The hero is reborn!")
            self.add_history("RESPAWN", user, "The hero is reborn!", issue_number)
            return

        self.state["turn_count"] += 1
        self.add_contributor(user)

        if self.state["combat"]:
            if command in VALID_COMBAT:
                self.handle_combat(command, user, issue_number)
            else:
                self.add_log(command, user, "Can't do that in combat!")
        elif command in VALID_MOVES:
            self.move(command.lower(), user, issue_number)
        elif command == "REST":
            self.rest(user, issue_number)
        elif command in VALID_SHOP:
            self.buy(int(command[-1]) - 1, user, issue_number)
        else:
            self.add_log(command, user, "Nothing happens...")

        if self.player["hp"] <= 0:
            self.player["alive"] = False
            self.player["hp"] = 0
            self.add_log("DEATH", "system", "The hero has fallen...")
            self.add_history("DEATH", user, "The hero has fallen...", issue_number)

    def move(self, direction, user, issue_number=None):
        room = self.current_room()
        if direction not in room["exits"]:
            self.add_log(direction.upper(), user, "There's no path that way!")
            return

        dest_id = room["exits"][direction]
        self.player["position"] = dest_id
        dest = self.current_room()
        msg = f"Moved to {dest['name']}"
        self.add_log(direction.upper(), user, msg)
        self.add_history(direction.upper(), user, msg, issue_number)
        self.enter_room(user, issue_number)

    def enter_room(self, user, issue_number=None):
        room = self.current_room()
        room_id = self.player["position"]

        if room_id in self.state["rooms_cleared"]:
            return

        event = room["event_type"]
        data = room["event_data"]

        if event == "monster" and data:
            self.state["combat"] = {
                "enemy_name": data["name"],
                "enemy_hp": data["hp"],
                "enemy_max_hp": data["hp"],
                "enemy_atk": data["atk"],
                "enemy_def": data["def"],
                "xp_reward": data["xp"],
                "gold_reward": data["gold"],
            }
            msg = f"{data['name']} appears!"
            self.add_log("ENCOUNTER", "system", msg)
            self.add_history("ENCOUNTER", user, msg, issue_number)

        elif event == "treasure" and data:
            self.player["gold"] += data["gold"]
            if data.get("item"):
                item = data["item"]
                self.player["inventory"].append(item["name"])
                if item["type"] == "atk":
                    self.player["atk"] += item["value"]
                elif item["type"] == "def":
                    self.player["def"] += item["value"]
                msg = f"Found {item['name']} (+{item['value']} {item['type'].upper()}) and {data['gold']} gold!"
            else:
                msg = f"Found {data['gold']} gold!"
            self.add_log("TREASURE", "system", msg)
            self.add_history("TREASURE", user, msg, issue_number)
            self.state["rooms_cleared"].append(room_id)

        elif event == "trap" and data:
            self.player["hp"] -= data["damage"]
            self.add_log("TRAP", "system", data["description"])
            self.add_history("TRAP", user, data["description"], issue_number)
            self.state["rooms_cleared"].append(room_id)

    def handle_combat(self, command, user, issue_number=None):
        combat = self.state["combat"]
        enemy = combat["enemy_name"]

        if command == "ATTACK":
            dmg = max(1, self.player["atk"] - combat["enemy_def"]) + random.randint(0, 3)
            combat["enemy_hp"] -= dmg
            msg = f"Attacked {enemy} for {dmg} dmg!"
            self.add_log("ATTACK", user, msg)
            self.add_history("ATTACK", user, msg, issue_number)

            if combat["enemy_hp"] <= 0:
                self.victory(user, issue_number)
                return

            enemy_dmg = max(1, combat["enemy_atk"] - self.player["def"]) + random.randint(0, 2)
            self.player["hp"] -= enemy_dmg
            self.add_log("ENEMY", "system", f"{enemy} strikes back for {enemy_dmg} dmg!")

        elif command == "DEFEND":
            enemy_dmg = max(1, (combat["enemy_atk"] - self.player["def"]) // 2)
            self.player["hp"] -= enemy_dmg
            counter = max(1, self.player["atk"] // 3)
            combat["enemy_hp"] -= counter
            msg = f"Blocked! Took {enemy_dmg} dmg, countered for {counter}"
            self.add_log("DEFEND", user, msg)
            self.add_history("DEFEND", user, msg, issue_number)

            if combat["enemy_hp"] <= 0:
                self.victory(user, issue_number)
                return

        elif command == "RUN":
            if random.random() < 0.6:
                self.state["combat"] = None
                self.add_log("RUN", user, "Escaped successfully!")
                self.add_history("RUN", user, "Escaped successfully!", issue_number)
            else:
                enemy_dmg = max(1, combat["enemy_atk"] - self.player["def"]) + random.randint(0, 2)
                self.player["hp"] -= enemy_dmg
                msg = f"Failed to escape! Took {enemy_dmg} dmg!"
                self.add_log("RUN", user, msg)
                self.add_history("RUN", user, msg, issue_number)

    def victory(self, user, issue_number=None):
        combat = self.state["combat"]
        xp = combat["xp_reward"]
        gold = combat["gold_reward"]
        enemy = combat["enemy_name"]
        msg = f"Defeated {enemy}! +{xp} XP, +{gold} gold"
        self.player["xp"] += xp
        self.player["gold"] += gold
        self.add_log("VICTORY", user, msg)
        self.add_history("VICTORY", user, msg, issue_number)
        self.state["rooms_cleared"].append(self.player["position"])
        self.state["combat"] = None
        self.check_level_up()

    def rest(self, user, issue_number=None):
        room = self.current_room()
        if room["event_type"] == "rest" and room["event_data"]:
            heal = room["event_data"]["heal"]
            self.player["hp"] = min(self.player["max_hp"], self.player["hp"] + heal)
            msg = f"Rested and healed {heal} HP"
            self.add_log("REST", user, msg)
            self.add_history("REST", user, msg, issue_number)
        else:
            self.add_log("REST", user, "Can't rest here!")

    def buy(self, slot, user, issue_number=None):
        room = self.current_room()
        if room["event_type"] != "shop" or not room["event_data"]:
            self.add_log("BUY", user, "There's no shop here!")
            return

        items = room["event_data"]["items"]
        if slot < 0 or slot >= len(items):
            self.add_log("BUY", user, "Invalid item!")
            return

        item = items[slot]
        if self.player["gold"] < item["cost"]:
            cost = item["cost"]
            self.add_log("BUY", user, f"Not enough gold! Need {cost}")
            return

        self.player["gold"] -= item["cost"]
        name = item["name"]
        val = item["value"]
        if item["effect"] == "hp":
            self.player["hp"] = min(self.player["max_hp"], self.player["hp"] + val)
            msg = f"Used {name}! +{val} HP"
        elif item["effect"] == "atk":
            self.player["atk"] += val
            self.player["inventory"].append(name)
            msg = f"Bought {name}! +{val} ATK"
        elif item["effect"] == "def":
            self.player["def"] += val
            self.player["inventory"].append(name)
            msg = f"Bought {name}! +{val} DEF"
        else:
            msg = f"Bought {name}!"
        self.add_log("BUY", user, msg)
        self.add_history("BUY", user, msg, issue_number)

    def respawn(self):
        self.player["hp"] = 50
        self.player["max_hp"] = 50
        self.player["atk"] = 8
        self.player["def"] = 4
        self.player["gold"] = 0
        self.player["xp"] = 0
        self.player["level"] = 1
        self.player["position"] = "entrance"
        self.player["inventory"] = []
        self.player["alive"] = True
        self.state["combat"] = None
        self.state["rooms_cleared"] = []

    def reset(self):
        self.respawn()
        self.state["log"] = []
        self.state["turn_count"] = 0


class Renderer:
    def __init__(self, state, world):
        self.state = state
        self.world = world
        self.player = state["player"]

    def render(self):
        parts = []
        parts.append("<!-- RPG:START -->")
        parts.append("")
        parts.append(self._render_header())
        parts.append(self._render_game_display())
        parts.append(self._render_actions())
        parts.append("")
        parts.append("---")
        parts.append("")
        parts.append(self._render_adventure_details())
        parts.append("")
        parts.append(self._render_how_to_play())
        parts.append("")
        parts.append("<!-- RPG:END -->")
        return "\n".join(parts)

    def _render_header(self):
        lines = []
        lines.append('<div align="center">')
        lines.append("")
        lines.append(f"**{E_SWORD} TERMINAL DUNGEON CRAWLER {E_SWORD}**")
        lines.append("")
        turn = self.state["turn_count"]
        total_heroes = len(self.state["contributors"])
        lines.append(f"*A community-driven RPG adventure — {total_heroes} heroes, {turn} turns played*")
        lines.append("")
        lines.append("</div>")
        lines.append("")
        return "\n".join(lines)

    def _render_game_display(self):
        lines = []
        lines.append("```")
        lines.append("gxcsoccer@github ~ $ ./dungeon_crawler")
        lines.append("")

        p = self.player
        room = self.world["rooms"][p["position"]]
        xp_next = self._next_xp()

        # Status bar
        bar = hp_bar(p['hp'], p['max_hp'])
        lines.append(f"  HP [{bar}] {p['hp']}/{p['max_hp']}   Lv.{p['level']}")
        lines.append(f"  ATK {p['atk']}  DEF {p['def']}  Gold {p['gold']}  XP {p['xp']}/{xp_next}")
        if p["inventory"]:
            inv = ', '.join(p['inventory'][:4])
            lines.append(f"  Items: {inv}")
        lines.append("")

        # Room
        room_name = room['name']
        lines.append(f"  {E_PIN} {room_name}")
        lines.append("")
        for art_line in room.get("art", []):
            lines.append(f"  {art_line}")
        lines.append("")
        lines.append(f"  {room['description']}")
        lines.append("")

        # Combat or event info
        if not p["alive"]:
            lines.append(f"  {E_SKULL} THE HERO HAS FALLEN...")
            lines.append("  Click any action to respawn and try again!")
            lines.append("")
        elif self.state["combat"]:
            c = self.state["combat"]
            enemy_name = c['enemy_name']
            enemy_bar = hp_bar(c['enemy_hp'], c['enemy_max_hp'])
            lines.append(f"  {E_SWORD} {enemy_name} appears!")
            lines.append(f"  Enemy HP [{enemy_bar}] {c['enemy_hp']}/{c['enemy_max_hp']}")
            lines.append("")
        else:
            event = room["event_type"]
            rid = p["position"]
            if event == "rest" and room["event_data"]:
                heal = room['event_data']['heal']
                lines.append(f"  {E_GREEN} A peaceful place to rest. (+{heal} HP)")
                lines.append("")
            elif event == "shop" and room["event_data"]:
                lines.append(f"  {E_CART} Shop:")
                for i, item in enumerate(room["event_data"]["items"]):
                    name = item['name']
                    cost = item['cost']
                    val = item['value']
                    eff = item['effect'].upper()
                    lines.append(f"    [{i+1}] {name} - {cost} gold (+{val} {eff})")
                lines.append("")
            elif rid in self.state["rooms_cleared"]:
                lines.append(f"  {E_CHECK} This area has been cleared.")
                lines.append("")

        # Exits
        exits = room.get("exits", {})
        if exits:
            exit_str = "  Exits: " + " | ".join(d.upper() for d in exits)
            lines.append(exit_str)
            lines.append("")

        # Adventure log (last 5)
        lines.append(f"  {E_SCROLL} Adventure Log:")
        for entry in self.state["log"][-5:]:
            if entry["user"] != "system":
                user_str = f"@{entry['user']}"
            else:
                user_str = E_ZAP
            lines.append(f"  > {user_str} {entry['message']}")

        lines.append("```")
        lines.append("")
        return "\n".join(lines)

    def _render_actions(self):
        p = self.player
        room = self.world["rooms"][p["position"]]
        lines = []

        if not p["alive"]:
            respawn = issue_link('RESET', f'{E_REFRESH} Respawn')
            lines.append(f"| {respawn} |")
            lines.append("|---|")
            return "\n".join(lines)

        if self.state["combat"]:
            atk = issue_link('ATTACK', f'{E_SWORD} Attack')
            dfn = issue_link('DEFEND', f'{E_SHIELD} Defend')
            run = issue_link('RUN', f'{E_RUN} Run')
            lines.append("| | | |")
            lines.append("|:---:|:---:|:---:|")
            lines.append(f"| {atk} | {dfn} | {run} |")
            return "\n".join(lines)

        # Build action grid
        exits = room.get("exits", {})
        event = room["event_type"]
        rows = []

        if "north" in exits:
            north = issue_link('NORTH', f'{E_UP} North')
            rows.append(f"| | {north} | |")

        west = issue_link("WEST", f"{E_LEFT} West") if "west" in exits else " "
        east = issue_link("EAST", f"{E_RIGHT} East") if "east" in exits else " "

        if event == "rest" and room.get("event_data"):
            center = issue_link("REST", f"{E_GREEN} Rest")
        elif event == "shop" and room.get("event_data"):
            center = issue_link("BUY1", f"{E_CART} Shop")
        else:
            center = " "

        rows.append(f"| {west} | {center} | {east} |")

        if "south" in exits:
            south = issue_link('SOUTH', f'{E_DOWN} South')
            rows.append(f"| | {south} | |")

        if event == "shop" and room.get("event_data"):
            items = room["event_data"]["items"]
            shop_cells = []
            for i, item in enumerate(items):
                name = item['name']
                shop_cells.append(issue_link(f"BUY{i+1}", f"{E_COIN} {name}"))
            rows.append(f"| {' | '.join(shop_cells)} |")

        lines.append("| | | |")
        lines.append("|:---:|:---:|:---:|")
        lines.extend(rows)

        return "\n".join(lines)

    def _render_adventure_details(self):
        lines = []
        lines.append("<details>")
        lines.append(f"<summary><b>{E_SCROLL} Adventure Log</b></summary>")
        lines.append("")

        # Heroes table
        lines.append(f"### {E_TROPHY} Heroes")
        lines.append("")

        contribs = self.state["contributors"]
        if contribs:
            # Sort by move count descending
            sorted_heroes = sorted(contribs.items(), key=lambda x: x[1], reverse=True)
            lines.append("<table>")
            lines.append("  <thead>")
            lines.append("    <tr><th>Hero</th><th>Moves</th></tr>")
            lines.append("  </thead>")
            lines.append("  <tbody>")
            for user, count in sorted_heroes:
                av = avatar(user)
                link = user_link(user)
                lines.append(f"    <tr><td>{av} {link}</td><td align='center'>{count}</td></tr>")
            lines.append("  </tbody>")
            lines.append("</table>")
        else:
            lines.append("*No heroes yet — be the first to join the adventure!*")
        lines.append("")

        # History table
        lines.append(f"### {E_MAP} Move History")
        lines.append("")

        history = self.state.get("history", [])
        if history:
            lines.append("| Turn | Time | Hero | Event | Issue |")
            lines.append("| :---: | :---: | :--- | :--- | :---: |")

            for entry in reversed(history[-30:]):
                turn = entry.get("turn", "?")
                time = entry.get("time", "")
                user = entry.get("user", "system")
                action = entry.get("action", "")
                message = entry.get("message", "")
                issue_num = entry.get("issue", "")

                emoji = ACTION_EMOJI.get(action, E_ZAP)
                if user != "system":
                    av = avatar(user)
                    link = user_link(user)
                    hero_cell = f"{av} {link}"
                else:
                    hero_cell = f"{E_ZAP} *system*"

                issue_cell = ""
                if issue_num:
                    issue_cell = f"[#{issue_num}](https://github.com/{REPO}/issues/{issue_num})"

                lines.append(f"| **{turn}** | {time} | {hero_cell} | {emoji} {message} | {issue_cell} |")
        else:
            lines.append("*No moves yet — the adventure awaits!*")

        lines.append("")
        lines.append("</details>")
        return "\n".join(lines)

    def _render_how_to_play(self):
        lines = []
        lines.append("<details>")
        lines.append(f"<summary><b>{E_GAME} How to Play</b></summary>")
        lines.append("")
        lines.append("### Rules")
        lines.append("")
        lines.append("This is a **community-driven dungeon crawler RPG**! Everyone controls the same hero together.")
        lines.append("")
        lines.append("**How it works:**")
        lines.append("1. Click an action button above (e.g. **South**, **Attack**)")
        lines.append("2. This creates a GitHub Issue automatically")
        lines.append("3. A GitHub Action processes your move and updates this README")
        lines.append("4. The issue is closed with a confirmation comment")
        lines.append("")
        lines.append("**Game mechanics:**")
        lines.append(f"- {E_UP}{E_DOWN}{E_LEFT}{E_RIGHT} **Move** through the dungeon rooms")
        lines.append(f"- {E_SWORD} **Attack** enemies to deal damage (ATK - enemy DEF + random 0~3)")
        lines.append(f"- {E_SHIELD} **Defend** to take half damage and counter-attack")
        lines.append(f"- {E_RUN} **Run** from combat (60% success rate)")
        lines.append(f"- {E_GREEN} **Rest** at peaceful locations to heal HP")
        lines.append(f"- {E_CART} **Shop** to buy potions, weapons, and armor")
        lines.append("")
        lines.append("**Leveling up:**")
        lines.append("- Defeat enemies to earn XP and Gold")
        lines.append("- Level up at XP thresholds: 20, 50, 100, 180, 300")
        lines.append("- Each level grants +5 HP, +2 ATK, +1 DEF and full heal")
        lines.append("")
        lines.append("**Death & Respawn:**")
        lines.append("- If HP reaches 0, the hero falls")
        lines.append("- Click any button to respawn at the entrance with base stats")
        lines.append("- Your contribution to the hero list is preserved!")
        lines.append("")
        lines.append(f"**Dungeon Map ({E_PIN} 10 rooms):**")
        lines.append("```")
        lines.append("         [Entrance]")
        lines.append("             |")
        lines.append("         [Hallway]        <- trap!")
        lines.append("        /         \\")
        lines.append("   [Armory]    [Library]   <- treasure / rest")
        lines.append("        \\         /")
        lines.append("       [Great Hall]        <- Skeleton Knight")
        lines.append("      /     |      \\")
        lines.append("  [Crypt] [Throne] [Garden]")
        lines.append("    |    Dragon!      |")
        lines.append("  [Vault]         [Fountain] <- shop")
        lines.append("```")
        lines.append("")
        lines.append("</details>")
        return "\n".join(lines)

    def _next_xp(self):
        for threshold in XP_THRESHOLDS:
            if threshold > self.player["xp"]:
                return threshold
        return XP_THRESHOLDS[-1] + 100


def update_readme(game_section):
    readme_path = GAME_DIR.parent / "README.md"
    content = readme_path.read_text(encoding="utf-8")

    start_marker = "<!-- RPG:START -->"
    end_marker = "<!-- RPG:END -->"

    start = content.find(start_marker)
    end = content.find(end_marker)

    if start != -1 and end != -1:
        new_content = content[:start] + game_section + content[end + len(end_marker):]
    else:
        insert_point = content.find('<div align="center">')
        if insert_point != -1:
            new_content = content[:insert_point] + game_section + "\n\n" + content[insert_point:]
        else:
            new_content = content + "\n\n" + game_section

    readme_path.write_text(new_content, encoding="utf-8")


def main():
    # Init mode: just render current state without processing
    if len(sys.argv) == 2 and sys.argv[1] == "--init":
        state = load_json(GAME_DIR / "state.json")
        world = load_json(GAME_DIR / "world.json")
        renderer = Renderer(state, world)
        game_section = renderer.render()
        update_readme(game_section)
        print("Initialized README with RPG section")
        return

    if len(sys.argv) < 3:
        print("Usage: python rpg.py <issue_title> <username> [issue_number]")
        print("       python rpg.py --init")
        sys.exit(1)

    issue_title = sys.argv[1]
    username = sys.argv[2]
    issue_number = sys.argv[3] if len(sys.argv) > 3 else None

    # Parse command
    if ":" not in issue_title:
        print(f"Invalid issue title: {issue_title}")
        sys.exit(1)

    command = issue_title.split(":", 1)[1].upper().strip()

    if command not in VALID_COMMANDS:
        print(f"Invalid command: {command}")
        sys.exit(1)

    # Load data
    state = load_json(GAME_DIR / "state.json")
    world = load_json(GAME_DIR / "world.json")

    # Process
    engine = GameEngine(state, world)
    engine.process(command, username, issue_number)

    # Save state
    save_json(GAME_DIR / "state.json", state)

    # Render and update README
    renderer = Renderer(state, world)
    game_section = renderer.render()
    update_readme(game_section)

    print(f"Processed: {command} by @{username}")


if __name__ == "__main__":
    main()
