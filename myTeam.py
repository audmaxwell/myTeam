# myTeam.py
# ---------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
#
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from captureAgents import CaptureAgent
import random, time, util
from game import Directions
import game

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'DefensiveAgent', second = 'DefensiveAgent'):
  """
  This function should return a list of two agents that will form the
  team, initialized using firstIndex and secondIndex as their agent
  index numbers.  isRed is True if the red team is being created, and
  will be False if the blue team is being created.

  As a potentially helpful development aid, this function can take
  additional string-valued keyword arguments ("first" and "second" are
  such arguments in the case of this function), which will come from
  the --redOpts and --blueOpts command-line arguments to capture.py.
  For the nightly contest, however, your team will be created without
  any extra arguments, so you should make sure that the default
  behavior is what you want for the nightly contest.
  """

  # The following line is an example only; feel free to change it.
  return [eval(first)(firstIndex), eval(second)(secondIndex)]

##########
# Agents #
##########


class DefensiveAgent(CaptureAgent):
    def registerInitialState(self, gameState):
        CaptureAgent.registerInitialState(self, gameState)
        self.visited = []
       # if self.isRed:
        self.enemystates = gameState.getBlueTeamIndices()
        self.food = gameState.getBlueFood().asList()
        for index in gameState.getRedTeamIndices():
            if index != self.index:
                self.friend = index
       # else:
        #    self.enemystates = gameState.getRedTeamIndices()
         #   self.food = gameState.getRedFood().asList()
          #  for index in gameState.getBlueTeamIndices():
           #     if index != self.index:
            #        self.friend = index
    def runAway(self, state):
        score = 0
        for agent in self.enemystates:
            if state.getAgentState(agent).scaredTimer == 0 and not state.getAgentState(agent).isPacman:
                dist = self.getMazeDistance(state.getAgentPosition(self.index), state.getAgentPosition(agent))
                score += dist * 1000000
                if dist <= 3:
                    score -= dist * 1000
        return score


    def pacmanMoves(self, successor):
        score = 0
        score -= len(self.food)
        for food in self.food:
            dist = self.getMazeDistance(successor.getAgentPosition(self.index), food)
            score -= dist
            if dist <= 5:
                score += 10000
            if dist <= 2:
                score += 100000

        if successor.getAgentPosition(self.index) in self.food:
            score += 10000000000
        score += self.getMazeDistance(successor.getAgentPosition(self.index), successor.getAgentPosition(self.friend)) * 10
        for agent in self.enemystates:
            if successor.getAgentState(agent).scaredTimer == 0:
                dist = self.getMazeDistance(successor.getAgentPosition(self.index), successor.getAgentPosition(agent))
                if dist <= 5:
                    score = self.runAway(successor)
                if dist <= 2:
                    score = self.runAway(successor) - 10000
        if len(self.visited) > 2:
            if successor.getAgentPosition(self.index) == self.visited[-2]:
                score -= 100000000000
            if successor.getAgentPosition(self.index) == self.visited[-3]:
                score -= 10000000
        return score

    def ghostTime(self, successor):
        score = 0
        if len(self.visited) > 2:
            if successor.getAgentPosition(self.index) == self.visited[-2]:
                score -= 10000
            if successor.getAgentPosition(self.index) == successor.getInitialAgentPosition(self.index):
                score -= 10000
        for agent in self.enemystates:
            if successor.getAgentState(agent).isPacman:
                dist = self.getMazeDistance(successor.getAgentPosition(self.index), successor.getAgentPosition(agent))
                score -= dist
        score += self.getMazeDistance(successor.getAgentPosition(self.index),
                                      successor.getAgentPosition(self.friend)) * 10
        return score

    def goHome(self, successor):
        score = 0
        dist = self.getMazeDistance(successor.getInitialAgentPosition(self.index), successor.getAgentPosition(self.index))
        score -= dist * 100
        return score
    def chooseAction(self, gameState):
        actions = gameState.getLegalActions(self.index)
        bestscore = float("-inf")
        bestaction = None
        enemyPacman = False
        bestsuccessor = None
        for agent in gameState.getBlueTeamIndices():
            if gameState.getAgentState(agent).isPacman:
                enemyPacman = True

        if enemyPacman:
            for action in actions:
                successor = gameState.generateSuccessor(self.index, action)
                if self.ghostTime(successor) > bestscore:
                    bestscore = self.ghostTime(successor)
                    bestaction = action
                    bestsuccessor = successor

        elif gameState.getAgentState(self.index).numCarrying >= 3:
            for action in actions:
                successor = gameState.generateSuccessor(self.index, action)
                if self.goHome(successor) > bestscore:
                    bestscore = self.goHome(successor)
                    bestaction = action
                    bestsuccessor = successor


        else:
            if 'Stop' in actions:
                actions.remove('Stop')
            for action in actions:
                successor = gameState.generateSuccessor(self.index, action)
                if self.pacmanMoves(successor) > bestscore:
                    bestscore = self.pacmanMoves(successor)
                    bestaction = action
                    bestsuccessor = successor

        self.visited.append(bestsuccessor.getAgentPosition(self.index))
        return bestaction
