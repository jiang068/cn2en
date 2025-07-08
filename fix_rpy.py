#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RPY文件修复工具
根据字典将RPY文件中的中文文件引用转换为拼音
"""

import os
import json
from typing import Dict, List

# 全局变量
CHINESE_TO_PINYIN = {}

def load_dictionary(dict_file: str) -> Dict[str, str]:
    """从JSON文件加载字典"""
    global CHINESE_TO_PINYIN
    if os.path.exists(dict_file):
        try:
            with open(dict_file, 'r', encoding='utf-8') as f:
                CHINESE_TO_PINYIN = json.load(f)
                print(f"已加载字典文件: {dict_file}")
                print(f"字典中包含 {len(CHINESE_TO_PINYIN)} 个字符")
                return CHINESE_TO_PINYIN
        except Exception as e:
            print(f"加载字典文件失败: {e}")
            CHINESE_TO_PINYIN = {}
    else:
        print(f"字典文件不存在: {dict_file}")
        CHINESE_TO_PINYIN = {}
    return CHINESE_TO_PINYIN

def extract_chinese_characters(text: str) -> set:
    """从文本中提取所有中文字符"""
    chinese_chars = set()
    for char in text:
        if '\u4e00' <= char <= '\u9fff':  # 中文字符范围
            chinese_chars.add(char)
    return chinese_chars

def load_rename_mapping_from_log(log_file: str) -> Dict[str, str]:
    """从重命名日志文件中加载文件重命名映射"""
    mapping = {}
    
    if not os.path.exists(log_file):
        print(f"重命名日志文件不存在: {log_file}")
        return mapping
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith('文件: ') and ' -> ' in line:
                    # 解析 "文件: old_name -> new_name" 格式
                    parts = line[4:].split(' -> ')  # 去掉 "文件: " 前缀
                    if len(parts) == 2:
                        old_name = parts[0].strip()
                        new_name = parts[1].strip()
                        mapping[old_name] = new_name
        
        print(f"从日志文件加载了 {len(mapping)} 个重命名映射")
        return mapping
    except Exception as e:
        print(f"读取重命名日志文件失败: {e}")
        return mapping

def normalize_text(text: str) -> str:
    """
    已弃用：现在使用重命名日志文件中的映射关系
    """
    return text

def scan_rpy_files(rpy_path: str, rename_mapping: Dict[str, str]) -> Dict[str, List[str]]:
    """扫描RPY文件，找出需要更新的文件引用"""
    rpy_updates = {}
    
    if not os.path.exists(rpy_path):
        print(f"RPY路径不存在: {rpy_path}")
        return rpy_updates
    
    for root, dirs, files in os.walk(rpy_path):
        for file in files:
            if file.endswith('.rpy'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                    
                    updates = []
                    for line_num, line in enumerate(lines, 1):
                        # 直接在每一行中查找需要替换的文件名
                        updated_line = line
                        line_changed = False
                        
                        for old_filename, new_filename in rename_mapping.items():
                            if old_filename in line:
                                updated_line = updated_line.replace(old_filename, new_filename)
                                line_changed = True
                        
                        if line_changed:
                            updates.append({
                                'line_num': line_num,
                                'old_line': line.strip(),
                                'new_line': updated_line.strip()
                            })
                    
                    if updates:
                        rpy_updates[file_path] = updates
                        
                except Exception as e:
                    print(f"读取文件失败: {file_path}, 错误: {e}")
    
    return rpy_updates

def generate_rpy_mapping(rpy_path: str, mapping_file: str, log_file: str):
    """生成RPY文件更新映射"""
    # 从重命名日志文件加载映射
    rename_mapping = load_rename_mapping_from_log(log_file)
    
    if not rename_mapping:
        print("没有找到文件重命名映射")
        return False
    
    rpy_updates = scan_rpy_files(rpy_path, rename_mapping)
    
    if not rpy_updates:
        print("未发现需要更新的RPY文件")
        return False
    
    # 保存映射到JSON文件
    try:
        with open(mapping_file, 'w', encoding='utf-8') as f:
            json.dump(rpy_updates, f, ensure_ascii=False, indent=2)
        print(f"RPY更新映射已保存到: {mapping_file}")
        
        # 显示统计信息
        total_files = len(rpy_updates)
        total_lines = sum(len(updates) for updates in rpy_updates.values())
        print(f"发现 {total_files} 个RPY文件需要更新，共 {total_lines} 行")
        return True
        
    except Exception as e:
        print(f"保存RPY映射失败: {e}")
        return False

def update_rpy_files(mapping_file: str):
    """根据映射文件更新RPY文件"""
    if not os.path.exists(mapping_file):
        print(f"映射文件不存在: {mapping_file}")
        return
    
    try:
        with open(mapping_file, 'r', encoding='utf-8') as f:
            rpy_updates = json.load(f)
    except Exception as e:
        print(f"读取映射文件失败: {e}")
        return
    
    updated_files = 0
    updated_lines = 0
    
    for file_path, updates in rpy_updates.items():
        try:
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # 应用更新（从后往前更新，避免行号变化）
            for update in sorted(updates, key=lambda x: x['line_num'], reverse=True):
                line_num = update['line_num'] - 1  # 转换为0基础索引
                if line_num < len(lines):
                    lines[line_num] = update['new_line'] + '\n'
                    updated_lines += 1
            
            # 写回文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            
            print(f"已更新RPY文件: {file_path}")
            updated_files += 1
            
        except Exception as e:
            print(f"更新RPY文件失败 {file_path}: {e}")
    
    print(f"\n总计更新了 {updated_files} 个RPY文件，{updated_lines} 行")

def main():
    """主函数"""
    print("=== RPY文件修复工具 ===")
    
    # 字典文件、映射文件和日志文件路径
    dict_file = "chinese_dictionary.json"
    mapping_file = "rename_mapping.json"
    log_file = "rename_log.txt"
    
    # 1. 加载字典
    load_dictionary(dict_file)
    
    if not CHINESE_TO_PINYIN:
        print("错误：字典文件为空或不存在，请先准备好字典文件")
        return
    
    # 2. 获取RPY文件目录
    rpy_path = input("请输入包含RPY文件的目录路径: ").strip().strip('"')
    
    if not os.path.exists(rpy_path):
        print(f"错误：RPY路径不存在: {rpy_path}")
        return
    
    # 3. 生成RPY更新映射
    print("\n=== 生成RPY更新映射 ===")
    if not generate_rpy_mapping(rpy_path, mapping_file, log_file):
        print("没有需要更新的RPY文件")
        return
    
    # 4. 用户确认是否继续更新RPY文件
    print(f"\n请查看RPY更新映射: {mapping_file}")
    choice = input("是否继续更新RPY文件？(y/n): ").strip().lower()
    if choice != 'y':
        print("操作已取消")
        return
    
    # 5. 更新RPY文件
    print("\n=== 更新RPY文件 ===")
    update_rpy_files(mapping_file)
    
    print("\n=== 所有操作完成 ===")

if __name__ == "__main__":
    main()
