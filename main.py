import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import datetime, date
import logging
from database_manager import DatabaseManager
from data_manager import DataManager

class DailyTrackerApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("日常数据跟踪器")
        self.root.geometry("800x700")
        self.root.minsize(600, 500)

        # 初始化数据库
        self.db_manager = DatabaseManager()
        self.data_manager = DataManager(self.db_manager)
        
        # 设置日志
        logging.basicConfig(level=logging.INFO)
        
        # 初始化筛选状态
        self.current_filter_applied = False  # 追踪是否已应用筛选

        # 创建主界面
        self._create_menu()
        self._create_main_interface()

    def _create_menu(self):
        """创建菜单栏"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="导入数据", command=self._import_data)
        file_menu.add_command(label="导出为CSV", command=self._export_csv)
        file_menu.add_command(label="导出为JSON", command=self._export_json)
        file_menu.add_separator()
        file_menu.add_command(label="下载CSV模板", command=self._download_template)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit)
        
        # 编辑菜单
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="编辑", menu=edit_menu)
        edit_menu.add_command(label="修改记录", command=self._edit_record)
        edit_menu.add_command(label="删除记录", command=self._delete_record)

        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="使用说明", command=self._show_help)
        help_menu.add_command(label="数据格式说明", command=self._show_data_format)
        help_menu.add_command(label="关于", command=self._show_about)
    
    def _create_main_interface(self):
        """创建主界面"""
        # 创建主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建数据录入区域
        self._create_input_section(main_frame)

        # 创建数据表格区域
        self._create_table_section(main_frame)

    def _create_input_section(self, parent):
        """创建数据录入区域"""
        input_frame = ttk.LabelFrame(parent, text="记录", padding=10)
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 配置列权重以实现均匀分布
        for i in range(6):  # 3个输入框 × 2（标签+输入框）
            input_frame.columnconfigure(i, weight=1)

        # 创建输入字段 - 改为一行三个的布局
        fields = [
            ("日期:", "date"),
            ("入睡时间 (HH:MM):", "sleep_time"),
            ("体重 (kg):", "weight"),
            ("评分 (1-10):", "rating"),
            ("步数:", "steps"),
            ("卡路里摄入:", "calories_intake")
        ]
        
        self.input_vars = {}
        
        # 前6个字段按一行三个排列
        for i, (label, field) in enumerate(fields):
            row = i // 3  # 每3个换一行
            col = (i % 3) * 2  # 每个字段占2列（标签+输入框）

            ttk.Label(input_frame, text=label).grid(row=row, column=col, sticky=tk.W, padx=(0, 5), pady=5)

            if field == "date":
                self.input_vars[field] = DateEntry(
                    input_frame, 
                    width=15,
                    background='darkblue',
                    foreground='white', 
                    borderwidth=2,
                    date_pattern='yyyy-mm-dd'
                )
                # 绑定日期选择事件
                self.input_vars[field].bind("<<DateEntrySelected>>", self._on_date_selected)
            else:
                self.input_vars[field] = ttk.Entry(input_frame, width=15)
            
            self.input_vars[field].grid(row=row, column=col+1, sticky=tk.W+tk.E, padx=(0, 15), pady=5)

        # 小记单独占一行
        note_row = 2  # 前面两行已经放了6个字段

        # 小记标签 - 移除粗体样式，与其他标签保持一致
        ttk.Label(input_frame, text="小记:").grid(
            row=note_row, column=0, sticky=tk.W, padx=(0, 5), pady=(10, 5)
        )

        # 小记输入框 - 跨越整行
        self.input_vars["note"] = tk.Text(input_frame, height=4, wrap=tk.WORD)
        self.input_vars["note"].grid(
            row=note_row+1, column=0, columnspan=6,
            sticky=tk.W+tk.E+tk.N+tk.S, padx=(0, 0), pady=(0, 10)
        )

        # 提交按钮区域
        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=note_row+2, column=0, columnspan=6, pady=10)

        ttk.Button(button_frame, text="提交记录", command=self._submit_record).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="清空表单", command=self._clear_form).pack(side=tk.LEFT, padx=5)

    def _on_date_selected(self, event):
        """当日期被选择时，加载该日期的数据"""
        selected_date = self.input_vars["date"].get_date()
        self._load_data_for_date(selected_date)

    def _load_data_for_date(self, selected_date):
        """为指定日期加载数据到表单"""
        try:
            # 从数据库获取该日期的记录
            record = self.db_manager.get_record_by_date(selected_date)

            if record:
                # 如果存在记录，填充表单
                # record结构: (id, date, sleep_time, weight, rating, steps, calories_intake, note, created_at, updated_at)

                # 填充入睡时间 - 修复格式显示，处理不同的时间类型
                if record[2]:  # sleep_time
                    self.input_vars["sleep_time"].delete(0, tk.END)
                    # 处理不同类型的时间对象
                    sleep_time_value = record[2]

                    if hasattr(sleep_time_value, 'strftime'):
                        # 如果是 time 或 datetime 对象
                        time_str = sleep_time_value.strftime('%H:%M')
                    elif hasattr(sleep_time_value, 'total_seconds'):
                        # 如果是 timedelta 对象，转换为时间格式
                        total_seconds = int(sleep_time_value.total_seconds())
                        hours = total_seconds // 3600
                        minutes = (total_seconds % 3600) // 60
                        time_str = f"{hours:02d}:{minutes:02d}"
                    else:
                        # 如果是字符串，直接使用
                        time_str = str(sleep_time_value)

                    self.input_vars["sleep_time"].insert(0, time_str)
                else:
                    self.input_vars["sleep_time"].delete(0, tk.END)

                # 填充体重
                if record[3]:  # weight
                    self.input_vars["weight"].delete(0, tk.END)
                    self.input_vars["weight"].insert(0, str(record[3]))
                else:
                    self.input_vars["weight"].delete(0, tk.END)

                # 填充评分
                if record[4]:  # rating
                    self.input_vars["rating"].delete(0, tk.END)
                    self.input_vars["rating"].insert(0, str(record[4]))
                else:
                    self.input_vars["rating"].delete(0, tk.END)

                # 填充步数
                if record[5]:  # steps
                    self.input_vars["steps"].delete(0, tk.END)
                    self.input_vars["steps"].insert(0, str(record[5]))
                else:
                    self.input_vars["steps"].delete(0, tk.END)

                # 填充卡路里摄入
                if record[6]:  # calories_intake
                    self.input_vars["calories_intake"].delete(0, tk.END)
                    self.input_vars["calories_intake"].insert(0, str(record[6]))
                else:
                    self.input_vars["calories_intake"].delete(0, tk.END)

                # 填充备注
                self.input_vars["note"].delete("1.0", tk.END)
                if record[7]:  # note
                    self.input_vars["note"].insert("1.0", record[7])

                # 存储记录ID，用于更新时使用
                self.current_record_id = record[0]

            else:
                # 如果没有记录，清空表单（除了日期）
                self._clear_form_except_date()
                self.current_record_id = None

        except Exception as e:
            logging.error(f"加载日期数据时发生错误: {e}")
            messagebox.showerror("错误", f"加载数据时发生错误: {str(e)}")

    def _clear_form_except_date(self):
        """清空表单但保留日期"""
        for field in ["sleep_time", "weight", "rating", "steps", "calories_intake"]:
            self.input_vars[field].delete(0, tk.END)

        self.input_vars["note"].delete("1.0", tk.END)

    def _create_table_section(self, parent):
        """创建数据表格区域"""
        table_frame = ttk.LabelFrame(parent, text="表格总览", padding=10)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # 添加筛选控制区域
        filter_frame = ttk.Frame(table_frame)
        filter_frame.pack(fill=tk.X, pady=(0, 10))

        # 筛选模式选择 - 移除"显示全部"选项
        ttk.Label(filter_frame, text="筛选模式:").pack(side=tk.LEFT)

        self.filter_mode = tk.StringVar(value="year")  # 默认为按年份
        filter_options = [("按年份", "year"), ("按年月", "year_month"), ("按日期范围", "date_range")]

        filter_combo = ttk.Combobox(filter_frame, textvariable=self.filter_mode, width=12, state="readonly")
        filter_combo['values'] = [option[0] for option in filter_options]
        filter_combo.pack(side=tk.LEFT, padx=5)
        filter_combo.bind('<<ComboboxSelected>>', self._on_filter_mode_change)

        # 筛选参数控件容器
        self.filter_params_frame = ttk.Frame(filter_frame)
        self.filter_params_frame.pack(side=tk.LEFT, padx=10)

        # 筛选按钮
        ttk.Button(filter_frame, text="应用筛选", command=self._apply_filter).pack(side=tk.LEFT, padx=5)
        ttk.Button(filter_frame, text="重置", command=self._reset_filter).pack(side=tk.LEFT, padx=5)

        # 映射显示名称到值
        self.filter_mode_mapping = {option[0]: option[1] for option in filter_options}

        # 创建表格
        columns = ("ID", "日期", "入睡时间", "体重", "评分", "步数", "卡路里", "备注")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)
        
        # 设置列标题和宽度
        column_widths = {"ID": 50, "日期": 80, "入睡时间": 80, "体重": 60, "评分": 50, "步数": 70, "卡路里": 70, "备注": 150}
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=column_widths.get(col, 100), minwidth=50)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # 布局
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 绑定双击事件
        self.tree.bind("<Double-1>", self._on_item_double_click)

        # 初始化筛选参数控件
        self._setup_filter_params()

    def _on_filter_mode_change(self, event):
        """当筛选模式改变时"""
        self._setup_filter_params()

    def _setup_filter_params(self):
        """设置筛选参数控件"""
        # 清空现有控件
        for widget in self.filter_params_frame.winfo_children():
            widget.destroy()

        mode_value = self.filter_mode_mapping.get(self.filter_mode.get(), "year")

        if mode_value == "year":
            # 年份选择
            ttk.Label(self.filter_params_frame, text="年份:").pack(side=tk.LEFT)
            self.filter_year = tk.StringVar(value=str(datetime.now().year))
            year_spinbox = ttk.Spinbox(self.filter_params_frame, from_=2020, to=2030, width=8, textvariable=self.filter_year)
            year_spinbox.pack(side=tk.LEFT, padx=5)

        elif mode_value == "year_month":
            # 年份和月份选择
            ttk.Label(self.filter_params_frame, text="年份:").pack(side=tk.LEFT)
            self.filter_year = tk.StringVar(value=str(datetime.now().year))
            year_spinbox = ttk.Spinbox(self.filter_params_frame, from_=2020, to=2030, width=8, textvariable=self.filter_year)
            year_spinbox.pack(side=tk.LEFT, padx=5)

            ttk.Label(self.filter_params_frame, text="月份:").pack(side=tk.LEFT)
            self.filter_month = tk.StringVar(value=str(datetime.now().month))
            month_spinbox = ttk.Spinbox(self.filter_params_frame, from_=1, to=12, width=6, textvariable=self.filter_month)
            month_spinbox.pack(side=tk.LEFT, padx=5)

        elif mode_value == "date_range":
            # 日期范围选择
            ttk.Label(self.filter_params_frame, text="开始日期:").pack(side=tk.LEFT)
            self.filter_start_date = DateEntry(
                self.filter_params_frame,
                width=10,
                background='darkblue',
                foreground='white',
                borderwidth=2,
                date_pattern='yyyy-mm-dd'
            )
            self.filter_start_date.pack(side=tk.LEFT, padx=5)

            ttk.Label(self.filter_params_frame, text="结束日期:").pack(side=tk.LEFT)
            self.filter_end_date = DateEntry(
                self.filter_params_frame,
                width=10,
                background='darkblue',
                foreground='white',
                borderwidth=2,
                date_pattern='yyyy-mm-dd'
            )
            self.filter_end_date.pack(side=tk.LEFT, padx=5)

    def _apply_filter(self, show_message=True):
        """应用筛选条件"""
        mode_value = self.filter_mode_mapping.get(self.filter_mode.get(), "year")

        try:
            if mode_value == "year":
                year = int(self.filter_year.get())
                records = self.db_manager.get_records_by_year_month(year)
            elif mode_value == "year_month":
                year = int(self.filter_year.get())
                month = int(self.filter_month.get())
                records = self.db_manager.get_records_by_year_month(year, month)
            elif mode_value == "date_range":
                start_date = self.filter_start_date.get_date()
                end_date = self.filter_end_date.get_date()
                if start_date > end_date:
                    if show_message:
                        messagebox.showerror("错误", "开始日期不能晚于结束日期")
                    return
                records = self.db_manager.get_records_by_date_range(start_date, end_date)
            else:
                records = self.db_manager.get_all_records('ASC')

            # 更新表格显示
            self._update_table_with_records(records)

            # 只有在show_message为True且用户主动点击"应用筛选"按钮时才显示结果统计
            if show_message:
                messagebox.showinfo("筛选结果", f"找到 {len(records)} 条符合条件的记录")

            # 更新当前筛选状态
            self.current_filter_applied = True

        except ValueError as e:
            if show_message:
                messagebox.showerror("输入错误", "请输入有效的年份或月份")
        except Exception as e:
            logging.error(f"应用筛选时发生错误: {e}")
            if show_message:
                messagebox.showerror("错误", f"筛选数据时发生错误: {str(e)}")

    def _reset_filter(self):
        """重置筛选条件"""
        self.filter_mode.set("按年份")
        self._setup_filter_params()

        # 清空表格，回到初始状态
        for item in self.tree.get_children():
            self.tree.delete(item)

        # 重置当前筛选状态
        self.current_filter_applied = False

    def _submit_record(self):
        """提交记录"""
        try:
            # 获取输入数据
            selected_date = self.input_vars["date"].get_date()

            # 解析入睡时间
            sleep_time = None
            sleep_time_str = self.input_vars["sleep_time"].get().strip()
            if sleep_time_str:
                try:
                    sleep_time = datetime.strptime(sleep_time_str, "%H:%M").time()
                except ValueError:
                    messagebox.showerror("输入错误", "入睡时间格式不正确，请使用 HH:MM 格式（如：23:30）")
                    return

            # 解析其他数值字段
            weight = self._parse_float_input("weight", "体重")
            rating = self._parse_int_input("rating", "评分")
            steps = self._parse_int_input("steps", "步数")
            calories_intake = self._parse_int_input("calories_intake", "卡路里摄入")

            if rating is not None and (rating < 1 or rating > 10):
                messagebox.showerror("输入错误", "评分必须在1-10之间")
                return

            # 获取备注
            note = self.input_vars["note"].get("1.0", tk.END).strip()
            if not note:
                note = None

            # 提交到数据库
            if self.db_manager.insert_record(
                date=selected_date,
                sleep_time=sleep_time,
                weight=weight,
                rating=rating,
                steps=steps,
                calories_intake=calories_intake,
                note=note
            ):
                messagebox.showinfo("成功", "记录已成功保存！")
                self._clear_form()
                # 只有在已应用筛选的情况下才静默刷新表格
                if self.current_filter_applied:
                    self._apply_filter(show_message=False)  # 静默刷新
            else:
                messagebox.showerror("错误", "保存记录时发生错误")

        except Exception as e:
            messagebox.showerror("错误", f"提交记录时发生错误: {str(e)}")
            logging.error(f"提交记录时发生错误: {e}")

    def _parse_float_input(self, field, field_name):
        """解析浮点数输入"""
        value_str = self.input_vars[field].get().strip()
        if not value_str:
            return None
        try:
            return float(value_str)
        except ValueError:
            messagebox.showerror("输入错误", f"{field_name}必须是有效的数字")
            raise

    def _parse_int_input(self, field, field_name):
        """解析整数输入"""
        value_str = self.input_vars[field].get().strip()
        if not value_str:
            return None
        try:
            return int(float(value_str))
        except ValueError:
            messagebox.showerror("输入错误", f"{field_name}必须是有效的整数")
            raise

    def _clear_form(self):
        """清空表单"""
        self.input_vars["date"].set_date(date.today())

        for field in ["sleep_time", "weight", "rating", "steps", "calories_intake"]:
            self.input_vars[field].delete(0, tk.END)

        self.input_vars["note"].delete("1.0", tk.END)

    def _update_table_with_records(self, records):
        """更新表格显示记录"""
        # 清空现有数据
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for record in records:
            # 格式化入睡时间显示 - 只显示时:分，固定四位数字
            sleep_time_display = ''
            if record[2]:  # sleep_time
                sleep_time_value = record[2]
                if hasattr(sleep_time_value, 'strftime'):
                    # 如果是 time 或 datetime 对象
                    sleep_time_display = sleep_time_value.strftime('%H:%M')
                elif hasattr(sleep_time_value, 'total_seconds'):
                    # 如果是 timedelta 对象，转换为时间格式
                    total_seconds = int(sleep_time_value.total_seconds())
                    hours = total_seconds // 3600
                    minutes = (total_seconds % 3600) // 60
                    sleep_time_display = f"{hours:02d}:{minutes:02d}"
                else:
                    # 如果是字符串，尝试解析并格式化
                    try:
                        if ':' in str(sleep_time_value):
                            parts = str(sleep_time_value).split(':')
                            hours = int(parts[0])
                            minutes = int(parts[1])
                            sleep_time_display = f"{hours:02d}:{minutes:02d}"
                        else:
                            sleep_time_display = str(sleep_time_value)
                    except:
                        sleep_time_display = str(sleep_time_value)

            # 格式化显示数据
            display_record = [
                record[0],  # ID
                record[1].strftime('%m-%d') if record[1] else '',  # date
                sleep_time_display,  # sleep_time - 使用格式化后的时间
                f"{record[3]:.1f}" if record[3] else '',  # weight
                record[4] if record[4] else '',  # rating
                record[5] if record[5] else '',  # steps
                record[6] if record[6] else '',  # calories_intake
                record[7][:50] + "..." if record[7] and len(record[7]) > 50 else (record[7] or '')  # note
            ]
            
            self.tree.insert("", tk.END, values=display_record)
    
    def _on_item_double_click(self, event):
        """处理表格项双击事件"""
        selection = self.tree.selection()
        if selection:
            self._edit_record()
    
    def _import_data(self):
        """导入数据"""
        self.data_manager.import_from_csv()
        # 导入后不自动刷新表格，保持当前状态
        # 用户需要主动使用筛选功能来查看数据

    def _export_csv(self):
        """导出CSV"""
        self.data_manager.export_to_csv()
    
    def _export_json(self):
        """导出JSON"""
        self.data_manager.export_to_json()
    
    def _download_template(self):
        """下载CSV模板"""
        self.data_manager.save_template_csv()
    
    def _edit_record(self):
        """编辑记录"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("选择记录", "请先选择要编辑的记录")
            return
        
        item = self.tree.item(selection[0])
        record_id = item['values'][0]
        
        # 这里应该打开编辑对话框，为简化暂时显示消息
        messagebox.showinfo("编辑记录", f"编辑记录功能开发中... 记录ID: {record_id}")
    
    def _delete_record(self):
        """删除记录"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("选择记录", "请先选择要编辑的记录")
            return
        
        item = self.tree.item(selection[0])
        record_id = item['values'][0]
        
        if messagebox.askyesno("确认删除", f"确定要删除记录 ID {record_id} 吗？"):
            if self.db_manager.delete_record(record_id):
                messagebox.showinfo("删除成功", "记录已成功删除")
                # 删除后不自动刷新表格，保持当前筛选状态
                # 如果当前已应用筛选，则静默重新应用筛选以更新显示
                if self.current_filter_applied:
                    self._apply_filter(show_message=False)  # 静默刷新
            else:
                messagebox.showerror("删除失败", "删除记录时发生错误")
    
    def _show_help(self):
        """显示使用说明"""
        help_text = """
日常数据跟踪器 使用说明

1. 数据录入：
   - 选择日期（默认为今天）
   - 输入入睡时间（格式：HH:MM，如 23:30）
   - 输入体重（单位：千克）
   - 输入评分（1-10分）
   - 输入步数
   - 输入卡路里摄入量
   - 添加备注（可选）

2. 数据查看：
   - 在数据表格区域查看所有记录
   - 使用筛选功能查看特定时间段的数据
   - 双击记录可编辑（开发中）

3. 数据管理：
   - 文件菜单可导入/导出数据
   - 支持CSV和JSON格式
   - 可下载导入模板

4. 快捷操作：
   - 双击表格记录进行编辑
   - 使用菜单进行数据管理
        """
        
        help_window = tk.Toplevel(self.root)
        help_window.title("使用说明")
        help_window.geometry("500x400")
        
        text_widget = tk.Text(help_window, wrap=tk.WORD, padx=10, pady=10)
        text_widget.pack(fill=tk.BOTH, expand=True)
        text_widget.insert(tk.END, help_text)
        text_widget.config(state=tk.DISABLED)
    
    def _show_data_format(self):
        """显示数据格式说明"""
        format_text = """
数据格式说明

CSV导入模板格式：
- 文件编码：UTF-8
- 分隔符：逗号
- 标题行：D,S,W,R,P,C,N

字段说明：
• D (Date) - 日期：YYYY-MM-DD格式 (如：2024-01-01)
• S (Sleep) - 入睡时间：HH:MM格式 (如：23:30)
• W (Weight) - 体重：数字，单位千克 (如：65.5)
• R (Rating) - 评分：1-10整数 (如：8)
• P (stePs) - 步数：整数 (如：8000)
• C (Calories) - 卡路里摄入：整数 (如：2000)
• N (Note) - 备注：文本内容

示例数据：
D,S,W,R,P,C,N
2024-01-01,23:30,65.5,8,8000,2000,今天感觉不错
2024-01-02,,66.0,7,7500,1800,体重有所增加

注意事项：
- 除日期外，所有字段都可以为空
- 空值直接留空即可，不要填写NULL
- 相同日期的记录会被更新覆盖
- 导入时会跳过格式错误的行
        """
        
        format_window = tk.Toplevel(self.root)
        format_window.title("数据格式说明")
        format_window.geometry("500x450")

        text_widget = tk.Text(format_window, wrap=tk.WORD, padx=10, pady=10)
        text_widget.pack(fill=tk.BOTH, expand=True)
        text_widget.insert(tk.END, format_text)
        text_widget.config(state=tk.DISABLED)
    
    def _show_about(self):
        """显示关于信息"""
        about_text = """
日常数据跟踪器 v1.0

一个轻量级的个人数据跟踪应用程序

功能特点：
• 记录每日睡眠、体重、评分等数据
• 数据筛选和表格展示
• 数据导入导出功能
• 简洁直观的用户界面

技术栈：
• Python + Tkinter
• MySQL 数据库

开发日期：2024年
        """

        messagebox.showinfo("关于", about_text)

    def run(self):
        """运行应用程序"""
        self.root.mainloop()

if __name__ == "__main__":
    app = DailyTrackerApp()
    app.root.mainloop()
