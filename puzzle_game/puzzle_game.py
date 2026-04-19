# 导入Python标准库，无需安装任何第三方依赖
import tkinter as tk                  # GUI图形界面库
from tkinter import ttk, messagebox  # 高级控件和消息对话框
import random                         # 随机数生成库
import json                           # JSON数据存储
import os                             # 系统文件操作

class PuzzleGame:
    """
    游戏主类：负责整个游戏的初始化、窗口管理和关卡切换
    """
    def __init__(self, root):
        # 主窗口对象
        self.root = root
        # 设置窗口标题
        self.root.title("益智闯关游戏")
        # 设置窗口尺寸 宽x高
        self.root.geometry("900x750")
        # 允许窗口调整大小
        self.root.resizable(True, True)
        
        # 设置窗口图标和任务栏图标
        try:
            icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Image', 'log.png')
            self.root.iconphoto(True, tk.PhotoImage(file=icon_path))
        except Exception as e:
            print(f"加载图标失败: {e}")
        
        # 游戏难度等级
        self.difficulty = 1
        # 最高记录
        self.highest_record = self.load_highest_record()
        # 当前轮次
        self.current_round = 1
        
        # 初始化主菜单界面
        self.show_main_menu()
    
    def load_highest_record(self):
        """加载最高记录"""
        try:
            if os.path.exists('game_record.json'):
                with open('game_record.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('highest_round', 1)
        except:
            pass
        return 1
    
    def save_highest_record(self):
        """保存最高记录"""
        try:
            with open('game_record.json', 'w', encoding='utf-8') as f:
                json.dump({'highest_round': self.highest_record}, f)
        except:
            pass
    
    def show_main_menu(self):
        """显示主菜单界面"""
        # 清空窗口
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # 标题
        title_label = ttk.Label(self.root, text="🧩 益智闯关游戏", font=('Arial', 32, 'bold'))
        title_label.pack(pady=40)
        
        # 最高记录显示
        record_label = ttk.Label(self.root, text=f"🏆 最高挑战记录: 第 {self.highest_record} 关", 
                               font=('Arial', 16), foreground='#e74c3c')
        record_label.pack(pady=10)
        
        # 难度选择
        diff_frame = ttk.Frame(self.root)
        diff_frame.pack(pady=30)
        
        ttk.Label(diff_frame, text="选择起始难度 (1-100):", font=('Arial', 14)).grid(row=0, column=0, padx=10)
        
        self.diff_var = tk.IntVar(value=1)
        diff_spin = ttk.Spinbox(diff_frame, from_=1, to=100, textvariable=self.diff_var, 
                               width=10, font=('Arial', 14), wrap=True)
        diff_spin.grid(row=0, column=1, padx=10)
        
        # 开始游戏按钮
        start_btn = ttk.Button(self.root, text="🎮 开始游戏", command=self.start_game,
                              style='Accent.TButton')
        start_btn.pack(pady=30, ipadx=30, ipady=15)
        
        # 游戏说明
        info_text = """
游戏规则:
✅ 完成3个关卡后难度会自动提升，挑战无限循环
✅ 第一关：记忆翻牌 - 找到所有配对卡片
✅ 第二关：滑块拼图 - 按顺序排列数字
✅ 第三关：数独挑战 - 每行每列数字不重复
✅ 难度越高，格子越多，挑战越大！
        """
        info_label = ttk.Label(self.root, text=info_text, font=('Arial', 12), justify='left')
        info_label.pack(pady=20)
    
    def start_game(self):
        """开始游戏"""
        self.difficulty = self.diff_var.get()
        self.current_round = self.difficulty
        self.current_level = 0
        self.start_level()
    
    def start_level(self):
        """开始当前关卡"""
        # 清空窗口
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # 显示轮次信息
        round_label = ttk.Label(self.root, text=f"🎯 第 {self.current_round} 轮挑战", 
                               font=('Arial', 16, 'bold'), foreground='#2980b9')
        round_label.pack(pady=10)
        
        # 根据当前关卡索引创建对应的关卡
        if self.current_level == 0:
            MemoryLevel(self.root, self.next_level, self.current_round)
        elif self.current_level == 1:
            SlidePuzzleLevel(self.root, self.next_level, self.current_round)
        elif self.current_level == 2:
            SudokuLevel(self.root, self.game_complete, self.current_round)
    
    def next_level(self):
        """进入下一关"""
        self.current_level += 1
        self.start_level()
    
    def game_complete(self):
        """本轮3个关卡全部完成"""
        # 更新最高记录
        if self.current_round > self.highest_record:
            self.highest_record = self.current_round
            self.save_highest_record()
            message = f"🎉 恭喜通过第 {self.current_round} 轮挑战！\n\n🏆 创造新的最高记录！\n\n准备进入第 {self.current_round + 1} 轮挑战，难度将提升！"
        else:
            message = f"🎉 恭喜通过第 {self.current_round} 轮挑战！\n\n准备进入第 {self.current_round + 1} 轮挑战，难度将提升！"
        
        messagebox.showinfo("轮次完成", message)
        
        # 进入下一轮
        self.current_round += 1
        self.current_level = 0
        self.start_level()


class BaseLevel:
    """
    关卡基类：所有关卡都继承这个类，统一接口规范
    """
    def __init__(self, root, on_complete, round_num):
        self.root = root                  # 主窗口引用
        self.on_complete = on_complete    # 通关回调函数
        self.round_num = round_num        # 当前轮次
        self.moves = 0                    # 移动次数计数
        
        # 创建关卡主框架
        self.frame = ttk.Frame(root)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
    
    def show(self):
        """显示当前关卡"""
        self.frame.pack(fill=tk.BOTH, expand=True)
    
    def hide(self):
        """隐藏当前关卡"""
        self.frame.pack_forget()


class MemoryLevel(BaseLevel):
    """
    关卡1: 记忆翻牌游戏 - 水果动物emoji配对
    难度越高，卡片数量越多
    """
    # 彩色emoji图标 - 水果和动物
    EMOJIS = ['🍎', '🍊', '🍋', '🍇', '🍓', '🍑', '🍒', '🥝', '🍌', '🥭',
              '🐶', '🐱', '🐰', '🐻', '🐼', '🐸', '🦊', '🐯', '🐷', '🐔',
              '🌸', '🌺', '🌻', '🌹', '🌷', '⭐', '❤️', '💎', '🔔', '🎈']
    
    def __init__(self, root, on_complete, round_num):
        super().__init__(root, on_complete, round_num)
        
        # 每轮增加2对卡片(4张)
        self.pairs = 6 + (round_num - 1)
        # 最多30对卡片
        self.pairs = min(self.pairs, 30)
        
        # 计算网格行列数
        total_cards = self.pairs * 2
        cols = min(8, (total_cards + 2) // 2)
        rows = (total_cards + cols - 1) // cols
        
        # 动态计算按钮大小 - emoji占满90%空间
        btn_size = max(4, int(90 / max(rows, cols)))
        font_size = max(24, int(40 / max(rows / 3, cols / 4)))
        
        # 关卡标题
        title_label = ttk.Label(self.frame, text=f"关卡 1: 记忆翻牌 | 第 {round_num} 轮", 
                               font=('Arial', 20, 'bold'))
        title_label.pack(pady=10)
        
        # 信息显示标签
        self.info_label = ttk.Label(self.frame, text=f"找到所有 {self.pairs} 对卡片", 
                                   font=('Arial', 12))
        self.info_label.pack(pady=5)
        
        # 卡片网格容器
        grid_frame = ttk.Frame(self.frame)
        grid_frame.pack(pady=15, expand=True)
        
        self.cards = []         # 卡片数值列表
        self.selected = []      # 当前选中待判断的卡片索引
        self.matched = []       # 已经配对成功的卡片索引
        self.buttons = []       # 卡片按钮控件列表
        
        # 生成卡片对
        values = list(range(self.pairs)) * 2
        random.shuffle(values)
        
        # 创建卡片按钮网格
        for i in range(rows):
            row = []
            for j in range(cols):
                idx = i * cols + j
                if idx < total_cards:
                    btn = tk.Button(grid_frame, text="❓", width=btn_size, height=btn_size//2,
                                   command=lambda idx=idx: self.card_click(idx),
                                   font=('Segoe UI Emoji', font_size), bg='#2f3542',
                                   bd=1, relief=tk.FLAT, highlightthickness=0,
                                   padx=0, pady=0)
                    btn.grid(row=i, column=j, padx=4, pady=4)
                    row.append(btn)
                    self.cards.append(values[idx])
                else:
                    # 占位空白
                    lbl = ttk.Label(grid_frame, text="")
                    lbl.grid(row=i, column=j, padx=4, pady=4)
                    row.append(None)
            self.buttons.append(row)
        
        self.cols = cols
        self.total_cards = total_cards
    
    def card_click(self, idx):
        """卡片点击事件处理"""
        i, j = idx // self.cols, idx % self.cols
        btn = self.buttons[i][j]
        
        if not btn or idx in self.matched or idx in self.selected or len(self.selected) >= 2:
            return
        
        self.selected.append(idx)
        # 每个emoji使用不同彩色背景，背景色也成为匹配要素
        bg_colors = ['#ff6b6b', '#feca57', '#48dbfb', '#1dd1a1', '#ff9ff3', '#54a0ff',
                     '#5f27cd', '#00d2d3', '#ff9f43', '#ee5a24', '#c8d6e5', '#10ac84']
        bg_color = bg_colors[self.cards[idx] % len(bg_colors)]
        btn.config(text=self.EMOJIS[self.cards[idx]], bg=bg_color, fg='white')
        self.moves += 1
        self.info_label.config(text=f"移动次数: {self.moves}  已配对: {len(self.matched)//2}/{self.pairs}")
        
        if len(self.selected) == 2:
            self.root.after(600, self.check_match)
    
    def check_match(self):
        """检查两张选中卡片是否匹配"""
        idx1, idx2 = self.selected
        i1, j1 = idx1 // self.cols, idx1 % self.cols
        i2, j2 = idx2 // self.cols, idx2 % self.cols
        
        btn1 = self.buttons[i1][j1]
        btn2 = self.buttons[i2][j2]
        
        if self.cards[idx1] == self.cards[idx2]:
            # 配对成功 - 保留原背景色，仅标记不可点击
            btn1.config(state='disabled', disabledforeground='white')
            btn2.config(state='disabled', disabledforeground='white')
            self.matched.extend([idx1, idx2])
            
            if len(self.matched) == self.total_cards:
                messagebox.showinfo("通关", f"✅ 记忆翻牌关卡完成！\n使用了 {self.moves} 次移动")
                self.hide()
                self.on_complete()
        else:
            # 配对失败
            btn1.config(text="❓", bg='#57606f')
            btn2.config(text="❓", bg='#57606f')
        
        self.selected.clear()


class SlidePuzzleLevel(BaseLevel):
    """
    关卡2: 滑块拼图游戏
    难度越高，网格越大: 3x3 → 4x4 → 5x5 → ...
    """
    def __init__(self, root, on_complete, round_num):
        super().__init__(root, on_complete, round_num)
        
        # 网格大小: 第1轮3x3, 第2轮4x4, 第3轮5x5, 最大7x7
        self.grid_size = min(7, 3 + (round_num - 1))
        total_tiles = self.grid_size * self.grid_size
        
        # 动态计算按钮大小
        btn_size = max(4, int(28 / self.grid_size))
        font_size = max(12, int(48 / self.grid_size))
        
        # 关卡标题
        title_label = ttk.Label(self.frame, text=f"关卡 2: 滑块拼图 | 第 {round_num} 轮 {self.grid_size}x{self.grid_size}", 
                               font=('Arial', 20, 'bold'))
        title_label.pack(pady=10)
        
        # 信息标签
        self.info_label = ttk.Label(self.frame, text="点击数字移动到空格，按顺序排列", 
                                   font=('Arial', 12))
        self.info_label.pack(pady=5)
        
        # 拼图网格容器
        grid_frame = ttk.Frame(self.frame)
        grid_frame.pack(pady=20, expand=True)
        
        # 初始化网格数据
        self.grid = [[i * self.grid_size + j for j in range(self.grid_size)] for i in range(self.grid_size)]
        self.empty = (self.grid_size - 1, self.grid_size - 1)
        
        # 按钮控件矩阵
        self.buttons = [[None for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        
        # 创建按钮网格
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                btn = tk.Button(grid_frame, text="", width=btn_size, height=btn_size//2,
                               font=('Arial', font_size, 'bold'), bg='#3498db', fg='white',
                               command=lambda i=i, j=j: self.tile_click(i,j))
                btn.grid(row=i, column=j, padx=2, pady=2)
                self.buttons[i][j] = btn
        
        # 随机打乱拼图
        shuffle_times = self.grid_size * self.grid_size * 20
        for _ in range(shuffle_times):
            moves = self.get_valid_moves()
            move = random.choice(moves)
            ex, ey = self.empty
            self.grid[ex][ey], self.grid[move[0]][move[1]] = self.grid[move[0]][move[1]], self.grid[ex][ey]
            self.empty = (move[0], move[1])
        
        # 更新界面显示
        self.update_display()
    
    def get_valid_moves(self):
        """获取当前空格旁边可以移动的方块位置"""
        x, y = self.empty
        moves = []
        if x > 0: moves.append((x-1, y))
        if x < self.grid_size - 1: moves.append((x+1, y))
        if y > 0: moves.append((x, y-1))
        if y < self.grid_size - 1: moves.append((x, y+1))
        return moves
    
    def swap_tile(self, i, j):
        """交换指定位置方块和空格的位置"""
        ex, ey = self.empty
        self.grid[ex][ey], self.grid[i][j] = self.grid[i][j], self.grid[ex][ey]
        self.empty = (i, j)
        self.moves += 1
    
    def tile_click(self, i, j):
        """方块点击事件"""
        if (i,j) in self.get_valid_moves():
            self.swap_tile(i, j)
            self.update_display()
            self.info_label.config(text=f"移动次数: {self.moves}")
            
            if self.check_win():
                messagebox.showinfo("通关", f"✅ 滑块拼图关卡完成！\n使用了 {self.moves} 次移动")
                self.hide()
                self.on_complete()
    
    def update_display(self):
        """根据矩阵数据更新界面显示"""
        max_num = self.grid_size * self.grid_size - 1
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                val = self.grid[i][j]
                if val == max_num:
                    self.buttons[i][j].config(text="", bg='white', state='disabled')
                else:
                    self.buttons[i][j].config(text=str(val + 1), bg='#3498db', state='normal')
    
    def check_win(self):
        """检查是否通关"""
        count = 0
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if self.grid[i][j] != count:
                    return False
                count += 1
        return True


class SudokuLevel(BaseLevel):
    """
    关卡3: 数独游戏
    先生成完整正确表格，再扣除需要填入的位置
    难度越高，数字范围越大，空格越多
    """
    def __init__(self, root, on_complete, round_num):
        super().__init__(root, on_complete, round_num)
        
        # 数独大小: 4x4, 5x5, 6x6 随难度增加
        self.size = min(9, 4 + (round_num - 1) // 2)
        # 空格数量: 随难度增加
        self.empty_cells = min(self.size * self.size // 2, 8 + round_num * 2)
        
        # 关卡标题
        title_label = ttk.Label(self.frame, text=f"关卡 3: 数独 | 第 {round_num} 轮 {self.size}x{self.size}", 
                               font=('Arial', 20, 'bold'))
        title_label.pack(pady=10)
        
        ttk.Label(self.frame, text=f"填写数字 1-{self.size}，每行每列数字不重复", font=('Arial', 12)).pack(pady=5)
        
        # 数独网格容器
        grid_frame = ttk.Frame(self.frame)
        grid_frame.pack(pady=15, expand=True)
        
        self.grid = [[0]*self.size for _ in range(self.size)]
        self.solution = [[0]*self.size for _ in range(self.size)]
        self.entries = [[None for _ in range(self.size)] for _ in range(self.size)]
        self.fixed = [[False]*self.size for _ in range(self.size)]
        
        # 第一步: 生成完整的正确答案
        self.generate_solution()
        
        # 复制答案到显示网格
        for i in range(self.size):
            for j in range(self.size):
                self.grid[i][j] = self.solution[i][j]
        
        # 第二步: 随机扣除位置生成题目
        positions = [(i,j) for i in range(self.size) for j in range(self.size)]
        random.shuffle(positions)
        
        for pos in positions[:self.empty_cells]:
            i,j = pos
            self.grid[i][j] = 0
            self.fixed[i][j] = False
        
        # 标记固定数字
        for i in range(self.size):
            for j in range(self.size):
                if self.grid[i][j] != 0:
                    self.fixed[i][j] = True
        
        # 动态计算输入框大小
        font_size = max(12, int(32 / self.size))
        entry_width = max(2, int(6 / self.size * 4))
        
        # 创建输入框网格
        for i in range(self.size):
            for j in range(self.size):
                entry = tk.Entry(grid_frame, width=entry_width, font=('Arial', font_size, 'bold'),
                               justify='center', bd=2)
                
                if self.fixed[i][j]:
                    entry.insert(0, str(self.grid[i][j]))
                    entry.config(state='readonly', bg='#ecf0f1')
                else:
                    entry.config(bg='white')
                    entry.bind('<KeyRelease>', lambda e, i=i, j=j: self.on_input(e, i, j))
                
                entry.grid(row=i, column=j, padx=3, pady=3, ipady=5)
                self.entries[i][j] = entry
        
        # 检查答案按钮
        ttk.Button(self.frame, text="检查答案", command=self.check_solution).pack(pady=15)
    
    def generate_solution(self):
        """生成合法的数独完整答案"""
        base = list(range(1, self.size + 1))
        random.shuffle(base)
        
        for i in range(self.size):
            offset = i
            for j in range(self.size):
                self.solution[i][j] = base[(j + offset) % self.size]
        
        # 随机打乱行和列保证随机性
        for _ in range(10):
            # 交换两行
            r1, r2 = random.sample(range(self.size), 2)
            self.solution[r1], self.solution[r2] = self.solution[r2], self.solution[r1]
            # 交换两列
            c1, c2 = random.sample(range(self.size), 2)
            for i in range(self.size):
                self.solution[i][c1], self.solution[i][c2] = self.solution[i][c2], self.solution[i][c1]
    
    def on_input(self, event, i, j):
        """键盘输入事件处理"""
        val = self.entries[i][j].get().strip()
        if val.isdigit() and 1 <= int(val) <= self.size:
            self.grid[i][j] = int(val)
        else:
            self.grid[i][j] = 0
    
    def check_solution(self):
        """检查用户填写的答案是否正确"""
        # 检查所有格子已填写
        for i in range(self.size):
            for j in range(self.size):
                if self.grid[i][j] == 0:
                    messagebox.showwarning("提示", "还有空格没有填写！")
                    return
        
        # 检查每行数字唯一
        for row in self.grid:
            if len(set(row)) != self.size:
                messagebox.showerror("错误", "❌ 答案不对，有重复数字！")
                return
        
        # 检查每列数字唯一
        for j in range(self.size):
            col = [self.grid[i][j] for i in range(self.size)]
            if len(set(col)) != self.size:
                messagebox.showerror("错误", "❌ 答案不对，有重复数字！")
                return
        
        # 全部正确
        messagebox.showinfo("通关", "✅ 数独关卡完成！")
        self.hide()
        self.on_complete()


# 程序入口
if __name__ == "__main__":
    # 创建主窗口
    root = tk.Tk()
    # 初始化游戏
    app = PuzzleGame(root)
    # 启动GUI主事件循环
    root.mainloop()
