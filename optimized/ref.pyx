from __future__ import annotations

import math
import random
from abc import abstractmethod
from functools import reduce
from typing import List, Optional

import numpy as np


class GameManager:
    max_turns: int
    league_level: int
    solo: bool
    players: List[Player]
    active_players: List[Player]

    def __init__(self, league_level=1, solo=False):
        self.players = []
        self.active_players = []
        self.players.append(Player("blue"))

        self.solo = solo
        if not self.solo:
            self.players.append(Player("red"))

        self.active_players = self.players
        self.league_level = league_level
        self.max_turns = 200


class Referee:
    obstacles: List[Obstacle]
    game_manager: GameManager
    end_game: bool
    turn: int
    towers: bool
    giants: bool
    mines: bool
    fixed_income: int
    obstacle_count: int
    queen_hp: int

    def __init__(self, params, solo=False):
        self.obstacles = []

        self.game_manager = GameManager(solo=solo)

        self.end_game = False
        self.turn = 0

        if "leagueLevel" in params:
            self.game_manager.league_level = params["leagueLevel"]

        if self.game_manager.league_level == 1:
            self.towers = False
            self.giants = False
            self.mines = False
            self.fixed_income = Constants.WOOD_FIXED_INCOME
            self.obstacles_count = sample(Constants.OBSTACLE_PAIRS)
            self.queen_hp = 100
        elif self.game_manager.league_level == 2:
            self.towers = True
            self.giants = True
            self.mines = False
            self.fixed_income = Constants.WOOD_FIXED_INCOME
            self.obstacles_count = sample(Constants.OBSTACLE_PAIRS)
            self.queen_hp = 100
        elif self.game_manager.league_level == 3:
            self.towers = True
            self.giants = True
            self.mines = True
            self.fixed_income = 0
            self.obstacles_count = Constants.OBSTACLE_PAIRS[-1]
            self.queen_hp = 100
        else:
            self.towers = True
            self.giants = True
            self.mines = True
            self.fixed_income = 0
            self.obstacles_count = Constants.OBSTACLE_PAIRS[-1]
            self.queen_hp = sample(Constants.QUEEN_HP) * Constants.QUEEN_HP_MULT

        if not self.game_manager.solo:
            self.game_manager.players[0].enemy_player = self.game_manager.players[1]
            self.game_manager.players[1].enemy_player = self.game_manager.players[0]
            self.game_manager.players[1].is_second_player = True
        for p in self.game_manager.players:
            p.health = self.queen_hp

        self.obstacles = build_map(self.obstacles_count)

        for activePlayer, invert in zip(self.game_manager.active_players, [False, True]):
            spawn_distance = 200
            if invert:
                corner = Vector2(Constants.WORLD_WIDTH - spawn_distance, Constants.WORLD_HEIGHT - spawn_distance)
            else:
                corner = Vector2(spawn_distance, spawn_distance)
            activePlayer.queen_unit = Queen(activePlayer)
            activePlayer.queen_unit.location = corner

        fix_collisions(self.all_entities())

    def get_buildings_of_player(self, player) -> List[Obstacle]:
        buildings = []
        for ent in self.obstacles:
            if ent.structure is not None and ent.structure.owner.name == player.name:
                buildings.append(ent)
        return buildings

    def game_end(self):
        for player in self.game_manager.players:
            if player.queen_unit.health <= 0:
                return True
        return False

    def all_units(self) -> List[Unit]:
        units = []
        for player in self.game_manager.players:
            units.extend(player.all_units())
        return units

    def all_entities(self):
        ent = []
        ent.extend(self.obstacles)
        ent.extend(self.all_units())
        return ent

    def schedule_building(self, player: Player, obs: Obstacle, struc_type: str, obstacles_attempted_to_build_upon: list,
                          scheduled_buildings: list):
        struc = obs.structure
        if struc is not None and struc.owner == player.enemy_player:
            raise Exception("Cannot build: owned by enemy player")
        if isinstance(struc, Barracks) and struc.owner == player and struc.is_training:
            raise Exception("Cannot rebuild: training is in progress")
        obstacles_attempted_to_build_upon.append(obs)
        token = struc_type.split('-')
        first_token = token.pop(0)

        if first_token == "MINE":
            if not self.mines:
                raise ValueError("MINE NOT ACTIVATED")

            if isinstance(struc, Mine):
                struc.income_rate += 1
                if struc.income_rate > obs.max_mine_size:
                    struc.income_rate = obs.max_mine_size
            else:
                obs.set_mine(player)
        elif first_token == "TOWER":
            if not self.towers:
                raise ValueError("TOWERS NOT ACTIVATED")

            if isinstance(struc, Tower):
                struc.health += Constants.TOWER_HP_INCREMENT
                if struc.health > Constants.TOWER_HP_MAXIMUM: struc.health = Constants.TOWER_HP_MAXIMUM
            else:
                obs.set_tower(player, Constants.TOWER_HP_INITIAL)

        elif first_token == "BARRACKS":
            creep_input_type = token.pop(0)
            if creep_input_type == "KNIGHT":
                creep_type = KNIGHT
            elif creep_input_type == "ARCHER":
                creep_type = ARCHER
            elif creep_input_type == "GIANT":
                creep_type = GIANT
            else:
                raise Exception(f"CreepType {creep_input_type} not found")
            obs.set_barracks(player, creep_type)
        else:
            raise ValueError(f"Invalid structure type: {first_token}")

        scheduled_buildings.append(player)

        return obstacles_attempted_to_build_upon, scheduled_buildings

    def process_player_actions(self, turn):
        obstacles_attempted_to_build_upon = []
        scheduled_buildings = []

        obstacles_attempted_to_build_upon, scheduled_buildings = self.player_loop(obstacles_attempted_to_build_upon,
                                                                                  scheduled_buildings)

        # If they're both building onto the same one, then actually build only one: depending on parity of the turn number
        if len(obstacles_attempted_to_build_upon) == 2 and obstacles_attempted_to_build_upon[0] == \
                obstacles_attempted_to_build_upon[1]:
            del scheduled_buildings[turn % 2]

    def process_creeps(self):
        all_creeps = flat_map(list(map(lambda player: player.active_creeps, self.game_manager.active_players)))
        for _ in range(5):
            for creep in all_creeps:
                creep.move(1.0 / 5)
            fix_collisions(self.all_entities(), 1)

        for creep in all_creeps:
            creep.deal_damage()

        for creep in all_creeps:
            dist_obstacle = None
            closest_obstacle = None
            for obs in self.obstacles:
                dist = obs.location.distance_to(creep.location)
                if dist_obstacle is None or dist < dist_obstacle:
                    dist_obstacle = dist
                    closest_obstacle = obs
                if closest_obstacle.location.distance_to(
                        creep.location) >= closest_obstacle.radius + creep.radius + Constants.TOUCHING_DELTA:
                    continue
                struc = closest_obstacle.structure
                if isinstance(struc, Mine) and struc.owner != creep.owner:
                    closest_obstacle.structure = None
        for creep in all_creeps:
            creep.damage(1)

        for it in self.game_manager.active_players:
            queen = it.queen_unit

            dist_obstacle = None
            closest_obstacle = None
            for obs in self.obstacles:
                dist = obs.location.distance_to(queen.location)
                if dist_obstacle is None or dist < dist_obstacle:
                    dist_obstacle = dist
                    closest_obstacle = obs
                if closest_obstacle.location.distance_to(
                        queen.location) >= closest_obstacle.radius + queen.radius + Constants.TOUCHING_DELTA:
                    continue
                struc = closest_obstacle.structure
                if (isinstance(struc, Mine) or isinstance(struc, Barracks)) and struc.owner != queen.owner:
                    closest_obstacle.structure = None

    def player_loop(self, obstacles_attempted_to_build_upon, scheduled_buildings):

        for player in self.game_manager.active_players:
            queen = player.queen_unit

            token = player.outputs[1].split(" ")

            if token.pop(0) != "TRAIN":
                raise ValueError("Expected TRAIN on the second line")

            # Process building creeps
            building_barracks: List[Obstacle] = []
            all_obstacles: List[Obstacle] = []
            for obstacle in self.obstacles:
                for obs in token:
                    obs_id = int(obs)
                    if obs_id == obstacle.obstacle_id:
                        if not isinstance(obstacle.structure, Barracks):
                            raise ValueError(f"Cannot spawn from {obstacle.obstacle_id}: not a barracks")
                        if obstacle.structure.owner != player:
                            raise ValueError(f"Cannot spawn from {obstacle.obstacle_id}: not owned")
                        if obstacle.structure.is_training:
                            raise ValueError(f"Barracks {obstacle.obstacle_id} is training")
                        building_barracks.append(obstacle)

                all_obstacles.append(obstacle)

            self.obstacles = all_obstacles
            fix_collisions(self.all_entities())

            remove_duplicates = [*set(map(lambda item: item.obstacle_id, building_barracks))]
            if len(building_barracks) > len(remove_duplicates):
                raise ValueError("Training from some barracks more than once")

            sum_costs = sum(map(lambda item: item.structure.creep_type.cost, building_barracks))
            if sum_costs > player.gold:
                print(
                    f"WARNING: Player {player.name} - Training too many creeps ({sum_costs} total gold requested and player has {player.gold})")
                continue

            for obstacle in building_barracks:
                barracks: Barracks = obstacle.structure
                barracks.progress = 0
                barracks.is_training = True

                def on_complete(ob):
                    structure = ob.structure
                    for i in range(structure.creep_type.count):
                        if structure.creep_type.asset_name == KNIGHT.asset_name:
                            it = KnightCreep(ob.structure.owner)
                        elif structure.creep_type.asset_name == ARCHER.asset_name:
                            it = ArcherCreep(ob.structure.owner)
                        elif structure.creep_type.asset_name == GIANT.asset_name:
                            it = GiantCreep(ob.structure.owner, self.obstacles)
                        else:
                            raise ValueError()

                        c = -1 if ob.structure.owner.is_second_player else 1
                        it.location = ob.location + Vector2(c * i, c * i)
                        it.location = it.location.towards(ob.structure.owner.enemy_player.queen_unit.location,
                                                          30.0)
                        ob.structure.owner.active_creeps.append(it)

                barracks.on_complete = on_complete
                obstacle.structure = barracks

            player.gold -= sum_costs

            # Process queen command
            line = player.outputs[0].strip()
            token = line.split(" ")
            command = token.pop(0)

            if command == "WAIT":
                pass
            elif command == "MOVE":
                try:
                    x = int(token.pop(0))
                    y = int(token.pop(0))
                    queen.move_towards(Vector2(x, y))
                except Exception as _:
                    raise ValueError("In MOVE command, x and y must be integers")
            elif command == "BUILD":
                try:
                    obs_id = int(token.pop(0))
                except Exception as _:
                    raise ValueError("Could not parse siteId")

                filter_obs = list(filter(lambda item: item.obstacle_id == obs_id, self.obstacles))
                if len(filter_obs) == 0 or len(filter_obs) > 1:
                    raise ValueError(f"Site id {obs_id} does not exist")

                obs = filter_obs[0]
                struc_type = token.pop(0)

                if queen.is_in_range_of(obs):
                    obstacles_attempted_to_build_upon, scheduled_buildings = self.schedule_building(player, obs,
                                                                                                    struc_type,
                                                                                                    obstacles_attempted_to_build_upon,
                                                                                                    scheduled_buildings)
                else:
                    queen.move_towards(obs.location)
            else:
                raise ValueError(f"Didn't understand command: {command}")

        return obstacles_attempted_to_build_upon, scheduled_buildings

    def game_turn(self, turn):
        self.turn = turn
        for it in self.game_manager.active_players:
            it.gold_per_turn = 0

        self.process_player_actions(turn)
        self.process_creeps()

        for it in self.obstacles:
            it.act()

        for it in self.game_manager.active_players:
            it.gold_per_turn = self.fixed_income
            it.gold += self.fixed_income

        for player in self.game_manager.active_players:
            for it in player.active_creeps:
                if it.health > 0:
                    continue
                player.active_creeps.remove(it)

        for player in self.game_manager.active_players:
            if player.is_queen_dead():
                self.end_game = True

        for it in self.all_entities():
            it.location = it.location.snap_to_integers()


def flat_map(array: List[List]):
    return reduce(list.__add__, array)


class FieldObject:
    location: Optional[Vector2]
    radius: int
    mass: int

    def __init__(self):
        self.location = None
        self.radius = 0
        self.mass = 0  # 0 := immovable


def collision_check(entities: List[FieldObject], acceptable_gap: float = 0.0) -> bool:
    for iu1, u1 in enumerate(entities):
        rad = u1.radius
        clamp_dist = Constants.OBSTACLE_GAP + rad if u1.mass == 0 else rad
        u1.location = u1.location.clamp_within(clamp_dist, Constants.WORLD_WIDTH - clamp_dist, clamp_dist,
                                               Constants.WORLD_HEIGHT - clamp_dist)

        u1.location.check_if_not_smaller_zero()
        for iu2, u2 in enumerate(entities):
            if iu1 == iu2:
                continue
            overlap = u1.radius + u2.radius + acceptable_gap - u1.location.distance_to(u2.location)
            if overlap <= 1e-6:
                continue
            else:
                if u1.mass == 0 and u2.mass == 0:
                    d1, d2 = 0.5, 0.5
                elif u1.mass == 0:
                    d1, d2 = 0.0, 1.0
                elif u2.mass == 0:
                    d1, d2 = 1.0, 0.0
                else:
                    d1, d2 = u2.mass / (u1.mass + u2.mass), u1.mass / (u1.mass + u2.mass)
                u1tou2 = u2.location - u1.location
                gap = 20.0 if u1.mass == 0 and u2.mass == 0 else 1.0
                u1.location -= u1tou2.resized_to(d1 * overlap + 0.0 if (u1.mass == 0 and u2.mass > 0) else gap)
                u2.location += u1tou2.resized_to(d2 * overlap + 0.0 if (u2.mass == 0 and u1.mass > 0) else gap)

                u1.location.check_if_not_smaller_zero()
                u2.location.check_if_not_smaller_zero()
                return True
    return False


class Obstacle(FieldObject):
    structure: Optional[Structure]
    obstacle_id: int
    max_mine_size: int
    gold: int
    params: dict
    obstacle_title_id: int
    area: int

    def __init__(self, max_mine_size: int, initial_gold: int, initial_radius: int, initial_location: Vector2,
                 obstacle_id: int):
        super().__init__()

        self.structure = None
        self.max_mine_size = max_mine_size
        self.obstacle_id = obstacle_id
        self.mass = 0
        self.radius = initial_radius
        self.location = initial_location
        self.gold = initial_gold
        self.params = {
            "id": self.obstacle_id,
            "type": "Site"
        }
        self.obstacle_tile_id = random.randint(1, 10)
        self.area = np.pi * self.radius * self.radius

    def destroy(self):
        pass

    def act(self):
        if self.structure is not None and self.structure.act():
            self.structure = None

    def set_mine(self, owner):
        self.structure = Mine(obstacle=self, owner=owner, income_rate=1)

    def set_tower(self, owner, health):
        self.structure = Tower(self, owner, 0, health)

    def set_barracks(self, owner, creep_type):
        self.structure = Barracks(self, owner=owner, creep_type=creep_type)

    def __str__(self):
        return f"{self.obstacle_id} - {self.location}"


def build_obstacles(obstacles: int) -> List[Obstacle]:
    obstacle_pairs = []
    obstacle_id = 0
    for _ in range(1, obstacles):
        gold = sample(Constants.OBSTACLE_GOLD_RANGE)
        radius = sample(Constants.OBSTACLE_RADIUS_RANGE)
        l1 = Vector2(random.randint(0, Constants.WORLD_WIDTH), random.randint(0, Constants.WORLD_HEIGHT))
        l2 = Vector2(Constants.WORLD_WIDTH, Constants.WORLD_HEIGHT) - l1
        gold_max_mine_size = sample(Constants.OBSTACLE_MINE_BASE_SIZE_RANGE)

        obstacle_id += 1
        o1 = Obstacle(max_mine_size=gold_max_mine_size, initial_gold=gold, initial_radius=radius, initial_location=l1,
                      obstacle_id=obstacle_id)

        obstacle_id += 1
        o2 = Obstacle(max_mine_size=gold_max_mine_size, initial_gold=gold, initial_radius=radius, initial_location=l2,
                      obstacle_id=obstacle_id)

        obstacle_pairs.append([o1, o2])

    obs = flat_map(obstacle_pairs)

    for i in range(1, 100 + 1):
        for pair in obstacle_pairs:
            o1, o2 = pair
            mid = (o1.location + Vector2(Constants.WORLD_WIDTH - o2.location.x,
                                         Constants.WORLD_HEIGHT - o2.location.y)) / 2.0
            o1.location = mid
            o2.location = Vector2(Constants.WORLD_WIDTH - mid.x, Constants.WORLD_HEIGHT - mid.y)

        collision_check(obs, float(Constants.OBSTACLE_GAP))
    return obs


def sample(list_like):
    return random.choice(list_like)


def build_map(obstacles_count: int) -> List[Obstacle]:
    obstacles = None
    while obstacles is None:
        obstacles = build_obstacles(obstacles=obstacles_count)

    map_center = Vector2(len(Constants.viewportX) / 2, len(Constants.viewportY) / 2)
    for o in obstacles:
        o.location = o.location.snap_to_integers()
        if o.location.distance_to(map_center) < Constants.OBSTACLE_GOLD_INCREASE_DISTANCE_1:
            o.max_mine_size += 1
            o.gold += Constants.OBSTACLE_GOLD_INCREASE
        if o.location.distance_to(map_center) < Constants.OBSTACLE_GOLD_INCREASE_DISTANCE_2:
            o.max_mine_size += 1
            o.gold += Constants.OBSTACLE_GOLD_INCREASE
    return obstacles


def fix_collisions(entities: List[FieldObject], max_iterations: int = 999):
    for _ in range(max_iterations):
        if not collision_check(entities):
            return


class Structure:
    owner: Player
    obstacle: Obstacle

    def __init__(self, owner, obstacle):
        self.owner = owner
        self.obstacle = obstacle

    def on_complete(self, ob=None):
        raise ValueError("Not Implemented")

    def act(self):
        raise ValueError("Not Implemented")

    def __str__(self):
        return f"{self.owner} - {self.obstacle}"


class Mine(Structure):
    income_rate: int

    def __init__(self, obstacle, owner, income_rate):
        super().__init__(owner, obstacle)
        self.income_rate = income_rate

    def act(self):
        cash = min(self.income_rate, self.obstacle.gold)
        self.owner.gold_per_turn += cash
        self.owner.gold += cash
        self.obstacle.gold -= cash
        if self.obstacle.gold <= 0:
            return True
        return False


class Tower(Structure):
    attack_radius: int
    health: int
    attack_range: Creep

    def __init__(self, obstacle, owner, attack_radius, health):
        super().__init__(owner, obstacle)
        self.attack_target = None
        self.attack_radius = attack_radius
        self.health = health

    def damage_creep(self, target):
        self._damage(target, Constants.TOWER_CREEP_DAMAGE_MIN, Constants.TOWER_CREEP_DAMAGE_CLIMB_DISTANCE)

    def damage_queen(self, target):
        self._damage(target, Constants.TOWER_QUEEN_DAMAGE_MIN, Constants.TOWER_QUEEN_DAMAGE_CLIMB_DISTANCE)

    def _damage(self, target, param1, param2):
        shot_distance = target.location.distance_to(self.obstacle.location) - self.obstacle.radius
        difference_from_max = self.attack_radius - shot_distance
        damage = param1 + int(difference_from_max / param2)
        target.damage(damage)

    def act(self):
        closest_enemy = None
        closest_enemy_dist = None
        for creep in self.owner.enemy_player.active_creeps:
            dist = self.obstacle.location.distance_to(creep.location)
            if closest_enemy_dist is None or dist < closest_enemy_dist:
                closest_enemy_dist = dist
                closest_enemy = creep

        enemy_queen = self.owner.enemy_player.queen_unit
        if closest_enemy is not None and closest_enemy.location.distance_to(
                self.obstacle.location) < self.attack_radius:
            self.damage_creep(closest_enemy)
        elif enemy_queen.location.distance_to(self.obstacle.location) < self.attack_radius:
            self.damage_queen(enemy_queen)
        # self.health = min(0, self.health - Constants.TOWER_MELT_RATE)
        self.health -= Constants.TOWER_MELT_RATE
        self.attack_radius = int(np.sqrt((self.health * Constants.TOWER_COVERAGE_PER_HP + self.obstacle.area) / np.pi))
        if self.health <= 0:
            return True
        return False


class Barracks(Structure):
    is_training: bool
    progress_max: int
    progress: int
    creep_type: CreepType

    def __init__(self, obstacle: Obstacle, owner: Player, creep_type: CreepType):
        super().__init__(owner, obstacle)
        self.obstacle = obstacle
        self.owner = owner
        self.creep_type = creep_type
        self.progress_max = creep_type.build_time
        self.progress = 0
        self.is_training = False

    def act(self):
        if self.is_training:
            self.progress += 1
            if self.progress == self.progress_max:
                self.progress = 0
                self.is_training = False
                self.on_complete(self.obstacle)  # create a creep ?
        return False


class Unit(FieldObject):
    unit_type: int
    owner: Player
    health: int

    def __init__(self, owner, unit_type):
        super().__init__()
        self.unit_type = unit_type
        self.owner = owner
        self.location = Vector2()
        self.health = 0

    @abstractmethod
    def damage(self, damage_amount):
        pass


class Queen(Unit):

    def __init__(self, owner):
        super().__init__(owner, -1)
        self.mass = Constants.QUEEN_MASS
        self.radius = Constants.QUEEN_RADIUS

    def move_towards(self, target: Vector2):
        self.location = self.location.towards(target, Constants.QUEEN_SPEED)

    def damage(self, damage_amount):
        if damage_amount <= 0:
            return
        self.owner.health = max(0, self.owner.health - damage_amount)

    def is_in_range_of(self, obs: Obstacle) -> bool:
        dist = obs.location.distance_to(self.location)
        return dist < self.radius + obs.radius + Constants.TOUCHING_DELTA


class Creep(Unit):
    speed: int
    attack_range: int
    last_location: Optional[Vector2]
    attacks_this_turn: bool

    def __init__(self, owner, creep_type):
        super().__init__(owner, creep_type.ordinal)
        self.speed = creep_type.speed
        self.attack_range = creep_type.attack_range
        self.mass = creep_type.mass
        self.maxHealth = creep_type.hp
        self.radius = creep_type.radius
        self.health = creep_type.hp
        self.last_location = None
        self.attacks_this_turn = False

    def damage(self, damage_amount):
        if damage_amount <= 0:
            return
        self.health -= damage_amount

    @abstractmethod
    def deal_damage(self):
        pass

    @abstractmethod
    def move(self, frames):
        pass


class GiantCreep(Creep):
    obstacles: List[Obstacle]

    def __init__(self, owner, obstacles=None):
        super().__init__(owner, GIANT)
        if obstacles is None:
            obstacles = []
        self.obstacles = obstacles

    def __str__(self):
        return f"GiantCreep - {self.location}"

    def move(self, frames):
        opp_structures = []
        for struct in self.obstacles:
            if struct.structure is None:
                continue
            if not isinstance(struct.structure, Tower):
                continue
            if struct.structure.owner != self.owner.enemy_player:
                continue
            opp_structures.append(struct)

        if len(opp_structures) == 0:
            return

        target = min(opp_structures, key=lambda st: st.location.distance_to(self.location)).location
        self.location = self.location.towards(target, self.speed * frames)

    def deal_damage(self):
        target = None
        for obs in self.obstacles:
            if obs.structure is None or obs.structure.owner != self.owner.enemy_player or not isinstance(obs.structure,
                                                                                                         Tower):
                continue
            dist = obs.location.distance_to(self.location)
            if dist >= self.radius + obs.radius + Constants.TOUCHING_DELTA:
                continue
            target = obs
            break
        if target is None:
            return

        target.structure.health = min(0, target.structure.health - Constants.GIANT_BUST_RATE)


class KnightCreep(Creep):

    def __init__(self, owner):
        super().__init__(owner, KNIGHT)
        self.owner = owner

    def __str__(self):
        return f"KnightCreep - {self.location}"

    def deal_damage(self):
        self.attacks_this_turn = False
        enemy_queen = self.owner.enemy_player.queen_unit
        if self.location.distance_to(
                enemy_queen.location) < self.radius + enemy_queen.radius + self.attack_range + Constants.TOUCHING_DELTA:
            self.attacks_this_turn = True
            self.owner.enemy_player.health -= Constants.KNIGHT_DAMAGE

    def move(self, frames: float):
        enemy_queen = self.owner.enemy_player.queen_unit
        # move toward enemy queen, if not yet in range
        if self.location.distance_to(enemy_queen.location) > self.radius + enemy_queen.radius + self.attack_range:
            self.location = self.location.towards(
                (enemy_queen.location + (self.location - enemy_queen.location).resized_to(3.0)),
                self.speed * frames)


class ArcherCreep(Creep):

    def __init__(self, owner):
        super().__init__(owner, ARCHER)
        self.owner = owner
        self.lastLocation = None
        self.attacks_this_turn = False
        self.attack_target = None

    def __str__(self):
        return f"ArcherCreep - {self.location}"

    def deal_damage(self):
        target = self.find_target()
        if target is None:
            return

        if self.location.distance_to(
                target.location) < self.radius + target.radius + self.attack_range + Constants.TOUCHING_DELTA:
            dmg = Constants.ARCHER_DAMAGE_TO_GIANTS if isinstance(target, GiantCreep) else Constants.ARCHER_DAMAGE
            target.damage(dmg)
            self.attack_target = target

    def move(self, frames: float):
        target = self.find_target()
        if target is None:
            return

        if self.location.distance_to(target.location) > self.radius + target.radius + self.attack_range:
            self.location = self.location.towards((target.location + (self.location - target.location).resized_to(3.0)),
                                                  self.speed * frames)

    def find_target(self) -> Creep:
        min_dist = None
        target = None
        for creep in self.owner.enemy_player.active_creeps:
            dist = creep.location.distance_to(self.location)
            if min_dist is None or dist < min_dist:
                min_dist = dist
                target = creep
        return target


class Player:
    # activeCreeps: List[Creep]
    # queen_unit: Optional[Queen]

    is_second_player: bool
    queen_unit: Optional[Queen]
    enemy_player: Optional[Player]
    active_creeps: List
    name: str
    outputs: List
    score: int
    gold: int
    health: int
    gold_per_turn: int

    def __init__(self, name):
        self.is_second_player = False
        self.queen_unit = None
        self.enemy_player = None
        self.active_creeps = []
        self.name = name
        self.outputs = [
            "",
            "",
        ]

        self.health = -1
        self.score = -2
        self.gold = Constants.STARTING_GOLD
        self.gold_per_turn = 0

    def print_obstacle_per_turn(self, obstacle: Obstacle):
        struc = obstacle.structure
        visible = (struc is not None and struc.owner.name == self.name) or obstacle.location.distance_to(
            self.queen_unit.location) < Constants.QUEEN_VISION

        if struc is None:
            struc_info = {
                "type": -1
            }
        elif isinstance(struc, Mine):
            struc_info = {
                "type": 0,
                "type_name": "Mine",
                "owner": self.fix_owner(struc.owner),
                "income_rate": struc.income_rate if visible else -1  # param1
            }
        elif isinstance(struc, Tower):
            struc_info = {
                "type": 1,
                "type_name": "Tower",
                "owner": self.fix_owner(struc.owner),
                "health": struc.health,
                "attack_radius": struc.attack_radius
            }
        elif isinstance(struc, Barracks):
            struc_info = {
                "type": 2,
                "type_name": "Tower",
                "owner": self.fix_owner(struc.owner),
                "until_next_train": 0 if not struc.is_training else struc.progress_max - struc.progress,
                "creep_type": struc.creep_type.ordinal
            }
        else:
            raise ValueError("")

        return {**struc_info, **{
            "id": obstacle.obstacle_id,
            "gold": obstacle.gold if visible else -1,
            "x": obstacle.location.x,
            "y": obstacle.location.y,
            "radius": obstacle.radius,
            "max_mine_size": obstacle.max_mine_size if visible else -1,
        }}

    def all_units(self):
        ent = []
        ent.extend(self.active_creeps)
        ent.append(self.queen_unit)
        return ent

    def is_queen_dead(self):
        self.queen_unit.health = self.health  # << really ?? double bookkeeping here.
        if self.health <= 0:
            return True
        return False

    def kill(self, reason):
        self.score = -1
        raise Exception(reason)

    def fix_owner(self, player: Player) -> int:
        if player is None:
            return -1
        if player.name == self.name:
            return 0
        return 1


cdef class Vector2:
    cdef public float x
    cdef public float y

    def __init__(self, x: float = 0, y: float = 0):
        self.x = x
        self.y = y

    cpdef Vector2 snap_to_integers(self):
        return Vector2(round(self.x), round(self.y))

    cpdef float distance_to(self, Vector2 other):
        return np.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)

    cpdef void check_if_not_smaller_zero(self):
        if self.x < 0:
            self.x = 0
        if self.y < 0:
            self.y = 0

    cdef Vector2 copy(self):
        return Vector2(self.x, self.y)

    def __add__(self, other: Vector2) -> Vector2:
        return Vector2(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Vector2) -> Vector2:
        return Vector2(self.x - other.x, self.y - other.y)

    def __truediv__(self, value: float):
        x = self.x / value
        y = self.y / value
        return Vector2(x, y)

    def __mul__(self, scalar: float):
        return Vector2(self.x * scalar, self.y * scalar)

    def __str__(self):
        return f"({self.x}, {self.y})"

    def __repr__(self):
        return f"({self.x}, {self.y})"

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    cpdef Vector2 clamp_within(self, float min_x, float max_x, float min_y, float max_y):
        nx: float = -1
        ny: float = -1
        if self.x < min_x:
            nx = min_x
        elif self.x > max_x:
            nx = max_x
        else:
            nx = self.x

        if self.y < min_y:
            ny = min_y
        elif self.y > max_y:
            ny = max_y
        else:
            ny = self.y

        return Vector2(nx, ny)

    cdef float length_squared(self):
        return self.x * self.x + self.y * self.y

    cpdef Vector2 resized_to(self, new_length):
        return self.normalized() * new_length

    cdef Vector2 normalized(self):
        length: float = math.sqrt(self.length_squared())
        if length < 1e-6:
            return Vector2(1, 0)
        return Vector2(self.x / length, self.y / length)

    cpdef Vector2 towards(self, Vector2 other, float max_distance):
        if self.distance_to(other) < max_distance:
            return other
        else:
            new_loc = self + (other - self).resized_to(max_distance)
            return new_loc


class Constants:
    STARTING_GOLD = 100

    WORLD_WIDTH = 1920
    WORLD_HEIGHT = 1000

    viewportX = list(range(0, WORLD_WIDTH + 1))  # np.arange(0, WORLD_WIDTH + 1)
    viewportY = list(range(0, WORLD_HEIGHT + 1))  # np.arange(0, WORLD_HEIGHT + 1)

    QUEEN_SPEED = 60
    TOWER_HP_INITIAL = 200
    TOWER_HP_INCREMENT = 100
    TOWER_HP_MAXIMUM = 800
    TOWER_CREEP_DAMAGE_MIN = 3
    TOWER_CREEP_DAMAGE_CLIMB_DISTANCE = 200
    TOWER_QUEEN_DAMAGE_MIN = 1
    TOWER_QUEEN_DAMAGE_CLIMB_DISTANCE = 200
    TOWER_MELT_RATE = 4
    TOWER_COVERAGE_PER_HP = 1000

    GIANT_BUST_RATE = 80

    OBSTACLE_GAP = 90
    OBSTACLE_RADIUS_RANGE = list(range(60, 90 + 1))  # np.arange(60, 90 + 1)  # 60..90
    OBSTACLE_GOLD_RANGE = list(range(200, 250 + 1))  # np.arange(200, 250 + 1)  # 200..250
    OBSTACLE_MINE_BASE_SIZE_RANGE = list(range(1, 3 + 1))  # np.arange(1, 3 + 1)  # 1..3
    OBSTACLE_GOLD_INCREASE = 50
    OBSTACLE_GOLD_INCREASE_DISTANCE_1 = 500
    OBSTACLE_GOLD_INCREASE_DISTANCE_2 = 200
    OBSTACLE_PAIRS = list(range(6, 12 + 1))  # np.arange(6, 12 + 1)  # 6..12

    KNIGHT_DAMAGE = 1
    ARCHER_DAMAGE = 2
    ARCHER_DAMAGE_TO_GIANTS = 10

    QUEEN_RADIUS = 30
    QUEEN_MASS = 10000
    QUEEN_HP = list(range(5, 20 + 1))  # np.arange(5, 20 + 1)  # 5..20
    QUEEN_HP_MULT = 5  # i.e. 25. .100 by 5
    QUEEN_VISION = 300

    TOUCHING_DELTA = 5
    WOOD_FIXED_INCOME = 10


class CreepType:
    ordinal: int
    count: int
    cost: int
    speed: int
    range: int
    attack_range: int
    radius: int
    mass: int
    hp: int
    build_time: int
    asset_name: str

    def __init__(self, count, cost, speed, range_, radius, mass, hp, build_time, asset_name, ordinal=-1):
        self.ordinal = ordinal
        self.count = count
        self.cost = cost
        self.speed = speed

        self.range = range_
        self.attack_range = range_

        self.radius = radius
        self.mass = mass
        self.hp = hp
        self.build_time = build_time
        self.asset_name = asset_name


KNIGHT = CreepType(count=4, cost=80, speed=100, range_=0, radius=20, mass=400, hp=30, build_time=5,
                   asset_name="Unite_Fantassin", ordinal=0)
ARCHER = CreepType(count=2, cost=100, speed=75, range_=200, radius=25, mass=900, hp=45, build_time=8,
                   asset_name="Unite_Archer", ordinal=1)
GIANT = CreepType(count=1, cost=140, speed=50, range_=0, radius=40, mass=2000, hp=200, build_time=10,
                  asset_name="Unite_Siege", ordinal=2)
