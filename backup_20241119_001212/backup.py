import os
import shutil
from datetime import datetime

# Lấy địa chỉ path của thư mục dự án
project_dir = os.path.dirname(os.path.abspath(__file__))

# Tên thư mục backup với thời gian hiện tại
backup_dir = f'backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'

# Liệt kê thư mục backup có sẵn
backup_dirs = [f for f in os.listdir(project_dir) if f.startswith('backup_')]

# Xóa các thư mục backup cũ nếu có
for bd in backup_dirs:
    shutil.rmtree(bd)

# Tạo thư mục backup
shutil.copytree(project_dir, backup_dir)

print(f'Backup created at: {os.path.abspath(backup_dir)}')
