import csv
import json
from datetime import datetime, date
import tkinter as tk
import tkinter.filedialog as filedialog
import tkinter.messagebox as messagebox
from tkinter import ttk
import logging

class DataManager:
    def __init__(self, database_manager):
        self.db_manager = database_manager

    def export_to_csv(self, filename=None):
        """导出数据到CSV文件（带选择模式对话框）"""
        # 显示导出模式选择对话框
        export_mode = self._show_export_mode_dialog()
        if not export_mode:
            return False

        # 根据模式获取数据
        if export_mode == "all":
            records = self.db_manager.get_all_records('ASC')  # 确保正序排列
            default_filename = f"daily_tracker_all_{datetime.now().strftime('%Y%m%d')}.csv"
        elif export_mode == "year":
            year = self._show_year_selection_dialog()
            if not year:
                return False
            records = self._get_records_by_year(year)
            default_filename = f"daily_tracker_{year}.csv"
        elif export_mode == "range":
            date_range = self._show_date_range_dialog()
            if not date_range:
                return False
            start_date, end_date = date_range
            records = self.db_manager.get_records_by_date_range(start_date, end_date)
            default_filename = f"daily_tracker_{start_date}_{end_date}.csv"
        else:
            return False

        if not records:
            messagebox.showinfo("提示", "没有找到符合条件的数据")
            return False

        # 选择保存文件
        if not filename:
            filename = filedialog.asksaveasfilename(
                initialname=default_filename,
                defaultextension=".csv",
                filetypes=[("CSV文件", "*.csv"), ("所有文件", "*.*")],
                title="导出数据到CSV"
            )

        if not filename:
            return False

        try:
            with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.writer(csvfile)

                # 写入标题行
                headers = ['ID', '日期', '入睡时间', '体重(kg)', '评分', '步数', '卡路里摄入', '备注', '创建时间', '更新时间']
                writer.writerow(headers)

                # 写入数据行
                for record in records:
                    # 格式化数据
                    formatted_record = [
                        record[0],  # id
                        record[1].strftime('%Y-%m-%d') if record[1] else '',  # date
                        str(record[2]) if record[2] else '',  # sleep_time
                        record[3] if record[3] else '',  # weight
                        record[4] if record[4] else '',  # rating
                        record[5] if record[5] else '',  # steps
                        record[6] if record[6] else '',  # calories_intake
                        record[7] if record[7] else '',  # note
                        record[8].strftime('%Y-%m-%d %H:%M:%S') if record[8] else '',  # created_at
                        record[9].strftime('%Y-%m-%d %H:%M:%S') if record[9] else ''   # updated_at
                    ]
                    writer.writerow(formatted_record)

            messagebox.showinfo("导出成功", f"共导出 {len(records)} 条记录到: {filename}")
            return True

        except Exception as e:
            messagebox.showerror("导出失败", f"导出数据时发生错误: {str(e)}")
            logging.error(f"导出CSV时发生错误: {e}")
            return False

    def _show_export_mode_dialog(self):
        """显示导出模式选择对话框"""
        dialog = tk.Toplevel()
        dialog.title("选择导出模式")
        dialog.geometry("300x200")
        dialog.resizable(False, False)
        dialog.transient()
        dialog.grab_set()

        # 居中显示
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")

        result = None

        def on_selection(mode):
            nonlocal result
            result = mode
            dialog.destroy()

        # 标题
        title_label = ttk.Label(dialog, text="请选择导出模式", font=("Arial", 12, "bold"))
        title_label.pack(pady=20)

        # 按钮框架
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)

        # 导出模式按钮
        ttk.Button(button_frame, text="全量导出", width=15,
                  command=lambda: on_selection("all")).pack(pady=5)

        ttk.Button(button_frame, text="按年份导出", width=15,
                  command=lambda: on_selection("year")).pack(pady=5)

        ttk.Button(button_frame, text="按日期范围导出", width=15,
                  command=lambda: on_selection("range")).pack(pady=5)

        ttk.Button(button_frame, text="取消", width=15,
                  command=dialog.destroy).pack(pady=5)

        dialog.wait_window()
        return result

    def _show_year_selection_dialog(self):
        """显示年份选择对话框"""
        dialog = tk.Toplevel()
        dialog.title("选择年份")
        dialog.geometry("250x150")
        dialog.resizable(False, False)
        dialog.transient()
        dialog.grab_set()

        # 居中显示
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")

        result = None

        def on_confirm():
            nonlocal result
            try:
                result = int(year_var.get())
                dialog.destroy()
            except ValueError:
                messagebox.showerror("错误", "请输入有效的年份")

        # 标题
        ttk.Label(dialog, text="请选择要导出的年份:", font=("Arial", 10)).pack(pady=20)

        # 年份选择
        year_frame = ttk.Frame(dialog)
        year_frame.pack(pady=10)

        year_var = tk.StringVar(value=str(datetime.now().year))
        year_spinbox = ttk.Spinbox(year_frame, from_=2020, to=2030, width=10, textvariable=year_var)
        year_spinbox.pack()

        # 按钮
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="确定", command=on_confirm).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT, padx=5)

        dialog.wait_window()
        return result

    def _show_date_range_dialog(self):
        """显示日期范围选择对话框"""
        dialog = tk.Toplevel()
        dialog.title("选择日期范围")
        dialog.geometry("400x200")
        dialog.resizable(False, False)
        dialog.transient()
        dialog.grab_set()

        # 居中显示
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")

        result = None

        def on_confirm():
            nonlocal result
            try:
                start_date = datetime.strptime(start_var.get(), '%Y-%m-%d').date()
                end_date = datetime.strptime(end_var.get(), '%Y-%m-%d').date()

                if start_date > end_date:
                    messagebox.showerror("错误", "开始日期不能晚于结束日期")
                    return

                result = (start_date, end_date)
                dialog.destroy()
            except ValueError:
                messagebox.showerror("错误", "请输入有效的日期格式 (YYYY-MM-DD)")

        # 标题
        ttk.Label(dialog, text="请选择日期范围:", font=("Arial", 10, "bold")).pack(pady=10)

        # 日期选择框架
        date_frame = ttk.Frame(dialog)
        date_frame.pack(pady=20)

        # 开始日期
        ttk.Label(date_frame, text="开始日期:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        start_var = tk.StringVar(value="2025-01-01")
        start_entry = ttk.Entry(date_frame, textvariable=start_var, width=15)
        start_entry.grid(row=0, column=1, padx=5, pady=5)

        # 结束日期
        ttk.Label(date_frame, text="结束日期:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        end_var = tk.StringVar(value=datetime.now().strftime('%Y-%m-%d'))
        end_entry = ttk.Entry(date_frame, textvariable=end_var, width=15)
        end_entry.grid(row=1, column=1, padx=5, pady=5)

        # 格式说明
        ttk.Label(date_frame, text="格式: YYYY-MM-DD", font=("Arial", 8), foreground="gray").grid(row=2, column=0, columnspan=2, pady=5)

        # 按钮
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=20)

        ttk.Button(button_frame, text="确定", command=on_confirm).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT, padx=5)

        dialog.wait_window()
        return result

    def _get_records_by_year(self, year):
        """根据年份获取记录"""
        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)
        return self.db_manager.get_records_by_date_range(start_date, end_date)

    def export_to_json(self, filename=None):
        """导出数据到JSON文件（带选择模式）"""
        # 复用CSV的模式选择逻辑
        export_mode = self._show_export_mode_dialog()
        if not export_mode:
            return False

        # 根据模式获取数据
        if export_mode == "all":
            records = self.db_manager.get_all_records('ASC')
            default_filename = f"daily_tracker_all_{datetime.now().strftime('%Y%m%d')}.json"
        elif export_mode == "year":
            year = self._show_year_selection_dialog()
            if not year:
                return False
            records = self._get_records_by_year(year)
            default_filename = f"daily_tracker_{year}.json"
        elif export_mode == "range":
            date_range = self._show_date_range_dialog()
            if not date_range:
                return False
            start_date, end_date = date_range
            records = self.db_manager.get_records_by_date_range(start_date, end_date)
            default_filename = f"daily_tracker_{start_date}_{end_date}.json"
        else:
            return False

        if not records:
            messagebox.showinfo("提示", "没有找到符合条件的数据")
            return False

        if not filename:
            filename = filedialog.asksaveasfilename(
                initialname=default_filename,
                defaultextension=".json",
                filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")],
                title="导出数据到JSON"
            )

        if not filename:
            return False

        try:
            # 转换数据格式
            data = []
            for record in records:
                record_dict = {
                    'id': record[0],
                    'date': record[1].strftime('%Y-%m-%d') if record[1] else None,
                    'sleep_time': str(record[2]) if record[2] else None,
                    'weight': float(record[3]) if record[3] else None,
                    'rating': record[4] if record[4] else None,
                    'steps': record[5] if record[5] else None,
                    'calories_intake': record[6] if record[6] else None,
                    'note': record[7] if record[7] else None,
                    'created_at': record[8].strftime('%Y-%m-%d %H:%M:%S') if record[8] else None,
                    'updated_at': record[9].strftime('%Y-%m-%d %H:%M:%S') if record[9] else None
                }
                data.append(record_dict)

            with open(filename, 'w', encoding='utf-8') as jsonfile:
                json.dump(data, jsonfile, ensure_ascii=False, indent=2)

            messagebox.showinfo("导出成功", f"共导出 {len(records)} 条记录到: {filename}")
            return True

        except Exception as e:
            messagebox.showerror("导出失败", f"导出数据时发生错误: {str(e)}")
            logging.error(f"导出JSON时发生错误: {e}")
            return False

    def _parse_float(self, value):
        """安全解析浮点数"""
        try:
            return float(value.strip()) if value.strip() else None
        except:
            return None

    def _parse_int(self, value):
        """安全解析整数"""
        try:
            return int(float(value.strip())) if value.strip() else None
        except:
            return None

    def get_template_csv_content(self):
        """获取CSV模板内容"""
        return """D,S,W,R,P,C,N
2024-01-01,23:30,65.5,8,8000,2000,今天感觉不错
2024-01-02,,66.0,7,7500,1800,体重有所增加
2024-01-03,22:45,64.8,9,9000,1900,早睡早起身体好"""

    def save_template_csv(self):
        """保存CSV导入模板"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV文件", "*.csv")],
            title="保存CSV导入模板",
            initialfile="导入模板.csv"
        )

        if filename:
            try:
                with open(filename, 'w', encoding='utf-8-sig') as f:
                    f.write(self.get_template_csv_content())
                messagebox.showinfo("保存成功", f"CSV导入模板已保存到: {filename}")
                return True
            except Exception as e:
                messagebox.showerror("保存失败", f"保存模板时发生错误: {str(e)}")
                return False
        return False

    def import_from_csv(self, filename=None):
        """从CSV文件导入数据"""
        if not filename:
            filename = filedialog.askopenfilename(
                filetypes=[("CSV文件", "*.csv"), ("所有文件", "*.*")],
                title="从CSV导入数据"
            )

        if not filename:
            return False

        try:
            success_count = 0
            error_count = 0

            with open(filename, 'r', encoding='utf-8-sig') as csvfile:
                # 检测CSV格式 - 支持两种格式
                first_line = csvfile.readline().strip()
                csvfile.seek(0)  # 重置文件指针

                # 判断是否为标准导入模板格式 (D,S,W,R,P,C,N)
                if first_line.startswith('D,S,W,R,P,C,N') or 'D,S,W,R,P,C,N' in first_line:
                    # 标准导入模板格式
                    reader = csv.DictReader(csvfile)
                    for row in reader:
                        try:
                            # 解析日期
                            date_str = row.get('D', '').strip()
                            if not date_str:
                                continue

                            date = datetime.strptime(date_str, '%Y-%m-%d').date()

                            # 解析入睡时间
                            sleep_time = None
                            sleep_time_str = row.get('S', '').strip()
                            if sleep_time_str:
                                try:
                                    sleep_time = datetime.strptime(sleep_time_str, '%H:%M:%S').time()
                                except:
                                    try:
                                        sleep_time = datetime.strptime(sleep_time_str, '%H:%M').time()
                                    except:
                                        pass

                            # 解析其他字段
                            weight = self._parse_float(row.get('W', ''))
                            rating = self._parse_int(row.get('R', ''))
                            steps = self._parse_int(row.get('P', ''))
                            calories_intake = self._parse_int(row.get('C', ''))
                            note = row.get('N', '').strip() or None

                            # 插入数据
                            if self.db_manager.insert_record(
                                date=date,
                                sleep_time=sleep_time,
                                weight=weight,
                                rating=rating,
                                steps=steps,
                                calories_intake=calories_intake,
                                note=note
                            ):
                                success_count += 1
                            else:
                                error_count += 1

                        except Exception as e:
                            error_count += 1
                            logging.error(f"导入行数据时发生错误: {e}")

                else:
                    # 完整导出格式 (包含ID、创建时间等字段)
                    reader = csv.DictReader(csvfile)
                    for row in reader:
                        try:
                            # 解析日期
                            date_str = row.get('日期', '').strip()
                            if not date_str:
                                continue

                            date = datetime.strptime(date_str, '%Y-%m-%d').date()

                            # 解析入睡时间
                            sleep_time = None
                            sleep_time_str = row.get('入睡时间', '').strip()
                            if sleep_time_str:
                                try:
                                    sleep_time = datetime.strptime(sleep_time_str, '%H:%M:%S').time()
                                except:
                                    try:
                                        sleep_time = datetime.strptime(sleep_time_str, '%H:%M').time()
                                    except:
                                        pass

                            # 解析其他字段
                            weight = self._parse_float(row.get('体重(kg)', ''))
                            rating = self._parse_int(row.get('评分', ''))
                            steps = self._parse_int(row.get('步数', ''))
                            calories_intake = self._parse_int(row.get('卡路里摄入', ''))
                            note = row.get('备注', '').strip() or None

                            # 插入数据
                            if self.db_manager.insert_record(
                                date=date,
                                sleep_time=sleep_time,
                                weight=weight,
                                rating=rating,
                                steps=steps,
                                calories_intake=calories_intake,
                                note=note
                            ):
                                success_count += 1
                            else:
                                error_count += 1

                        except Exception as e:
                            error_count += 1
                            logging.error(f"导入行数据时发生错误: {e}")

            message = f"导入完成！成功: {success_count} 条，失败: {error_count} 条"
            if error_count > 0:
                messagebox.showwarning("导入完成", message)
            else:
                messagebox.showinfo("导入成功", message)

            return success_count > 0

        except Exception as e:
            messagebox.showerror("导入失败", f"导入数据时发生错误: {str(e)}")
            logging.error(f"导入CSV时发生错误: {e}")
            return False
