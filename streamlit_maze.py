import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image, ImageDraw
from maze_logic import MazeSolver, solve_bfs, solve_dfs, solve_astar, solve_greedy, solve_uniform_cost, solve_ids
from random_map_generator import generate_map_with_paths
import uuid
import time

# Cấu hình thuật toán
ALGORITHMS = {
    "BFS": solve_bfs,
    "DFS": solve_dfs,
    "A*": solve_astar,
    "Greedy": solve_greedy,
    "Uniform Cost": solve_uniform_cost
}

# Cấu hình mặc định
CELL_SIZE = 20
MAZE_WIDTH = 30
MAZE_HEIGHT = 20

# Vẽ mê cung
def draw_maze():
    maze = st.session_state["maze"]
    img_width = MAZE_WIDTH * CELL_SIZE
    img_height = MAZE_HEIGHT * CELL_SIZE

    img = Image.new("RGB", (img_width, img_height), "white")
    draw = ImageDraw.Draw(img)

    for y, row in enumerate(maze):
        for x, cell in enumerate(row):
            color = "black" if cell == "#" else "white"
            if cell == "o":
                color = "blue"
            elif cell == "x":
                color = "red"

            draw.rectangle(
                [
                    x * CELL_SIZE,
                    y * CELL_SIZE,
                    (x + 1) * CELL_SIZE,
                    (y + 1) * CELL_SIZE,
                ],
                fill=color,
                outline="black",
            )
    return img

# Khởi tạo trạng thái
if "maze" not in st.session_state:
    st.session_state["maze"] = generate_map_with_paths(MAZE_WIDTH, MAZE_HEIGHT, min_paths=50)

if "start_point" not in st.session_state:
    st.session_state["start_point"] = None

if "goal_point" not in st.session_state:
    st.session_state["goal_point"] = None

if "path" not in st.session_state:
    st.session_state["path"] = []

if "warning" not in st.session_state:
    st.session_state["warning"] = lambda message: st.session_state.update({"warning_message": message})

if "draw" not in st.session_state:
    st.session_state["draw"] = draw_maze()

if "canvas_key" not in st.session_state:
    st.session_state["canvas_key"] = str(uuid.uuid4())

maze = st.session_state["maze"]

# Hàm xử lý chọn điểm bắt đầu và kết thúc
def select_point(x, y):
    maze = st.session_state["maze"]

    if maze[y][x] == "#":
        if callable(st.session_state["warning"]):
            st.session_state["warning"]("Không thể chọn vào tường!")
        return

    if st.session_state["start_point"] is None:
        st.session_state["start_point"] = (x, y)
        if callable(st.session_state["warning"]):
            st.session_state["warning"]("Điểm bắt đầu là: " + str((x, y)))
        maze[y][x] = "o"

    elif st.session_state["goal_point"] is None:
        st.session_state["goal_point"] = (x, y)
        if callable(st.session_state["warning"]):
            st.session_state["warning"]("Điểm kết thúc là: " + str((x, y)))
        maze[y][x] = "x"
    else:
        if callable(st.session_state["warning"]):
            st.session_state["warning"]("Đã chọn đủ điểm bắt đầu và kết thúc!")
        

        return

    st.session_state["maze"] = maze


# Hàm xử lý giải mê cung
def solve_maze():
    maze = st.session_state["maze"]
    start_point = st.session_state["start_point"]
    goal_point = st.session_state["goal_point"]

    if start_point is None or goal_point is None:
        st.error("Hãy chọn điểm bắt đầu và kết thúc trước khi giải!")
        return

    algorithm = st.session_state["algorithm"]
    solver = MazeSolver(maze)
    solver.initial = start_point
    solver.goal = goal_point

    try:
        path_result = ALGORITHMS[algorithm](solver)
        if path_result is None:
            st.error("Không tìm thấy đường đi!")
            return

        # Lưu đường đi
        path_positions = [step[1] for step in path_result.path()]
        st.session_state["path"] = path_positions

        # Vẽ đường đi lên mê cung
        solved_img = draw_path_on_maze(path_positions)
        st.image(solved_img, caption="Đường đi trong mê cung", use_column_width=True)
        st.success(f"Hoàn tất giải mê cung! Số bước đi: {len(path_positions)}")

    except Exception as e:
        st.error(f"Đã xảy ra lỗi: {e}")

# Hàm vẽ đường đi lên mê cung
def draw_path_on_maze(path_positions):
    img = draw_maze()
    draw = ImageDraw.Draw(img)

    for x, y in path_positions:
        draw.ellipse(
            [
                x * CELL_SIZE + 5,
                y * CELL_SIZE + 5,
                (x + 1) * CELL_SIZE - 5,
                (y + 1) * CELL_SIZE - 5,
            ],
            fill="purple",
            outline="purple",
        )
    return img

def draw_search_step(state, frames, color="yellow"):
    """
    Lưu trạng thái duyệt vào danh sách khung hình để tạo GIF.
    """
    # Lấy hình ảnh mê cung hiện tại
    maze_img = st.session_state["draw"].copy()
    draw = ImageDraw.Draw(maze_img)

    # Lấy tọa độ điểm đang duyệt
    x, y = state
    x1, y1 = x * CELL_SIZE, y * CELL_SIZE
    x2, y2 = x1 + CELL_SIZE, y1 + CELL_SIZE

    # Vẽ ô màu trạng thái
    draw.rectangle([x1, y1, x2, y2], fill=color, outline="black")
    st.session_state["draw"] = maze_img

    # Lưu khung hình để tạo GIF
    frames.append(maze_img)

def draw_shortest_path(path_positions, frames, color="purple"):
    """
    Vẽ đường đi ngắn nhất lên hình ảnh mê cung.
    """
    maze_img = st.session_state["draw"]
    draw = ImageDraw.Draw(maze_img)

    for x, y in path_positions:
        x1, y1 = x * CELL_SIZE, y * CELL_SIZE
        x2, y2 = x1 + CELL_SIZE, y1 + CELL_SIZE

        # Tô màu trạng thái
        draw.rectangle([x1, y1, x2, y2], fill=color, outline="black")
        st.session_state["draw"] = maze_img
        frames.append(maze_img.copy())

    # Cập nhật hình ảnh trong trạng thái
    st.session_state["draw"] = maze_img

def save_gif(frames, filename="search_process.gif", duration=100):
    """
    Lưu danh sách khung hình thành file GIF.
    """
    if len(frames) > 0:
        frames[0].save(
            filename,
            save_all=True,
            append_images=frames[1:],
            duration=duration,
            loop=1,
        )
    else:
        st.error("Không có khung hình nào để lưu GIF.")

def solve_maze_with_gif():
    """
    Giải mê cung và lưu quá trình tìm kiếm dưới dạng GIF.
    """
    maze = st.session_state["maze"]
    start_point = st.session_state["start_point"]
    goal_point = st.session_state["goal_point"]

    if start_point is None or goal_point is None:
        st.error("Hãy chọn điểm bắt đầu và kết thúc trước khi giải!")
        return

    # Lưu các khung hình để tạo GIF
    frames = []

    # Tạo solver
    solver = MazeSolver(maze, draw_search_step=lambda state: draw_search_step(state, frames))

    # Chọn thuật toán và chạy
    algorithm = st.session_state["algorithm"]
    result = ALGORITHMS[algorithm](solver)

    if result is None:
        st.error("Không tìm thấy đường đi!")
        return

    # Vẽ đường đi ngắn nhất
    path_positions = [step[1] for step in result.path()]
    draw_shortest_path(path_positions, frames)

    # Tạo GIF
    save_gif(frames, filename="search_process.gif")

    # Hiển thị file GIF
    st.image("search_process.gif", caption="Quá trình tìm kiếm", use_column_width=True)
    st.success(f"Hoàn tất giải mê cung! Số bước đi: {len(path_positions)}")

# Giao diện Streamlit
st.title("Maze Solver - Tìm đường thông minh")

# Chọn thuật toán
st.session_state["algorithm"] = st.selectbox("Chọn thuật toán:", list(ALGORITHMS.keys()))

# Hiển thị cảnh báo nếu có
if "warning_message" in st.session_state and st.session_state["warning_message"]:
    st.warning(st.session_state["warning_message"])

# Nút giải mê cung
if st.button("Giải mê cung"):
    solve_maze()

# Nút giải mê cung từng bước
if st.button("Giải mê cung từng bước"):
    solve_maze_with_gif()

# Nút tạo lại mê cung
if st.button("Tạo lại mê cung"):

    st.session_state["maze"] = generate_map_with_paths(MAZE_WIDTH, MAZE_HEIGHT, min_paths=50) # Tạo mê cung mới
    st.session_state["start_point"] = None
    st.session_state["goal_point"] = None
    st.session_state["path"] = []
    st.session_state["draw"] = draw_maze()

    st.session_state["canvas_key"] = str(uuid.uuid4())

    st.session_state["warning"] = None

    st.session_state[maze] = maze

# Hiển thị canvas để chọn điểm
canvas_result = st_canvas(
    fill_color="rgba(0, 0, 0, 0)",  # Màu mặc định
    background_image=st.session_state["draw"],  # Mê cung hiện tại
    height=MAZE_HEIGHT * CELL_SIZE,  # Chiều cao canvas
    width=MAZE_WIDTH * CELL_SIZE,  # Chiều rộng canvas
    drawing_mode="point",  # Chỉ click để chọn
    point_display_radius=0,  # Bán kính hiển thị khi click
    key= st.session_state.get("canvas_key", "canvas"),  # Key của canvas
    display_toolbar= False,  # Ẩn toolbar
)

count = 0

# Xử lý sự kiện click
if canvas_result.json_data is not None:
    objects = canvas_result.json_data["objects"]
    if objects:
        for obj in objects:
            obj = objects[-1]
            x = int(obj["left"]) // CELL_SIZE
            y = int(obj["top"]) // CELL_SIZE
            if 0 <= x < MAZE_WIDTH and 0 <= y < MAZE_HEIGHT and count % 2 == 0:
                select_point(x, y)
                count += 1
                st.session_state["draw"] = draw_maze()
                
