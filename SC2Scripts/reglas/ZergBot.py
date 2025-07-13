from sc2.bot_ai import BotAI
from sc2.generate_ids import UnitTypeId
import random

class ZergBot(BotAI):

    async def on_step(self, iteration: int):
        self.log_status(iteration)
        await self.distribute_workers()
        if self.townhalls:
            hatchery = self.townhalls.random
            await self.manage_drones_and_overlords(hatchery)
            await self.manage_essential_structures(hatchery)
            await self.manage_army(hatchery)
            await self.attack_with_army()
            await self.expand_now_if_possible()
        else:
            await self.expand_now_if_possible()

    def log_status(self, iteration: int):
        """Logs the current game state."""
        print(f"{iteration}, n_workers: {self.workers.amount}, n_idle_workers: {self.workers.idle.amount}, "
              f"minerals: {self.minerals}, gas: {self.vespene}, spines: {self.structures(UnitTypeId.SPINECRAWLER).amount}, "
              f"overlords: {self.units(UnitTypeId.OVERLORD).amount}, hatcheries: {self.structures(UnitTypeId.HATCHERY).amount}, "
              f"queens: {self.units(UnitTypeId.QUEEN).amount}, mutalisks: {self.units(UnitTypeId.MUTALISK).amount}, "
              f"zerglings: {self.units(UnitTypeId.ZERGLING).amount}, hydralisks: {self.units(UnitTypeId.HYDRALISK).amount}, "
              f"ultralisks: {self.units(UnitTypeId.ULTRALISK).amount}, supply: {self.supply_used}/{self.supply_cap}")

    async def manage_drones_and_overlords(self, hatchery):
        """Manage Drone and Overlord production."""
        supply_remaining = self.supply_cap - self.supply_used

        if self.can_afford(UnitTypeId.DRONE) and hatchery.is_idle and supply_remaining > 0:
            hatchery.train(UnitTypeId.DRONE)
        if self.supply_left < 2 and self.can_afford(UnitTypeId.OVERLORD) and self.already_pending(UnitTypeId.OVERLORD) == 0:
            hatchery.train(UnitTypeId.OVERLORD)

    async def manage_essential_structures(self, hatchery):
        """Build essential structures like Extractors, Spawning Pool, Roach Warren, Spires, and Ultralisks Cavern."""
        if self.structures(UnitTypeId.SPAWNINGPOOL).amount == 0 and self.can_afford(UnitTypeId.SPAWNINGPOOL):
            await self.build(UnitTypeId.SPAWNINGPOOL, near=hatchery)

        if self.structures(UnitTypeId.SPAWNINGPOOL).ready:
            if not self.structures(UnitTypeId.LAIR) and self.can_afford(UnitTypeId.LAIR):
                await self.do(hatchery.build(UnitTypeId.LAIR))

            if self.structures(UnitTypeId.LAIR).ready:
                if not self.structures(UnitTypeId.SPIRE) and self.can_afford(UnitTypeId.SPIRE):
                    await self.build(UnitTypeId.SPIRE, near=hatchery)

                if not self.structures(UnitTypeId.HYDRALISKDEN) and self.can_afford(UnitTypeId.HYDRALISKDEN):
                    await self.build(UnitTypeId.HYDRALISKDEN, near=hatchery)

                if not self.structures(UnitTypeId.ULTRALISKCAVERN) and self.structures(UnitTypeId.HIVE).ready and self.can_afford(UnitTypeId.ULTRALISKCAVERN):
                    await self.build(UnitTypeId.ULTRALISKCAVERN, near=hatchery)
    
    async def build_extractors(self):
        """Build Extractors on nearby Vespene Geysers."""
        for hatchery in self.townhalls.ready:
            vespenes = self.vespene_geyser.closer_than(15, hatchery)
            for vespene in vespenes:
                if self.can_afford(UnitTypeId.EXTRACTOR) and not self.already_pending(UnitTypeId.EXTRACTOR):
                    drone = self.workers.random
                    if drone:
                        await self.do(drone.build_gas(vespene))

    async def manage_army(self, hatchery):
        """Manage the production of Zerglings, Hydralisks, and Ultralisks."""
        larvae = self.units(UnitTypeId.LARVA)

        if larvae and self.can_afford(UnitTypeId.ZERGLING) and self.structures(UnitTypeId.SPAWNINGPOOL).ready:
            larvae.random.train(UnitTypeId.ZERGLING)
        
        if larvae and self.can_afford(UnitTypeId.HYDRALISK) and self.structures(UnitTypeId.HYDRALISKDEN).ready:
            larvae.random.train(UnitTypeId.HYDRALISK)

        if larvae and self.can_afford(UnitTypeId.ULTRALISK) and self.structures(UnitTypeId.ULTRALISKCAVERN).ready:
            larvae.random.train(UnitTypeId.ULTRALISK)

        if larvae and self.can_afford(UnitTypeId.MUTALISK) and self.structures(UnitTypeId.SPIRE).ready:
            larvae.random.train(UnitTypeId.MUTALISK)

    async def attack_with_army(self):
        """Command the army to attack."""
        if self.units(UnitTypeId.ZERGLING).amount >= 20:
            for zergling in self.units(UnitTypeId.ZERGLING).idle:
                zergling.attack(self.enemy_start_locations[0])
        if self.units(UnitTypeId.HYDRALISK).amount >= 10:
            for hydralisk in self.units(UnitTypeId.HYDRALISK).idle:
                hydralisk.attack(self.enemy_start_locations[0])
        if self.units(UnitTypeId.ULTRALISK).amount >= 3:
            for ultralisk in self.units(UnitTypeId.ULTRALISK).idle:
                ultralisk.attack(self.enemy_start_locations[0])
        if self.units(UnitTypeId.MUTALISK).amount >= 3:
            if self.enemy_units:
                for mutalisk in self.units(UnitTypeId.MUTALISK).idle:
                    mutalisk.attack(random.choice(self.enemy_units))
            elif self.enemy_structures:
                for mutalisk in self.units(UnitTypeId.MUTALISK).idle:
                    mutalisk.attack(random.choice(self.enemy_structures))
            else:
                for mutalisk in self.units(UnitTypeId.MUTALISK).idle:
                    mutalisk.attack(self.enemy_start_locations[0])

    async def expand_now_if_possible(self):
        """Expand to a new base if possible."""
        if self.can_afford(UnitTypeId.HATCHERY):
            await self.expand_now()
