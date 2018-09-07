class Coordinate(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Pathfinding(object):
    walkablePositions = []
    nodeParents = {}

    def __init__(self, nodes):
        self.walkableNodes = nodes

    def getShortestPath(self, start, goal):
        path = self.determineShortestPath(start, goal)
        if path == start or self.nodeParents[goal] not in self.nodeParents:
            return None

        path = []
        curr = goal
        while curr != start:
            path.append(curr)
            curr = self.nodeParents[curr]

        return path

    def determineShortestPath(self, start, goal):
        stack = []
        exploredNodes = []
        stack.append(start)

        while len(stack) != 0:
            currentNode = stack.pop()
            if currentNode == goal:
                return currentNode

            nodes = self.getWalkableNodes(currentNode)

            for node in nodes:
                if not node in exploredNodes:
                    exploredNodes.append(node)
                    self.nodeParents[node] = currentNode
                    stack.append(node)

        return start

    def getWalkableNodes(self, curr):
        walkableNodes = []

        possibleNodes = [
            Coordinate(curr.x + 1, curr.y),
            Coordinate(curr.x - 1, curr.y),
            Coordinate(curr.x, curr.y + 1),
            Coordinate(curr.x, curr.y - 1),
            Coordinate(curr.x + 1, curr.y + 1),
            Coordinate(curr.x - 1, curr.y - 1),
            Coordinate(curr.x - 1, curr.y + 1),
            Coordinate(curr.x + 1, curr.y - 1)
        ]

        for node in possibleNodes:
            if self.canMove(node):
                walkableNodes.append(node)

        return walkableNodes

    def canMove(self, next):
        return next in self.walkablePositions
