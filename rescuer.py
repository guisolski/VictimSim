# RESCUER AGENT
# @Author: Tacla (UTFPR)
# Demo of use of VictimSim

import os
import random
from abstract_agent import AbstractAgent
from physical_agent import PhysAgent
from abc import ABC, abstractmethod


# Classe que define o Agente Rescuer com um plano fixo
class Rescuer(AbstractAgent):
    def __init__(self, env, config_file):
        """ 
        @param env: a reference to an instance of the environment class
        @param config_file: the absolute path to the agent's config file"""

        super().__init__(env, config_file)

        # Specific initialization for the rescuer
        self.plan = []              # a list of planned actions
        self.rtime = self.TLIM      # for controlling the remaining time

        # Starts in IDLE state.
        # It changes to ACTIVE when the map arrives
        self.body.set_state(PhysAgent.IDLE)
        self.path = []

    def go_save_victims(self, path):
        """ The explorer sends the map containing the walls and
        victims' location. The rescuer becomes ACTIVE. From now,
        the deliberate method is called by the environment"""
        self.body.set_state(PhysAgent.ACTIVE)
        self.plan = path
      
    def absPosition(self):
        key = str([sum(col) for col in zip(*self.path)]
                  ).replace("[", "(").replace("]", ")")

        return str((0, 0)) if key == "()" else key

    def calcNextMove(self, m):
        x, y = self.stringToTuple(self.absPosition())
        return m[0]-x, m[1]-y
    
    def stringToTuple(self, s):
        return tuple([int(i.replace("(", "").replace(")", "")) for i in s.split(",")])
   
        
    def deliberate(self) -> bool:
        """ This is the choice of the next action. The simulator calls this
        method at each reasonning cycle if the agent is ACTIVE.
        Must be implemented in every agent
        @return True: there's one or more actions to do
        @return False: there's no more action to do """

        # No more actions to do
        if self.plan == []:  # empty list, no more actions to do
            return False
   
        # Takes the first action of the plan (walk action) and removes it from the plan
        dx, dy = self.calcNextMove(
                self.stringToTuple(self.plan.pop(0)))
        self.path.append((dx, dy))
        # Walk - just one step per deliberation
        result = self.body.walk(dx, dy)

        # Rescue the victim at the current position
        if result == PhysAgent.EXECUTED:
            # check if there is a victim at the current position
            seq = self.body.check_for_victim()
            if seq >= 0:
                res = self.body.first_aid(seq)  # True when rescued

        return True
