import random
from pysc2.agents import base_agent
from pysc2.lib import actions, features

# Acciones simplificadas
_NO_OP = actions.FUNCTIONS.no_op.id
_MOVE_SCREEN = actions.FUNCTIONS.Move_screen.id

# Parámetros
_PLAYER_RELATIVE = features.SCREEN_FEATURES.player_relative.index
_SELECT_POINT = actions.FUNCTIONS.select_point.id

_NOT_QUEUED = [0]
_SELECT_ALL = [2]

class BasicAgent(base_agent.BaseAgent):
    def step(self, obs):
        super(BasicAgent, self).step(obs)

        # Realiza una acción aleatoria
        if _MOVE_SCREEN in obs.observation.available_actions:
            x = random.randint(0, obs.observation.feature_screen.shape[1] - 1)
            y = random.randint(0, obs.observation.feature_screen.shape[0] - 1)
            return actions.FunctionCall(_MOVE_SCREEN, [_NOT_QUEUED, [x, y]])

        return actions.FunctionCall(_NO_OP, [])