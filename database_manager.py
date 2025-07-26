import mysql.connector
from mysql.connector import Error
from datetime import datetime
import logging

class DatabaseManager:
    def __init__(self, host='127.0.0.1', database='daily_tracker', user='root', password='200249'):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.connection = None
        self._create_database_if_not_exists()
        self._create_table_if_not_exists()

    def _create_database_if_not_exists(self):
        """创建数据库（如果不存在）"""
        try:
            # 连接到MySQL服务器（不指定数据库）
            temp_connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password
            )
            cursor = temp_connection.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")
            temp_connection.commit()
            cursor.close()
            temp_connection.close()
        except Error as e:
            logging.error(f"创建数据库时发生错误: {e}")

    def connect(self):
        """连接到数据库"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password
            )
            return True
        except Error as e:
            logging.error(f"数据库连接错误: {e}")
            return False

    def disconnect(self):
        """断开数据库连接"""
        if self.connection and self.connection.is_connected():
            self.connection.close()

    def _create_table_if_not_exists(self):
        """创建数据表（如果不存在）"""
        if not self.connect():
            return False

        try:
            cursor = self.connection.cursor()
            create_table_query = """
            CREATE TABLE IF NOT EXISTS daily_records (
                id INT AUTO_INCREMENT PRIMARY KEY,
                date DATE NOT NULL UNIQUE,
                sleep_time TIME,
                weight DECIMAL(5,2),
                rating INT,
                steps INT,
                calories_intake INT,
                note TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
            """
            cursor.execute(create_table_query)
            self.connection.commit()
            cursor.close()
            return True
        except Error as e:
            logging.error(f"创建表时发生错误: {e}")
            return False
        finally:
            self.disconnect()

    def insert_record(self, date, sleep_time=None, weight=None, rating=None, steps=None, calories_intake=None, note=None):
        """插入新记录"""
        if not self.connect():
            return False

        try:
            cursor = self.connection.cursor()
            query = """
            INSERT INTO daily_records (date, sleep_time, weight, rating, steps, calories_intake, note)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            sleep_time = VALUES(sleep_time),
            weight = VALUES(weight),
            rating = VALUES(rating),
            steps = VALUES(steps),
            calories_intake = VALUES(calories_intake),
            note = VALUES(note)
            """
            cursor.execute(query, (date, sleep_time, weight, rating, steps, calories_intake, note))
            self.connection.commit()
            cursor.close()
            return True
        except Error as e:
            logging.error(f"插入记录时发生错误: {e}")
            return False
        finally:
            self.disconnect()

    def get_all_records(self, order='ASC'):
        """获取所有记录

        Args:
            order (str): 排序方式 'ASC'(正序) 或 'DESC'(倒序)
        """
        if not self.connect():
            return []

        try:
            cursor = self.connection.cursor()
            # 修改为默认按日期正序排列，这样历史数据会按时间线显示
            order_clause = "ASC" if order.upper() == "ASC" else "DESC"
            cursor.execute(f"SELECT * FROM daily_records ORDER BY date {order_clause}")
            records = cursor.fetchall()
            cursor.close()
            return records
        except Error as e:
            logging.error(f"获取记录时发生错误: {e}")
            return []
        finally:
            self.disconnect()

    def get_all_records_desc(self):
        """获取所有记录（按日期倒序）- 兼容性方法"""
        return self.get_all_records('DESC')

    def get_records_by_date_range(self, start_date, end_date):
        """根据日期范围获取记录"""
        if not self.connect():
            return []

        try:
            cursor = self.connection.cursor()
            query = "SELECT * FROM daily_records WHERE date BETWEEN %s AND %s ORDER BY date ASC"
            cursor.execute(query, (start_date, end_date))
            records = cursor.fetchall()
            cursor.close()
            return records
        except Error as e:
            logging.error(f"获取记录时发生错误: {e}")
            return []
        finally:
            self.disconnect()

    def update_record(self, record_id, **kwargs):
        """更新记录"""
        if not self.connect():
            return False

        try:
            cursor = self.connection.cursor()

            # 构建动态更新语句
            set_clause = []
            values = []
            for key, value in kwargs.items():
                if value is not None:
                    set_clause.append(f"{key} = %s")
                    values.append(value)

            if not set_clause:
                return False

            query = f"UPDATE daily_records SET {', '.join(set_clause)} WHERE id = %s"
            values.append(record_id)

            cursor.execute(query, values)
            self.connection.commit()
            cursor.close()
            return True
        except Error as e:
            logging.error(f"更新记录时发生错误: {e}")
            return False
        finally:
            self.disconnect()

    def delete_record(self, record_id):
        """删除记录"""
        if not self.connect():
            return False

        try:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM daily_records WHERE id = %s", (record_id,))
            self.connection.commit()
            cursor.close()
            return True
        except Error as e:
            logging.error(f"删除记录时发生错误: {e}")
            return False
        finally:
            self.disconnect()

    def get_column_data(self, column_name):
        """获取特定列的数据用于图表显示"""
        if not self.connect():
            return []

        try:
            cursor = self.connection.cursor()
            query = f"SELECT date, {column_name} FROM daily_records WHERE {column_name} IS NOT NULL ORDER BY date ASC"
            cursor.execute(query)
            records = cursor.fetchall()
            cursor.close()
            return records
        except Error as e:
            logging.error(f"获取列数据时发生错误: {e}")
            return []
        finally:
            self.disconnect()

    def get_record_by_date(self, target_date):
        """根据日期获取单条记录"""
        if not self.connect():
            return None

        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM daily_records WHERE date = %s", (target_date,))
            record = cursor.fetchone()
            cursor.close()
            return record
        except Error as e:
            logging.error(f"获取单条记录时发生错误: {e}")
            return None
        finally:
            self.disconnect()

    def get_records_by_year_month(self, year, month=None):
        """根据年份和月份获取记录"""
        if not self.connect():
            return []

        try:
            cursor = self.connection.cursor()
            if month:
                # 获取指定年月的记录
                start_date = f"{year}-{month:02d}-01"
                if month == 12:
                    end_date = f"{year + 1}-01-01"
                else:
                    end_date = f"{year}-{month + 1:02d}-01"
                query = "SELECT * FROM daily_records WHERE date >= %s AND date < %s ORDER BY date ASC"
                cursor.execute(query, (start_date, end_date))
            else:
                # 获取整年的记录
                start_date = f"{year}-01-01"
                end_date = f"{year + 1}-01-01"
                query = "SELECT * FROM daily_records WHERE date >= %s AND date < %s ORDER BY date ASC"
                cursor.execute(query, (start_date, end_date))

            records = cursor.fetchall()
            cursor.close()
            return records
        except Error as e:
            logging.error(f"获取年月记录时发生错误: {e}")
            return []
        finally:
            self.disconnect()
