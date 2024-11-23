import random

def generate_map_with_paths(width, height, min_paths, max_attempts=1000):
    """
    Tạo bản đồ ngẫu nhiên với kích thước width x height và đảm bảo có đủ số lượng đường đi.
    Sử dụng DFS (Depth-First Search) để tạo các đường đi.
    """
    # Khởi tạo bản đồ toàn tường
    maze = [["#" for _ in range(width)] for _ in range(height)]

    # Hàm tạo mê cung bằng DFS (Backtracking)
    def dfs(x, y):
        # Tạo các hướng di chuyển hợp lệ: lên, xuống, trái, phải (không di chuyển chéo)
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        random.shuffle(directions)  # Xáo trộn các hướng di chuyển để tạo sự ngẫu nhiên

        for dx, dy in directions:
            nx, ny = x + dx * 2, y + dy * 2
            # Kiểm tra xem vị trí có hợp lệ và chưa được thăm
            if 0 < nx < width - 1 and 0 < ny < height - 1 and maze[ny][nx] == "#":
                # Tạo đường đi từ (x, y) đến (nx, ny)
                maze[ny][nx] = " "
                maze[y + dy][x + dx] = " "  # Tạo đường nối giữa 2 ô
                dfs(nx, ny)  # Tiếp tục tìm đường từ (nx, ny)

    # Chọn vị trí bắt đầu cố định
    start_x, start_y = 1, 1
    maze[start_y][start_x] = " "  # Ô bắt đầu

    # Khởi chạy DFS từ điểm bắt đầu
    dfs(start_x, start_y)

    # Đảm bảo rằng có đủ số lượng đường đi (min_paths)
    path_count = sum(row.count(" ") for row in maze)
    attempts = 0
    while path_count < min_paths and attempts < max_attempts:
        # Nếu số lượng đường đi không đủ, thử tạo thêm đường
        maze = [["#" for _ in range(width)] for _ in range(height)]  # Reset maze
        dfs(start_x, start_y)  # Chạy lại DFS để tạo thêm đường đi
        path_count = sum(row.count(" ") for row in maze)
        attempts += 1

    return maze

def print_maze(maze):
    """Hàm in mê cung ra màn hình"""
    for row in maze:
        print("".join(row))

