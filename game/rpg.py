#!/usr/bin/env python3
"""Terminal Dungeon Crawler RPG for GitHub Profile README."""

import json
import random
import sys
import urllib.parse
from pathlib import Path

REPO = "gxcsoccer/gxcsoccer"
GAME_DIR = Path(__file__).parent
XP_THRESHOLDS = [0, 20, 50, 100, 180, 300]

VALID_MOVES = {"NORTH", "SOUTH", "EAST", "WEST"}
VALID_COMBAT = {"ATTACK", "DEFEND", "RUN"}
VALID_SHOP = {"BUY1", "BUY2", "BUY3"}
VALID_OTHER = {"REST", "SEARCH", "RESET"}
VALID_COMMANDS = VALID_MOVES | VALID_COMBAT | VALID_SHOP | VALID_OTHER

DIR_EMOJI = {"north": "\u2b06\ufe0f", "south": "\u2b07\ufe0f", "east": "\u27a1\ufe0f", "west": "\u2b05\ufe0f"}

# Emoji constants to avoid backslash-in-fstring issues
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

    def add_contributor(self, user):
        if user not in self.state["contributors"]:
            self.state["contributors"].append(user)
        if len(self.state["contributors"]) > 10:
            self.state["contributors"] = self.state["contributors"][-10:]

    def check_level_up(self):
        for i, threshold in enumerate(XP_THRESHOLDS):
            if i > self.player["level"] and self.player["xp"] >= threshold:
                self.player["level"] = i
                self.player["max_hp"] += 5
                self.player["atk"] += 2
                self.player["def"] += 1
                self.player["hp"] = self.player["max_hp"]
                self.message += f" Level up! Now level {i}!"

    def process(self, command, user):
        if command == "RESET":
            self.reset()
            self.add_log("RESET", user, "The dungeon resets...")
            return

        if not self.player["alive"]:
            self.respawn()
            self.add_log("RESPAWN", user, "The hero is reborn!")
            return

        self.state["turn_count"] += 1
        self.add_contributor(user)

        if self.state["combat"]:
            if command in VALID_COMBAT:
                self.handle_combat(command, user)
            else:
                self.add_log(command, user, "Can't do that in combat!")
        elif command in VALID_MOVES:
            self.move(command.lower(), user)
        elif command == "REST":
            self.rest(user)
        elif command in VALID_SHOP:
            self.buy(int(command[-1]) - 1, user)
        else:
            self.add_log(command, user, "Nothing happens...")

        if self.player["hp"] <= 0:
            self.player["alive"] = False
            self.player["hp"] = 0
            self.add_log("DEATH", "system", "The hero has fallen...")

    def move(self, direction, user):
        room = self.current_room()
        if direction not in room["exits"]:
            self.add_log(direction.upper(), user, "There's no path that way!")
            return

        dest_id = room["exits"][direction]
        self.player["position"] = dest_id
        dest = self.current_room()
        self.add_log(direction.upper(), user, f"Moved to {dest['name']}")
        self.enter_room(user)

    def enter_room(self, user):
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
            self.add_log("ENCOUNTER", "system", f"{data['name']} appears!")

        elif event == "treasure" and data:
            self.player["gold"] += data["gold"]
            if data.get("item"):
                item = data["item"]
                self.player["inventory"].append(item["name"])
                if item["type"] == "atk":
                    self.player["atk"] += item["value"]
                elif item["type"] == "def":
                    self.player["def"] += item["value"]
                self.add_log("TREASURE", "system", f"Found {item['name']} (+{item['value']} {item['type'].upper()}) and {data['gold']} gold!")
            else:
                self.add_log("TREASURE", "system", f"Found {data['gold']} gold!")
            self.state["rooms_cleared"].append(room_id)

        elif event == "trap" and data:
            self.player["hp"] -= data["damage"]
            self.add_log("TRAP", "system", data["description"])
            self.state["rooms_cleared"].append(room_id)

    def handle_combat(self, command, user):
        combat = self.state["combat"]

        if command == "ATTACK":
            dmg = max(1, self.player["atk"] - combat["enemy_def"]) + random.randint(0, 3)
            combat["enemy_hp"] -= dmg
            self.add_log("ATTACK", user, f"Attacked {combat['enemy_name']} for {dmg} dmg!")

            if combat["enemy_hp"] <= 0:
                self.victory(user)
                return

            enemy_dmg = max(1, combat["enemy_atk"] - self.player["def"]) + random.randint(0, 2)
            self.player["hp"] -= enemy_dmg
            self.add_log("ENEMY", "system", f"{combat['enemy_name']} strikes back for {enemy_dmg} dmg!")

        elif command == "DEFEND":
            enemy_dmg = max(1, (combat["enemy_atk"] - self.player["def"]) // 2)
            self.player["hp"] -= enemy_dmg
            counter = max(1, self.player["atk"] // 3)
            combat["enemy_hp"] -= counter
            self.add_log("DEFEND", user, f"Blocked! Took {enemy_dmg} dmg, countered for {counter}")

            if combat["enemy_hp"] <= 0:
                self.victory(user)
                return

        elif command == "RUN":
            if random.random() < 0.6:
                self.state["combat"] = None
                # go back to previous room - just stay in current room
                self.add_log("RUN", user, "Escaped successfully!")
            else:
                enemy_dmg = max(1, combat["enemy_atk"] - self.player["def"]) + random.randint(0, 2)
                self.player["hp"] -= enemy_dmg
                self.add_log("RUN", user, f"Failed to escape! Took {enemy_dmg} dmg!")

    def victory(self, user):
        combat = self.state["combat"]
        self.player["xp"] += combat["xp_reward"]
        self.player["gold"] += combat["gold_reward"]
        self.add_log("VICTORY", user, f"Defeated {combat['enemy_name']}! +{combat['xp_reward']} XP, +{combat['gold_reward']} gold")
        self.state["rooms_cleared"].append(self.player["position"])
        self.state["combat"] = None
        self.check_level_up()

    def rest(self, user):
        room = self.current_room()
        if room["event_type"] == "rest" and room["event_data"]:
            heal = room["event_data"]["heal"]
            self.player["hp"] = min(self.player["max_hp"], self.player["hp"] + heal)
            self.add_log("REST", user, f"Rested and healed {heal} HP")
        else:
            self.add_log("REST", user, "Can't rest here!")

    def buy(self, slot, user):
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
            self.add_log("BUY", user, f"Not enough gold! Need {item['cost']}")
            return

        self.player["gold"] -= item["cost"]
        if item["effect"] == "hp":
            self.player["hp"] = min(self.player["max_hp"], self.player["hp"] + item["value"])
            self.add_log("BUY", user, f"Used {item['name']}! +{item['value']} HP")
        elif item["effect"] == "atk":
            self.player["atk"] += item["value"]
            self.player["inventory"].append(item["name"])
            self.add_log("BUY", user, f"Bought {item['name']}! +{item['value']} ATK")
        elif item["effect"] == "def":
            self.player["def"] += item["value"]
            self.player["inventory"].append(item["name"])
            self.add_log("BUY", user, f"Bought {item['name']}! +{item['value']} DEF")

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
        lines = []
        lines.append("<!-- RPG:START -->")
        lines.append("")
        lines.append('<div align="center">')
        lines.append("")
        lines.append(f"**{E_SWORD} TERMINAL DUNGEON CRAWLER {E_SWORD}**")
        lines.append("")
        lines.append("</div>")
        lines.append("")
        lines.append("```")
        lines.append("gxcsoccer@github ~ $ ./dungeon_crawler")
        lines.append("")

        p = self.player
        room = self.world["rooms"][p["position"]]
        xp_next = self._next_xp()

        # Status bar
        lines.append(f"  HP [{hp_bar(p['hp'], p['max_hp'])}] {p['hp']}/{p['max_hp']}   Lv.{p['level']}")
        lines.append(f"  ATK {p['atk']}  DEF {p['def']}  Gold {p['gold']}  XP {p['xp']}/{xp_next}")
        if p["inventory"]:
            lines.append(f"  Items: {', '.join(p['inventory'][:4])}")
        lines.append("")

        # Room
        lines.append(f"  {E_PIN} {room['name']}")
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
            lines.append(f"  {E_SWORD} {c['enemy_name']} appears!")
            lines.append(f"  Enemy HP [{hp_bar(c['enemy_hp'], c['enemy_max_hp'])}] {c['enemy_hp']}/{c['enemy_max_hp']}")
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

        # Adventure log
        lines.append(f"  {E_SCROLL} Adventure Log:")
        for entry in self.state["log"][-5:]:
            user_str = f"@{entry['user']}" if entry["user"] != "system" else E_ZAP
            lines.append(f"  > {user_str} {entry['message']}")
        lines.append("")

        # Footer
        contribs = self.state["contributors"][-8:]
        if contribs:
            hero_list = ' '.join('@' + c for c in contribs)
            lines.append(f"  {E_TROPHY} Heroes: {hero_list}")
        turn = self.state['turn_count']
        lines.append(f"  {E_CHART} Turn #{turn}")

        lines.append("```")
        lines.append("")

        # Action buttons (outside code block for clickability)
        lines.append(self._render_actions())
        lines.append("")
        lines.append("<!-- RPG:END -->")

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

        # Direction row 1: North
        if "north" in exits:
            north = issue_link('NORTH', f'{E_UP} North')
            rows.append(f"| | {north} | |")
        # Direction row 2: West + East
        west = issue_link("WEST", f"{E_LEFT} West") if "west" in exits else " "
        east = issue_link("EAST", f"{E_RIGHT} East") if "east" in exits else " "

        # Center action
        if event == "rest" and room.get("event_data"):
            center = issue_link("REST", f"{E_GREEN} Rest")
        elif event == "shop" and room.get("event_data"):
            center = issue_link("BUY1", f"{E_CART} Shop")
        else:
            center = " "

        rows.append(f"| {west} | {center} | {east} |")

        # Direction row 3: South
        if "south" in exits:
            south = issue_link('SOUTH', f'{E_DOWN} South')
            rows.append(f"| | {south} | |")

        # Shop extra buttons
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
        # First time: insert before the snake div
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
        print("Usage: python rpg.py <issue_title> <username>")
        print("       python rpg.py --init")
        sys.exit(1)

    issue_title = sys.argv[1]
    username = sys.argv[2]

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
    engine.process(command, username)

    # Save state
    save_json(GAME_DIR / "state.json", state)

    # Render and update README
    renderer = Renderer(state, world)
    game_section = renderer.render()
    update_readme(game_section)

    print(f"Processed: {command} by @{username}")


if __name__ == "__main__":
    main()
