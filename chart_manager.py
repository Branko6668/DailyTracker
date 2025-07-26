import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import tkinter as tk

class ChartManager:
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.figure = None
        self.canvas = None

        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
        plt.rcParams['axes.unicode_minus'] = False

    def create_line_chart(self, data, column_name, title=None):
        """创建折线图"""
        if not data:
            self._show_no_data_message()
            return

        # 清除之前的图表
        if self.canvas:
            self.canvas.get_tk_widget().destroy()

        # 创建新的图表
        self.figure = plt.Figure(figsize=(10, 6), dpi=100)
        ax = self.figure.add_subplot(111)

        # 提取日期和数值
        dates = [row[0] for row in data]
        values = [row[1] for row in data if row[1] is not None]
        dates = [dates[i] for i, row in enumerate(data) if row[1] is not None]

        if not values:
            self._show_no_data_message()
            return

        # 绘制折线图
        ax.plot(dates, values, marker='o', linewidth=2, markersize=6)

        # 设置标题和标签
        chart_titles = {
            'weight': '体重变化趋势',
            'rating': '评分变化趋势',
            'sleep_time': '入睡时间变化趋势',
            'steps': '步数变化趋势',
            'calories_intake': '卡路里摄入变化趋势'
        }

        chart_title = title or chart_titles.get(column_name, f'{column_name}变化趋势')
        ax.set_title(chart_title, fontsize=14, fontweight='bold')
        ax.set_xlabel('日期', fontsize=12)

        # 设置Y轴标签
        y_labels = {
            'weight': '体重 (kg)',
            'rating': '评分',
            'sleep_time': '入睡时间',
            'steps': '步数',
            'calories_intake': '卡路里摄入'
        }
        ax.set_ylabel(y_labels.get(column_name, column_name), fontsize=12)

        # 智能设置横坐标刻度
        self._setup_intelligent_x_axis(ax, dates)

        # 添加网格
        ax.grid(True, alpha=0.3)

        # 调整布局
        self.figure.tight_layout()

        # 创建canvas并显示
        self.canvas = FigureCanvasTkAgg(self.figure, self.parent_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def _setup_intelligent_x_axis(self, ax, dates):
        """智能设置横坐标刻度"""
        if not dates:
            return

        # 计算日期范围
        min_date = min(dates)
        max_date = max(dates)
        date_range = (max_date - min_date).days

        if date_range <= 60:  # 两个月以内（60天）
            # 每天都显示刻度，但只显示日期标签
            ax.xaxis.set_major_locator(mdates.DayLocator())
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))

            # 设置刻度样式
            ax.tick_params(axis='x', which='major', labelsize=8)

            # 如果日期太多，适当稀疏显示标签
            if date_range > 30:
                # 每隔一天显示一个标签
                ax.xaxis.set_major_locator(mdates.DayLocator(interval=2))
            elif date_range > 14:
                # 每天显示标签，但字体更小
                ax.tick_params(axis='x', which='major', labelsize=7)

            # 旋转标签
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')

        else:  # 超过两个月
            # 每月第一天显示为大刻度，其他天显示为小刻度
            ax.xaxis.set_major_locator(mdates.MonthLocator())
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))

            # 设置次要刻度为每天
            ax.xaxis.set_minor_locator(mdates.DayLocator())

            # 设置主刻度样式（月份）
            ax.tick_params(axis='x', which='major', labelsize=10, length=8, width=2)
            # 设置次要刻度样式（每天）
            ax.tick_params(axis='x', which='minor', length=4, width=1)

            # 旋转主标签
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')

    def _show_no_data_message(self):
        """显示无数据消息"""
        if self.canvas:
            self.canvas.get_tk_widget().destroy()

        self.figure = plt.Figure(figsize=(10, 6), dpi=100)
        ax = self.figure.add_subplot(111)
        ax.text(0.5, 0.5, '暂无数据', ha='center', va='center',
                fontsize=20, transform=ax.transAxes)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')

        self.canvas = FigureCanvasTkAgg(self.figure, self.parent_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def clear_chart(self):
        """清除图表"""
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
            self.canvas = None
        if self.figure:
            plt.close(self.figure)
            self.figure = None

    def save_chart(self, filename):
        """保存图表到文件"""
        if self.figure:
            try:
                self.figure.savefig(filename, dpi=300, bbox_inches='tight')
                return True
            except Exception as e:
                print(f"保存图表时发生错误: {e}")
                return False
        return False
