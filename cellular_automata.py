import random
import copy


class CellularAutomata:
    def __init__(self, chance_to_come_alive=0.45, birth_limit=2, death_limit=3, width=2, height=2):
        self.chance_to_come_alive = chance_to_come_alive
        self.birth_limit = birth_limit
        self.death_limit = death_limit
        self.map_width = width
        self.map_height = height

        self.map = []

    def initialize_map(self):
        for x in range(self.map_width):
            row = []
            for y in range(self.map_height):
                if random.random() < self.chance_to_come_alive:
                    row.append(True)
                else:
                    row.append(False)
            self.map.append(row)

        return self.map

    def do_simulation_step(self, old_map):
        new_map = copy.copy(old_map)
        for x in range(self.map_width):
            for y in range(self.map_height):
                neighbor_count = self.count_alive_neighbors(old_map, x, y)

                # check conditions for live cell to die
                if old_map[x][y]:
                    if neighbor_count < self.death_limit:
                        new_map[x][y] = False
                    else:
                        new_map[x][y] = True
                # check conditions to revive dead cell
                else:
                    if neighbor_count > self.birth_limit:
                        new_map[x][y] = True
                    else:
                        new_map[x][y] = False
        self.map = new_map
        return self.map

    def count_alive_neighbors(self, old_map, x, y):
        count = 0
        i = -1
        j = -1
        for i in range(2):
            for j in range(2):
                neighbor_x = x + i
                neighbor_y = y + j

                # looking at ourselves
                if i == 0 and j == 0:
                    continue
                elif neighbor_x < 0 or neighbor_y < 0 or neighbor_x >= self.map_width or neighbor_y >= self.map_height:
                    count += 1
                elif old_map[neighbor_x][neighbor_y]:
                    count += 1
        return count

    def generate_dungeon(self, number_of_steps):
        self.initialize_map()
        for i in range(number_of_steps):
            self.map = self.do_simulation_step(self.map)


def main():
    test = CellularAutomata()
    test.generate_dungeon(1)
    for row in test.map:
        print(row)


if __name__ == '__main__':
    main()
