import sys
assert sys.version_info >= (3, 5)

import itertools, functools, heapq, collections

def memoize(fn, slot = None, maxSize = 128):
    if slot:
        def memoized_fn(object, *args):
            if hasattr(object, slot):
                return getattr(object, slot)
            else:
                val = fn(object, *args)
                setattr(object, slot, val)
                return val
            
    else:
        @functools.lru_cache(maxsize=maxSize)
        def memoized_fn(*args):
            return fn(*args)
        
    return memoized_fn

class Queue:
    def __init__(self):
        raise NotImplementedError
    
    def extend(self: list, items:list):
        for item in items:
            self.append(item)

def LIFOQueue():
    return []

class FIFOQueue(collections.deque):
    def __init__(self):
        collections.deque.__init__(self)
    def pop(self):
        return self.popleft()

class PriorityQueue:
    def __init__(self, order='min', f=lambda x: x):
        self.heap = []
        if order == 'min':
            self.f = f
        elif order == 'max':
            self.f = lambda x: -f(x)
        else:
            raise ValueError("Order must be either 'min' or 'max'.")

    def append(self, item):
        heapq.heappush(self.heap, (self.f(item), item))

    def extend(self, items):
        for item in items:
            self.append(item)

    def pop(self):
        if self.heap:
            return heapq.heappop(self.heap)[1]
        else:
            raise Exception('Trying to pop from empty PriorityQueue')
        
    def __len__(self):
        return len(self.heap)
    
    def __contains__(self, key):
        return any([item == key for _, item in self.heap])
    
    def __getitem__(self, key):
        for value, item in self.heap:
            if item == key:
                return value
        raise KeyError(str(key) + " is not in the priority queue")
    
    def __delitem__(self, key):
        try:
            del self.heap[[item == key for _, item in self.heap].index(True)]
        except ValueError:
            raise KeyError(str(key) + " is not in the priority queue")
        heapq.heapify(self.heap)


class Problem(object):
    def __init__(self, initial, goal = None):
        self.initial = initial
        self.goal = goal

    def actions(self, state):
        raise NotImplementedError
    
    def result(self, state, action):
        raise NotImplementedError
    
    def goal_test(self, state):
        return state == self.goal
    
    def path_cost(self, c, first_state, action, second_state):
        return c + 1
    
    def value(self, state):
        raise NotImplementedError
    


class Node:
    def __init__(self, state, parent: 'Node' = None, action = None, path_cost = 0):
        self.state = state
        self.parent = parent
        self.action = action
        self.path_cost = path_cost
        self.depth = 0

        if parent:
            self.depth = parent.depth + 1

    def __repr__(self):
        return "<Node\n{}>".format(self.state)
    
    def __lt__(self, node: 'Node') -> bool:
        return self.state < node.state

    def expand(self, problem: Problem) -> list['Node']:
        return [self.child_node(problem, action)
                for action in problem.actions(self.state)]
    
    def child_node(self, problem: Problem, action) -> 'Node':
        next_state = problem.result(self, action)
        return Node(next_state,
                    self,
                    action,
                    problem.path_cost(self.path_cost, self.state, action, next_state)
                    )
    
    def solution(self):
        return [node.action for node in self.path()[1:]]
    
    def path(self) -> list['Node']:
        node, path_back = self, []

        while node:
            path_back.append(node)
            node = node.parent
            
        return list(reversed(path_back))
    
    def __eq__(self, other: 'Node'):
        return isinstance(other, Node) and self.state == other.state
    
    def __hash__(self):
        return hash(self.state)
    
def tree_search(problem: Problem, frontier):
    frontier.append(Node(problem.initial))
    while frontier:
        node:Node = frontier.pop()
        if problem.goal_test(node.state):
            return node
        frontier.extend(node.expand(problem))
    return None

def graph_search(problem: Problem, frontier):
    frontier.append(Node(problem.initial))
    explored = set()
    while frontier:
        node:Node = frontier.pop()
        if problem.goal_test(node.state):
            return node
        explored.add(node.state)

        frontier.extend(child for child in node.expand(problem)
                        if child.state not in explored
                        and child not in frontier)
        
    return None


def breadth_first_search(problem: Problem):
    return graph_search(problem, FIFOQueue())

def depth_first_search(problem: Problem):
    return graph_search(problem, LIFOQueue())

def best_first_graph_search(problem: Problem, f):
    node = Node(problem.initial)
    if problem.goal_test(node.state):
        return node
    frontier = PriorityQueue(order='min', f=f)
    frontier.append(node)
    explored = set()

    while frontier:
        node: Node = frontier.pop()
        if problem.goal_test(node.state):
            return node
        explored.add(node.state)

        for child in node.expand(problem):
            if child.state not in explored and child not in frontier:
                frontier.append(child)
            elif child in frontier:
                if f(child) < frontier[child]:
                    frontier.append(child)

    return None

def uniform_cost_search(problem: Problem):
    return best_first_graph_search(problem, lambda node : node.path_cost)

def astar_search(problem: Problem, h=None):
    h = memoize(h or problem.h, slot = 'h')
    return best_first_graph_search(problem, lambda n: n.path_cost + h(n))
