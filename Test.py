import tkinter as tk
from tkinter import ttk, messagebox
import random
import json
import os
from datetime import datetime

# --- Sistem Elemen ---
element_system = {
    "Solar": {"weakness": "Taufan", "strength": "Halilintar", "color": "#ff6b35", "icon": "☀️"},
    "Taufan": {"weakness": "Gempa", "strength": "Solar", "color": "#4ecdc4", "icon": "🌪️"},
    "Gempa": {"weakness": "Halilintar", "strength": "Taufan", "color": "#8b4513", "icon": "🌋"},
    "Halilintar": {"weakness": "Solar", "strength": "Gempa", "color": "#ffd700", "icon": "⚡"}
}

# --- Expanded Player Classes ---
classes = {
    "Warrior": {
        "hp": 120, "attack": 15, "defense": 8, "speed": 5, "potions": 3, 
        "special_ability": "Power Strike", "elemen": "Halilintar",
        "description": "Tanky warrior with high HP and defense"
    },
    "Mage": {
        "hp": 80, "attack": 25, "defense": 3, "speed": 8, "potions": 4, 
        "special_ability": "Fireball", "elemen": "Solar",
        "description": "Powerful spellcaster with high attack"
    },
    "Archer": {
        "hp": 100, "attack": 18, "defense": 5, "speed": 12, "potions": 3, 
        "special_ability": "Multi-Shot", "elemen": "Gempa",
        "description": "Fast ranged attacker with high speed"
    },
    "Rogue": {
        "hp": 90, "attack": 20, "defense": 4, "speed": 15, "potions": 3, 
        "special_ability": "Backstab", "elemen": "Taufan",
        "description": "Agile assassin with critical strikes"
    }
}

# --- Enemy Types ---
enemy_types = {
    "Goblin": {"hp_range": (20, 30), "attack_range": (4, 8), "defense_range": (2, 4), "xp": 15, "gold": 5, "elemen": "Gempa"},
    "Orc": {"hp_range": (40, 60), "attack_range": (8, 12), "defense_range": (5, 8), "xp": 25, "gold": 10, "elemen": "Gempa"},
    "Bandit": {"hp_range": (30, 45), "attack_range": (6, 10), "defense_range": (3, 6), "xp": 20, "gold": 8, "elemen": "Taufan"},
    "Slime": {"hp_range": (25, 35), "attack_range": (3, 6), "defense_range": (1, 3), "xp": 10, "gold": 3, "elemen": "Solar"},
    "Skeleton": {"hp_range": (35, 50), "attack_range": (7, 11), "defense_range": (4, 7), "xp": 22, "gold": 7, "elemen": "Halilintar"},
    "Dragon": {"hp_range": (100, 150), "attack_range": (15, 25), "defense_range": (10, 15), "xp": 100, "gold": 50, "elemen": "Solar"},
    "Elemental": {"hp_range": (50, 70), "attack_range": (10, 15), "defense_range": (6, 9), "xp": 35, "gold": 15, "elemen": "Random"}
}

# --- Items Shop ---
shop_items = {
    "Healing Potion": {"price": 10, "type": "consumable", "effect": "heal"},
    "Strength Elixir": {"price": 20, "type": "consumable", "effect": "strength"},
    "Bomb": {"price": 15, "type": "consumable", "effect": "damage"},
    "Iron Sword": {"price": 50, "type": "weapon", "attack_bonus": 5},
    "Steel Armor": {"price": 60, "type": "armor", "defense_bonus": 5},
    "Magic Amulet": {"price": 80, "type": "accessory", "hp_bonus": 20},
    "Elemental Crystal": {"price": 100, "type": "special", "effect": "element_boost"},
    "Phoenix Down": {"price": 150, "type": "consumable", "effect": "revive"}
}

# --- Elemental Skills ---
elemental_skills = {
    "Solar": ["Tembakan Solar", "Pedang Solar", "Tembakan Solar Maksimal"],
    "Taufan": ["Pelindung Taufan", "Puting Beliung", "Naga Taufan"],
    "Gempa": ["Tanah Tinggi", "Golem Tanah", "Naga Tanah"],
    "Halilintar": ["Pedang Halilintar", "Tebasan Kilat", "Hujan Halilintar"]
}

class RPGGame:
    def __init__(self):
        self.initialize_game()
        
    def initialize_game(self):
        # Player setup
        self.player = {
            "name": "Hero",
            "class": None,
            "elemen": None,
            "hp": 0,
            "max_hp": 0,
            "attack": 0,
            "base_attack": 0,
            "defense": 0,
            "base_defense": 0,
            "speed": 0,
            "level": 1,
            "xp": 0,
            "xp_to_next": 100,
            "gold": 50,
            "inventory": {
                "Healing Potion": 3,
                "Strength Elixir": 1,
                "Bomb": 1
            },
            "equipment": {
                "weapon": None,
                "armor": None,
                "accessory": None
            },
            "buff_turns": 0,
            "special_cooldown": 0,
            "elemental_charge": 0,
            "skills": [],
            "quests": [],
            "location": "Forest",
            "element_mastery": {"Solar": 0, "Taufan": 0, "Gempa": 0, "Halilintar": 0}
        }

        # Enemy setup
        self.enemy = {
            "name": "Goblin",
            "hp": 0,
            "max_hp": 0,
            "attack": 0,
            "defense": 0,
            "level": 1,
            "type": "Goblin",
            "elemen": None,
            "gold": 0
        }

        # Game state
        self.game_state = {
            "current_turn": "player",
            "battle_log": [],
            "game_active": True,
            "boss_defeated": False,
            "day": 1,
            "elemental_events": []
        }
        
        # GUI references
        self.root = None
        self.player_hp_label = None
        self.enemy_hp_label = None
        self.player_hp_bar = None
        self.enemy_hp_bar = None
        self.attack_button = None
        self.special_button = None
        self.elemental_button = None
        self.heal_button = None
        self.item_button = None
        self.flee_button = None
        self.log_text = None
        self.gold_label = None
        self.day_label = None
        self.location_label = None
        self.element_label = None

    def calculate_element_advantage(self, attacker_element, defender_element):
        if not attacker_element or not defender_element:
            return 1.0
        
        element_info = element_system[attacker_element]
        if element_info["strength"] == defender_element:
            return 1.5  # Advantage
        elif element_info["weakness"] == defender_element:
            return 0.5  # Disadvantage
        return 1.0  # Neutral

    def get_element_color(self, element):
        return element_system.get(element, {}).get("color", "white")

    def get_element_icon(self, element):
        return element_system.get(element, {}).get("icon", "⚡")

    def update_status(self):
        if self.player_hp_bar:
            self.player_hp_bar["maximum"] = self.player["max_hp"]
            self.player_hp_bar["value"] = self.player["hp"]
            self.enemy_hp_bar["maximum"] = self.enemy["max_hp"]
            self.enemy_hp_bar["value"] = self.enemy["hp"]

            element_icon = self.get_element_icon(self.player["elemen"])
            self.player_hp_label.config(
                text=f"{element_icon} {self.player['name']} ({self.player['class']}) - Lvl {self.player['level']} | HP: {self.player['hp']}/{self.player['max_hp']} | XP: {self.player['xp']}/{self.player['xp_to_next']}"
            )
            
            enemy_element_icon = self.get_element_icon(self.enemy["elemen"])
            self.enemy_hp_label.config(
                text=f"{enemy_element_icon} {self.enemy['name']} (Lvl {self.enemy['level']}) HP: {self.enemy['hp']}/{self.enemy['max_hp']}"
            )
            
            self.gold_label.config(text=f"Gold: {self.player['gold']}")
            self.day_label.config(text=f"Day: {self.game_state['day']}")
            self.location_label.config(text=f"Location: {self.player['location']}")
            self.element_label.config(text=f"Element: {self.player['elemen']} | Charge: {self.player['elemental_charge']}/100")

    def log_message(self, message):
        if self.log_text:
            self.log_text.config(state="normal")
            self.log_text.insert(tk.END, message + "\n")
            self.log_text.config(state="disabled")
            self.log_text.see(tk.END)
            self.game_state["battle_log"].append(message)

    def calculate_damage(self, attacker, defender, is_special=False, is_elemental=False):
        base_damage = attacker["attack"]
        if is_special:
            base_damage = int(base_damage * 1.5)
        
        # Element advantage calculation
        element_multiplier = 1.0
        if is_elemental and attacker.get("elemen") and defender.get("elemen"):
            element_multiplier = self.calculate_element_advantage(attacker["elemen"], defender["elemen"])
        
        damage = max(1, int((base_damage - defender["defense"] // 2) * element_multiplier))
        
        # Critical hit chance based on speed
        crit_chance = attacker["speed"] / 100
        if random.random() < crit_chance:
            damage = int(damage * 1.5)
            return damage, True, element_multiplier
        
        return damage, False, element_multiplier

    def attack(self, is_special=False, is_elemental=False):
        if not self.game_state["game_active"] or self.player["hp"] <= 0 or self.enemy["hp"] <= 0:
            return

        if is_special and self.player["special_cooldown"] > 0:
            self.log_message(f"❌ {classes[self.player['class']]['special_ability']} is on cooldown for {self.player['special_cooldown']} more turns!")
            return

        if is_elemental and self.player["elemental_charge"] < 30:
            self.log_message("❌ Not enough elemental charge! Need 30 charge.")
            return

        damage, is_critical, element_multiplier = self.calculate_damage(self.player, self.enemy, is_special, is_elemental)
        self.enemy["hp"] = max(0, self.enemy["hp"] - damage)
        
        # Element charge generation
        if not is_elemental:
            self.player["elemental_charge"] = min(100, self.player["elemental_charge"] + 10)
        
        if is_special:
            ability_name = classes[self.player["class"]]["special_ability"]
            self.log_message(f"✨ You use {ability_name} on the {self.enemy['name']} for {damage} damage!")
            self.player["special_cooldown"] = 3
        elif is_elemental:
            self.player["elemental_charge"] -= 30
            skill_name = random.choice(elemental_skills[self.player["elemen"]])
            element_effect = ""
            if element_multiplier > 1:
                element_effect = " 🎯 EFFECTIVE!"
            elif element_multiplier < 1:
                element_effect = " 💤 INEFFECTIVE!"
            self.log_message(f"{self.get_element_icon(self.player['elemen'])} You use {skill_name} for {damage} damage!{element_effect}")
        else:
            crit_text = " 💥 CRITICAL!" if is_critical else ""
            self.log_message(f"⚔️ You strike the {self.enemy['name']} for {damage} damage!{crit_text}")

        # Handle element mastery
        if is_elemental:
            self.player["element_mastery"][self.player["elemen"]] += 1

        # Handle buffs
        if self.player["buff_turns"] > 0:
            self.player["buff_turns"] -= 1
            if self.player["buff_turns"] == 0:
                self.player["attack"] = self.player["base_attack"]
                self.log_message("💨 Your Strength Elixir effect wore off!")

        # Check if enemy is defeated
        if self.enemy["hp"] <= 0:
            gold_earned = self.enemy["gold"]
            xp_earned = enemy_types[self.enemy["type"]]["xp"] * self.enemy["level"]
            self.player["gold"] += gold_earned
            
            self.log_message(f"🎉 You defeated the {self.enemy['name']}! 🎉")
            self.log_message(f"💰 You found {gold_earned} gold!")
            
            self.gain_xp(xp_earned)
            self.check_quest_progress(self.enemy["type"])
            
            # Chance to find item
            if random.random() < 0.3:
                found_item = random.choice(list(shop_items.keys())[:3])
                self.player["inventory"][found_item] = self.player["inventory"].get(found_item, 0) + 1
                self.log_message(f"🎁 You found a {found_item}!")
            
            # Elemental mastery reward
            if is_elemental:
                self.player["element_mastery"][self.player["elemen"]] += 5
                self.log_message(f"🌟 +5 {self.player['elemen']} Mastery!")
            
            self.spawn_enemy()
        else:
            self.enemy_turn()

        self.update_status()

    def use_elemental_skill(self):
        self.attack(is_special=False, is_elemental=True)

    def heal(self):
        if not self.game_state["game_active"] or self.player["hp"] <= 0 or self.enemy["hp"] <= 0:
            return

        if self.player["inventory"].get("Healing Potion", 0) > 0:
            heal_amount = random.randint(15, 25)
            self.player["hp"] = min(self.player["max_hp"], self.player["hp"] + heal_amount)
            self.player["inventory"]["Healing Potion"] -= 1
            self.log_message(f"🧪 You used a Healing Potion and recovered {heal_amount} HP!")
            
            if self.player["inventory"]["Healing Potion"] == 0:
                del self.player["inventory"]["Healing Potion"]
        else:
            self.log_message("No Healing Potions left!")
            return

        if self.enemy["hp"] > 0:
            self.enemy_turn()

        self.update_status()

    def use_item(self, item):
        if self.player["inventory"].get(item, 0) <= 0:
            self.log_message(f"❌ You have no {item} left!")
            return

        if item == "Healing Potion":
            self.heal()
        elif item == "Strength Elixir":
            self.player["attack"] = self.player["base_attack"] + 5
            self.player["buff_turns"] = 3
            self.player["inventory"][item] -= 1
            self.log_message("💪 You used a Strength Elixir! Attack boosted for 3 turns.")
            if self.enemy["hp"] > 0:
                self.enemy_turn()
        elif item == "Bomb":
            damage = random.randint(15, 25)
            self.enemy["hp"] = max(0, self.enemy["hp"] - damage)
            self.player["inventory"][item] -= 1
            self.log_message(f"💣 You threw a Bomb! {self.enemy['name']} took {damage} damage!")
            if self.enemy["hp"] > 0:
                self.enemy_turn()
            else:
                gold_earned = self.enemy["gold"]
                xp_earned = enemy_types[self.enemy["type"]]["xp"] * self.enemy["level"]
                self.player["gold"] += gold_earned
                
                self.log_message(f"🎉 You defeated the {self.enemy['name']}! 🎉")
                self.log_message(f"💰 You found {gold_earned} gold!")
                
                self.gain_xp(xp_earned)
                self.check_quest_progress(self.enemy["type"])
                self.spawn_enemy()
        elif item == "Elemental Crystal":
            self.player["elemental_charge"] = 100
            self.player["inventory"][item] -= 1
            self.log_message(f"💎 Elemental Crystal used! Charge set to 100!")
        elif item == "Phoenix Down":
            if self.player["hp"] <= 0:
                self.player["hp"] = self.player["max_hp"] // 2
                self.player["inventory"][item] -= 1
                self.log_message("🕊️ Phoenix Down used! You've been revived!")
                self.game_state["game_active"] = True
                self.enable_buttons()
            else:
                self.log_message("❌ You can only use Phoenix Down when defeated!")

        # Clean up inventory if item count reaches zero
        if self.player["inventory"].get(item, 0) == 0:
            del self.player["inventory"][item]
            
        self.update_status()

    def enemy_turn(self):
        if self.enemy["hp"] > 0 and self.game_state["game_active"]:
            # Enemy has chance to use elemental attack
            use_elemental = random.random() < 0.3 and self.enemy["elemen"]
            
            damage, is_critical, element_multiplier = self.calculate_damage(self.enemy, self.player, is_elemental=use_elemental)
            self.player["hp"] = max(0, self.player["hp"] - damage)
            
            crit_text = " 💥 CRITICAL!" if is_critical else ""
            if use_elemental:
                element_effect = ""
                if element_multiplier > 1:
                    element_effect = " 🎯 EFFECTIVE!"
                elif element_multiplier < 1:
                    element_effect = " 💤 INEFFECTIVE!"
                self.log_message(f"{self.get_element_icon(self.enemy['elemen'])} {self.enemy['name']} uses elemental attack for {damage} damage!{element_effect}{crit_text}")
            else:
                self.log_message(f"The {self.enemy['name']} hits you for {damage} damage!{crit_text}")

            if self.player["hp"] <= 0:
                self.log_message("💀 You were defeated... Game Over.")
                self.end_game()

    def end_game(self):
        self.game_state["game_active"] = False
        self.disable_buttons()
        
        # Show game over screen
        game_over_win = tk.Toplevel(self.root)
        game_over_win.title("Game Over")
        game_over_win.geometry("300x250")
        game_over_win.configure(bg="#2c2f33")
        
        tk.Label(game_over_win, text="GAME OVER", font=("Arial", 18, "bold"), 
                 fg="red", bg="#2c2f33").pack(pady=20)
        tk.Label(game_over_win, text=f"You reached Level {self.player['level']}", 
                 font=("Arial", 12), fg="white", bg="#2c2f33").pack(pady=5)
        tk.Label(game_over_win, text=f"Defeated {self.game_state['day'] - 1} enemies", 
                 font=("Arial", 12), fg="white", bg="#2c2f33").pack(pady=5)
        
        # Show elemental mastery
        best_element = max(self.player["element_mastery"], key=self.player["element_mastery"].get)
        tk.Label(game_over_win, text=f"Best Element: {best_element}", 
                 font=("Arial", 12), fg="white", bg="#2c2f33").pack(pady=5)
        
        tk.Button(game_over_win, text="New Game", command=self.restart_game,
                  bg="#4caf50", fg="white", font=("Arial", 12)).pack(pady=10)

    def disable_buttons(self):
        buttons = [self.attack_button, self.special_button, self.elemental_button, 
                  self.heal_button, self.item_button, self.flee_button]
        for btn in buttons:
            if btn:
                btn.config(state="disabled")

    def enable_buttons(self):
        if self.game_state["game_active"]:
            buttons = [self.attack_button, self.special_button, self.elemental_button,
                      self.heal_button, self.item_button, self.flee_button]
            for btn in buttons:
                if btn:
                    btn.config(state="normal")

    def restart_game(self):
        if self.root:
            self.root.destroy()
        self.initialize_game()
        self.show_class_selection()

    def gain_xp(self, amount):
        self.player["xp"] += amount
        self.log_message(f"⭐ You gained {amount} XP!")

        if self.player["xp"] >= self.player["xp_to_next"]:
            self.level_up()

    def level_up(self):
        self.player["level"] += 1
        self.player["xp"] = 0
        self.player["xp_to_next"] = int(self.player["xp_to_next"] * 1.5)
        
        # Stat increases
        hp_increase = random.randint(10, 20)
        self.player["max_hp"] += hp_increase
        self.player["hp"] = self.player["max_hp"]
        
        self.player["base_attack"] += 2
        self.player["base_defense"] += 1
        self.player["attack"] = self.player["base_attack"]
        self.player["defense"] = self.player["base_defense"]
        
        # Add potion on level up
        self.player["inventory"]["Healing Potion"] = self.player["inventory"].get("Healing Potion", 0) + 1
        
        # Chance to learn new elemental skill
        if self.player["level"] % 3 == 0 and len(self.player["skills"]) < len(elemental_skills[self.player["elemen"]]):
            available_skills = [s for s in elemental_skills[self.player["elemen"]] if s not in self.player["skills"]]
            if available_skills:
                new_skill = random.choice(available_skills)
                self.player["skills"].append(new_skill)
                self.log_message(f"🎓 You learned a new skill: {new_skill}!")
        
        self.log_message(f"⬆️ Level Up! You are now Level {self.player['level']}!")
        self.log_message(f"❤️ Max HP increased by {hp_increase}!")
        self.log_message(f"⚔️ Attack increased to {self.player['attack']}!")
        self.log_message(f"🛡️ Defense increased to {self.player['defense']}!")
        self.log_message(f"🧪 You received a Healing Potion!")

    def spawn_enemy(self):
        self.game_state["day"] += 1
        
        # Elemental events based on day
        if self.game_state["day"] % 7 == 0:
            self.trigger_elemental_event()
        
        # Chance to spawn boss every 5 days
        if self.game_state["day"] % 5 == 0 and not self.game_state["boss_defeated"]:
            enemy_type = "Dragon"
            self.game_state["boss_defeated"] = True
        else:
            enemy_type = random.choice(list(enemy_types.keys()))
        
        enemy_stats = enemy_types[enemy_type]
        
        self.enemy["name"] = enemy_type
        self.enemy["type"] = enemy_type
        
        # Set enemy element
        if enemy_type == "Elemental":
            self.enemy["elemen"] = random.choice(list(element_system.keys()))
        else:
            self.enemy["elemen"] = enemy_stats["elemen"]
        
        self.enemy["level"] = max(1, self.player["level"] - 1 + random.randint(0, 2))
        self.enemy["max_hp"] = random.randint(*enemy_stats["hp_range"]) + (self.enemy["level"] * 5)
        self.enemy["hp"] = self.enemy["max_hp"]
        self.enemy["attack"] = random.randint(*enemy_stats["attack_range"]) + (self.enemy["level"] * 2)
        self.enemy["defense"] = random.randint(*enemy_stats["defense_range"]) + (self.enemy["level"] * 1)
        self.enemy["gold"] = enemy_stats["gold"] + (self.enemy["level"] * 2)

        self.log_message(f"\n⚔️ Day {self.game_state['day']}: A {self.enemy['name']} (Lvl {self.enemy['level']}) approaches!\n")
        self.log_message(f"Element: {self.get_element_icon(self.enemy['elemen'])} {self.enemy['elemen']}")
        
        # Show element advantage info
        advantage = self.calculate_element_advantage(self.player["elemen"], self.enemy["elemen"])
        if advantage > 1:
            self.log_message(f"🎯 Your element is effective against {self.enemy['elemen']}!")
        elif advantage < 1:
            self.log_message(f"💤 Your element is weak against {self.enemy['elemen']}!")
        
        # Reset special cooldown
        self.player["special_cooldown"] = max(0, self.player["special_cooldown"] - 1)
        
        self.update_status()

    def trigger_elemental_event(self):
        event_element = random.choice(list(element_system.keys()))
        events = {
            "Solar": "A solar eclipse empowers Solar element!",
            "Taufan": "A great storm enhances Taufan element!", 
            "Gempa": "Earth tremors boost Gempa element!",
            "Halilintar": "Lightning storm strengthens Halilintar element!"
        }
        
        event_msg = events[event_element]
        self.log_message(f"\n🌠 ELEMENTAL EVENT: {event_msg}")
        
        # Bonus for players using matching element
        if self.player["elemen"] == event_element:
            self.player["elemental_charge"] = 100
            self.player["attack"] += 5
            self.log_message(f"🌟 Your {event_element} powers are enhanced! +5 Attack, Full Charge!")
            self.game_state["elemental_events"].append(f"Day {self.game_state['day']}: {event_element} Event")

    def open_inventory(self):
        inv_win = tk.Toplevel(self.root)
        inv_win.title("Inventory")
        inv_win.geometry("450x500")
        inv_win.configure(bg="#2c2f33")

        # Inventory items
        tk.Label(inv_win, text="Inventory", font=("Arial", 16, "bold"), 
                 bg="#2c2f33", fg="white").pack(pady=10)
        
        inventory_frame = tk.Frame(inv_win, bg="#2c2f33")
        inventory_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        if not self.player["inventory"]:
            tk.Label(inventory_frame, text="Your inventory is empty!", 
                     font=("Arial", 12), bg="#2c2f33", fg="white").pack()
        else:
            for item, qty in self.player["inventory"].items():
                item_frame = tk.Frame(inventory_frame, bg="#2c2f33")
                item_frame.pack(fill="x", pady=2)
                
                tk.Label(item_frame, text=f"{item} x{qty}", font=("Arial", 12), 
                         bg="#2c2f33", fg="white", width=20, anchor="w").pack(side="left")
                
                use_btn = tk.Button(item_frame, text="Use", width=8,
                                  command=lambda i=item: [self.use_item(i), inv_win.destroy()])
                use_btn.pack(side="right", padx=5)
        
        # Equipment
        tk.Label(inv_win, text="Equipment", font=("Arial", 14, "bold"), 
                 bg="#2c2f33", fg="white").pack(pady=(20, 5))
        
        equipment_frame = tk.Frame(inv_win, bg="#2c2f33")
        equipment_frame.pack(fill="x", padx=20, pady=10)
        
        for slot, item in self.player["equipment"].items():
            slot_name = slot.capitalize()
            item_name = item if item else "Empty"
            tk.Label(equipment_frame, text=f"{slot_name}: {item_name}", 
                     font=("Arial", 11), bg="#2c2f33", fg="white").pack(anchor="w")
        
        # Elemental Mastery
        tk.Label(inv_win, text="Elemental Mastery", font=("Arial", 14, "bold"), 
                 bg="#2c2f33", fg="white").pack(pady=(20, 5))
        
        mastery_frame = tk.Frame(inv_win, bg="#2c2f33")
        mastery_frame.pack(fill="x", padx=20, pady=10)
        
        for element, mastery in self.player["element_mastery"].items():
            color = self.get_element_color(element)
            icon = self.get_element_icon(element)
            tk.Label(mastery_frame, text=f"{icon} {element}: {mastery}", 
                     font=("Arial", 10), bg="#2c2f33", fg=color).pack(anchor="w")

    def open_skills_window(self):
        skills_win = tk.Toplevel(self.root)
        skills_win.title("Elemental Skills")
        skills_win.geometry("300x400")
        skills_win.configure(bg="#2c2f33")

        tk.Label(skills_win, text="Elemental Skills", font=("Arial", 16, "bold"), 
                 bg="#2c2f33", fg="white").pack(pady=10)
        
        # Current element skills
        current_element = self.player["elemen"]
        element_color = self.get_element_color(current_element)
        
        tk.Label(skills_win, text=f"Current Element: {current_element}", 
                 font=("Arial", 12, "bold"), bg="#2c2f33", fg=element_color).pack(pady=5)
        
        skills_frame = tk.Frame(skills_win, bg="#2c2f33")
        skills_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        for skill in elemental_skills[current_element]:
            learned = skill in self.player["skills"]
            status = "✅ Learned" if learned else "❌ Not Learned"
            color = "lightgreen" if learned else "gray"
            tk.Label(skills_frame, text=f"{skill} - {status}", 
                     font=("Arial", 10), bg="#2c2f33", fg=color).pack(anchor="w", pady=2)
        
        tk.Label(skills_win, text="Use Elemental Skill in battle (Cost: 30 charge)", 
                 font=("Arial", 9), bg="#2c2f33", fg="lightblue").pack(pady=10)

    def open_shop(self):
        shop_win = tk.Toplevel(self.root)
        shop_win.title("Shop")
        shop_win.geometry("400x500")
        shop_win.configure(bg="#2c2f33")

        tk.Label(shop_win, text="Shop", font=("Arial", 16, "bold"), 
                 bg="#2c2f33", fg="gold").pack(pady=10)
        
        tk.Label(shop_win, text=f"Your Gold: {self.player['gold']}", font=("Arial", 12), 
                 bg="#2c2f33", fg="white").pack(pady=5)

        for item, details in shop_items.items():
            item_frame = tk.Frame(shop_win, bg="#2c2f33")
            item_frame.pack(fill="x", padx=20, pady=5)
            
            item_text = f"{item} - {details['price']} gold"
            if details['type'] == 'weapon':
                item_text += f" (ATK+{details['attack_bonus']})"
            elif details['type'] == 'armor':
                item_text += f" (DEF+{details['defense_bonus']})"
            elif details['type'] == 'accessory':
                item_text += f" (HP+{details['hp_bonus']})"
            
            tk.Label(item_frame, text=item_text, font=("Arial", 11), 
                     bg="#2c2f33", fg="white", width=30, anchor="w").pack(side="left")
            
            buy_btn = tk.Button(item_frame, text="Buy", width=8,
                              command=lambda i=item, d=details: self.buy_item(i, d, shop_win))
            buy_btn.pack(side="right")

    def buy_item(self, item, details, shop_window):
        if self.player["gold"] >= details["price"]:
            self.player["gold"] -= details["price"]
            
            if details["type"] == "consumable" or details["type"] == "special":
                self.player["inventory"][item] = self.player["inventory"].get(item, 0) + 1
                self.log_message(f"🛒 You bought a {item}!")
            else:
                slot = "weapon" if details["type"] == "weapon" else "armor" if details["type"] == "armor" else "accessory"
                self.player["equipment"][slot] = item
                
                if "attack_bonus" in details:
                    self.player["base_attack"] += details["attack_bonus"]
                if "defense_bonus" in details:
                    self.player["base_defense"] += details["defense_bonus"]
                if "hp_bonus" in details:
                    self.player["max_hp"] += details["hp_bonus"]
                
                self.player["attack"] = self.player["base_attack"]
                self.player["defense"] = self.player["base_defense"]
                self.log_message(f"🛒 You bought and equipped {item}!")
            
            self.update_status()
            shop_window.destroy()
            self.open_shop()
        else:
            messagebox.showwarning("Not Enough Gold", "You don't have enough gold to buy this item!")

    def flee(self):
        if random.random() < 0.7:
            self.log_message("🏃‍♂️ You successfully fled from battle!")
            self.spawn_enemy()
        else:
            self.log_message("❌ You failed to flee!")
            self.enemy_turn()
        self.update_status()

    def check_quest_progress(self, enemy_type):
        if enemy_type == "Dragon":
            self.log_message("🏆 QUEST COMPLETE: Dragon Slayer! You've defeated the mighty dragon!")
            self.player["gold"] += 100
            self.log_message("💰 You received 100 gold as reward!")

    def save_game(self):
        save_data = {
            "player": self.player,
            "game_state": self.game_state,
            "timestamp": datetime.now().isoformat()
        }
        
        with open("rpg_save.json", "w") as f:
            json.dump(save_data, f)
        
        self.log_message("💾 Game saved successfully!")

    def load_game(self):
        if os.path.exists("rpg_save.json"):
            with open("rpg_save.json", "r") as f:
                save_data = json.load(f)
            
            self.player.update(save_data["player"])
            self.game_state.update(save_data["game_state"])
            
            self.log_message("📂 Game loaded successfully!")
            self.update_status()
            self.spawn_enemy()
        else:
            messagebox.showinfo("No Save File", "No saved game found!")

    def game_window(self):
        self.root = tk.Tk()
        self.root.title("⚔️ Enhanced RPG with Element System ⚔️")
        self.root.geometry("750x750")
        self.root.configure(bg="#2c2f33")

        # Header with game info
        header_frame = tk.Frame(self.root, bg="#2c2f33")
        header_frame.pack(pady=10)
        
        self.gold_label = tk.Label(header_frame, text="", font=("Arial", 10), fg="gold", bg="#2c2f33")
        self.gold_label.pack(side="left", padx=10)
        
        self.day_label = tk.Label(header_frame, text="", font=("Arial", 10), fg="white", bg="#2c2f33")
        self.day_label.pack(side="left", padx=10)
        
        self.location_label = tk.Label(header_frame, text="", font=("Arial", 10), fg="white", bg="#2c2f33")
        self.location_label.pack(side="left", padx=10)
        
        self.element_label = tk.Label(header_frame, text="", font=("Arial", 10), fg="lightblue", bg="#2c2f33")
        self.element_label.pack(side="left", padx=10)

        # Enemy
        enemy_frame = tk.Frame(self.root, bg="#2c2f33")
        enemy_frame.pack(pady=10)
        self.enemy_hp_label = tk.Label(enemy_frame, text="", font=("Arial", 12, "bold"), fg="red", bg="#2c2f33")
        self.enemy_hp_label.pack()
        self.enemy_hp_bar = ttk.Progressbar(enemy_frame, length=300, maximum=100)
        self.enemy_hp_bar.pack(pady=5)

        # Player
        player_frame = tk.Frame(self.root, bg="#2c2f33")
        player_frame.pack(pady=10)
        self.player_hp_label = tk.Label(player_frame, text="", font=("Arial", 12, "bold"), fg="lightgreen", bg="#2c2f33")
        self.player_hp_label.pack()
        self.player_hp_bar = ttk.Progressbar(player_frame, length=300, maximum=100)
        self.player_hp_bar.pack(pady=5)

        # Action Buttons
        button_frame = tk.Frame(self.root, bg="#2c2f33")
        button_frame.pack(pady=15)
        
        self.attack_button = tk.Button(button_frame, text="⚔️ Attack", width=12, height=2,
                                      bg="#ff4c4c", fg="white", font=("Arial", 11), 
                                      command=lambda: self.attack(False))
        self.attack_button.grid(row=0, column=0, padx=5, pady=5)
        
        self.special_button = tk.Button(button_frame, text=f"✨ Special", width=12, height=2,
                                       bg="#9c27b0", fg="white", font=("Arial", 11),
                                       command=lambda: self.attack(True))
        self.special_button.grid(row=0, column=1, padx=5, pady=5)
        
        self.elemental_button = tk.Button(button_frame, text="🌠 Elemental", width=12, height=2,
                                        bg="#ff9800", fg="white", font=("Arial", 11),
                                        command=self.use_elemental_skill)
        self.elemental_button.grid(row=0, column=2, padx=5, pady=5)
        
        self.heal_button = tk.Button(button_frame, text="🧪 Heal", width=12, height=2,
                                    bg="#4caf50", fg="white", font=("Arial", 11), command=self.heal)
        self.heal_button.grid(row=1, column=0, padx=5, pady=5)
        
        self.item_button = tk.Button(button_frame, text="🎒 Inventory", width=12, height=2,
                                    bg="#ffa500", fg="white", font=("Arial", 11), command=self.open_inventory)
        self.item_button.grid(row=1, column=1, padx=5, pady=5)
        
        self.flee_button = tk.Button(button_frame, text="🏃‍♂️ Flee", width=12, height=2,
                                   bg="#607d8b", fg="white", font=("Arial", 11), command=self.flee)
        self.flee_button.grid(row=1, column=2, padx=5, pady=5)

        # Additional Buttons
        extra_button_frame = tk.Frame(self.root, bg="#2c2f33")
        extra_button_frame.pack(pady=10)
        
        skills_button = tk.Button(extra_button_frame, text="📚 Skills", width=12, height=1,
                                 bg="#2196f3", fg="white", font=("Arial", 10), command=self.open_skills_window)
        skills_button.pack(side="left", padx=5)
        
        shop_button = tk.Button(extra_button_frame, text="🛒 Shop", width=12, height=1,
                               bg="#ffd700", fg="black", font=("Arial", 10), command=self.open_shop)
        shop_button.pack(side="left", padx=5)

        # Game Menu
        menu_frame = tk.Frame(self.root, bg="#2c2f33")
        menu_frame.pack(pady=10)
        
        save_button = tk.Button(menu_frame, text="💾 Save", width=10,
                               bg="#2196f3", fg="white", font=("Arial", 10), command=self.save_game)
        save_button.pack(side="left", padx=5)
        
        load_button = tk.Button(menu_frame, text="📂 Load", width=10,
                               bg="#2196f3", fg="white", font=("Arial", 10), command=self.load_game)
        load_button.pack(side="left", padx=5)

        # Log
        log_frame = tk.Frame(self.root)
        log_frame.pack(pady=10, fill="both", expand=True, padx=20)
        
        self.log_text = tk.Text(log_frame, height=15, width=80, state="disabled", wrap="word",
                               bg="#1a1a1a", fg="white", font=("Consolas", 9))
        
        scrollbar = tk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Initialize game
        self.log_message("⚔️ Welcome to the Enhanced RPG with Element System! ⚔️")
        self.log_message(f"You chose {self.player['class']} class!")
        self.log_message(f"Element: {self.get_element_icon(self.player['elemen'])} {self.player['elemen']}")
        self.log_message(f"Special Ability: {classes[self.player['class']]['special_ability']}")
        self.log_message("A wild enemy appears!\n")
        
        self.spawn_enemy()
        self.update_status()

        self.root.mainloop()

    def show_class_selection(self):
        class_window = tk.Tk()
        class_window.title("Choose Your Class")
        class_window.geometry("550x500")
        class_window.configure(bg="#2c2f33")

        title_label = tk.Label(class_window, text="Choose Your Class", font=("Arial", 18, "bold"),
                               fg="white", bg="#2c2f33")
        title_label.pack(pady=20)

        class_desc_frame = tk.Frame(class_window, bg="#2c2f33")
        class_desc_frame.pack(pady=10)

        class_description = tk.Label(class_desc_frame, text="Hover over a class to see details", 
                                    font=("Arial", 10), fg="lightblue", bg="#2c2f33", wraplength=500)
        class_description.pack()

        def start_game(chosen_class):
            stats = classes[chosen_class]
            self.player["class"] = chosen_class
            self.player["elemen"] = stats["elemen"]
            self.player["hp"] = stats["hp"]
            self.player["max_hp"] = stats["hp"]
            self.player["attack"] = stats["attack"]
            self.player["base_attack"] = stats["attack"]
            self.player["defense"] = stats["defense"]
            self.player["base_defense"] = stats["defense"]
            self.player["speed"] = stats["speed"]
            
            # Initialize elemental skills
            self.player["skills"] = [elemental_skills[stats["elemen"]][0]]  # Start with first skill

            class_window.destroy()
            self.game_window()

        for cls in classes.keys():
            stats = classes[cls]
            element_icon = self.get_element_icon(stats["elemen"])
            
            btn_frame = tk.Frame(class_window, bg="#2c2f33")
            btn_frame.pack(pady=5)
            
            btn = tk.Button(btn_frame,
                            text=f"{element_icon} {cls} | HP:{stats['hp']} ATK:{stats['attack']} DEF:{stats['defense']} SPD:{stats['speed']}",
                            width=50, height=1, font=("Arial", 11),
                            command=lambda c=cls: start_game(c))
            btn.pack()
            
            # Tooltip functionality
            def on_enter(e, c=cls):
                stats = classes[c]
                element_info = element_system[stats["elemen"]]
                desc = f"{c}: {stats['description']}\nElement: {stats['elemen']} | Strong vs: {element_info['strength']} | Weak vs: {element_info['weakness']}\nSpecial: {stats['special_ability']}"
                class_description.config(text=desc)
            
            def on_leave(e):
                class_description.config(text="Hover over a class to see details")
            
            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)

        class_window.mainloop()

# --- Start the game ---
if __name__ == "__main__":
    game = RPGGame()
    game.show_class_selection()