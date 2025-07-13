# main.py

import importlib
from sc2.main import run_game
from sc2 import maps
from sc2.player import Bot, Computer
from sc2.data import Race
from SC2Scripts.reglas.config_window import get_user_config

# Diccionario para mapear razas a módulos de bot
bot_modules = {
    "Protoss": "ProtossBot",
    "Terran": "TerranBot",
    "Zerg": "ZergBot"
}

# Diccionario para mapear nombres de raza a constantes de sc2
race_dict = {
    "Protoss": Race.Protoss,
    "Terran": Race.Terran,
    "Zerg": Race.Zerg
}

def get_bot_class(race):
    module_name = bot_modules.get(race)
    if module_name is None:
        raise ValueError(f"No module found for race: {race}")
    module = importlib.import_module(module_name)
    bot_class_name = f"{race}Bot"  # Asume que la clase en cada módulo se llama <Race>Bot
    return getattr(module, bot_class_name)

if __name__ == "__main__":
    # Mostrar la ventana de configuración
    config = get_user_config()

    # Imprimir configuración para depuración
    print(f"Configuration: {config}")

    # Obtener la clase del bot
    bot_class = get_bot_class(config['player_race'])
    
    # Convertir la raza a la constante Race
    player_race = race_dict[config['player_race']]
    enemy_race = race_dict[config['enemy_race']]
    
    # Ejecutar el juego
    run_game(
        maps.get("TritonLE"),
        [
            Bot(player_race, bot_class()),  # Usa la clase de bot determinada por la raza
            Computer(enemy_race, config['difficulty'])  # Configura el enemigo con la raza y dificultad seleccionadas
        ],
        realtime=False
    )
