import tkinter as tk
from tkinter import messagebox
from maze_logic import MazeSolver, solve_bfs, solve_dfs, solve_astar, solve_greedy, solve_uniform_cost, solve_ids
from random_map_generator import generate_map_with_paths
import time
import threading

ALGORITHMS = {
    "BFS": solve_bfs,
    "DFS": solve_dfs,
    "A*": solve_astar,
    "Greedy": solve_greedy,
    "Uniform Cost": solve_uniform_cost
}

running_algorithm = False  # Biến kiểm tra thuật toán đang chạy
steps_count = 0  # Biến đếm số bước đi

def start_tkinter_gui():
    root = tk.Tk()
    root.title("Maze Solver - Tìm đường thông minh")
    root.configure(bg="#f5f5f5")

    cell_size = 30
    maze = generate_map_with_paths(width=50, height=20, min_paths=20)
    maze = [list(row) for row in maze]
    start_point = None
    goal_point = None
    solved = False

    rows = len(maze)
    cols = len(maze[0])
    canvas_width = cols * cell_size
    canvas_height = rows * cell_size
    steps_count = 0

    root.geometry(f"{canvas_width+100}x{canvas_height+150}")

    canvas = tk.Canvas(root, width=canvas_width, height=canvas_height, bg="#ffffff")
    canvas.pack(pady=10)

    status_label = tk.Label(root, text="Sẵn sàng", bg="#f5f5f5", font=("Arial", 12))
    status_label.pack(pady=5)

    def draw_maze():
        canvas.delete("all")
        for i in range(rows):
            for j in range(cols):
                x1, y1 = j * cell_size, i * cell_size
                x2, y2 = x1 + cell_size, y1 + cell_size
                color = "white" if maze[i][j] == " " else "black"
                if maze[i][j] == "o":
                    color = "blue"
                elif maze[i][j] == "x":
                    color = "red"
                canvas.create_rectangle(x1, y1, x2, y2, fill=color)

    draw_maze()

    def generate_new_map():
        nonlocal maze, start_point, goal_point, solved
        status_label.config(text="Đang tạo bản đồ...")
        root.update()  # Cập nhật giao diện ngay lập tức

        try:
            maze = generate_map_with_paths(width=50, height=20, min_paths=50)
            maze = [list(row) for row in maze]
            start_point = None
            goal_point = None
            solved = False
            draw_maze()
            solve_button.config(state="normal")
            status_label.config(text="Bản đồ đã sẵn sàng!")
        except Exception as e:
            status_label.config(text="Lỗi khi tạo bản đồ!")
            messagebox.showerror("Lỗi", f"Đã xảy ra lỗi: {e}")

    search_steps = []  # Mảng lưu các trạng thái duyệt qua
    def draw_search_step(state):
        """
        Lưu trạng thái duyệt vào mảng và vẽ lên canvas màu vàng.
        """
        global steps_count

        if not running_algorithm:
            return  # Dừng vẽ nếu thuật toán đã bị ngừng

        search_steps.append(state)  # Lưu trạng thái duyệt vào mảng
        x, y = state
        x1, y1 = x * cell_size, y * cell_size
        x2, y2 = x1 + cell_size, y1 + cell_size
        canvas.create_rectangle(x1, y1, x2, y2, fill="pink", outline="black")
        canvas.update()  # Cập nhật Canvas sau mỗi bước
        canvas.after(50)  # Thêm độ trễ để dễ theo dõi

        # Tăng số bước đi
        steps_count += 1
        status_label.config(text=f"Đang duyệt... Số bước đi: {steps_count}")

    def on_canvas_click(event):
        nonlocal start_point, goal_point, solved

        if solved:
            messagebox.showinfo("Thông báo", "Hãy nhấn 'Tạo lại bản đồ' để bắt đầu lại!")
            return

        x, y = event.x // cell_size, event.y // cell_size

        if maze[y][x] == "#":
            messagebox.showinfo("Thông báo", "Bạn không thể chọn vị trí là tường!")
            return

        if start_point is None:
            start_point = (x, y)
            maze[y][x] = "o"
            canvas.create_rectangle(x * cell_size, y * cell_size, (x + 1) * cell_size, (y + 1) * cell_size, fill="blue")
        elif goal_point is None:
            goal_point = (x, y)
            maze[y][x] = "x"
            canvas.create_rectangle(x * cell_size, y * cell_size, (x + 1) * cell_size, (y + 1) * cell_size, fill="red")
        else:
            messagebox.showinfo("Thông báo", "Bạn đã chọn đủ điểm bắt đầu và kết thúc!")

    canvas.bind("<Button-1>", on_canvas_click)

    def on_algorithm_change(*args):
        status_label.config(text=f"Thuật toán hiện tại: {algorithm_var.get()}")
        canvas.delete("all")
        solve_button.config(state="normal")
        stop_button.config(state="disabled")
        draw_maze()

    def stop_algorithm():
        global running_algorithm
        running_algorithm = False  # Đặt flag về False để dừng thuật toán
        status_label.config(text="Thuật toán đã bị dừng.")
        solve_button.config(state="normal")
        stop_button.config(state="disabled")

    def solve_maze():
        global running_algorithm, steps_count, solved, search_steps
        steps_count = 0  # Đặt lại số bước đi
        search_steps = []  # Xóa trạng thái đã duyệt
        solved = False  # Đặt lại trạng thái giải xong
        canvas.delete("all")  # Xóa canvas cũ
        draw_maze()  # Vẽ lại mê cung ban đầu
        try:
            if start_point is None or goal_point is None:
                raise ValueError("Hãy chọn điểm bắt đầu và điểm kết thúc trước!")

            algorithm = algorithm_var.get()
            algorithm_func = ALGORITHMS[algorithm]  # Lấy hàm giải thuật tương ứng với tên thuật toán

            solver = MazeSolver(maze, draw_search_step=draw_search_step)  # Truyền callback vào MazeSolver
            solver.initial = start_point
            solver.goal = goal_point

            print(f"Start: {start_point}, Goal: {goal_point}")
            running_algorithm = True
            solve_button.config(state="disabled")
            stop_button.config(state="normal")

            path_result = algorithm_func(solver)  # Gọi hàm giải thuật với bài toán cụ thể
            print(f"Path Result: {path_result}")

            if path_result is None:
                raise ValueError("Không tìm thấy đường đi!")

            path_positions = [step[1] for step in path_result.path()]
            draw_path(path_positions)
            solved = True
            status_label.config(text=f"Hoàn tất giải mê cung! Số bước đi: {steps_count} - Độ dài đường đi: {len(path_positions)}")

        except Exception as e:
            messagebox.showerror("Lỗi", f"Đã xảy ra lỗi: {e}")
        finally:
            running_algorithm = False
            stop_button.config(state="disabled")

    def draw_path(path_positions):
        for pos in path_positions:
            x, y = pos
            x1, y1 = x * cell_size, y * cell_size
            x2, y2 = x1 + cell_size, y1 + cell_size
            canvas.create_rectangle(x1, y1, x2, y2, fill="purple")
            root.update()

    algorithm_label = tk.Label(root, text="Chọn thuật toán:", bg="#f5f5f5", font=("Arial", 12))
    algorithm_label.pack()

    algorithm_var = tk.StringVar(value="BFS")
    algorithm_menu = tk.OptionMenu(root, algorithm_var, *ALGORITHMS.keys())
    algorithm_menu.pack()
    # Gắn callback vào StringVar khi giá trị thay đổi
    algorithm_var.trace("w", on_algorithm_change)

    # Tạo một Frame cho các nút và thanh trượt
    control_frame = tk.Frame(root, bg="#f5f5f5")
    control_frame.pack(pady=10, fill="x")

    # Tạo một Frame cho các nút
    button_frame = tk.Frame(control_frame, bg="#f5f5f5")
    button_frame.pack(side="top", padx=20)

    generate_button = tk.Button(button_frame, text="Tạo lại bản đồ", command=generate_new_map, bg="#4caf50", fg="white", font=("Arial", 12))
    generate_button.pack(side="left", padx=10)

    solve_button = tk.Button(button_frame, text="Giải mê cung", command=solve_maze, bg="#2196f3", fg="white", font=("Arial", 12))
    solve_button.pack(side="left", padx=10)

    stop_button = tk.Button(button_frame, text="Ngừng Thuật Toán", command=stop_algorithm, bg="#f44336", fg="white", font=("Arial", 12))
    stop_button.pack(side="left", padx=10)
    stop_button.config(state="disabled")  # Ban đầu ngừng thuật toán bị tắt

    root.mainloop()

if __name__ == "__main__":
    start_tkinter_gui()
