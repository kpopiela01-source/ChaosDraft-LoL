import streamlit as st
import requests
import random
import os

os.makedirs("avatars", exist_ok=True)

st.set_page_config(page_title="ChaosDraft", page_icon="🎲", layout="wide")

def set_background():
    page_bg_img = """
    <style>
    [data-testid="stAppViewContainer"] {
        background-image: url("https://images.contentstack.io/v3/assets/blt731acb42bb3d1659/blt42b3bf0c2e391cb4/5e964041b31a382c420fec36/Summoners_Rift_1.jpg");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    [data-testid="stHeader"] {
        background: rgba(0,0,0,0);
    }
    .block-container {
        background-color: rgba(14, 17, 23, 0.95);
        border-radius: 20px;
        padding: 2rem;
        margin-top: 1rem;
        border: 1px solid #c8aa6e;
        box-shadow: 0 0 20px rgba(200, 170, 110, 0.3);
    }
    .item-container {
        display: flex;
        align-items: center;
        margin-bottom: 12px;
    }
    .small-item-img {
        width: 48px;
        height: 48px;
        border-radius: 6px;
        border: 1px solid #c8aa6e;
        box-shadow: 0 2px 4px rgba(0,0,0,0.5);
    }
    .item-name {
        font-size: 13px;
        font-weight: 600;
        margin-left: 10px;
        color: #eee;
        line-height: 1.2;
    }
    .tooltip {
        position: relative;
        display: inline-block;
        cursor: help;
        flex-shrink: 0;
    }
    .tooltip .tooltiptext {
        visibility: hidden;
        width: max-content;
        max-width: 200px;
        background-color: rgba(15, 20, 25, 0.98);
        color: #fff;
        text-align: center;
        padding: 10px;
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
    }
    .tooltip:hover .tooltiptext {
        visibility: visible;
        opacity: 1;
    }
    .comp-img {
        width: 32px;
        height: 32px;
        border-radius: 4px;
        border: 1px solid #777;
        margin: 2px;
    }
    .spell-img {
        border-radius: 4px;
        border: 1px solid #a5c2d3;
    }
    </style>
    """
    st.markdown(page_bg_img, unsafe_allow_html=True)

set_background()

def get_avatar_path(player_name):
    if not player_name:
        return None
    safe_name = player_name.strip().lower()
    path = os.path.join("avatars", f"{safe_name}.png")
    return path if os.path.exists(path) else None

@st.cache_data(ttl=3600)
def fetch_riot_data():
    versions = requests.get("https://ddragon.leagueoflegends.com/api/versions.json").json()
    target_version = versions[0] 
            
    base_url = f"https://ddragon.leagueoflegends.com/cdn/{target_version}/data/en_US"
    
    champions = list(requests.get(f"{base_url}/champion.json").json()['data'].values())
    all_item_data = requests.get(f"{base_url}/item.json").json()['data']
    
    unique_items_dict = {}
    support_items_pool = {}
    support_names = ["Celestial Opposition", "Dream Maker", "Zaz'Zak's Realmspike", "Bloodsong", "Solstice Sleigh", "World Atlas", "Bounty of Worlds"]
    
    for item_id, item in all_item_data.items():
        is_sr = item.get('maps', {}).get('11', False) == True
        in_store = item.get('inStore', True)
        purchasable = item.get('gold', {}).get('purchasable', True)
        cost = item.get('gold', {}).get('total', 0)
        required_ally = item.get('requiredAlly', None)
        
        if is_sr and (item['name'] in support_names or ('GoldPer' in item.get('tags', []) and cost in [0, 400])):
            item['id'] = item_id
            support_items_pool[item['name']] = item
            
        if is_sr and in_store and purchasable and cost > 2000 and required_ally is None:
            if item['name'] not in unique_items_dict:
                item['id'] = item_id
                unique_items_dict[item['name']] = item
                
    valid_items = list(unique_items_dict.values())
    valid_support_items = list(support_items_pool.values())
    
    summoners_data = requests.get(f"{base_url}/summoner.json").json()['data']
    valid_summoners = [s for s in summoners_data.values() if 'CLASSIC' in s.get('modes', [])]
    
    return target_version, champions, valid_items, valid_support_items, all_item_data, valid_summoners

def build_item_html(item, version, all_items):
    item_img_url = f"https://ddragon.leagueoflegends.com/cdn/{version}/img/item/{item['image']['full']}"
    components_html = ""
    for comp_id in item.get('from', []):
        if comp_id in all_items:
            comp = all_items[comp_id]
            comp_img = f"https://ddragon.leagueoflegends.com/cdn/{version}/img/item/{comp['image']['full']}"
            components_html += f'<img src="{comp_img}" class="comp-img" title="{comp["name"]}">'
            
    if not components_html:
        components_html = "<span style='font-size:12px; color:#aaa;'>Brak przepisu (podstawa)</span>"
        
    html = f"""
    <div class="item-container">
        <div class="tooltip">
            <img src="{item_img_url}" class="small-item-img">
            <div class="tooltiptext">
                <b style="font-size:13px; display:block; margin-bottom:6px;">Składniki:</b>
                <div style="display:flex; justify-content:center; flex-wrap:wrap;">
                    {components_html}
                </div>
            </div>
        </div>
        <div class="item-name">{item['name']}</div>
    </div>
    """
    return html

class ChaosDraft:
    def __init__(self, champions, items, support_items, summoners):
        self.champions = champions
        self.items = items
        self.support_items = support_items
        self.positions = ["Top", "Jungle", "Mid", "ADC", "Support"]
        
        self.smite_spell = next((s for s in summoners if s['name'] == 'Smite'), None)
        self.other_spells = [s for s in summoners if s['name'] != 'Smite']
        
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
        
        self.combos = {
            "Czarnoskórzy": ["Lucian", "Senna", "KSante", "Ekko", "Pyke", "Rell", "Illaoi", "Karma", "Nilah"],
            "Duże cycki": ["Sona", "MissFortune", "Ahri", "Evelynn", "Morgana", "Syndra", "Janna", "Katarina", "Zyra", "Elise", "Leblanc"],
            "Niskorośli (Yordle i spółka)": ["Teemo", "Tristana", "Lulu", "Veigar", "Kennen", "Poppy", "Rumble", "Kled", "Gnar", "Amumu", "Heimerdinger", "Vex", "Corki", "Ziggs"],
            "Zwierzyniec (Tylko futro)": ["Rengar", "Nidalee", "Warwick", "Nasus", "Renekton", "Volibear", "Yuumi", "Naafiri", "Wukong", "Rammus", "Alistar", "Hecarim", "Azir", "Kindred", "Smolder"],
            "Globalne Ulty (Z drugiego końca mapy)": ["Ashe", "Ezreal", "Jinx", "Draven", "Senna", "Karthus", "Gangplank", "Shen", "Soraka", "Pantheon", "TwistedFate", "Ziggs", "Nocturne", "Galio"],
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
            "Mecha-Kombinezony": ["Blitzcrank", "Orianna", "Viktor", "Camille", "Rumble", "Heimerdinger", "Jayce", "Vi", "Urgot"],
            "Płonący (Ogień)": ["Brand", "Annie", "Rumble", "Shyvana", "Smolder", "Milio", "Ornn", "Udyr"],
            "Wodne Istoty": ["Nami", "Fizz", "Nautilus", "Pyke", "TahmKench", "Nilah", "Illaoi", "Gangplank"],
            "Niewidzialni": ["Teemo", "Evelynn", "Shaco", "Twitch", "Pyke", "Rengar", "Akshan", "Khazix", "Vayne", "Akali", "Talon", "Wukong", "Leblanc"],
            "Zespół Muzyczny (KDA i inni)": ["Seraphine", "Sona", "Bard", "Yasuo", "Jhin", "Gragas", "Ahri", "Akali", "Evelynn", "Kaisa"]
        }

    def generate_build(self, champion, role):
        primary_class = champion['tags'][0]
        desired_tags = self.build_logic.get(primary_class, ["Damage", "Health"])
        suitable_items = [item for item in self.items if any(tag in item.get('tags', []) for tag in desired_tags)]
        
        if role == "Support" and self.support_items:
            sup_item = random.choice(self.support_items)
            build = [sup_item] + random.sample(suitable_items, min(5, len(suitable_items)))
        else:
            build = random.sample(suitable_items, min(6, len(suitable_items)))
        return build

    def generate_spells(self, role):
        if role == "Jungle" and self.smite_spell:
            spells = [self.smite_spell, random.choice(self.other_spells)]
        else:
            spells = random.sample(self.other_spells, 2)
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
            
            valid_champions_for_role = [
                champ for champ in self.champions 
                if (any(tag in champ.get('tags', []) for tag in allowed_tags) or champ['id'] in allowed_exceptions)
                and champ['name'] not in used_champions
            ]
            
            assigned_champs = random.sample(valid_champions_for_role, min(champs_per_player, len(valid_champions_for_role)))
            
            champs_data = []
            for champ in assigned_champs:
                used_champions.add(champ['name'])
                build = self.generate_build(champ, role)
                spells = self.generate_spells(role)
                champs_data.append({
                    "name": champ['name'],
                    "class": champ['tags'][0],
                    "image": champ['image']['full'],
                    "build": build,
                    "spells": spells
                })
            
            draft_result[player] = {"role": role, "options": champs_data}
        return draft_result
        
    def draft_combo(self, players, combo_name, champs_per_player):
        random.shuffle(players)
        random.shuffle(self.positions)
        draft_result = {}
        used_champions = set() 
        
        allowed_champ_ids = self.combos[combo_name]
        combo_champs = [champ for champ in self.champions if champ['id'] in allowed_champ_ids]
        
        for i, player in enumerate(players):
            role = self.positions[i]
            
            available_for_player = [c for c in combo_champs if c['name'] not in used_champions]
            to_assign_count = min(champs_per_player, len(available_for_player))
            
            if to_assign_count > 0:
                assigned_champs = random.sample(available_for_player, to_assign_count)
            else:
                assigned_champs = []
                
            champs_data = []
            for champ in assigned_champs:
                used_champions.add(champ['name'])
                build = self.generate_build(champ, role)
                spells = self.generate_spells(role)
                champs_data.append({
                    "name": champ['name'],
                    "class": champ['tags'][0],
                    "image": champ['image']['full'],
                    "build": build,
                    "spells": spells
                })
            
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
            
            valid_champions_for_role = [
                champ for champ in self.champions 
                if (any(tag in champ.get('tags', []) for tag in allowed_tags) or champ['id'] in allowed_exceptions)
            ]
            
            player_specific_champs = [
                champ for champ in valid_champions_for_role
                if champ['name'] in player_pools[player] and champ['name'] not in used_champions
            ]
            
            if not player_specific_champs:
                player_specific_champs = [
                    champ for champ in self.champions
                    if champ['name'] in player_pools[player] and champ['name'] not in used_champions
                ]
            
            to_assign_count = min(champs_per_player, len(player_specific_champs))
            if to_assign_count > 0:
                assigned_champs = random.sample(player_specific_champs, to_assign_count)
            else:
                assigned_champs = []
            
            champs_data = []
            for champ in assigned_champs:
                used_champions.add(champ['name'])
                build = self.generate_build(champ, role)
                spells = self.generate_spells(role)
                champs_data.append({
                    "name": champ['name'],
                    "class": champ['tags'][0],
                    "image": champ['image']['full'],
                    "build": build,
                    "spells": spells
                })
            
            draft_result[player] = {"role": role, "options": champs_data}
        return draft_result


# --- INTERFEJS STRONY WEBOWEJ ---

st.markdown("<h1 style='text-align: center; color: #f2d590; text-shadow: 2px 2px 4px #000;'>⚔️ ChaosDraft - League of Legends ⚔️</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: #a5c2d3; text-shadow: 1px 1px 2px #000;'>Narzędzie do tworzenia grywalnego chaosu na Summoner's Rift</h4>", unsafe_allow_html=True)

# Duży baner graficzny na samej górze
st.image("https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-clash/global/default/assets/images/rewards-modal/header-background.png", use_container_width=True)

# Dodatkowa grafika obok statusu API
col_api1, col_api2 = st.columns([1, 10])
with col_api1:
    # Ikona poro/pingu
    st.image("https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/profile-icons/4655.jpg", width=60)
with col_api2:
    with st.spinner('Zaciągam najświeższe dane o LoL-u wprost z serwerów Riot Games...'):
        version, champs, valid_items, valid_support_items, all_items, valid_summoners = fetch_riot_data()
        app = ChaosDraft(champs, valid_items, valid_support_items, valid_summoners)
    st.success(f"✔️ Dane gotowe! Ekipa zsynchronizowana z Patchem: **{version}**")

with st.expander("📸 Dodaj lub zmień zdjęcie profilowe gracza (Opcjonalne)"):
    col_prof1, col_prof2 = st.columns(2)
    with col_prof1:
        prof_name = st.text_input("Wpisz nick gracza:")
    with col_prof2:
        prof_img = st.file_uploader("Wybierz zdjęcie (JPG/PNG)", type=['jpg', 'jpeg', 'png'])
    
    if st.button("Zapisz Avatar"):
        if prof_name and prof_img:
            safe_name = prof_name.strip().lower()
            file_path = os.path.join("avatars", f"{safe_name}.png")
            with open(file_path, "wb") as f:
                f.write(prof_img.getbuffer())
            st.success(f"Zapisano zdjęcie dla gracza: {prof_name}!")
        else:
            st.warning("Najpierw podaj nick i wybierz zdjęcie.")

st.markdown("---")
st.markdown("### 👥 Wybierz swoją drużynę:")

def player_input(col, label, default_value):
    with col:
        player_name = st.text_input(label, value=default_value)
        avatar_path = get_avatar_path(player_name)
        if avatar_path:
            st.image(avatar_path, width=80)
        else:
            st.markdown("<h1 style='font-size: 50px; margin: 0; padding: 0;'>👤</h1>", unsafe_allow_html=True)
        return player_name

col1, col2, col3, col4, col5 = st.columns(5)
p1 = player_input(col1, "Gracz 1", "Majkel")
p2 = player_input(col2, "Gracz 2", "Pecker")
p3 = player_input(col3, "Gracz 3", "arekjanicki")
p4 = player_input(col4, "Gracz 4", "Menni")
p5 = player_input(col5, "Gracz 5", "Przemuś")

st.markdown("<br>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["⚔️ Standardowy Draft", "🎭 Szalone Comba", "🎯 Własna Pula Postaci"])

with tab1:
    st.image("https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Garen_0.jpg", use_container_width=True)
    st.markdown("#### Losowanie klasyczne (wg pozycji w mecie)")
    champs_count_std = st.slider("Ile postaci wylosować dla każdego gracza? (Standard)", 1, 3, 2, key="std_slider")
    
    if st.button("🔥 LOSUJ STANDARDOWO!", use_container_width=True, type="primary"):
        players = [p1, p2, p3, p4, p5]
        if "" in players:
            st.error("Wpisz nicki wszystkich 5 graczy przed losowaniem!")
        elif len(set(players)) != len(players):
            st.error("Nicki graczy muszą być unikalne!")
        else:
            st.session_state['wyniki'] = app.draft_standard(players, champs_per_player=champs_count_std)

with tab2:
    st.image("https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Shaco_0.jpg", use_container_width=True)
    st.markdown("#### Losowanie Tematyczne (Zabawne Kompozycje)")
    selected_combo = st.selectbox("Wybierz Szalone Combo dla swojej drużyny:", list(app.combos.keys()))
    champs_count_combo = st.slider("Ile postaci wylosować dla każdego gracza? (Comba)", 1, 3, 2, key="combo_slider")
    
    if st.button("🎭 LOSUJ Z COMBO!", use_container_width=True, type="primary"):
        players = [p1, p2, p3, p4, p5]
        if "" in players:
            st.error("Wpisz nicki wszystkich 5 graczy przed losowaniem!")
        elif len(set(players)) != len(players):
            st.error("Nicki graczy muszą być unikalne!")
        else:
            st.session_state['wyniki'] = app.draft_combo(players, combo_name=selected_combo, champs_per_player=champs_count_combo)

with tab3:
    st.image("https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Ekko_0.jpg", use_container_width=True)
    st.markdown("#### Losowanie z ograniczonej puli")
    
    all_champ_names = sorted([c['name'] for c in champs])
    player_pools = {}
    players_list = [p1, p2, p3, p4, p5]
    
    cols_pool = st.columns(5)
    for idx, p in enumerate(players_list):
        with cols_pool[idx]:
            pool = st.multiselect(f"Pula dla: {p}", all_champ_names, key=f"pool_{idx}")
            player_pools[p] = pool if len(pool) > 0 else all_champ_names
            
    champs_count_custom = st.slider("Ile postaci wylosować dla każdego gracza? (Własna pula)", 1, 3, 2, key="custom_slider")
    
    if st.button("🎯 LOSUJ Z WŁASNEJ PULI!", use_container_width=True, type="primary"):
        if "" in players_list:
            st.error("Wpisz nicki wszystkich 5 graczy przed losowaniem!")
        elif len(set(players_list)) != len(players_list):
            st.error("Nicki graczy muszą być unikalne!")
        else:
            st.session_state['wyniki'] = app.draft_custom(players_list, player_pools, champs_per_player=champs_count_custom)

if 'wyniki' in st.session_state:
    st.markdown("---")
    st.header("🏆 Wyniki Losowania")
    
    wyniki = st.session_state['wyniki']
    
    max_options = 1
    for data in wyniki.values():
        if len(data['options']) > max_options:
            max_options = len(data['options'])
            
    for player, data in wyniki.items():
        st.markdown("<br>", unsafe_allow_html=True) 
        
        if len(data['options']) == 0:
            st.warning(f"Gracz {player} (Pozycja: {data['role'].upper()}) nie mógł wylosować żadnej postaci z podanej puli!")
            continue
            
        layout_ratios = [1.5] + [3] * max_options
        row_cols = st.columns(layout_ratios)
        
        with row_cols[0]:
            avatar_path = get_avatar_path(player)
            if avatar_path:
                st.image(avatar_path, width=120)
            else:
                st.markdown("<h1 style='font-size: 80px; margin: 0;'>👤</h1>", unsafe_allow_html=True)
                
            st.markdown(f"## {player}")
            st.markdown(f"### 📍 {data['role'].upper()}")
        
        for i, option in enumerate(data['options']):
            with row_cols[i + 1]:
                st.markdown(f"**Opcja {i+1}**")
                
                champ_img_url = f"https://ddragon.leagueoflegends.com/cdn/{version}/img/champion/{option['image']}"
                
                col_img, col_text, col_spells = st.columns([1.5, 2, 1])
                
                with col_img:
                    st.image(champ_img_url, use_container_width=True)
                    
                with col_text:
                    st.markdown(f"**{option['name']}**")
                    st.caption(f"({option['class']})")
                    
                with col_spells:
                    spell1_url = f"https://ddragon.leagueoflegends.com/cdn/{version}/img/spell/{option['spells'][0]['image']['full']}"
                    spell2_url = f"https://ddragon.leagueoflegends.com/cdn/{version}/img/spell/{option['spells'][1]['image']['full']}"
                    st.markdown(f'<img src="{spell1_url}" class="spell-img" width="100%" title="{option["spells"][0]["name"]}">', unsafe_allow_html=True)
                    st.markdown("<div style='margin-bottom: 4px;'></div>", unsafe_allow_html=True)
                    st.markdown(f'<img src="{spell2_url}" class="spell-img" width="100%" title="{option["spells"][1]["name"]}">', unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                for item_idx in range(0, len(option['build']), 2):
                    item_cols = st.columns(2)
                    with item_cols[0]:
                        st.markdown(build_item_html(option['build'][item_idx], version, all_items), unsafe_allow_html=True)
                    if item_idx + 1 < len(option['build']):
                        with item_cols[1]:
                            st.markdown(build_item_html(option['build'][item_idx + 1], version, all_items), unsafe_allow_html=True)
        
        st.markdown("<hr style='border:1px solid #c8aa6e;'>", unsafe_allow_html=True)