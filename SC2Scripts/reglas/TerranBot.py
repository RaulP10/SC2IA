from sc2.bot_ai import BotAI
from sc2.generate_ids import UnitTypeId
import random

class TerranBot(BotAI):
    
    async def on_step(self, iteration: int):
        self.log_status(iteration)
        await self.distribute_workers()
        if self.townhalls:
            command_center = self.townhalls.random
            await self.manage_scvs_and_supply_depots(command_center)
            await self.manage_essential_structures(command_center)
            await self.manage_units()
            await self.attack_with_all_units_together()
            await self.expand_now_if_possible()
        else:
            await self.expand_now_if_possible()
    
    def log_status(self, iteration: int):
        """Logs the current game state."""
        print(f"{iteration}, n_workers: {self.workers.amount}, n_idle_workers: {self.workers.idle.amount}, "
              f"minerals: {self.minerals}, gas: {self.vespene}, bunkers: {self.structures(UnitTypeId.BUNKER).amount}, "
              f"supply_depots: {self.structures(UnitTypeId.SUPPLYDEPOT).amount}, command_centers: {self.structures(UnitTypeId.COMMANDCENTER).amount}, "
              f"factories: {self.structures(UnitTypeId.FACTORY).amount}, starports: {self.structures(UnitTypeId.STARPORT).amount}, "
              f"marines: {self.units(UnitTypeId.MARINE).amount}, supply: {self.supply_used}/{self.supply_cap}")

    async def manage_marine(self):
        """Manage the production of Marine."""
        if self.units(UnitTypeId.MARINE).amount < 12 and self.can_afford(UnitTypeId.MARINE):
            for factory in self.structures(UnitTypeId.BARRACKS).ready.idle:
                if self.can_afford(UnitTypeId.MARINE):
                    factory.train(UnitTypeId.MARINE)

    async def manage_hellion(self):
        """Mange the production of Hellion."""
        if self.units(UnitTypeId.HELLION).amount < 8 and self.can_afford(UnitTypeId.HELLION):
            for factory in self.structures(UnitTypeId.FACTORY).ready.idle:
                if self.can_afford(UnitTypeId.HELLION):
                    factory.train(UnitTypeId.HELLION)

    async def manage_liberator(self):
        """Mange the production of Liberatos."""
        if self.units(UnitTypeId.LIBERATOR).amount < 4 and self.can_afford(UnitTypeId.LIBERATOR):
            for factory in self.structures(UnitTypeId.STARPORT).ready.idle:
                if self.can_afford(UnitTypeId.LIBERATOR):
                    factory.train(UnitTypeId.LIBERATOR)

    async def manage_scvs_and_supply_depots(self, command_center):
        """Manage SCV and Supply Depot production."""
        supply_remaining = self.supply_cap - self.supply_used
        if command_center.is_idle and self.can_afford(UnitTypeId.SCV) and supply_remaining > 4:
            command_center.train(UnitTypeId.SCV)
        elif not self.structures(UnitTypeId.SUPPLYDEPOT) and self.already_pending(UnitTypeId.SUPPLYDEPOT) == 0:
            if self.can_afford(UnitTypeId.SUPPLYDEPOT):
                await self.build(UnitTypeId.SUPPLYDEPOT, near=command_center)
        elif self.structures(UnitTypeId.SUPPLYDEPOT).amount < 5:
            if self.can_afford(UnitTypeId.SUPPLYDEPOT):
                await self.build_supply_depot_away_from_enemy()
    
    async def build_supply_depot_away_from_enemy(self):
        """Build a Supply Depot away from the enemy's starting location."""
        target_supply_depot = self.structures(UnitTypeId.SUPPLYDEPOT).closest_to(self.enemy_start_locations[0])
        pos = target_supply_depot.position.towards(self.enemy_start_locations[0], random.randrange(8, 15))
        await self.build(UnitTypeId.SUPPLYDEPOT, near=pos)
    
    async def manage_essential_structures(self, command_center):
        """Build essential structures like Refineries, Barracks, TechLab, Factories, and Starports."""
        if self.structures(UnitTypeId.REFINERY).amount <= 1:
            await self.build_refineries()
        elif not self.structures(UnitTypeId.SUPPLYDEPOT):
            if self.can_afford(UnitTypeId.SUPPLYDEPOT):
                await self.build(UnitTypeId.SUPPLYDEPOT, near=self.structures(UnitTypeId.PYLON).closest_to(command_center))
        elif not self.structures(UnitTypeId.BARRACKS) and self.structures(UnitTypeId.SUPPLYDEPOT).amount > 2:
            if self.can_afford(UnitTypeId.BARRACKS):
                await self.build(UnitTypeId.BARRACKS, near=self.structures(UnitTypeId.SUPPLYDEPOT).closest_to(command_center))
        elif not self.structures(UnitTypeId.FACTORY):
            if self.can_afford(UnitTypeId.FACTORY):
                await self.build(UnitTypeId.FACTORY, near=self.structures(UnitTypeId.SUPPLYDEPOT).closest_to(command_center))
        elif not self.structures(UnitTypeId.STARPORT):
            if self.can_afford(UnitTypeId.STARPORT):
                await self.build(UnitTypeId.STARPORT, near=self.structures(UnitTypeId.SUPPLYDEPOT).closest_to(command_center))
    
    async def build_refineries(self):
        """Build Refineries on nearby Vespene Geysers."""
        for command_center in self.structures(UnitTypeId.COMMANDCENTER):
            vespenes = self.vespene_geyser.closer_than(15, command_center)
            for vespene in vespenes:
                if self.can_afford(UnitTypeId.REFINERY) and not self.already_pending(UnitTypeId.REFINERY):
                    await self.build(UnitTypeId.REFINERY, vespene)
    
    async def expand_now_if_possible(self):
        """Expand to a new base if possible."""
        if self.can_afford(UnitTypeId.COMMANDCENTER):
            await self.expand_now()
    
    async def attack_with_marine(self):
        """Command Marine to attack."""
        if self.units(UnitTypeId.MARINE).amount >= 12:
            if self.enemy_units:
                for marine in self.units(UnitTypeId.MARINE).idle:
                    marine.attack(random.choice(self.enemy_units))
            elif self.enemy_structures:
                for marine in self.units(UnitTypeId.MARINE).idle:
                    marine.attack(random.choice(self.enemy_structures))
            else:
                for marine in self.units(UnitTypeId.MARINE).idle:
                    marine.attack(self.enemy_start_locations[0])

    async def attack_with_hellions(self):
        """Command Hellions to attack."""
        if self.units(UnitTypeId.HELLION).amount >= 8:
            if self.enemy_units:
                for hellion in self.units(UnitTypeId.HELLION).idle:
                    hellion.attack(random.choice(self.enemy_units))
            elif self.enemy_structures:
                for hellion in self.units(UnitTypeId.HELLION).idle:
                    hellion.attack(random.choice(self.enemy_structures))
            else:
                for hellion in self.units(UnitTypeId.HELLION).idle:
                    hellion.attack(self.enemy_start_locations[0])


    async def attack_with_liberators(self):
        """Command Liberators to attack."""
        if self.units(UnitTypeId.LIBERATOR).amount >= 4:
            if self.enemy_units:
                for liberator in self.units(UnitTypeId.LIBERATOR).idle:
                    liberator.attack(random.choice(self.enemy_units))
            elif self.enemy_structures:
                for liberator in self.units(UnitTypeId.LIBERATOR).idle:
                    liberator.attack(random.choice(self.enemy_structures))
            else:
                for liberator in self.units(UnitTypeId.LIBERATOR).idle:
                    liberator.attack(self.enemy_start_locations[0])
    
    async def attack_with_all_units_together(self):
        if self.units(UnitTypeId.MARINE).amount >= 10 and self.units(UnitTypeId.HELLION).amount >= 8 and self.units(UnitTypeId.LIBERATOR).amount >= 4:
            await self.attack_with_marine()
            await self.attack_with_hellions()
            await self.attack_with_liberators()

    async def manage_units(self):
        if self.units(UnitTypeId.MARINE).amount <= 12:
            await self.manage_marine()
        if self.units(UnitTypeId.MARINE).amount >= 10 and self.units(UnitTypeId.HELLION).amount <= 8:
            await self.manage_hellion()
        if self.units(UnitTypeId.HELLION).amount >= 6 and self.units(UnitTypeId.LIBERATOR).amount <= 4:
            await self.manage_liberator()
    
