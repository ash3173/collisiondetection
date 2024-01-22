import numpy as np
####
class Node:
    def __init__(self, point, axis):
        self.point = point  # Coordinates of the point stored in the node
        self.axis = axis  # Axis (0 for x-axis, 1 for y-axis)
        self.left = None  # Left child node
        self.right = None  # Right child node

class KDTree:
    def __init__(self):
        self.root = None

    def insert(self, point):
        if self.root is None:
            self.root = Node(point, axis=0)
        else:
            self._insert_recursive(point, self.root)

    def _insert_recursive(self, point, node):
        axis = node.axis
        if point[axis] < node.point[axis]:
            if node.left is None:
                node.left = Node(point, axis=(axis + 1) % 2)
            else:
                self._insert_recursive(point, node.left)
        else:
            if node.right is None:
                node.right = Node(point, axis=(axis + 1) % 2)
            else:
                self._insert_recursive(point, node.right)

    def construct_kdtree(self, points):
        for point in points:
            self.insert(point)

    def find_nearest_neighbor(self, target):
        best_node = None
        best_distance = float('inf')

        def traverse(node, point, depth):
            nonlocal best_node, best_distance

            if node is None:
                return

            axis = node.axis

            if node.point != point:
                distance = np.linalg.norm(np.array(node.point) - np.array(point))
                if distance < best_distance:
                    best_node = node
                    best_distance = distance

            if point[axis] < node.point[axis]:
                traverse(node.left, point, depth + 1)
            else:
                traverse(node.right, point, depth + 1)

            if abs(node.point[axis] - point[axis]) < best_distance:
                if point[axis] < node.point[axis]:
                    traverse(node.right, point, depth + 1)
                else:
                    traverse(node.left, point, depth + 1)

        traverse(self.root, target, 0)
        return best_node
########################
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Rectangle:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def contains(self, point):
        return (self.x - self.width/2 <= point.x <= self.x + self.width/2 and  
                self.y - self.height/2 <= point.y <= self.y + self.height/2)

    def intersects(self, range_boundary):
        return not (self.x - self.width/2 > range_boundary.x + range_boundary.width/2 or
                    self.x + self.width/2 < range_boundary.x - range_boundary.width/2 or
                    self.y - self.height/2 > range_boundary.y + range_boundary.height/2 or
                    self.y + self.height/2 < range_boundary.y - range_boundary.height/2)
class QuadTree:
    def __init__(self,boundary,capacity):
        self.boundary = boundary
        self.capacity = capacity
        self.points = []
        self.kdtree = KDTree()
        self.divided = False      # Flag indicating if the node is divided

        self.northwest = None
        self.northeast = None
        self.southwest = None
        self.southeast = None

    def insert(self, point):
        # If the point is not within the boundary, ignore it
        if not self.boundary.contains(point):
            return

        # If the capacity is not reached, add the point to the current node
        if len(self.points) < self.capacity:
            self.points.append(point)
            temp=(point.x, point.y)
            self.kdtree.insert(temp)
        else:
            # If the node is not divided, create sub-quadrants and redistribute the points
            if not self.divided:
                self.subdivide()
            
            self.northwest.insert(point)
            self.northeast.insert(point)
            self.southwest.insert(point)
            self.southeast.insert(point)

    
    def subdivide(self):
        # Create sub-quadrants with half the width and height of the current boundary
        x = self.boundary.x
        y = self.boundary.y
        w = self.boundary.width / 2
        h = self.boundary.height / 2

        # Create sub-quadrants
        nw_boundary = Rectangle(x - w/2, y + h/2, w, h)
        ne_boundary = Rectangle(x + w/2, y + h/2, w, h)
        sw_boundary = Rectangle(x - w/2, y - h/2, w, h)
        se_boundary = Rectangle(x + w/2, y - h/2, w, h)

        self.northwest = QuadTree(nw_boundary, self.capacity)
        self.northeast = QuadTree(ne_boundary, self.capacity)
        self.southwest = QuadTree(sw_boundary, self.capacity)
        self.southeast = QuadTree(se_boundary, self.capacity)

        self.divided = True
    def query_range(self, range_boundary):
        # Create a list to store the points within the range
        points_in_range = []

        # If the query range does not intersect with the boundary, return the empty list
        if not self.boundary.intersects(range_boundary):
            return points_in_range

        # Check each point in the current node and add it to the result list if it is within the range
        for point in self.points:
            if range_boundary.contains(point):
                points_in_range.append(point)

        # If the node is divided, recursively query each sub-quadrant and add the points to the result list
        if self.divided:
            points_in_range += self.northwest.query_range(range_boundary)
            points_in_range += self.northeast.query_range(range_boundary)
            points_in_range += self.southwest.query_range(range_boundary)
            points_in_range += self.southeast.query_range(range_boundary)

        return points_in_range
    def nearest(self,point):
        return self.kdtree.find_nearest_neighbor(point)
        
############################

boundary=Rectangle(0, 0, 100, 100)
qt=QuadTree(boundary,4)

qt.insert(Point(10, 10))
qt.insert(Point(20, 20))
qt.insert(Point(30, 30))
qt.insert(Point(35, 35))
qt.insert(Point(50, 50))
qt.insert(Point(60, 60))
qt.insert(Point(70, 70))
qt.insert(Point(80, 80))
qt.insert(Point(90, 90))

# Query points within a range
range_boundary = Rectangle(25, 25, 10,10)
points_in_range = qt.query_range(range_boundary)

# Print the points within the range
print("Points which are colliding are:")
for point in qt.query_range(range_boundary):
    print("(",point.x,",",point.y,")")
a=qt.nearest((50,50))
print("Nearest point is:",a.point)



