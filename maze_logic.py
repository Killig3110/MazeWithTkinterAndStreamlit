import math
from simpleai.search import SearchProblem, breadth_first, depth_first, astar, greedy, uniform_cost, iterative_limited_depth_first

# Định nghĩa các hướng di chuyển và chi phí tương ứng
COSTS = {
    "up": 1.0,
    "down": 1.0,
    "left": 1.0,
    "right": 1.0
}

class MazeSolver(SearchProblem):
    def __init__(self, board, draw_search_step=None):
        self.board = board
        self.goal = (0, 0)
        self.initial = (0, 0)
        self.explored = set()  # Biến lưu các trạng thái đã được khám phá
        self.draw_search_step = draw_search_step  # Callback để vẽ quá trình duyệt

        # Xác định điểm bắt đầu và kết thúc
        for y, row in enumerate(self.board):
            for x, cell in enumerate(row):
                if cell.lower() == "o":
                    self.initial = (x, y)
                elif cell.lower() == "x":
                    self.goal = (x, y)

        # Khởi tạo lớp cha với trạng thái ban đầu
        super(MazeSolver, self).__init__(initial_state=self.initial)

    def actions(self, state):
        actions = []
        for action in COSTS.keys():
            newx, newy = self.result(state, action)
            # Kiểm tra vị trí mới không phải tường và chưa được khám phá
            if self.board[newy][newx] != "#" and (newx, newy) not in self.explored:
                actions.append(action)
                self.explored.add((newx, newy))  # Đánh dấu ô này là đã được khám phá

                # Gọi callback để vẽ khi duyệt qua
                if self.draw_search_step:
                    self.draw_search_step((newx, newy))  # Vẽ trạng thái mới duyệt qua
        return actions

    def result(self, state, action):
        x, y = state
        if "up" in action:
            y -= 1
        if "down" in action:
            y += 1
        if "left" in action:
            x -= 1
        if "right" in action:
            x += 1
        return (x, y)

    def is_goal(self, state):
        return state == self.goal

    def cost(self, state, action, state2):
        return COSTS[action]

    def heuristic(self, state):
        # Sử dụng khoảng cách Euclidean làm heuristic
        x, y = state
        gx, gy = self.goal
        return math.sqrt((x - gx) ** 2 + (y - gy) ** 2)

# Hàm giải mê cung với các thuật toán tìm kiếm
def solve_bfs(solver, use_graph_search=True):
    return breadth_first(solver, graph_search=use_graph_search)

def solve_dfs(solver, use_graph_search=True):
    return depth_first(solver, graph_search=use_graph_search)

def solve_astar(solver, use_graph_search=True):
    return astar(solver, graph_search=use_graph_search)

def solve_greedy(solver, use_graph_search=True):
    return greedy(solver, graph_search=use_graph_search)

def solve_uniform_cost(solver, use_graph_search=True):
    return uniform_cost(solver, graph_search=use_graph_search)

def solve_ids(solver):
    return iterative_limited_depth_first(solver, limit=50)  # Giới hạn độ sâu là 50
