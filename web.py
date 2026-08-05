import streamlit as st
import requests
import random
import os
import base64

# Tworzymy folder avatars jeśli nie istnieje
os.makedirs("avatars", exist_ok=True)

st.set_page_config(page_title="ChaosDraft", page_icon="🎲", layout="wide")

# Funkcja pomocnicza do kodowania obrazka do base64 (potrzebne do CSS)
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Funkcja ustawiająca tło strony
def set_background():
    # Sprawdzamy czy istnieje nasz dedykowany obrazek tła w folderze avatars
    bg_path_jpg = os.path.join("avatars", "majkmeme.jpg")
    bg_path_png = os.path.join("avatars", "majkmeme.png")
    
    # Domyślne tło internetowe, jeśli pliku nie ma lokalnie
    bg_img_url = "https://images.contentstack.io/v3/assets/blt731acb42bb3d1659/blt42b3bf0c2e391cb4/5e964041b31a382c420fec36/Summoners_Rift_1.jpg"
    
    if os.path.exists(bg_path_jpg):
        bg_b64 = get_base64_of_bin_file(bg_path_jpg)
        bg_img_url = f"data:image/jpeg;base64,{bg_b64}"
    elif os.path.exists(bg_path_png):
        bg_b64 = get_base64_of_bin_file(bg_path_png)
        bg_img_url = f"data:image/png;base64,{bg_b64}"

    # Styl CSS
    page_bg_img = f"""
    <style>
    [data-testid="stAppViewContainer"] {{
        background-image: url("{bg_img_url}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    /* Przyciemniamy tło żeby interfejs był widoczny */
    [data-testid="stAppViewContainer"]::before {{
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background: rgba(0, 0, 0, 0.4);
        z-index: 0;
    }}
    .block-container {{
        position: relative;
        z-index: 1;
        background-color: rgba(14, 17, 23, 0.94);
        border-radius: 20px;
        padding: 1.5rem 2rem;
        margin-top: 1rem;
        border: 1px solid #c8aa6e;
        box-shadow: 0 0 25px rgba(200, 170, 110, 0.35);
    }}
    [data-testid="stHeader"] {{
        background: rgba(0,0,0,0);
    }}
    .small-item-img {{
        width: 36px; 
        height: 36px;
        border-radius: 6px;
        border: 1px solid #c8aa6e;
        box-shadow: 0 2px 4px rgba(0,0,0,0.5);
    }}
    .tooltip {{
        position: relative;
        display: inline-block;
        cursor: help;
        margin: 0; 
    }}
    .tooltip .tooltiptext {{
        visibility: hidden;
        width: max-content;
        max-width: 200px;
        background-color: rgba(15, 20, 25, 0.98);
        color: #fff;
        text-align: center;
        padding: 8px;
        border-radius: 8px;
        border: 1px solid #c8aa6e;
        position: absolute;
        z-index: 9999;
        bottom: 125%;
        left: 50%;
        transform: translateX(-50%);
        opacity: 0;
        transition: opacity 0.2s ease-in-out;
        box-shadow: 0px 8px 16px rgba(0,0,0,0.8);
    }}
    .tooltip:hover .tooltiptext {{
        visibility: visible;
        opacity: 1;
    }}
    .comp-img {{
        width: 24px;
        height: 24px;
        border-radius: 4px;
        border: 1px solid #777;
        margin: 2px;
    }}
    </style>
    """
    st.markdown(page_bg_img, unsafe_allow_html=True)

# Wywołujemy ustawienie tła na początku
set_background()

# Funkcja pobierająca awatary graczy
def get_avatar_b64(player_name):
    if not player_name:
        return None
    safe_name = player_name.strip().lower()
    for ext in ['png', 'jpg', 'jpeg']:
        path = os.path.join("avatars", f"{safe_name}.{ext}")
        if os.path.exists(path):
            with open(path, "rb") as img_file:
                mime_type = "image/jpeg" if ext in ['jpg', 'jpeg'] else "image/png"
                encoded = base64.b64encode(img_file.read()).decode()
                return f"data:{mime_type};base64,{encoded}"
    return None

# --- ŁADOWANIE DANYCH RIOT Z CACHE (1h) ---
@st.cache_data(ttl=3600)
def fetch_riot_data():
    versions = requests.get("https://ddragon.leagueoflegends.com/api/versions.json").json()
    target_version = versions[0] 
            
    base_url = f"https://ddragon.leagueoflegends.com/cdn/{target_version}/data/en_US"
    
    champions = requests.get(f"{base_url}/championFull.json").json()['data']
    all_item_data = requests.get(f"{base_url}/item.json").json()['data']
    
    unique_items_dict = {}
    classic_items_dict = {}
    support_items_pool = {}
    support_names = ["Celestial Opposition", "Dream Maker", "Zaz'Zak's Realmspike", "Bloodsong", "Solstice Sleigh", "World Atlas", "Bounty of Worlds"]
    
    # Wstrzykujemy zapomniane przedmioty TYLKO do puli Classic
    old_items_to_inject = [
        {"id": "3128", "name": "Deathfire Grasp", "image": {"full": "3128.png"}, "tags": ["SpellDamage", "CooldownReduction"], "from": []},
        {"id": "3092", "name": "Heart of Gold", "image": {"full": "3092.png"}, "tags": ["Health"], "from": []},
        {"id": "3096", "name": "Philosopher's Stone", "image": {"full": "3096.png"}, "tags": ["HealthRegen", "ManaRegen"], "from": []},
        {"id": "3126", "name": "Madred's Bloodrazor", "image": {"full": "3126.png"}, "tags": ["Damage", "AttackSpeed", "Armor"], "from": []},
        {"id": "3005", "name": "Atma's Impaler", "image": {"full": "3005.png"}, "tags": ["Armor", "CriticalStrike", "Damage"], "from": []},
        {"id": "3131", "name": "Sword of the Divine", "image": {"full": "3131.png"}, "tags": ["AttackSpeed"], "from": []},
        {"id": "3152", "name": "Will of the Ancients", "image": {"full": "3152.png"}, "tags": ["SpellDamage", "SpellVamp"], "from": []},
        {"id": "3001", "name": "Abyssal Scepter", "image": {"full": "3001.png"}, "tags": ["SpellDamage", "SpellBlock"], "from": []}
    ]
    for item in old_items_to_inject:
        classic_items_dict[item['name']] = item
        all_item_data[item['id']] = item # Tylko do HTML tooltipa
    
    classic_item_keywords = [
        "Infinity Edge", "Rabadon's Deathcap", "Warmog's Armor", "Trinity Force", "The Bloodthirster", 
        "Frozen Heart", "Sunfire Aegis", "Guardian Angel", "Lich Bane", "Nashor's Tooth", 
        "Rylai's Crystal Scepter", "Void Staff", "Thornmail", "Spirit Visage", "Banshee's Veil",
        "Phantom Dancer", "Blade of the Ruined King", "Force of Nature", "Randuin's Omen", 
        "Locket of the Iron Solari", "Black Cleaver", "Rod of Ages", "Zhonya's Hourglass",
        "Abyssal Mask", "Guinsoo's Rageblade", "Wit's End", "Mejai's Soulstealer", "Archangel's Staff",
        "Manamune", "Warmog"
    ]
    
    for item_id, item in all_item_data.items():
        is_sr = item.get('maps', {}).get('11', False) == True
        in_store = item.get('inStore', True)
        purchasable = item.get('gold', {}).get('purchasable', True)
        cost = item.get('gold', {}).get('total', 0)
        required_ally = item.get('requiredAlly', None)
        
        # Pula Support dla Standardu
        if is_sr and (item['name'] in support_names or ('GoldPer' in item.get('tags', []) and cost in [0, 400])):
            item['id'] = item_id
            support_items_pool[item['name']] = item
            
        # Pule ogólne
        if is_sr and in_store and purchasable and cost > 2000 and required_ally is None:
            if item['name'] not in unique_items_dict:
                item['id'] = item_id
                unique_items_dict[item['name']] = item
                
            if any(kw.lower() in item['name'].lower() for kw in classic_item_keywords):
                if item['name'] not in classic_items_dict:
                    item['id'] = item_id
                    classic_items_dict[item['name']] = item
                
    valid_items = list(unique_items_dict.values())
    valid_classic_items = list(classic_items_dict.values())
    valid_support_items = list(support_items_pool.values())
    
    summoners_data = requests.get(f"{base_url}/summoner.json").json()['data']
    valid_summoners = [s for s in summoners_data.values() if 'CLASSIC' in s.get('modes', [])]
    
    extra_spells = [
        {"id": "SummonerRevive", "name": "Revive", "image": {"full": "SummonerRevive.png"}},
        {"id": "SummonerClairvoyance", "name": "Clairvoyance", "image": {"full": "SummonerClairvoyance.png"}}
    ]
    for sp in extra_spells:
        if not any(s['name'] == sp['name'] for s in valid_summoners):
            valid_summoners.append(sp)
            
    return target_version, champions, valid_items, valid_classic_items, valid_support_items, all_item_data, valid_summoners

# Funkcja budująca tooltip przedmiotu w HTML
def build_item_html(item, version, all_items):
    old_items_names = ["Deathfire Grasp", "Heart of Gold", "Philosopher's Stone", "Madred's Bloodrazor", "Atma's Impaler", "Sword of the Divine", "Will of the Ancients", "Abyssal Scepter"]
    img_ver = "5.4.1" if item['name'] in old_items_names else version
    
    item_img_url = f"https://ddragon.leagueoflegends.com/cdn/{img_ver}/img/item/{item['image']['full']}"
    components_html = ""
    for comp_id in item.get('from', []):
        if comp_id in all_items:
            comp = all_items[comp_id]
            comp_img = f"https://ddragon.leagueoflegends.com/cdn/{version}/img/item/{comp['image']['full']}"
            components_html += f'<img src="{comp_img}" class="comp-img" title="{comp["name"]}">'
            
    if not components_html:
        components_html = "<span style='font-size:11px; color:#aaa;'>Brak przepisu (podstawa)</span>"
        
    html = f"""<div class="tooltip">
<img src="{item_img_url}" class="small-item-img">
<div class="tooltiptext">
<b style="color: #f2d590; font-size: 13px;">{item['name']}</b>
<div style="margin: 4px 0; font-size: 11px;">Składniki:</div>
<div style="display:flex; justify-content:center; flex-wrap:wrap;">
{components_html}
</div>
</div>
</div>"""
    return html

def get_spell_url(spell_name, spell_image, current_ver):
    if spell_name in ["Revive", "Clairvoyance"]:
        return f"https://ddragon.leagueoflegends.com/cdn/5.4.1/img/spell/{spell_image}"
    return f"https://ddragon.leagueoflegends.com/cdn/{current_ver}/img/spell/{spell_image}"

class ChaosDraft:
    def __init__(self, champions, items, classic_items, support_items, summoners):
        self.champions = champions
        self.items = items
        self.classic_items = classic_items
        self.support_items = support_items
        self.positions = ["Top", "Jungle", "Mid", "ADC", "Support"]
        
        self.smite_spell = next((s for s in summoners if s['name'] == 'Smite'), None)
        
        # ODDZIELENIE CZARÓW
        self.standard_spells = [s for s in summoners if s['name'] not in ['Smite', 'Revive', 'Clairvoyance']]
        classic_spell_names = ["Flash", "Ghost", "Heal", "Exhaust", "Ignite", "Teleport", "Cleanse", "Clarity", "Revive", "Clairvoyance"]
        self.classic_spells = [s for s in summoners if s['name'] in classic_spell_names]
        
        self.build_logic = {
            "Fighter": ["Damage", "Health", "Armor", "SpellBlock", "LifeSteal"],
            "Mage": ["SpellDamage", "Mana", "CooldownReduction", "MagicPenetration"],
            "Marksman": ["Damage", "AttackSpeed", "CriticalStrike", "LifeSteal"],
            "Assassin": ["Damage", "ArmorPenetration", "CooldownReduction", "Lethality"],
            "Tank": ["Health", "Armor", "SpellBlock", "HealthRegen"],
            "Support": ["ManaRegen", "HealthRegen", "Aura", "Active"]
        }
        
        self.role_allowed_classes = {
            "Top": {"tags": ["Fighter", "Tank"], "exceptions": ["Vayne", "Quinn", "Teemo", "Cassiopeia", "Vladimir", "Heimerdinger", "Kennen"]},
            "Jungle": {"tags": ["Assassin", "Fighter", "Tank"], "exceptions": ["Ivern", "Karthus", "Taliyah", "Kindred"]},
            "Mid": {"tags": ["Mage", "Assassin"], "exceptions": ["Yasuo", "Yone", "Irelia", "Lucian", "Tristana", "Pantheon", "Renekton"]},
            "ADC": {"tags": ["Marksman"], "exceptions": ["Yasuo", "Ziggs", "Seraphine", "Karthus"]},
            "Support": {"tags": ["Support", "Tank"], "exceptions": ["Senna", "Pyke", "Ashe", "MissFortune", "Heimerdinger", "Brand", "Zyra", "Xerath", "Velkoz"]}
        }
        
        self.classic_champions = [
            "Ahri", "Akali", "Alistar", "Amumu", "Anivia", "Annie", "Ashe", "Blitzcrank", "ChoGath", "Corki", 
            "DrMundo", "Evelynn", "Ezreal", "Fiddlesticks", "Gangplank", "Garen", "Heimerdinger", "Irelia", "Janna", "Jax", 
            "Karthus", "Kassadin", "Katarina", "Kayle", "Kennen", "KogMaw", "Leblanc", "LeeSin", "Malphite", "MasterYi", 
            "Morgana", "Nasus", "Nidalee", "Nunu", "Olaf", "Pantheon", "Rammus", "Renekton", "Ryze", "Shaco", 
            "Shen", "Singed", "Sion", "Sivir", "Skarner", "Sona", "Soraka", "Swain", "Talon", "Taric", 
            "Teemo", "Tristana", "Tryndamere", "TwistedFate", "Twitch", "Udyr", "Vayne", "Veigar", "Warwick", "Zilean"
        ]

        self.combos = {
            "Wombocombo": ["Malphite", "Orianna", "Yasuo", "MissFortune", "Amumu", "Wukong", "Rakan", "Neexa", "Velkoz", "Fiddlesticks"],
            "Combo pod trolla": ["Trundle", "Teemo", "Shaco", "Bard", "TahmKench", "Singed", "Nunu", "Blitzcrank", "Pyke"],
            "Homoseksualni (interpretacja dowolna)": ["Taric", "Ezreal", "Varus", "Neeko", "Sett", "Aphelios", "TF", "Graves", "Leona", "Diana", "Rakan", "Xayah"],
            "Czarnoskórzy": ["Lucian", "Senna", "KSante", "Ekko", "Pyke", "Rell", "Illaoi", "Karma", "Nilah"],
            "Duże cycki": ["Sona", "MissFortune", "Ahri", "Evelynn", "Morgana", "Syndra", "Janna", "Katarina", "Zyra", "Elise", "Leblanc"],
            "Mecha-Kombinezony": ["Blitzcrank", "Orianna", "Viktor", "Camille", "Rumble", "Heimerdinger", "Jayce", "Vi", "Urgot", "Khazix|Mecha", "Sion|Mecha", "Yasuo|PROJECT", "Leona|PROJECT"],
            "Płonący (Ogień)": ["Brand", "Annie", "Rumble", "Shyvana", "Smolder", "Milio", "Ornn", "Udyr", "Renekton|Scorched", "Xerath|Scorched", "Alistar|Infernal", "Shen|Infernal"],
            "Wodne Istoty": ["Nami", "Fizz", "Nautilus", "Pyke", "TahmKench", "Nilah", "Illaoi", "Gangplank", "Zoe|Pool Party", "RekSai|Pool Party", "Renekton|Pool Party", "LeeSin|Pool Party"],
            "Zespół Muzyczny (KDA i inni)": ["Seraphine", "Sona", "Bard", "Jhin", "Gragas", "Yasuo|True Damage", "Ahri|K/DA", "Akali|K/DA", "Evelynn|K/DA", "Kaisa|K/DA", "Senna|True Damage", "Ekko|True Damage"],
            "Niskorośli (Yordle i spółka)": ["Teemo", "Tristana", "Lulu", "Veigar", "Kennen", "Poppy", "Rumble", "Kled", "Gnar", "Amumu", "Heimerdinger", "Vex", "Corki", "Ziggs"],
            "Zwierzyniec (Tylko futro)": ["Rengar", "Nidalee", "Warwick", "Nasus", "Renekton", "Volibear", "Yuumi", "Naafiri", "Wukong", "Rammus", "Alistar", "Hecarim", "Azir", "Kindred", "Smolder"],
            "Globalne Ulty": ["Ashe", "Ezreal", "Jinx", "Draven", "Senna", "Karthus", "Gangplank", "Shen", "Soraka", "Pantheon", "TwistedFate", "Ziggs", "Nocturne", "Galio"],
            "Ninja i Samuraje": ["Shen", "Zed", "Akali", "Kennen", "Yasuo", "Yone", "MasterYi", "Irelia", "Talon", "Kayn", "XinZhao"],
            "Piekielne Demony": ["Aatrox", "Shaco", "Evelynn", "Nocturne", "Fiddlesticks", "TahmKench", "Swain", "Vladimir", "Brand", "Kayn", "Morgana", "Varus", "Belveth"],
            "Wielkie Chłopy (Tylko masa)": ["ChoGath", "Sion", "Malphite", "Zac", "Nautilus", "Ornn", "Maokai", "TahmKench", "DrMundo", "Urgot", "Galio", "Gragas", "Sett", "Alistar"],
            "Miasto Haczyków (Tylko Hooki)": ["Blitzcrank", "Thresh", "Nautilus", "Pyke", "Amumu", "Darius", "Swain", "Mordekaiser", "Kled", "Zac", "Sett"],
            "Szpital Zakaźny (Healerzy)": ["Soraka", "Sona", "Nami", "Yuumi", "Taric", "Seraphine", "Milio", "Senna", "Nidalee", "Ivern", "Bard", "Janna", "Karma"],
            "Truciciele (Toksyczni)": ["Teemo", "Cassiopeia", "Singed", "Twitch", "Malzahar", "Lillia", "Renata", "Urgot", "Shaco"],
            "Wąsacze i Brodacze": ["Braum", "Graves", "Olaf", "Gragas", "Zilean", "Draven", "Heimerdinger", "Gangplank", "Sylas", "Udyr", "Corki", "Kled"],
            "Inwazja z Pustki (Void)": ["Belveth", "Chogath", "Kassadin", "Kaisa", "Khazix", "KogMaw", "Malzahar", "RekSai", "Velkoz"],
            "Armia Demacii": ["Garen", "JarvanIV", "XinZhao", "Lux", "Sylas", "Fiora", "Galio", "Lucian", "Quinn", "Sona", "Vayne", "Shyvana", "Poppy"],
            "Noxianska Siła": ["Darius", "Draven", "Katarina", "Sion", "Swain", "Talon", "Cassiopeia", "Kled", "Riven", "Samira", "Vladimir"],
            "Zamarznięci (Freljord)": ["Ashe", "Braum", "Lissandra", "Sejuani", "Trundle", "Anivia", "Nunu", "Volibear", "Olaf", "Udyr"],
            "Nieumarli (Shadow Isles)": ["Hecarim", "Karthus", "Thresh", "Viego", "Kalista", "Gwen", "Maokai", "Yorick", "Sion", "Mordekaiser"],
            "Niewidzialni": ["Teemo", "Evelynn", "Shaco", "Twitch", "Pyke", "Rengar", "Akshan", "Khazix", "Vayne", "Akali", "Talon", "Wukong", "Leblanc"]
        }

    def generate_build(self, champion, role, is_classic=False):
        pool_items = self.classic_items if is_classic else self.items
        primary_class = champion['tags'][0]
        desired_tags = self.build_logic.get(primary_class, ["Damage", "Health"])
        suitable_items = [item for item in pool_items if any(tag in item.get('tags', []) for tag in desired_tags)]
        
        if not suitable_items:
            suitable_items = pool_items
            
        if role == "Support" and self.support_items and not is_classic:
            sup_item = random.choice(self.support_items)
            build = [sup_item] + random.sample(suitable_items, min(5, len(suitable_items)))
        else:
            build = random.sample(suitable_items, min(6, len(suitable_items)))
        return build

    def generate_spells(self, role, is_classic=False):
        pool = self.classic_spells if is_classic else self.standard_spells
            
        if role == "Jungle" and self.smite_spell:
            spells = [self.smite_spell, random.choice(pool)]
        else:
            spells = random.sample(pool, 2)
        random.shuffle(spells)
        return spells

    def draft_standard(self, players, champs_per_player):
        random.shuffle(players)
        random.shuffle(self.positions)
        draft_result = {}
        used_champions = set() 

        for i, player in enumerate(players):
            role = self.positions[i]
            allowed_tags = self.role_allowed_classes[role]["tags"]
            allowed_exceptions = self.role_allowed_classes[role]["exceptions"]
            
            valid_champions = [
                champ for champ in self.champions.values()
                if (any(tag in champ.get('tags', []) for tag in allowed_tags) or champ['id'] in allowed_exceptions)
                and champ['name'] not in used_champions
            ]
            
            assigned_champs = random.sample(valid_champions, min(champs_per_player, len(valid_champions)))
            
            champs_data = []
            for champ in assigned_champs:
                used_champions.add(champ['name'])
                build = self.generate_build(champ, role, is_classic=False)
                spells = self.generate_spells(role, is_classic=False)
                champs_data.append({
                    "id": champ['id'], "name": champ['name'], "class": champ['tags'][0],
                    "skin_num": 0, "build": build, "spells": spells
                })
            
            draft_result[player] = {"role": role, "options": champs_data}
        return draft_result
        
    def draft_combo(self, players, combo_name, champs_per_player):
        random.shuffle(players)
        random.shuffle(self.positions)
        draft_result = {}
        used_champions = set() 
        
        allowed_champ_strings = self.combos[combo_name]
        parsed_combo_champs = []
        
        for c_str in allowed_champ_strings:
            if "|" in c_str:
                c_id, skin_keyword = c_str.split("|")
            else:
                c_id, skin_keyword = c_str, None
                
            if c_id in self.champions:
                champ = self.champions[c_id]
                skin_num = 0
                if skin_keyword:
                    for skin in champ['skins']:
                        if skin_keyword.lower() in skin['name'].lower():
                            skin_num = skin['num']
                            break
                parsed_combo_champs.append({
                    "id": champ['id'], "name": champ['name'], "class": champ['tags'][0], 
                    "skin_num": skin_num, "tags": champ['tags']
                })
        
        for i, player in enumerate(players):
            role = self.positions[i]
            available_for_player = [c for c in parsed_combo_champs if c['name'] not in used_champions]
            to_assign_count = min(champs_per_player, len(available_for_player))
            assigned_champs = random.sample(available_for_player, to_assign_count) if to_assign_count > 0 else []
                
            champs_data = []
            for champ in assigned_champs:
                used_champions.add(champ['name'])
                build = self.generate_build(champ, role, is_classic=False)
                spells = self.generate_spells(role, is_classic=False)
                champ['build'] = build
                champ['spells'] = spells
                champs_data.append(champ)
            
            draft_result[player] = {"role": role, "options": champs_data}
        return draft_result

    def draft_custom(self, players, player_pools, champs_per_player):
        random.shuffle(players)
        random.shuffle(self.positions)
        draft_result = {}
        used_champions = set() 

        for i, player in enumerate(players):
            role = self.positions[i]
            allowed_tags = self.role_allowed_classes[role]["tags"]
            allowed_exceptions = self.role_allowed_classes[role]["exceptions"]
            
            valid_champions = [
                champ for champ in self.champions.values()
                if (any(tag in champ.get('tags', []) for tag in allowed_tags) or champ['id'] in allowed_exceptions)
            ]
            
            player_specific_champs = [c for c in valid_champions if c['name'] in player_pools[player] and c['name'] not in used_champions]
            if not player_specific_champs:
                player_specific_champs = [c for c in self.champions.values() if c['name'] in player_pools[player] and c['name'] not in used_champions]
            
            to_assign_count = min(champs_per_player, len(player_specific_champs))
            assigned_champs = random.sample(player_specific_champs, to_assign_count) if to_assign_count > 0 else []
            
            champs_data = []
            for champ in assigned_champs:
                used_champions.add(champ['name'])
                build = self.generate_build(champ, role, is_classic=False)
                spells = self.generate_spells(role, is_classic=False)
                champs_data.append({
                    "id": champ['id'], "name": champ['name'], "class": champ['tags'][0],
                    "skin_num": 0, "build": build, "spells": spells
                })
            
            draft_result[player] = {"role": role, "options": champs_data}
        return draft_result

    def draft_classic(self, players, champs_per_player):
        random.shuffle(players)
        random.shuffle(self.positions)
        draft_result = {}
        used_champions = set() 

        for i, player in enumerate(players):
            role = self.positions[i]
            allowed_tags = self.role_allowed_classes[role]["tags"]
            allowed_exceptions = self.role_allowed_classes[role]["exceptions"]
            
            valid_champions = [
                champ for champ in self.champions.values()
                if (any(tag in champ.get('tags', []) for tag in allowed_tags) or champ['id'] in allowed_exceptions)
                and champ['name'] in self.classic_champions
                and champ['name'] not in used_champions
            ]
            
            to_assign_count = min(champs_per_player, len(valid_champions))
            assigned_champs = random.sample(valid_champions, to_assign_count) if to_assign_count > 0 else []
            
            champs_data = []
            for champ in assigned_champs:
                used_champions.add(champ['name'])
                build = self.generate_build(champ, role, is_classic=True)
                spells = self.generate_spells(role, is_classic=True)
                champs_data.append({
                    "id": champ['id'], "name": champ['name'], "class": champ['tags'][0],
                    "skin_num": 0, "build": build, "spells": spells
                })
            
            draft_result[player] = {"role": role, "options": champs_data}
        return draft_result

# --- INTERFEJS STRONY WEBOWEJ ---

# --- DUŻY DEEP U GÓRY EKRANU ---
big_deep_b64 = get_avatar_b64("deepmeme") or get_avatar_b64("deep")
if big_deep_b64:
    st.markdown(f"""
    <div style="display: flex; justify-content: center; margin-top: -10px; margin-bottom: 20px;">
        <img src="{big_deep_b64}" style="width: 250px; height: 250px; border-radius: 50%; object-fit: cover; border: 4px solid #c8aa6e; box-shadow: 0 0 30px rgba(242, 213, 144, 0.6);">
    </div>
    """, unsafe_allow_html=True)


# Nagłówek bez małych awatarów w prawym górnym rogu
header_col1, header_col2, header_col3 = st.columns([1, 8, 1])
with header_col2:
    st.markdown("<h1 style='text-align: center; color: #f2d590; text-shadow: 2px 2px 4px #000; margin-bottom: 0;'>⚔️ ChaosDraft - League of Legends ⚔️</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center; color: #a5c2d3; text-shadow: 1px 1px 2px #000; margin-top: 0;'>Narzędzie do tworzenia grywalnego chaosu na Summoner's Rift</h4>", unsafe_allow_html=True)

# Baner Clash
st.image("https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-clash/global/default/assets/images/rewards-modal/header-background.png", use_container_width=True)

# Ładowanie danych
with st.spinner('Zaciągam najświeższe dane o LoL-u wprost z serwerów Riot Games...'):
    version, champs, valid_items, valid_classic_items, valid_support_items, all_items, valid_summoners = fetch_riot_data()
    app = ChaosDraft(champs, valid_items, valid_classic_items, valid_support_items, valid_summoners)

# Wejście graczy
def player_input(col, label, default_value):
    with col:
        player_name = st.text_input(label, value=default_value)
        return player_name

st.markdown("### 👥 Wybierz swoją drużynę:")
col1, col2, col3, col4, col5 = st.columns(5)
p1 = player_input(col1, "Gracz 1", "Majkel")
p2 = player_input(col2, "Gracz 2", "Pecker")
p3 = player_input(col3, "Gracz 3", "arekjanicki")
p4 = player_input(col4, "Gracz 4", "Menni")
p5 = player_input(col5, "Gracz 5", "Przemuś")

# Zmieniony styl banerów - width: 100%, height: auto zapewnia idealne proporcje bez pustych przestrzeni
banner_style = "width: 100%; height: auto; border-radius: 12px; margin-bottom: 15px; border: 2px solid #c8aa6e; box-shadow: 0 8px 16px rgba(0,0,0,0.6); display: block;"

# --- ZAKŁADKI TRYBÓW ---
tab1, tab2, tab3, tab4 = st.tabs(["⚔️ Standard", "🎭 Comba", "🎯 Własna Pula", "⏳ Tryb Classic"])

with tab1:
    majkmeme_b64 = get_avatar_b64("majkmeme")
    if majkmeme_b64:
        st.markdown(f'<img src="{majkmeme_b64}" style="{banner_style}">', unsafe_allow_html=True)
    else:
        st.image("https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Garen_0.jpg", use_container_width=True)
        
    champs_count_std = st.slider("Ile postaci wylosować dla każdego gracza? (Standard)", 1, 3, 2, key="std_slider")
    if st.button("🔥 LOSUJ STANDARDOWO!", use_container_width=True, type="primary"):
        players = [p1, p2, p3, p4, p5]
        if "" not in players and len(set(players)) == len(players):
            st.session_state['wyniki'] = app.draft_standard(players, champs_per_player=champs_count_std)

with tab2:
    rudymeme_b64 = get_avatar_b64("rudymeme")
    if rudymeme_b64:
        st.markdown(f'<img src="{rudymeme_b64}" style="{banner_style}">', unsafe_allow_html=True)
    else:
        st.image("https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Shaco_0.jpg", use_container_width=True)
        
    selected_combo = st.selectbox("Wybierz Szalone Combo dla swojej drużyny:", list(app.combos.keys()))
    champs_count_combo = st.slider("Ile postaci wylosować dla każdego gracza? (Comba)", 1, 3, 2, key="combo_slider")
    if st.button("🎭 LOSUJ Z COMBO!", use_container_width=True, type="primary"):
        players = [p1, p2, p3, p4, p5]
        if "" not in players and len(set(players)) == len(players):
            st.session_state['wyniki'] = app.draft_combo(players, combo_name=selected_combo, champs_per_player=champs_count_combo)

with tab3:
    mennimeme_b64 = get_avatar_b64("mennimeme")
    if mennimeme_b64:
        st.markdown(f'<img src="{mennimeme_b64}" style="{banner_style}">', unsafe_allow_html=True)
    else:
        st.image("https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Ekko_0.jpg", use_container_width=True)

    all_champ_names = sorted([c['name'] for c in champs.values()])
    player_pools = {}
    players_list = [p1, p2, p3, p4, p5]
    cols_pool = st.columns(5)
    for idx, p in enumerate(players_list):
        with cols_pool[idx]:
            pool = st.multiselect(f"Pula dla: {p}", all_champ_names, key=f"pool_{idx}")
            player_pools[p] = pool if len(pool) > 0 else all_champ_names
    champs_count_custom = st.slider("Ile postaci wylosować dla każdego gracza? (Własna pula)", 1, 3, 2, key="custom_slider")
    if st.button("🎯 LOSUJ Z WŁASNEJ PULI!", use_container_width=True, type="primary"):
        if "" not in players_list and len(set(players_list)) == len(players_list):
            st.session_state['wyniki'] = app.draft_custom(players_list, player_pools, champs_per_player=champs_count_custom)

with tab4:
    szymimeme_b64 = get_avatar_b64("szymimeme")
    if szymimeme_b64:
        st.markdown(f'<img src="{szymimeme_b64}" style="{banner_style}">', unsafe_allow_html=True)
    else:
        st.image("https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Annie_0.jpg", use_container_width=True)
        
    st.info("⏳ Tryb Classic (Patch 26.15): Wyłącznie 60 pierwszych postaci, oryginalne czary oraz powrót starych przedmiotów z premiery trybu Classic!")
    champs_count_classic = st.slider("Ile postaci wylosować dla każdego gracza? (Classic)", 1, 3, 2, key="classic_slider")
    if st.button("⏳ LOSUJ TRYB CLASSIC!", use_container_width=True, type="primary"):
        players = [p1, p2, p3, p4, p5]
        if "" not in players and len(set(players)) == len(players):
            st.session_state['wyniki'] = app.draft_classic(players, champs_per_player=champs_count_classic)

# --- WYNIKI LOSOWANIA ---
if 'wyniki' in st.session_state:
    st.markdown("---")
    
    wyniki = st.session_state['wyniki']
    for player, data in wyniki.items():
        if len(data['options']) == 0:
            continue
            
        avatar_b64 = get_avatar_b64(player)
        avatar_img_src = avatar_b64 if avatar_b64 else "https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/profile-icons/29.jpg"
        
        options_html = ""
        for option in data['options']:
            champ_img_url = f"https://ddragon.leagueoflegends.com/cdn/img/champion/tiles/{option['id']}_{option['skin_num']}.jpg"
            
            spell1_url = get_spell_url(option['spells'][0]['name'], option['spells'][0]['image']['full'], version)
            spell2_url = get_spell_url(option['spells'][1]['name'], option['spells'][1]['image']['full'], version)
            
            items_html = "".join([build_item_html(item, version, all_items) for item in option['build']])
            
            champ_image_html = f'<img src="{champ_img_url}" style="width: 70px; height: 70px; object-fit: cover; border-radius: 6px; border: 1px solid #a5c2d3;">'
            
            options_html += f"""<div style="flex: 1; min-width: 250px; background: rgba(10,10,10,0.6); border-radius: 8px; padding: 10px; border: 1px solid #444;">
<div style="display: flex; align-items: center; gap: 12px; margin-bottom: 10px;">
{champ_image_html}
<div style="display: flex; flex-direction: column;">
<span style="font-size: 16px; font-weight: bold; color: #f2d590;">{option['name']}</span>
<span style="font-size: 12px; color: #aaa; margin-bottom: 4px;">{option['class']}</span>
<div style="display: flex; gap: 4px;">
<img src="{spell1_url}" style="width: 24px; border-radius: 4px;" title="{option['spells'][0]['name']}">
<img src="{spell2_url}" style="width: 24px; border-radius: 4px;" title="{option['spells'][1]['name']}">
</div>
</div>
</div>
<div style="display: flex; flex-wrap: wrap; gap: 6px;">
{items_html}
</div>
</div>"""
            
        player_row_html = f"""<div style="display: flex; background: rgba(20,25,30,0.85); border: 1px solid #c8aa6e; border-radius: 12px; padding: 15px; margin-bottom: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
<div style="flex: 0 0 100px; text-align: center; border-right: 1px solid #555; padding-right: 15px; margin-right: 15px;">
<img src="{avatar_img_src}" style="width: 70px; height: 70px; border-radius: 50%; object-fit: cover; border: 2px solid #a5c2d3;">
<div style="font-weight: 800; font-size: 16px; margin-top: 5px; color: #fff;">{player}</div>
<div style="color: #c8aa6e; font-size: 14px; font-weight: bold; text-transform: uppercase;">{data['role']}</div>
</div>
<div style="display: flex; flex-wrap: wrap; gap: 15px; flex-grow: 1;">
{options_html}
</div>
</div>"""
        st.markdown(player_row_html, unsafe_allow_html=True)
