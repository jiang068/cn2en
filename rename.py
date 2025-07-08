#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
音频文件重命名工具
将中文文件名转换为拼音并更新相关的rpy文件引用
"""

import os
import json
from typing import Dict, List

# 全局变量 - 从空字典开始，只包含实际扫描到的汉字
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

def normalize_filename(filename: str) -> str:
    """
    将文件名中的中文字符转换为拼音，去掉中文符号、省略号和空格
    保留文件扩展名不变
    """
    global CHINESE_TO_PINYIN
    
    # 分离文件名和扩展名
    name_part, ext_part = os.path.splitext(filename)
    
    # 定义要删除的中文符号、省略号和空格
    symbols_to_remove = {
        '，', '。', '？', '！', '：', '；', '、', '"', '"', ''', ''', 
        '【', '】', '（', '）', '〔', '〕', '《', '》', '〈', '〉',
        '…', '——', '～', '·', '＋', '－', '＝', '＜', '＞',
        '　',  # 全角空格
        '／', '＼', '｜', '＃', '＄', '％', '＆', '＊',
        '￥', '＠', '＾', '｀', '｛', '｝', '［', '］',
        ' '   # 半角空格
    }
    
    # 英文省略号
    ellipsis = {'...', '…'}
    
    result = []
    i = 0
    while i < len(name_part):
        char = name_part[i]
        
        # 检查是否是省略号（英文或中文）
        if char == '.' and i + 2 < len(name_part) and name_part[i:i+3] == '...':
            # 跳过英文省略号
            i += 3
            continue
        elif char == '…':
            # 跳过中文省略号
            i += 1
            continue
        
        # 检查是否是需要删除的符号或空格
        if char in symbols_to_remove:
            # 跳过符号和空格
            i += 1
            continue
        
        # 处理中文字符
        if '\u4e00' <= char <= '\u9fff':  # 中文字符
            pinyin = CHINESE_TO_PINYIN.get(char, char)  # 如果没有拼音，保持原字符
            result.append(pinyin)
        else:
            # 保留英文、数字和英文符号
            result.append(char)
        
        i += 1
    
    # 重新组合文件名和扩展名
    return ''.join(result) + ext_part

def extract_chinese_characters(text: str) -> set:
    """从文本中提取所有中文字符"""
    chinese_chars = set()
    for char in text:
        if '\u4e00' <= char <= '\u9fff':  # 中文字符范围
            chinese_chars.add(char)
    return chinese_chars

def generate_preview_log(target_path: str, log_file: str):
    """生成预转换日志，供用户预览"""
    global CHINESE_TO_PINYIN
    
    preview_content = []
    preview_content.append("=== 文件和文件夹重命名预览 ===\n")
    
    # 检查字典完整性
    missing_chars = []
    for root, dirs, files in os.walk(target_path):
        # 检查文件夹名中的中文字符
        for dir_name in dirs:
            chinese_chars = extract_chinese_characters(dir_name)
            for char in chinese_chars:
                if char not in CHINESE_TO_PINYIN:
                    missing_chars.append(char)
        
        # 检查文件名中的中文字符
        for file in files:
            chinese_chars = extract_chinese_characters(file)
            for char in chinese_chars:
                if char not in CHINESE_TO_PINYIN:
                    missing_chars.append(char)
    
    if missing_chars:
        preview_content.append(f"警告：字典中缺少以下字符的拼音：{', '.join(set(missing_chars))}\n")
        preview_content.append("请先完善字典后再进行转换！\n\n")
    
    # 构建完整的重命名映射
    def normalize_path(path: str) -> str:
        """标准化路径中的所有组件"""
        parts = path.split(os.sep)
        normalized_parts = []
        for part in parts:
            if part:  # 跳过空字符串
                normalized_parts.append(normalize_filename(part))
        return os.sep.join(normalized_parts)
    
    # 收集所有需要重命名的项目
    folder_renames = []
    file_renames = []
    
    # 扫描要重命名的文件夹
    for root, dirs, files in os.walk(target_path):
        for dir_name in dirs:
            # 构建完整的文件夹路径
            full_dir_path = os.path.join(root, dir_name)
            relative_path = os.path.relpath(full_dir_path, target_path)
            
            # 检查相对路径中是否包含中文字符
            chinese_chars = extract_chinese_characters(relative_path)
            if chinese_chars:
                # 计算标准化后的相对路径
                new_relative_path = normalize_path(relative_path)
                if relative_path != new_relative_path:
                    folder_renames.append((relative_path, new_relative_path))
    
    # 扫描要重命名的文件
    for root, dirs, files in os.walk(target_path):
        for file in files:
            # 构建完整的文件路径
            full_file_path = os.path.join(root, file)
            relative_path = os.path.relpath(full_file_path, target_path)
            
            # 检查相对路径中是否包含中文字符（包括目录和文件名）
            chinese_chars = extract_chinese_characters(relative_path)
            if chinese_chars:
                # 计算标准化后的相对路径
                new_relative_path = normalize_path(relative_path)
                if relative_path != new_relative_path:
                    file_renames.append((relative_path, new_relative_path))
    
    # 输出文件夹重命名预览
    for old_path, new_path in folder_renames:
        preview_content.append(f"文件夹: {old_path} -> {new_path}\n")
    
    # 输出文件重命名预览
    for old_path, new_path in file_renames:
        preview_content.append(f"文件: {old_path} -> {new_path}\n")
    
    folder_rename_count = len(folder_renames)
    file_rename_count = len(file_renames)
    
    preview_content.append(f"\n总计需要重命名的文件夹: {folder_rename_count}\n")
    preview_content.append(f"总计需要重命名的文件: {file_rename_count}\n")
    
    # 保存预览日志
    try:
        with open(log_file, 'w', encoding='utf-8') as f:
            f.writelines(preview_content)
        print(f"预览日志已保存到: {log_file}")
        print(f"发现 {folder_rename_count} 个需要重命名的文件夹")
        print(f"发现 {file_rename_count} 个需要重命名的文件")
        return (folder_rename_count > 0 or file_rename_count > 0), len(missing_chars) == 0
    except Exception as e:
        print(f"保存预览日志失败: {e}")
        return False, False

def rename_files(target_path: str):
    """实际执行文件和文件夹重命名"""
    global CHINESE_TO_PINYIN
    
    renamed_folders = 0
    renamed_files = 0
    
    # 先收集所有需要重命名的文件夹，按深度排序（深度大的先处理）
    folders_to_rename = []
    for root, dirs, files in os.walk(target_path):
        for dir_name in dirs:
            chinese_chars = extract_chinese_characters(dir_name)
            if chinese_chars:
                old_dir_path = os.path.join(root, dir_name)
                new_dir_name = normalize_filename(dir_name)
                new_dir_path = os.path.join(root, new_dir_name)
                
                if old_dir_path != new_dir_path:
                    # 计算深度（路径分隔符的数量）
                    depth = old_dir_path.count(os.sep)
                    folders_to_rename.append((depth, old_dir_path, new_dir_path, dir_name, new_dir_name))
    
    # 按深度降序排序，先处理深层文件夹
    folders_to_rename.sort(reverse=True)
    
    # 重命名文件夹
    for depth, old_dir_path, new_dir_path, old_name, new_name in folders_to_rename:
        try:
            os.rename(old_dir_path, new_dir_path)
            print(f"已重命名文件夹: {old_name} -> {new_name}")
            renamed_folders += 1
        except Exception as e:
            print(f"重命名文件夹失败: {old_name} -> {new_name}, 错误: {e}")
    
    # 重命名文件（需要重新遍历，因为文件夹路径可能已经改变）
    for root, dirs, files in os.walk(target_path):
        for file in files:
            chinese_chars = extract_chinese_characters(file)
            if chinese_chars:
                old_path = os.path.join(root, file)
                new_name = normalize_filename(file)
                new_path = os.path.join(root, new_name)
                
                if old_path != new_path:
                    try:
                        os.rename(old_path, new_path)
                        print(f"已重命名文件: {file} -> {new_name}")
                        renamed_files += 1
                    except Exception as e:
                        print(f"重命名文件失败: {file} -> {new_name}, 错误: {e}")
    
    print(f"\n总计重命名了 {renamed_folders} 个文件夹")
    print(f"总计重命名了 {renamed_files} 个文件")
    return renamed_folders + renamed_files

def main():
    """主函数"""
    print("=== 音频文件重命名工具 ===")
    
    # 1. 获取目标文件夹路径
    target_path = input("请输入目标文件夹路径: ").strip().strip('"')
    
    if not os.path.exists(target_path):
        print(f"错误：路径不存在: {target_path}")
        return
    
    # 字典文件和日志文件路径
    dict_file = "chinese_dictionary.json"
    log_file = "rename_log.txt"
    
    # 2. 加载字典
    load_dictionary(dict_file)
    
    if not CHINESE_TO_PINYIN:
        print("错误：字典文件为空或不存在，请先准备好字典文件")
        return
    
    # 3. 生成预转换日志
    print("\n=== 生成预转换日志 ===")
    has_files, dict_complete = generate_preview_log(target_path, log_file)
    
    if not has_files:
        print("没有需要重命名的文件和文件夹")
        return
    
    if not dict_complete:
        print("字典不完整，请先完善字典文件")
        return
    
    # 4. 用户确认是否继续
    print(f"\n请查看预转换日志: {log_file}")
    choice = input("是否继续进行文件和文件夹重命名？(y/n): ").strip().lower()
    if choice != 'y':
        print("操作已取消")
        return
    
    # 5. 执行文件重命名
    print("\n=== 执行文件和文件夹重命名 ===")
    renamed_count = rename_files(target_path)
    
    if renamed_count == 0:
        print("没有文件或文件夹被重命名")
    else:
        print(f"重命名完成！如需修复RPY文件，请运行 python fix_rpy.py")
    
    print("\n=== 操作完成 ===")

if __name__ == "__main__":
    main()
