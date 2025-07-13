# config_window.py

import tkinter as tk
from tkinter import ttk
from sc2.data import Difficulty, Race  # difficulty for bots, race for the 1 of 3 races

def get_user_config():
    root = tk.Tk()
    root.title("Configuración del Juego")

    # Variables para almacenar las selecciones del usuario
    player_race_var = tk.StringVar(value="Protoss")
    enemy_race_var = tk.StringVar(value="Terran")
    difficulty_var = tk.StringVar(value="Fácil")

    # Diccionarios para traducir los nombres de las opciones a los valores de sc2
    race_dict = {
        "Protoss": Race.Protoss,
        "Terran": Race.Terran,
        "Zerg": Race.Zerg
    }

    difficulty_dict = {
        "Fácil": Difficulty.Easy,
        "Medio": Difficulty.Medium,
        "Difícil": Difficulty.Hard,
        "Muy Difícil": Difficulty.VeryHard,
        "Imposible": Difficulty.CheatInsane
    }

    # Crear y agregar los widgets de selección
    tk.Label(root, text="Selecciona tu raza:").grid(row=0, column=0, padx=10, pady=10)
    player_race_combobox = ttk.Combobox(root, textvariable=player_race_var, values=list(race_dict.keys()))
    player_race_combobox.grid(row=0, column=1, padx=10, pady=10)

    tk.Label(root, text="Selecciona la raza del enemigo:").grid(row=1, column=0, padx=10, pady=10)
    enemy_race_combobox = ttk.Combobox(root, textvariable=enemy_race_var, values=list(race_dict.keys()))
    enemy_race_combobox.grid(row=1, column=1, padx=10, pady=10)

    tk.Label(root, text="Selecciona la dificultad del enemigo:").grid(row=2, column=0, padx=10, pady=10)
    difficulty_combobox = ttk.Combobox(root, textvariable=difficulty_var, values=list(difficulty_dict.keys()))
    difficulty_combobox.grid(row=2, column=1, padx=10, pady=10)

    # Función para capturar la selección del usuario y cerrar la ventana
    def on_start():
        user_config = {
            'player_race': player_race_var.get(),  # Guardar la raza como cadena
            'enemy_race': enemy_race_var.get(),    # Guardar la raza como cadena
            'difficulty': difficulty_dict[difficulty_var.get()]  # Guardar dificultad como valor de Difficulty
        }
        print(f"User Config: {user_config}")  # Imprimir configuración para depuración
        root.destroy()  # Cerrar la ventana
        root.user_config = user_config  # Guardar la configuración en la ventana principal

    # Botón para iniciar el juego
    start_button = tk.Button(root, text="Iniciar Juego", command=on_start)
    start_button.grid(row=3, columnspan=2, pady=20)

    # Iniciar el bucle de la interfaz gráfica
    root.mainloop()

    return root.user_config
