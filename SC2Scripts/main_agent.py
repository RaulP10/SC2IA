from pysc2.env import sc2_env
from pysc2.lib import actions, features, units
import numpy as np

# Definir acciones básicas
NO_OP = actions.FUNCTIONS.no_op.id
SELECT_POINT = actions.FUNCTIONS.select_point.id
TRAIN_SCV = actions.FUNCTIONS.Train_SCV_quick.id

def main():
    # Configuración del entorno SC2
    env = sc2_env.SC2Env(
        map_name="Simple64",
        players=[sc2_env.Agent(sc2_env.Race.terran),
                 sc2_env.Bot(sc2_env.Race.zerg, sc2_env.Difficulty.easy)],
        agent_interface_format=features.AgentInterfaceFormat(
            feature_dimensions=features.Dimensions(screen=84, minimap=64),
            use_feature_units=True
        ),
        step_mul=8,
        game_steps_per_episode=0,
        visualize=True
    )

    try:
        for episode in range(5):
            obs = env.reset()
            done = False
            selected_command_center = False  # Bandera para saber si el CommandCenter está seleccionado

            print(f"--- Episodio {episode + 1} iniciado ---")
            while not done:
                obs = obs[0]
                available_actions = obs.observation["available_actions"]
                feature_units = obs.observation.feature_units

                # Seleccionar Command Center si no está seleccionado
                if not selected_command_center and SELECT_POINT in available_actions:
                    for unit in feature_units:
                        if unit.unit_type == units.Terran.CommandCenter:
                            action = actions.FUNCTIONS.select_point("select", (unit.x, unit.y))
                            print("Acción: Seleccionando Command Center")
                            obs = env.step([action])
                            selected_command_center = True
                            break
                    continue  # Pasar al siguiente paso después de seleccionar

                # Verificar si se puede entrenar un SCV
                if TRAIN_SCV in available_actions:
                    action = actions.FUNCTIONS.Train_SCV_quick("now")
                    print("Acción: Entrenando SCV")
                else:
                    action = actions.FUNCTIONS.no_op()
                    print("Acción: No op")

                # Ejecutar la acción en el entorno
                obs = env.step([action])
                done = obs[0].last()

            print(f"--- Episodio {episode + 1} completado ---")

    except KeyboardInterrupt:
        print("\nInterrupción por teclado detectada. Cerrando el programa...")

    finally:
        env.close()
        print("Entorno cerrado.")

if __name__ == "__main__":
    main()
