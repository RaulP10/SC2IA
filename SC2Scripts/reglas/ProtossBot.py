from sc2.bot_ai import BotAI
from sc2.generate_ids import UnitTypeId
import random

class ProtossBot(BotAI):
    
    async def on_step(self, iteration: int):
        self.log_status(iteration)
        await self.distribute_workers()
        if self.townhalls:
            nexus = self.townhalls.random
            await self.manage_voidrays()
            await self.manage_probes_and_pylons(nexus)
            await self.manage_essential_structures(nexus)
            await self.attack_with_voidrays()
            await self.expand_now_if_possible()
        else:
            await self.expand_now_if_possible()
    
    def log_status(self, iteration: int):
        """Logs the current game state."""
        print(f"{iteration}, n_workers: {self.workers.amount}, n_idle_workers: {self.workers.idle.amount}, "
              f"minerals: {self.minerals}, gas: {self.vespene}, cannons: {self.structures(UnitTypeId.PHOTONCANNON).amount}, "
              f"pylons: {self.structures(UnitTypeId.PYLON).amount}, nexus: {self.structures(UnitTypeId.NEXUS).amount}, "
              f"gateways: {self.structures(UnitTypeId.GATEWAY).amount}, cybernetics cores: {self.structures(UnitTypeId.CYBERNETICSCORE).amount}, "
              f"stargates: {self.structures(UnitTypeId.STARGATE).amount}, voidrays: {self.units(UnitTypeId.VOIDRAY).amount}, "
              f"supply: {self.supply_used}/{self.supply_cap}")

    async def manage_voidrays(self):
        """Manage the production of Void Rays."""
        if self.structures(UnitTypeId.VOIDRAY).amount < 10 and self.can_afford(UnitTypeId.VOIDRAY):
            for sg in self.structures(UnitTypeId.STARGATE).ready.idle:
                if self.can_afford(UnitTypeId.VOIDRAY):
                    sg.train(UnitTypeId.VOIDRAY)

    async def manage_probes_and_pylons(self, nexus):
        """Manage Probe and Pylon production."""
        supply_remaining = self.supply_cap - self.supply_used
        if nexus.is_idle and self.can_afford(UnitTypeId.PROBE) and supply_remaining > 4:
            nexus.train(UnitTypeId.PROBE)
        elif not self.structures(UnitTypeId.PYLON) and self.already_pending(UnitTypeId.PYLON) == 0:
            if self.can_afford(UnitTypeId.PYLON):
                await self.build(UnitTypeId.PYLON, near=nexus)
        elif self.structures(UnitTypeId.PYLON).amount < 5:
            if self.can_afford(UnitTypeId.PYLON):
                await self.build_pylon_away_from_enemy()
    
    async def build_pylon_away_from_enemy(self):
        """Build a Pylon away from the enemy's starting location."""
        target_pylon = self.structures(UnitTypeId.PYLON).closest_to(self.enemy_start_locations[0])
        pos = target_pylon.position.towards(self.enemy_start_locations[0], random.randrange(8, 15))
        await self.build(UnitTypeId.PYLON, near=pos)
    
    async def manage_essential_structures(self, nexus):
        """Build essential structures like Assimilators, Forge, Gateways, Cybernetics Cores, and Stargates."""
        if self.structures(UnitTypeId.ASSIMILATOR).amount <= 1:
            await self.build_assimilators()
        elif not self.structures(UnitTypeId.FORGE):
            if self.can_afford(UnitTypeId.FORGE):
                await self.build(UnitTypeId.FORGE, near=self.structures(UnitTypeId.PYLON).closest_to(nexus))
        elif self.structures(UnitTypeId.FORGE).ready and self.structures(UnitTypeId.PHOTONCANNON).amount < 3:
            if self.can_afford(UnitTypeId.PHOTONCANNON):
                await self.build(UnitTypeId.PHOTONCANNON, near=nexus)
        elif not self.structures(UnitTypeId.GATEWAY):
            if self.can_afford(UnitTypeId.GATEWAY):
                await self.build(UnitTypeId.GATEWAY, near=self.structures(UnitTypeId.PYLON).closest_to(nexus))
        elif not self.structures(UnitTypeId.CYBERNETICSCORE):
            if self.can_afford(UnitTypeId.CYBERNETICSCORE):
                await self.build(UnitTypeId.CYBERNETICSCORE, near=self.structures(UnitTypeId.PYLON).closest_to(nexus))
        elif not self.structures(UnitTypeId.STARGATE):
            if self.can_afford(UnitTypeId.STARGATE):
                await self.build(UnitTypeId.STARGATE, near=self.structures(UnitTypeId.PYLON).closest_to(nexus))
    
    async def build_assimilators(self):
        """Build Assimilators on nearby Vespene Geysers."""
        for nexus in self.structures(UnitTypeId.NEXUS):
            vespenes = self.vespene_geyser.closer_than(15, nexus)
            for vespene in vespenes:
                if self.can_afford(UnitTypeId.ASSIMILATOR) and not self.already_pending(UnitTypeId.ASSIMILATOR):
                    await self.build(UnitTypeId.ASSIMILATOR, vespene)
    
    async def expand_now_if_possible(self):
        """Expand to a new base if possible."""
        if self.can_afford(UnitTypeId.NEXUS):
            await self.expand_now()
    
    async def attack_with_voidrays(self):
        """Command Void Rays to attack."""
        if self.units(UnitTypeId.VOIDRAY).amount >= 3:
            if self.enemy_units:
                for vr in self.units(UnitTypeId.VOIDRAY).idle:
                    vr.attack(random.choice(self.enemy_units))
            elif self.enemy_structures:
                for vr in self.units(UnitTypeId.VOIDRAY).idle:
                    vr.attack(random.choice(self.enemy_structures))
            else:
                for vr in self.units(UnitTypeId.VOIDRAY).idle:
                    vr.attack(self.enemy_start_locations[0])
