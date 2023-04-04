from random import randint
import math
import numpy as np
import networkx as nx


class LocalSearch:
    def __init__(self, map, victims, victims_pos) -> None:
        self.timer = 10000  # number of time we the fit fuc it call
        self.fit_time = 0
        self.fit_max =  100
        self.map = map
        self.victims = victims
        self.victims_pos = victims_pos
        self.path = []
        self.score = 0
        level = [0,0,0,0]
        for _, value in victims.items():
            # [index 7] 1=CRÍTICO 2=INSTÁVEL 3=POTENCIALMENTE ESTÁVEL 4=ESTÁVEL
            pos =int(value[7])-1
            if level[pos] == 0:
                level[pos] = 1
            else:
                level[pos] += level[pos]
        self.best = sum(level)
        self.len_visited = []
    def vsg(self,victims):
        level = [0,0,0,0]
        for i in victims:
            pos =int(self.victims[i][7])-1
            if level[pos] == 0:
                level[pos] = 1
            level[pos] += level[pos]
        return sum(level)/self.best

    def fit(self, cost, victims):
        self.fit_time += 1
        if cost > 100.0:
            return 0

        return  self.vsg(victims)

    def create_neighbors(self, neighbors_size, pool):
        neighbors = []
        for i in range(neighbors_size):
            neighbors.append(np.random.permutation(pool))
        return neighbors

    def stringToTuple(self, s):
        return tuple([int(i.replace('(', '').replace(')', '')) for i in s.split(',')])

    def dist(self, a, b):
        (x1, y1) = self.stringToTuple(a)

        (x2, y2) = self.stringToTuple(b)

        return ((x1 - x2) ** 2 + (y1 - y2) ** 2)

    def create_path(self, n):
        cost = 0
        path = nx.astar_path(self.map, '(0, 0)', str(n[0]),
                             heuristic=self.dist, weight='cost')
        cost += nx.path_weight(self.map, path, 'cost')
        for i in range(len(n)):
            if i+1 < len(n):
                p = nx.astar_path(self.map,  str(n[i]), str(n[i+1]),
                                  heuristic=self.dist, weight='cost')
                cost += nx.path_weight(self.map, p, 'cost')
                path = path + p

        p = nx.astar_path(self.map,  str(n[len(n)-1]), '(0, 0)',
                          heuristic=self.dist, weight='cost')
        cost += nx.path_weight(self.map, p, 'cost')
        path = path + p
        return path, cost

    def generated_size(self):
        length = len(self.victims_pos)
        run = True
        while run:
            t = randint(math.ceil(length*0.4), length-1)
            if t not in self.len_visited:
                self.len_visited.append(t)
                run = False
        return t

    def deliberate(self):


        while self.fit_time < self.fit_max:
            # number of victims whe choose to try save
            pool_size = self.generated_size()

            # victims
            pool = np.array(self.victims_pos[0:pool_size])


            fat = math.factorial(len(pool))

            n_neighbors = randint(math.ceil(fat*0.4), math.ceil(fat*0.7))
            neighbors = self.create_neighbors(n_neighbors, pool)

            for i in neighbors:
                path, cost = self.create_path(i)
                fit = self.fit(cost, i)
                if fit > self.score:
                    self.score = fit
                    self.path = path
                if self.fit_time >= self.fit_max:
                    break
        print('path: ',path)
        return self.path
