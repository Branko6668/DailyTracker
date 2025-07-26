#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
睡眠数据转换脚本
将原始睡眠数据转换为标准CSV模板格式
"""

import csv
import pandas as pd
from datetime import datetime, time

def convert_sleep_time(hours_offset):
    """
    将小时偏移量转换为时间格式
    负值表示早于午夜，正值表示晚于午夜

    Args:
        hours_offset (float): 相对于午夜的小时偏移量

    Returns:
        str: HH:MM 格式的时间字符串
    """
    if hours_offset is None or hours_offset == '':
        return ''

    try:
        hours_offset = float(hours_offset)

        # 计算总分钟数（相对于午夜）
        total_minutes = round(abs(hours_offset) * 60)

        if hours_offset < 0:
            # 负值：早于午夜（如-0.5表示23:30）
            total_midnight_minutes = 24 * 60  # 一天的总分钟数
            actual_minutes = total_midnight_minutes - total_minutes
            hours = actual_minutes // 60
            minutes = actual_minutes % 60
        else:
            # 正值：晚于午夜（如0.5表示00:30）
            hours = total_minutes // 60
            minutes = total_minutes % 60

        # 格式化为HH:MM
        return f"{hours:02d}:{minutes:02d}"

    except (ValueError, TypeError):
        return ''

def convert_sleep_data():
    """
    转换睡眠数据文件
    """
    input_file = 'sleep.csv'
    output_file = 'converted_sleep_data.csv'

    try:
        # 读取原始数据
        print("正在读取原始数据...")
        df = pd.read_csv(input_file, encoding='utf-8')

        # 显示原始数据信息
        print(f"原始数据行数: {len(df)}")
        print("原始数据前5行:")
        print(df.head())

        # 创建新的DataFrame，按照标准模板格式
        converted_data = []

        for index, row in df.iterrows():
            # 处理日期 - 更新为2025年
            date_str = row['D']
            if date_str and '-' in str(date_str):
                # 添加年份
                full_date = f"2025-{date_str}"
            else:
                full_date = ''

            # 转换睡眠时间
            sleep_time = convert_sleep_time(row['S']) if pd.notna(row['S']) else ''

            # 处理体重
            weight = row['W'] if pd.notna(row['W']) else ''

            # 创建标准格式的记录
            converted_record = {
                'D': full_date,           # 日期
                'S': sleep_time,          # 入睡时间
                'W': weight,              # 体重
                'R': '',                  # 评分（空）
                'P': '',                  # 步数（空）
                'C': '',                  # 卡路里（空）
                'N': ''                   # 备注（空）
            }

            converted_data.append(converted_record)

        # 创建转换后的DataFrame
        converted_df = pd.DataFrame(converted_data)

        # 保存为CSV文件
        converted_df.to_csv(output_file, index=False, encoding='utf-8')

        print(f"\n转换完成！")
        print(f"输出文件: {output_file}")
        print(f"转换后数据行数: {len(converted_df)}")
        print("\n转换后数据前5行:")
        print(converted_df.head())

        # 显示睡眠时间转换示例
        print("\n睡眠时间转换示例:")
        for index, row in df.head().iterrows():
            if pd.notna(row['S']):
                original = row['S']
                converted = convert_sleep_time(original)
                print(f"原始: {original} -> 转换后: {converted}")

        return True

    except FileNotFoundError:
        print(f"错误: 找不到文件 {input_file}")
        return False
    except Exception as e:
        print(f"转换过程中发生错误: {e}")
        return False

def test_sleep_time_conversion():
    """
    测试睡眠时间转换函数
    """
    print("测试睡眠时间转换:")
    test_cases = [
        (-0.43, "23:26"),  # 早于午夜26分钟 (23:34)
        (-0.07, "23:56"),  # 早于午夜4分钟
        (-0.33, "23:40"),  # 早于午夜20分钟
        (-0.83, "23:10"),  # 早于午夜50分钟
        (-1.0, "23:00"),   # 早于午夜1小时
        (-0.28, "23:43"),  # 早于午夜17分钟
        (0.5, "00:30"),    # 午夜后30分钟
        (1.0, "01:00"),    # 午夜后1小时
    ]

    for offset, expected in test_cases:
        result = convert_sleep_time(offset)
        status = "✓" if result == expected else "✗"
        print(f"{status} {offset:5.2f} -> {result} (期望: {expected})")

if __name__ == "__main__":
    print("睡眠数据转换脚本")
    print("=" * 50)

    # 测试转换函数
    test_sleep_time_conversion()
    print("\n" + "=" * 50)

    # 执行数据转换
    if convert_sleep_data():
        print("\n数据转换成功完成！")
        print("生成的文件 'converted_sleep_data.csv' 可以直接导入到应用程序中。")
    else:
        print("\n数据转换失败，请检查错误信息。")
