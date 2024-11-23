import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image, ImageDraw
from maze_logic import MazeSolver, solve_bfs, solve_dfs, solve_astar, solve_greedy, solve_uniform_cost, solve_ids
from random_map_generator import generate_map_with_paths

# Cấu hình thuật toán
ALGORITHMS = {
    "BFS": solve_bfs,
    "DFS": solve_dfs,
    "A*": solve_astar,
    "Greedy": solve_greedy,
    "Uniform Cost": solve_uniform_cost,
    "IDS": solve_ids,
}

# Cấu hình mặc định
CELL_SIZE = 30
MAZE_WIDTH = 50
MAZE_HEIGHT = 20
SCALE = 0.4

# Khởi tạo trạng thái
if "maze" not in st.session_state:
    st.session_state["maze"] = generate_map_with_paths(MAZE_WIDTH, MAZE_HEIGHT, min_paths=50)

if "start_point" not in st.session_state:
    st.session_state["start_point"] = None

if "goal_point" not in st.session_state:
    st.session_state["goal_point"] = None

if "path" not in st.session_state:
    st.session_state["path"] = []

maze = st.session_state["maze"]
# Xác định chiều rộng hiển thị cố định (px)
DISPLAY_WIDTH = 800  # Độ rộng hiển thị
CELL_SIZE = DISPLAY_WIDTH // MAZE_WIDTH  # Tính kích thước ô dựa trên số cột

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

# Hàm xử lý chọn điểm bắt đầu và kết thúc
def select_point(x, y):
    maze = st.session_state["maze"]

    if maze[y][x] == "#":
        st.warning("Không thể chọn vị trí là tường!")
        return

    if st.session_state["start_point"] is None:
        st.session_state["start_point"] = (x, y)
        maze[y][x] = "o"
    elif st.session_state["goal_point"] is None:
        st.session_state["goal_point"] = (x, y)
        maze[y][x] = "x"
    else:
        st.warning("Bạn đã chọn đủ điểm bắt đầu và kết thúc!")
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

# Giao diện Streamlit
st.title("Maze Solver - Tìm đường thông minh")

# Hiển thị canvas để chọn điểm
maze_img = draw_maze()

maze_img = maze_img.resize(
    (MAZE_WIDTH * CELL_SIZE, MAZE_HEIGHT * CELL_SIZE)
)

canvas_result = st_canvas(
    fill_color="rgba(0, 0, 0, 0)",  # Màu mặc định
    background_image=maze_img,  # Đặt hình ảnh mê cung làm nền
    height=MAZE_HEIGHT * CELL_SIZE,  # Chiều cao canvas
    width=MAZE_WIDTH * CELL_SIZE,  # Chiều rộng canvas
    drawing_mode="point",  # Chỉ click để chọn
    point_display_radius=5,  # Bán kính hiển thị khi click
    key="canvas",  # Khóa duy nhất cho canvas
)

# Xử lý sự kiện click
if canvas_result.json_data is not None:
    objects = canvas_result.json_data["objects"]
    if objects:
        for obj in objects:
            x = int(obj["left"]) // CELL_SIZE
            y = int(obj["top"]) // CELL_SIZE
            if 0 <= x < MAZE_WIDTH and 0 <= y < MAZE_HEIGHT and maze[y][x] != "#":
                st.write(f"Bạn đã chọn điểm: ({x}, {y})")


# Chọn thuật toán
st.session_state["algorithm"] = st.selectbox("Chọn thuật toán:", list(ALGORITHMS.keys()))

# Nút giải mê cung
if st.button("Giải mê cung"):
    solve_maze()

# Nút tạo lại mê cung
if st.button("Tạo lại mê cung"):
    st.session_state["maze"] = generate_map_with_paths(MAZE_WIDTH, MAZE_HEIGHT, min_paths=50)
    st.session_state["start_point"] = None
    st.session_state["goal_point"] = None
    st.session_state["path"] = []
    st.experimental_rerun()
