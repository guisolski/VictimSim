# EXPLORER AGENT
# @Author: Tacla, UTFPR
# It walks randomly in the environment looking for victims.

import sys
import os
import random
import time
from abstract_agent import AbstractAgent
from physical_agent import PhysAgent
from abc import ABC, abstractmethod
import networkx as nx
from local_search import LocalSearch
from victim import Victim

class Explorer(AbstractAgent):
    def __init__(self, env, config_file, resc):
        """ Construtor do agente random on-line
        @param env referencia o ambiente
        @config_file: the absolute path to the explorer's config file
        @param resc referencia o rescuer para poder acorda-lo
        """

        super().__init__(env, config_file)

        # Specific initialization for the rescuer
        self.resc = resc           # reference to the rescuer agent
        self.rtime = self.TLIM     # remaining time to explore
        self.map = nx.Graph()
        self.position = (0, 0)
        self.actions = {
            "S":   [0, 1],
            "N":   [0, -1],
            "W":   [-1, 0],
            "E":   [1, 0],
            "SE":  [1, 1],
            "NE":  [1, -1],
            "NW":  [-1, -1],
            "SW":  [-1, 1]
        }
        self.path = []
        self.positions = []
        self.victims = {}
        self.victims_pos = []
        self.returnBase = []
        self.old = ()
        self.stop = False

    def returnInfos(self):
        return {
            "map": self.map,
            "victims": self.victims
        }

    def absPosition(self):
        key = str([sum(col) for col in zip(*self.path)]
                  ).replace("[", "(").replace("]", ")")

        return str((0, 0)) if key == "()" else key

    def createNode(self):
        key = self.absPosition()
        if key not in self.positions:
            self.map.add_node(key)

            attrs = {
                key: {
                    "untried": ["NW", "SW", "SE", "E", "W", "NE", "N", "S"],
                    "path": str(self.path)
                }
            }
            nx.set_node_attributes(self.map, attrs)

            self.positions.append(key)

        if len(self.positions) > 1:
            # old = str(self.positions[self.positions.index(key)-1])
            self.map.add_edge(key, self.old)

            tKey = self.stringToTuple(key)

            if self.old[0] != tKey[0] and self.old[1] != tKey[1]:
                self.map.edges[key, self.old]['cost'] = 1.5
            else:
                self.map.edges[key, self.old]['cost'] = 1
            self.returnBaseF()

        self.old = key

    def returnBaseF(self):
        if self.rtime < 50.0:
            path = nx.astar_path(self.map, "(0, 0)", str(self.absPosition()),
                                 heuristic=self.dist, weight="cost")
            cost = nx.path_weight(self.map, path, "cost")
            if cost*1.2 >= self.rtime:
                self.returnBase = path

    def stringToTuple(self, s):
        return tuple([int(i.replace("(", "").replace(")", "")) for i in s.split(",")])

    def action(self):
        key = self.absPosition()
        try:
            untried = self.map.nodes[key]["untried"].pop()
            return self.actions[untried]
        except:
            i = self.positions.index(key)-1
            return self.positions[i]

    def dist(self, a, b):
        (x1, y1) = self.stringToTuple(a)

        (x2, y2) = self.stringToTuple(b)

        return ((x1 - x2) ** 2 + (y1 - y2) ** 2)

    def walk(self, dx, dy):
        # Moves the body to another position
        result = self.body.walk(dx, dy)

        # Update remaining time
        if dx != 0 and dy != 0:
            self.rtime -= self.COST_DIAG
        else:
            self.rtime -= self.COST_LINE
        return result

    def calcNextMove(self, m):
        x, y = self.stringToTuple(self.absPosition())
        return m[0]-x, m[1]-y

    def end(self):
        print(f"{self.NAME} I believe I've remaining time of {self.rtime:.1f}")
        nx.write_gml(self.map, "map.gml")
        print("Victims: ", self.victims)

        local_search = LocalSearch(self.map, self.victims,self.victims_pos)
        best_path = local_search.deliberate()
        self.resc.go_save_victims(best_path)

        return False

    def deliberate(self) -> bool:
        """ The agent chooses the next action. The simulator calls this
        method at each cycle. Must be implemented in every agent"""
        if self.rtime == 0 or self.stop:
            # time to wake up the rescuer
            # pass the walls and the victims (here, they're empty)
            return self.end()

        # No more actions, time almost ended
        if len(self.returnBase) > 0:
            dx, dy = self.calcNextMove(
                self.stringToTuple(self.returnBase.pop()))
            self.walk(dx, dy)
            self.position = (dx, dy)
            self.path.append(self.position)
            if len(self.returnBase) == 0:
                return self.end()
            return True

        self.createNode()

        dx, dy = self.action()

        result = self.walk(dx, dy)

        # Test the result of the walk action
        if result == PhysAgent.BUMPED:
            walls = 1  # build the map- to do
            # print(self.name() + ": wall or grid limit reached")

        if result == PhysAgent.EXECUTED:
            self.position = (dx, dy)
            self.path.append(self.position)
            # check for victim returns -1 if there is no victim or the sequential
            # the sequential number of a found victim
            seq = self.body.check_for_victim()
            key = self.absPosition()
            if seq >= 0:
                vs = self.body.read_vital_signals(seq)
                self.rtime -= self.COST_READ
                if key not in self.victims:
                    self.victims_pos.append(key)
                    self.victims[key] = vs
                # print("exp: read vital signals of " + str(seq))
                # print(vs)

        return True
