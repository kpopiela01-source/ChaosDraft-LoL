import streamlit as st
import streamlit.components.v1 as components
import requests
import random
import os
import base64
import json
import re

# Tworzymy foldery, jeśli nie istnieją
os.makedirs("avatars", exist_ok=True)
os.makedirs("nuty", exist_ok=True)

# Nazwa pliku bazy danych
DB_FILE = "players_db.json"

# Unikalne teksty dla graczy z bazy (wyskakujące na hover)
PLAYER_QUOTES = {
    "Majkel": "Toplane to wyspa, proszę mi tu nie gankować!",
    "Pecker": "Zaufajcie mi, gramy pode mnie i wygrywamy.",
    "arekjanicki": "Spokojnie panowie, odrobimy to w late game...",
    "Menni": "To off-meta combo to pewniaczek, mówię wam!",
    "Przemuś": "Znowu dostałem Supporta?! Dobra, robię full AP."
}

DEFAULT_QUOTES = [
    "GG WP, jungle diff!",
    "Gramy bezpiecznie, nie feedować!",
    "Za Demacię! I za darmowe LP!",
    "Czy ja znowu muszę was carrować?",
    "First blood albo AFK."
]

st.set_page_config(page_title="ChaosDraft", page_icon="🎲", layout="wide")

# --- FUNKCJE BAZY DANYCH GRACZY ---
def load_db():
    if not os.path.exists(DB_FILE):
        default_db = {
            "Majkel": {"opgg": ""},
            "Pecker": {"opgg": ""},
            "arekjanicki": {"opgg": ""},
            "Menni": {"opgg": ""},
            "Przemuś": {"opgg": ""}
        }
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(default_db, f, ensure_ascii=False, indent=4)
        return default_db
    
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_player_to_db(name, opgg_link, avatar_file):
    db = load_db()
    name_key = name.strip()
    
    if name_key not in db:
        db[name_key] = {}
    
    if opgg_link:
        if not opgg_link.startswith("http"):
            opgg_link = "https://" + opgg_link
    db[name_key]["opgg"] = opgg_link
    
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=4)
        
    if avatar_file is not None:
        safe_name = name_key.lower()
        for ext in ['png', 'jpg', 'jpeg']:
            p = os.path.join("avatars", f"{safe_name}.{ext}")
            if os.path.exists(p): os.remove(p)
        ext = avatar_file.name.split('.')[-1]
        with open(os.path.join("avatars", f"{safe_name}.{ext}"), "wb") as f:
            f.write(avatar_file.getvalue())

def clean_riot_html(text):
    if not text: return "Brak opisu."
    text = text.replace("<br>", "\n").replace("<br/>", "\n").replace("<br />", "\n")
    text = re.sub(r'<[^>]+>', '', text)
    return text.replace("\n", "<br>")

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Funkcja ustawiająca tło strony i ANIMACJE CSS
def set_background():
    bg_path_jpg = os.path.join("avatars", "majkmeme.jpg")
    bg_path_png = os.path.join("avatars", "majkmeme.png")
    
    bg_img_url = "https://images.contentstack.io/v3/assets/blt731acb42bb3d1659/blt42b3bf0c2e391cb4/5e964041b31a382c420fec36/Summoners_Rift_1.jpg"
    
    if os.path.exists(bg_path_jpg):
        bg_b64 = get_base64_of_bin_file(bg_path_jpg)
        bg_img_url = f"data:image/jpeg;base64,{bg_b64}"
    elif os.path.exists(bg_path_png):
        bg_b64 = get_base64_of_bin_file(bg_path_png)
        bg_img_url = f"data:image/png;base64,{bg_b64}"

    page_bg_img = f"""
    <style>
    /* Tło strony */
    [data-testid="stAppViewContainer"] {{
        background-image: url("{bg_img_url}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    [data-testid="stAppViewContainer"]::before {{
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background: rgba(0, 0, 0, 0.4);
        z-index: 0;
    }}
    
    /* Główne kontenery */
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
    
    /* ANIMACJE: Lewitujący Deep i dymek */
    @keyframes floating {{
        0% {{ transform: translateY(0px); }}
        50% {{ transform: translateY(-15px); }}
        100% {{ transform: translateY(0px); }}
    }}
    .deep-container {{
        position: relative;
        display: inline-block;
    }}
    .deep-img {{
        animation: floating 4s ease-in-out infinite;
        cursor: pointer;
        transition: transform 0.2s;
    }}
    .deep-img:active {{
        transform: scale(0.95);
    }}
    .deep-text {{
        visibility: hidden;
        width: 300px;
        background-color: rgba(20,25,30,0.95);
        color: #f2d590;
        text-align: center;
        border-radius: 12px;
        padding: 15px;
        position: absolute;
        z-index: 101;
        top: 100%;
        left: 50%;
        transform: translateX(-50%) translateY(20px);
        border: 2px solid #c8aa6e;
        opacity: 0;
        transition: all 0.3s ease-in-out;
        font-size: 15px;
        font-weight: bold;
        pointer-events: none;
        box-shadow: 0px 10px 20px rgba(0,0,0,0.8);
    }}
    .deep-container:hover .deep-text, .deep-container:active .deep-text {{
        visibility: visible;
        opacity: 1;
        transform: translateX(-50%) translateY(5px);
    }}
    
    /* --- ANIMACJE I DYMKI PO BOKACH EKRANU (Zablokowane na górze = absolute) --- */
    @keyframes bobLeft {{
        0% {{ transform: translateY(0px) rotate(-5deg); }}
        50% {{ transform: translateY(-20px) rotate(5deg); }}
        100% {{ transform: translateY(0px) rotate(-5deg); }}
    }}
    @keyframes bobRight {{
        0% {{ transform: translateY(0px) rotate(5deg); }}
        50% {{ transform: translateY(-25px) rotate(-5deg); }}
        100% {{ transform: translateY(0px) rotate(5deg); }}
    }}
    
    .teemo-container {{
        position: absolute;
        top: 150px;
        left: 2%;
        z-index: 100;
        animation: bobLeft 5s ease-in-out infinite;
    }}
    .teemo-img {{
        width: 130px;
        border-radius: 50%;
        border: 4px solid #c8aa6e;
        box-shadow: 0 0 25px rgba(200,170,110,0.5);
        cursor: pointer;
        transition: 0.2s;
    }}
    .teemo-img:active {{
        transform: scale(0.9);
    }}
    .teemo-text {{
        visibility: hidden;
        width: 220px;
        background-color: rgba(20,25,30,0.95);
        color: #f2d590;
        text-align: center;
        border-radius: 12px;
        padding: 12px;
        position: absolute;
        z-index: 101;
        top: 110%;
        left: 50%;
        transform: translateX(-50%) translateY(20px);
        border: 2px solid #c8aa6e;
        opacity: 0;
        transition: all 0.3s ease-in-out;
        font-size: 14px;
        font-weight: bold;
        pointer-events: none;
        box-shadow: 0px 10px 20px rgba(0,0,0,0.8);
    }}
    .teemo-container:hover .teemo-text, .teemo-container:active .teemo-text {{
        visibility: visible;
        opacity: 1;
        transform: translateX(-50%) translateY(0px);
    }}

    .shaco-container {{
        position: absolute;
        top: 150px;
        right: 2%;
        z-index: 100;
        animation: bobRight 6s ease-in-out infinite;
    }}
    .shaco-img {{
        width: 130px;
        border-radius: 50%;
        border: 4px solid #c8aa6e;
        box-shadow: 0 0 25px rgba(200,170,110,0.5);
        cursor: pointer;
        transition: 0.2s;
    }}
    .shaco-img:active {{
        transform: scale(0.9);
    }}
    .shaco-text {{
        visibility: hidden;
        width: 220px;
        background-color: rgba(20,25,30,0.95);
        color: #f2d590;
        text-align: center;
        border-radius: 12px;
        padding: 12px;
        position: absolute;
        z-index: 101;
        top: 110%;
        left: 50%;
        transform: translateX(-50%) translateY(20px);
        border: 2px solid #c8aa6e;
        opacity: 0;
        transition: all 0.3s ease-in-out;
        font-size: 14px;
        font-weight: bold;
        pointer-events: none;
        box-shadow: 0px 10px 20px rgba(0,0,0,0.8);
    }}
    .shaco-container:hover .shaco-text, .shaco-container:active .shaco-text {{
        visibility: visible;
        opacity: 1;
        transform: translateX(-50%) translateY(0px);
    }}
    
    /* ANIMACJE: Awatary graczy w wynikach draftu */
    .player-avatar-container {{
        position: relative;
        display: inline-block;
        cursor: pointer;
    }}
    .player-avatar-img {{
        transition: transform 0.2s, box-shadow 0.2s;
    }}
    .player-avatar-container:hover .player-avatar-img {{
        transform: scale(1.1);
        box-shadow: 0 0 15px #f2d590;
    }}
    .player-quote {{
        visibility: hidden;
        width: 160px;
        background-color: rgba(20,25,30,0.95);
        color: #f2d590;
        text-align: center;
        border-radius: 10px;
        padding: 8px;
        position: absolute;
        z-index: 102;
        bottom: 110%;
        left: 50%;
        transform: translateX(-50%) translateY(15px);
        border: 1px solid #c8aa6e;
        opacity: 0;
        transition: all 0.2s ease-in-out;
        font-size: 12px;
        font-weight: bold;
        pointer-events: none;
        box-shadow: 0px 5px 15px rgba(0,0,0,0.7);
    }}
    .player-avatar-container:hover .player-quote {{
        visibility: visible;
        opacity: 1;
        transform: translateX(-50%) translateY(0px);
    }}
    
    /* ANIMACJE: Pojawianie się kart graczy (Fade In Up) */
    @keyframes fadeInUp {{
        0% {{ opacity: 0; transform: translateY(30px); }}
        100% {{ opacity: 1; transform: translateY(0); }}
    }}
    .draft-card-anim {{
        animation: fadeInUp 0.7s cubic-bezier(0.165, 0.84, 0.44, 1) forwards;
    }}
    
    /* ANIMACJE: Przyciski Losowania */
    div[data-testid="stButton"] button {{
        transition: transform 0.2s ease, box-shadow 0.2s ease !important;
    }}
    div[data-testid="stButton"] button:hover {{
        transform: scale(1.03) !important;
        box-shadow: 0 0 15px rgba(200, 170, 110, 0.8) !important;
    }}

    /* Elementy UI */
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
        background-color: rgba(15, 20, 25, 0.98);
        color: #fff;
        text-align: left;
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
        font-size: 11px;
        line-height: 1.3;
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
    
    # Renderowanie elementów po bokach z dymkami HTML
    st.markdown(f"""
    <div class="teemo-container">
        <img src="https://ddragon.leagueoflegends.com/cdn/14.2.1/img/champion/Teemo.png" class="teemo-img">
        <div class="teemo-text">🍄 "Rozmiar to nie wszystko! Uważaj na moje grzyby w dżungli!" 🍄</div>
    </div>
    <div class="shaco-container">
        <img src="https://ddragon.leagueoflegends.com/cdn/14.2.1/img/champion/Shaco.png" class="shaco-img">
        <div class="shaco-text">🤡 "The joke's on you! Ten draft to była tylko iluzja!" 🤡</div>
    </div>
    """, unsafe_allow_html=True)

set_background()

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
    
    classic_item_whitelist = [
        "Boots of Speed", "Berserker's Greaves", "Boots of Mobility", "Boots of Swiftness", 
        "Ionian Boots of Lucidity", "Mercury's Treads", "Ninja Tabi", "Sorcerer's Shoes",
        "Abyssal Scepter", "Archangel's Staff", "Atma's Impaler", "Banner of Command", 
        "Banshee's Veil", "Blade of the Ruined King", "Bloodthirster", "Deathfire Grasp", 
        "Eleisa's Miracle", "Executioner's Calling", "Feral Flare", "Force of Nature", 
        "Frozen Heart", "Frozen Mallet", "Guardian Angel", "Guinsoo's Rageblade", 
        "Hextech Gunblade", "Iceborn Gauntlet", "Infinity Edge", "Innervating Locket", 
        "Ionic Spark", "Last Whisper", "Leviathan", "Liandry's Torment", "Lich Bane", 
        "Locket of the Iron Solari", "Madred's Bloodrazor", "Malady", "Manamune", 
        "Maw of Malmortius", "Mejai's Soulstealer", "Mercurial Scimitar", "Mikael's Crucible", 
        "Morellonomicon", "Muramana", "Ohmwrecker", "Phantom Dancer", "Rabadon's Deathcap", 
        "Randuin's Omen", "Ravenous Hydra", "Rod of Ages", "Ruby Sightstone", "Runaan's Hurricane", 
        "Runic Bulwark", "Rylai's Crystal Scepter", "Seraph's Embrace", "Shard of True Ice", 
        "Soul Shroud", "Spirit Stone", "Spirit Visage", "Spirit of the Ancient Golem", 
        "Spirit of the Elder Lizard", "Spirit of the Spectral Wraith", "Statikk Shiv", 
        "Sunfire Cape", "Sword of the Divine", "Sword of the Occult", "The Black Cleaver", 
        "Thornmail", "Twin Shadows", "Void Staff", "Warmog's Armor", "Will of the Ancients", 
        "Wit's End", "Wriggle's Lantern", "Youmuu's Ghostblade", "Zeke's Herald", "Zephyr", "Zhonya's Hourglass"
    ]
    
    old_items_to_inject = [
        {"id": "3128", "name": "Deathfire Grasp", "image": {"full": "3128.png"}, "img_version": "5.4.1", "plaintext": "+120 AP, +10% Cooldown Reduction.<br><br>Aktywne: Zadaje 15% maksymalnego zdrowia celu jako obrażenia magiczne i zwiększa otrzymywane przez niego obrażenia magiczne o 20% na 4 sekundy.", "from": []},
        {"id": "3092", "name": "Heart of Gold", "image": {"full": "3092.png"}, "img_version": "5.4.1", "plaintext": "+200 Health.<br><br>Pasywne: Zyskujesz 5 sztuk złota co 10 sekund.", "from": []},
        {"id": "3096", "name": "Philosopher's Stone", "image": {"full": "3096.png"}, "img_version": "5.4.1", "plaintext": "+15 Health Regen, +8 Mana Regen.<br><br>Pasywne: Zyskujesz 5 sztuk złota co 10 sekund.", "from": []},
        {"id": "3126", "name": "Madred's Bloodrazor", "image": {"full": "3126.png"}, "img_version": "5.4.1", "plaintext": "+40 AD, +40% Attack Speed, +25 Armor.<br><br>Pasywne: Podstawowe ataki zadają dodatkowe 4% maksymalnego zdrowia celu jako obrażenia magiczne.", "from": []},
        {"id": "3005", "name": "Atma's Impaler", "image": {"full": "3005.png"}, "img_version": "5.4.1", "plaintext": "+45 Armor, +15% Critical Strike Chance.<br><br>Pasywne: Zyskujesz bonusowe AD równe 1.5% twojego maksymalnego zdrowia.", "from": []},
        {"id": "3131", "name": "Sword of the Divine", "image": {"full": "3131.png"}, "img_version": "5.4.1", "plaintext": "+45% Attack Speed.<br><br>Aktywne: Zyskujesz 100% Attack Speed i 100% Crit Chance na 3 sekundy lub do 3 ataków krytycznych.", "from": []},
        {"id": "3152", "name": "Will of the Ancients", "image": {"full": "3152.png"}, "img_version": "5.4.1", "plaintext": "+50 AP.<br><br>Aura: Pobliskim sojusznikom daje +30 AP i 20% Spell Vamp.", "from": []},
        {"id": "3001", "name": "Abyssal Scepter", "image": {"full": "3001.png"}, "img_version": "5.4.1", "plaintext": "+70 AP, +45 Magic Resist.<br><br>Aura: Zmniejsza Magic Resist pobliskich wrogów o 20.", "from": []},
        {"id": "3141", "name": "Sword of the Occult", "image": {"full": "3141.png"}, "img_version": "5.4.1", "plaintext": "+10 AD.<br><br>Pasywne: Zyskujesz 5 AD za zabójstwo i 2 AD za asystę (max 20 stacków). Przy max stackach zyskujesz +20% Movement Speed.", "from": []},
        {"id": "3138", "name": "Leviathan", "image": {"full": "3138.png"}, "img_version": "5.4.1", "plaintext": "+180 Health.<br><br>Pasywne: Zyskujesz 32 HP za zabójstwo (max 20 stacków). Przy 20 stackach otrzymujesz 15% mniej obrażeń.", "from": []},
        {"id": "3113", "name": "Innervating Locket", "image": {"full": "3113.png"}, "img_version": "5.4.1", "plaintext": "+430 HP, +450 Mana, +10% CDR.<br><br>Pasywne: Rzucenie zaklęcia regeneruje 50 HP i 20 Many przez 2 sekundy.", "from": []},
        {"id": "3105", "name": "Force of Nature", "image": {"full": "3105.png"}, "img_version": "5.4.1", "plaintext": "+76 Magic Resist, +40 HP Regen, +8% Movement Speed.<br><br>Pasywne: Odtwarza 1.75% twojego max HP co 5 sekund.", "from": []},
        {"id": "3154", "name": "Wriggle's Lantern", "image": {"full": "3154.png"}, "img_version": "5.4.1", "plaintext": "+23 AD, +30 Armor, +12% Life Steal.<br><br>Pasywne: 20% szansy na 425 magicznego dmg potworom.<br>Aktywne: Stawia darmowego Warda na 3 minuty.", "from": []},
        {"id": "3114", "name": "Malady", "image": {"full": "3114.png"}, "img_version": "5.4.1", "plaintext": "+25 AP, +50% Attack Speed.<br><br>Pasywne: Ataki zadają 15 + 10% AP magicznego dmg i redukują MR celu o 4 (stackuje się do 7 razy).", "from": []},
        {"id": "3069", "name": "Eleisa's Miracle", "image": {"full": "3069.png"}, "img_version": "5.4.1", "plaintext": "+10 HP Regen, +15 Mana Regen.<br><br>Pasywne: Redukuje CD Heal/Clairvoyance o 20%. Po zdobyciu 3 poziomów item znika z EQ trwale zostawiając swoje statystyki w bohaterze.", "from": []},
        {"id": "3173", "name": "Zephyr", "image": {"full": "3173.png"}, "img_version": "5.4.1", "plaintext": "+25 AD, +50% AS, +10% Movement Speed, +10% CDR.<br><br>Pasywne: Zapewnia Tenacity (odporność na CC).", "from": []},
        {"id": "3050", "name": "Zeke's Herald", "image": {"full": "3050.png"}, "img_version": "5.4.1", "plaintext": "+250 HP, +20% CDR.<br><br>Aura: Sojusznicy wokół zyskują +20 AD i +10% Life Steal.", "from": []},
        {"id": "3098", "name": "Shard of True Ice", "image": {"full": "3098.png"}, "img_version": "5.4.1", "plaintext": "+45 AP.<br><br>Aura: +4 Mana Regen. Aktywne: Spowalnia wrogów dookoła wybranego sojusznika o 30%.", "from": []},
        {"id": "3107", "name": "Soul Shroud", "image": {"full": "3107.png"}, "img_version": "5.4.1", "plaintext": "+520 Health.<br><br>Aura: +10% CDR i +12 Mana Regen dla pobliskich sojuszników.", "from": []},
        {"id": "3206", "name": "Ionic Spark", "image": {"full": "3206.png"}, "img_version": "5.4.1", "plaintext": "+50% AS, +250 Health.<br><br>Pasywne: Co czwarty atak wypuszcza piorun zadający 125 magic dmg do 4 celów.", "from": []},
        {"id": "3060", "name": "Banner of Command", "image": {"full": "3060.png"}, "img_version": "5.4.1", "plaintext": "+80 AP, +20% CDR.<br><br>Aura: Miniony zadają 15% więcej dmg.<br>Aktywne: Promuje miniona dodając mu pancerz, obrażenia i odporność na magię.", "from": []},
        {"id": "3106", "name": "Runic Bulwark", "image": {"full": "3106.png"}, "img_version": "5.4.1", "plaintext": "+300 HP, +20 Armor, +30 MR.<br><br>Aura: Legion - Pobliskim sojusznikom daje +10 Armor, +25 MR i +10 HP Regen.", "from": []}
    ]
    
    for item in old_items_to_inject:
        classic_items_dict[item['name']] = item
        all_item_data[item['id']] = item 
        
    historic_versions = ["5.4.1", "10.15.1", target_version]
    for hv in historic_versions:
        try:
            old_items_req = requests.get(f"https://ddragon.leagueoflegends.com/cdn/{hv}/data/en_US/item.json")
            if old_items_req.status_code == 200:
                old_items = old_items_req.json()['data']
                for item_id, item_info in old_items.items():
                    if item_info['name'] in classic_item_whitelist and item_info['name'] not in classic_items_dict:
                        item_info['id'] = item_id
                        item_info['img_version'] = hv
                        classic_items_dict[item_info['name']] = item_info
                        all_item_data[item_id] = item_info
        except:
            pass
            
    for item_id, item in list(all_item_data.items()):
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
                item['img_version'] = target_version
                unique_items_dict[item['name']] = item
                
    valid_items = list(unique_items_dict.values())
    valid_classic_items = list(classic_items_dict.values())
    valid_support_items = list(support_items_pool.values())
    
    summoners_data = requests.get(f"{base_url}/summoner.json").json()['data']
    valid_summoners = [s for s in summoners_data.values() if 'CLASSIC' in s.get('modes', [])]
    
    extra_spells = [
        {"id": "SummonerRevive", "name": "Revive", "image": {"full": "SummonerRevive.png"}, "img_version": "5.4.1", "description": "Natychmiast wskrzesza twojego bohatera na spawnie i daje na kilka sekund masywny bonus do Movement Speedu (cooldown 510s)."},
        {"id": "SummonerClairvoyance", "name": "Clairvoyance", "image": {"full": "SummonerClairvoyance.png"}, "img_version": "5.4.1", "description": "Odkrywa całkowicie niewielki obszar mapy na 5 sekund dla twojej drużyny (cooldown 60s)."},
        {"id": "SummonerFortify", "name": "Fortify", "image": {"full": "SummonerFortify.png"}, "img_version": "5.4.1", "description": "Czyni WSZYSTKIE sojusznicze wieże niewrażliwymi na ataki i zwiększa ich prędkość ataku o 100% na 7 sekund. Pasywnie zadajesz 9 bonusowego dmg minionom."},
        {"id": "SummonerRally", "name": "Rally", "image": {"full": "SummonerRally.png"}, "img_version": "5.4.1", "description": "Stawia celowalny sztandar na 15 sekund, który zwiększa Attack Damage (AD) pobliskim sojusznikom o 10-35 w zależności od poziomu."},
        {"id": "SummonerPromote", "name": "Promote", "image": {"full": "SummonerPromote.png"}, "img_version": "5.4.1", "description": "Ulepsza najbliższego Siege Miniona, lecząc go, dając mu aurę pancerza i masywne obrażenia. Dostajesz złoto za wszystkie jego zabójstwa."},
        {"id": "SummonerSurge", "name": "Surge", "image": {"full": "SummonerSurge.png"}, "img_version": "5.4.1", "description": "Wzmacnia twojego bohatera na 12 sekund, natychmiastowo dodając mu 35% Attack Speed oraz do 78 Ability Power (zależnie od lvl)."}
    ]
    for sp in extra_spells:
        if not any(s['name'] == sp['name'] for s in valid_summoners):
            valid_summoners.append(sp)
            
    return target_version, champions, valid_items, valid_classic_items, valid_support_items, all_item_data, valid_summoners

def build_item_html(item, version, all_items):
    img_ver = item.get('img_version', version)
    item_img_url = f"https://ddragon.leagueoflegends.com/cdn/{img_ver}/img/item/{item['image']['full']}"
    
    desc = item.get('plaintext')
    if not desc:
        desc = clean_riot_html(item.get('description', 'Brak opisu.'))
    else:
        desc = clean_riot_html(desc)
        
    components_html = ""
    for comp_id in item.get('from', []):
        if str(comp_id) in all_items:
            comp = all_items[str(comp_id)]
            comp_img_ver = comp.get('img_version', version)
            comp_img = f"https://ddragon.leagueoflegends.com/cdn/{comp_img_ver}/img/item/{comp['image']['full']}"
            components_html += f'<img src="{comp_img}" class="comp-img" title="{comp["name"]}">'
            
    return f"""<div class="tooltip" style="margin: 2px;">
        <img src="{item_img_url}" class="small-item-img">
        <div class="tooltiptext" style="width: 260px;">
            <b style="color: #f2d590; font-size: 14px;">{item['name']}</b>
            <div style="font-size: 12px; margin-top: 6px; color: #dcdcdc; border-top: 1px solid #c8aa6e; padding-top: 6px;">{desc}</div>
            <div style="margin: 8px 0 2px 0; font-size: 10px; color: #888; text-transform: uppercase; font-weight: bold;">Składniki:</div>
            <div style="display:flex; flex-wrap:wrap; gap: 2px;">
                {components_html if components_html else "<span style='font-size:10px; color:#666;'>Brak przepisu (Przedmiot podstawowy)</span>"}
            </div>
        </div>
    </div>"""

def build_spell_html(spell, version):
    img_ver = spell.get('img_version', version)
    spell_img_url = f"https://ddragon.leagueoflegends.com/cdn/{img_ver}/img/spell/{spell['image']['full']}"
    desc = clean_riot_html(spell.get('description', 'Brak opisu.'))
    
    return f"""<div class="tooltip" style="margin-right: 4px; display: inline-block;">
        <img src="{spell_img_url}" style="width: 26px; border-radius: 4px; border: 1px solid #777;">
        <div class="tooltiptext" style="width: 220px;">
            <b style="color: #f2d590; font-size: 13px;">{spell['name']}</b>
            <div style="font-size: 11px; margin-top: 4px; color: #ccc;">{desc}</div>
        </div>
    </div>"""

class ChaosDraft:
    def __init__(self, champions, items, classic_items, support_items, summoners):
        self.champions = champions
        self.items = items
        self.classic_items = classic_items
        self.support_items = support_items
        self.positions = ["Top", "Jungle", "Mid", "ADC", "Support"]
        
        self.smite_spell = next((s for s in summoners if s['name'] == 'Smite'), None)
        
        classic_spell_names = [
            "Barrier", "Clairvoyance", "Clarity", "Cleanse", "Exhaust", 
            "Flash", "Fortify", "Ghost", "Heal", "Ignite", "Promote", 
            "Rally", "Revive", "Smite", "Surge", "Teleport"
        ]
        
        self.standard_spells = [s for s in summoners if s['name'] not in ['Smite', 'Revive', 'Clairvoyance', 'Fortify', 'Rally', 'Promote', 'Surge']]
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
            
        if role == "Jungle":
            smite_in_pool = next((s for s in pool if s['name'] == 'Smite'), None)
            if smite_in_pool:
                other_spells = [s for s in pool if s['name'] != 'Smite']
                spells = [smite_in_pool, random.choice(other_spells)]
            else:
                spells = random.sample(pool, 2)
        else:
            non_smite_pool = [s for s in pool if s['name'] != 'Smite']
            spells = random.sample(non_smite_pool, 2)
            
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

db = load_db()
all_players_db = sorted(list(db.keys()))

# --- ZARZĄDZANIE AUDIO Z FOLDERU NUTY (WŁASNY ODTWARZACZ HTML/JS) ---
playlist_data = []
supported_formats = ('.mp3', '.wav', '.ogg')
if os.path.exists("nuty"):
    for f in sorted(os.listdir("nuty")):
        if f.lower().endswith(supported_formats):
            b64 = get_base64_of_bin_file(os.path.join("nuty", f))
            playlist_data.append(f"data:audio/mp3;base64,{b64}")

if not playlist_data:
    playlist_data.append("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3")
    playlist_data.append("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3")

playlist_json = json.dumps(playlist_data)

audio_html = f"""
<div style="font-family: sans-serif; text-align:center; padding: 10px; background: rgba(0,0,0,0.5); border-radius: 10px; border: 1px solid #c8aa6e; color: #fff;">
    <h4 style="color: #f2d590; margin-top: 0; margin-bottom: 10px;">🎵 Złota Szafa Grająca (Playlista)</h4>
    <audio id="custom-audio-player" controls autoplay style="height: 35px; border-radius: 20px; outline: none; width: 100%; max-width: 400px;">
        <source id="audio-source" src="" type="audio/mp3">
    </audio>
    <div style="font-size: 11px; color: #aaa; margin-top: 5px;">
        <i>*Zabezpieczenia przeglądarek blokują autoplay. Kliknij raz <b>"Play"</b>, a utwory z folderu <b>"nuty"</b> będą leciały jeden za drugim!*</i>
    </div>
    <script>
        var playlist = {playlist_json};
        var current_song = 0;
        var audio = document.getElementById('custom-audio-player');
        
        if (playlist.length > 0) {{
            audio.src = playlist[0];
            audio.volume = 0.3;
            var playPromise = audio.play();
            if (playPromise !== undefined) {{
                playPromise.catch(function(error) {{
                    console.log("Autoplay zablokowany. Wymagana interakcja użytkownika.");
                }});
            }}
        }}
        
        audio.onended = function() {{
            current_song++;
            if (current_song >= playlist.length) current_song = 0;
            audio.src = playlist[current_song];
            audio.play();
        }};
    </script>
</div>
"""
components.html(audio_html, height=130)

# --- DUŻY DEEP U GÓRY EKRANU Z DYMKIEM ---
big_deep_b64 = get_avatar_b64("deepmeme") or get_avatar_b64("deep")
if big_deep_b64:
    st.markdown(f"""
    <div style="display: flex; justify-content: center; margin-top: 10px; margin-bottom: 20px;">
        <div class="deep-container">
            <img src="{big_deep_b64}" class="deep-img" style="width: 250px; height: 250px; border-radius: 50%; object-fit: cover; border: 4px solid #c8aa6e; box-shadow: 0 0 30px rgba(242, 213, 144, 0.6);">
            <div class="deep-text">👑 "To ja tu rządzę! Losuj te śmieci, może w końcu ugracie chociaż Clash'a w Tier 4!" 👑</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Nagłówek
header_col1, header_col2, header_col3 = st.columns([1, 8, 1])
with header_col2:
    st.markdown("<h1 style='text-align: center; color: #f2d590; text-shadow: 2px 2px 4px #000; margin-bottom: 0;'>⚔️ ChaosDraft - League of Legends ⚔️</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center; color: #a5c2d3; text-shadow: 1px 1px 2px #000; margin-top: 0;'>Narzędzie do tworzenia grywalnego chaosu na Summoner's Rift</h4>", unsafe_allow_html=True)

# --- PANEL ZARZĄDZANIA GRACZAMI I WYSZUKIWARKA OP.GG ---
if 'db_msg' in st.session_state:
    st.success(st.session_state['db_msg'])
    del st.session_state['db_msg']

with st.expander("📜 Rejestr Przywoływaczy (OP.GG i Avatary)", expanded=False):
    col_search, col_add = st.columns(2)
    
    with col_search:
        st.markdown("#### 🕵️‍♂️ Prześwietl Przywoływacza")
        selected_search = st.selectbox("Kogo bierzemy pod lupę?", ["-- Wybierz --"] + all_players_db)
        if selected_search != "-- Wybierz --":
            p_data = db[selected_search]
            p_ava = get_avatar_b64(selected_search) or "https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/profile-icons/29.jpg"
            opgg_href = p_data.get('opgg', '#')
            opgg_display = f'<a href="{opgg_href}" target="_blank" style="color: #00a8ff; text-decoration: none; font-weight: bold; background: #1a5c8a; padding: 4px 10px; border-radius: 5px; border: 1px solid #4eb5f1;">🔗 Przejdź do OP.GG</a>' if opgg_href != '#' and opgg_href != '' else '<span style="color: #aaa;">Brak linku OP.GG</span>'
            
            st.markdown(f"""
            <div style="display:flex; align-items:center; gap: 15px; margin-top: 10px; background: rgba(0,0,0,0.4); padding: 15px; border-radius: 10px; border: 1px solid #c8aa6e;">
                <img src="{p_ava}" style="width: 80px; height: 80px; border-radius: 50%; object-fit: cover; border: 2px solid #a5c2d3;">
                <div>
                    <h3 style="margin: 0 0 10px 0; color: #f2d590;">{selected_search}</h3>
                    {opgg_display}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
    with col_add:
        st.markdown("#### 🛠️ Kuźnia Legend (Dodaj / Edytuj)")
        with st.form("add_player_form", clear_on_submit=True):
            new_name = st.text_input("Nick gracza (np. Majkel)")
            new_opgg = st.text_input("Link do profilu OP.GG (opcjonalnie)")
            new_avatar = st.file_uploader("Wgraj Avatar gracza (opcjonalnie)", type=['png', 'jpg', 'jpeg'])
            submit_btn = st.form_submit_button("Zapisz w Bazie")
            
            if submit_btn and new_name:
                save_player_to_db(new_name, new_opgg, new_avatar)
                st.session_state['db_msg'] = f"Zapisano gracza: {new_name}!"
                st.rerun()

# Baner Clash
st.image("https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-clash/global/default/assets/images/rewards-modal/header-background.png", use_container_width=True)

# Ładowanie danych
with st.spinner('Zaciągam najświeższe dane o LoL-u wprost z serwerów Riot Games...'):
    version, champs, valid_items, valid_classic_items, valid_support_items, all_items, valid_summoners = fetch_riot_data()
    app = ChaosDraft(champs, valid_items, valid_classic_items, valid_support_items, valid_summoners)

def get_idx(name):
    return all_players_db.index(name) if name in all_players_db else 0

st.markdown("### 👥 Wybierz swoją drużynę:")
col1, col2, col3, col4, col5 = st.columns(5)
with col1: p1 = st.selectbox("Gracz 1", all_players_db, index=get_idx("Majkel"))
with col2: p2 = st.selectbox("Gracz 2", all_players_db, index=get_idx("Pecker"))
with col3: p3 = st.selectbox("Gracz 3", all_players_db, index=get_idx("arekjanicki"))
with col4: p4 = st.selectbox("Gracz 4", all_players_db, index=get_idx("Menni"))
with col5: p5 = st.selectbox("Gracz 5", all_players_db, index=get_idx("Przemuś"))

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
        if len(set(players)) == len(players):
            st.session_state['wyniki'] = app.draft_standard(players, champs_per_player=champs_count_std)
        else:
            st.error("Gracze nie mogą się powtarzać!")

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
        if len(set(players)) == len(players):
            st.session_state['wyniki'] = app.draft_combo(players, combo_name=selected_combo, champs_per_player=champs_count_combo)
        else:
            st.error("Gracze nie mogą się powtarzać!")

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
        if len(set(players_list)) == len(players_list):
            st.session_state['wyniki'] = app.draft_custom(players_list, player_pools, champs_per_player=champs_count_custom)
        else:
            st.error("Gracze nie mogą się powtarzać!")

with tab4:
    przemusmeme_b64 = get_avatar_b64("przemuśmeme")
    if przemusmeme_b64:
        st.markdown(f'<img src="{przemusmeme_b64}" style="{banner_style}">', unsafe_allow_html=True)
    else:
        st.image("https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Annie_0.jpg", use_container_width=True)
        
    st.info("⏳ Tryb Classic (Patch 26.15): Ścisła pula przedmiotów z premiery trybu Classic! Naciśnij na przedmiot w wynikach aby przypomnieć sobie jego oryginalne statystyki.")
    champs_count_classic = st.slider("Ile postaci wylosować dla każdego gracza? (Classic)", 1, 3, 2, key="classic_slider")
    if st.button("⏳ LOSUJ TRYB CLASSIC!", use_container_width=True, type="primary"):
        players = [p1, p2, p3, p4, p5]
        if len(set(players)) == len(players):
            st.session_state['wyniki'] = app.draft_classic(players, champs_per_player=champs_count_classic)
        else:
            st.error("Gracze nie mogą się powtarzać!")

# --- WYNIKI LOSOWANIA ---
if 'wyniki' in st.session_state:
    st.markdown("---")
    
    wyniki = st.session_state['wyniki']
    for player, data in wyniki.items():
        if len(data['options']) == 0:
            continue
            
        avatar_b64 = get_avatar_b64(player)
        avatar_img_src = avatar_b64 if avatar_b64 else "https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/profile-icons/29.jpg"
        
        player_opgg = db.get(player, {}).get("opgg", "")
        opgg_html = f'<div style="margin-top: 8px;"><a href="{player_opgg}" target="_blank" style="background: #1a5c8a; color: white; padding: 4px 10px; border-radius: 6px; text-decoration: none; font-size: 12px; border: 1px solid #4eb5f1; box-shadow: 0 2px 4px rgba(0,0,0,0.5); transition: background 0.3s;">OP.GG</a></div>' if player_opgg else ""
        
        # Wyciąganie unikalnego cytatu gracza
        player_quote = PLAYER_QUOTES.get(player, random.choice(DEFAULT_QUOTES))
        
        options_html = ""
        for option in data['options']:
            champ_img_url = f"https://ddragon.leagueoflegends.com/cdn/img/champion/tiles/{option['id']}_{option['skin_num']}.jpg"
            
            spell1_html = build_spell_html(option['spells'][0], version)
            spell2_html = build_spell_html(option['spells'][1], version)
            
            items_html = "".join([build_item_html(item, version, all_items) for item in option['build']])
            
            champ_image_html = f'<img src="{champ_img_url}" style="width: 70px; height: 70px; object-fit: cover; border-radius: 6px; border: 1px solid #a5c2d3;">'
            
            options_html += f"""<div style="flex: 1; min-width: 250px; background: rgba(10,10,10,0.6); border-radius: 8px; padding: 10px; border: 1px solid #444;">
<div style="display: flex; align-items: center; gap: 12px; margin-bottom: 10px;">
{champ_image_html}
<div style="display: flex; flex-direction: column;">
<span style="font-size: 16px; font-weight: bold; color: #f2d590;">{option['name']}</span>
<span style="font-size: 12px; color: #aaa; margin-bottom: 4px;">{option['class']}</span>
<div style="display: flex; align-items: center;">
{spell1_html}
{spell2_html}
</div>
</div>
</div>
<div style="display: flex; flex-wrap: wrap; gap: 6px; margin-top: 10px;">
{items_html}
</div>
</div>"""
            
        player_row_html = f"""<div class="draft-card-anim" style="display: flex; background: rgba(20,25,30,0.85); border: 1px solid #c8aa6e; border-radius: 12px; padding: 15px; margin-bottom: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
<div style="flex: 0 0 100px; text-align: center; border-right: 1px solid #555; padding-right: 15px; margin-right: 15px;">

<div class="player-avatar-container">
    <img src="{avatar_img_src}" class="player-avatar-img" style="width: 70px; height: 70px; border-radius: 50%; object-fit: cover; border: 2px solid #a5c2d3;">
    <div class="player-quote">💬 "{player_quote}"</div>
</div>

<div style="font-weight: 800; font-size: 16px; margin-top: 5px; color: #fff;">{player}</div>
<div style="color: #c8aa6e; font-size: 14px; font-weight: bold; text-transform: uppercase;">{data['role']}</div>
{opgg_html}
</div>
<div style="display: flex; flex-wrap: wrap; gap: 15px; flex-grow: 1;">
{options_html}
</div>
</div>"""
        st.markdown(player_row_html, unsafe_allow_html=True)
