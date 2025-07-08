#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
音频文件重命名工具
将中文文件名转换为拼音并更新相关的rpy文件引用
"""

import os
import json
import re
import shutil
from pathlib import Path
from typing import Dict, List

# 简单的中文转拼音映射（常用字）
CHINESE_TO_PINYIN = {
    '一': 'yi', '二': 'er', '三': 'san', '四': 'si', '五': 'wu', '六': 'liu', '七': 'qi', '八': 'ba', '九': 'jiu', '十': 'shi',
    '万': 'wan', '能': 'neng', '级': 'ji', '菜': 'cai', '单': 'dan', '存': 'cun', '读': 'du', '取': 'qu', '游': 'you', '戏': 'xi',
    '内': 'nei', '选': 'xuan', '项': 'xiang', '常': 'chang', '夏': 'xia', '奏': 'zou', '机': 'ji', '设': 'she', '置': 'zhi',
    '题': 'ti', '目': 'mu', '进': 'jin', '入': 'ru', '退': 'tui', '出': 'chu', '点': 'dian', '击': 'ji', '声': 'sheng',
    '效': 'xiao', '音': 'yin', '乐': 'le', '语': 'yu', '言': 'yan', '文': 'wen', '字': 'zi', '速': 'su', '度': 'du',
    '自': 'zi', '动': 'dong', '播': 'bo', '放': 'fang', '快': 'kuai', '进': 'jin', '回': 'hui', '滚': 'gun', '轮': 'lun',
    '滑': 'hua', '动': 'dong', '条': 'tiao', '全': 'quan', '屏': 'ping', '幕': 'mu', '窗': 'chuang', '口': 'kou',
    '模': 'mo', '式': 'shi', '跳': 'tiao', '过': 'guo', '未': 'wei', '读': 'du', '文': 'wen', '本': 'ben',
    '开': 'kai', '始': 'shi', '跳': 'tiao', '过': 'guo', '菜': 'cai', '单': 'dan', '已': 'yi', '读': 'du',
    '章': 'zhang', '节': 'jie', '名': 'ming', '称': 'cheng', '显': 'xian', '示': 'shi', '在': 'zai', '顶': 'ding',
    '部': 'bu', '导': 'dao', '航': 'hang', '条': 'tiao', '中': 'zhong', '显': 'xian', '示': 'shi', '章': 'zhang',
    '节': 'jie', '名': 'ming', '称': 'cheng', '强': 'qiang', '调': 'tiao', '侧': 'ce', '边': 'bian', '栏': 'lan',
    '中': 'zhong', '滚': 'gun', '动': 'dong', '条': 'tiao', '是': 'shi', '否': 'fou', '可': 'ke', '见': 'jian',
    '操': 'cao', '作': 'zuo', '系': 'xi', '统': 'tong', '鼠': 'shu', '标': 'biao', '键': 'jian', '盘': 'pan',
    '触': 'chu', '摸': 'mo', '手': 'shou', '柄': 'bing', '性': 'xing', '能': 'neng', '低': 'di', '功': 'gong',
    '耗': 'hao', '模': 'mo', '式': 'shi', '帧': 'zhen', '率': 'lv', '限': 'xian', '制': 'zhi', '垂': 'chui',
    '直': 'zhi', '同': 'tong', '步': 'bu', '渲': 'xuan', '染': 'ran', '缩': 'suo', '放': 'fang', '模': 'mo',
    '式': 'shi', '着': 'zhuo', '色': 'se', '器': 'qi', '色': 'se', '彩': 'cai', '配': 'pei', '置': 'zhi',
    '文': 'wen', '件': 'jian', '更': 'geng', '新': 'xin', '检': 'jian', '查': 'cha', '图': 'tu', '像': 'xiang',
    '质': 'zhi', '量': 'liang', '设': 'she', '置': 'zhi', '纹': 'wen', '理': 'li', '缩': 'suo', '放': 'fang',
    '方': 'fang', '式': 'shi', '双': 'shuang', '线': 'xian', '性': 'xing', '过': 'guo', '滤': 'lv', '抗': 'kang',
    '锯': 'ju', '齿': 'chi', '多': 'duo', '重': 'zhong', '采': 'cai', '样': 'yang', '缓': 'huan', '存': 'cun',
    '大': 'da', '小': 'xiao', '个': 'ge', '人': 'ren', '化': 'hua', '设': 'she', '置': 'zhi', '用': 'yong',
    '户': 'hu', '界': 'jie', '面': 'mian', '主': 'zhu', '题': 'ti', '背': 'bei', '景': 'jing', '音': 'yin',
    '量': 'liang', '控': 'kong', '制': 'zhi', '器': 'qi', '外': 'wai', '观': 'guan', '样': 'yang', '式': 'shi',
    '主': 'zhu', '音': 'yin', '量': 'liang', '音': 'yin', '乐': 'le', '音': 'yin', '量': 'liang', '音': 'yin',
    '效': 'xiao', '音': 'yin', '量': 'liang', '语': 'yu', '音': 'yin', '音': 'yin', '量': 'liang', '环': 'huan',
    '境': 'jing', '音': 'yin', '效': 'xiao', '音': 'yin', '量': 'liang', '静': 'jing', '音': 'yin', '静': 'jing',
    '音': 'yin', '时': 'shi', '测': 'ce', '试': 'shi', '音': 'yin', '频': 'pin', '设': 'she', '备': 'bei',
    '输': 'shu', '出': 'chu', '设': 'she', '备': 'bei', '合': 'he', '成': 'cheng', '器': 'qi', '混': 'hun',
    '音': 'yin', '器': 'qi', '缓': 'huan', '冲': 'chong', '区': 'qu', '大': 'da', '小': 'xiao', '采': 'cai',
    '样': 'yang', '率': 'lv', '转': 'zhuan', '换': 'huan', '质': 'zhi', '量': 'liang', '加': 'jia', '载': 'zai',
    '页': 'ye', '面': 'mian', '保': 'bao', '存': 'cun', '页': 'ye', '面': 'mian', '删': 'shan', '除': 'chu',
    '页': 'ye', '面': 'mian', '自': 'zi', '动': 'dong', '保': 'bao', '存': 'cun', '快': 'kuai', '速': 'su',
    '保': 'bao', '存': 'cun', '插': 'cha', '槽': 'cao', '数': 'shu', '量': 'liang', '缩': 'suo', '略': 'lve',
    '图': 'tu', '网': 'wang', '格': 'ge', '布': 'bu', '局': 'ju', '缩': 'suo', '略': 'lve', '图': 'tu',
    '行': 'xing', '数': 'shu', '缩': 'suo', '略': 'lve', '图': 'tu', '列': 'lie', '数': 'shu', '每': 'mei',
    '行': 'xing', '页': 'ye', '面': 'mian', '数': 'shu', '量': 'liang', '时': 'shi', '间': 'jian', '格': 'ge',
    '式': 'shi', '文': 'wen', '件': 'jian', '名': 'ming', '格': 'ge', '式': 'shi', '日': 'ri', '期': 'qi',
    '格': 'ge', '式': 'shi', '空': 'kong', '插': 'cha', '槽': 'cao', '名': 'ming', '称': 'cheng', '返': 'fan',
    '回': 'hui', '标': 'biao', '题': 'ti', '确': 'que', '定': 'ding', '是': 'shi', '取': 'qu', '消': 'xiao',
    '编': 'bian', '辑': 'ji', '重': 'zhong', '新': 'xin', '命': 'ming', '名': 'ming', '输': 'shu', '入': 'ru',
    '历': 'li', '史': 'shi', '记': 'ji', '录': 'lu', '无': 'wu', '历': 'li', '史': 'shi', '记': 'ji',
    '录': 'lu', '历': 'li', '史': 'shi', '记': 'ji', '录': 'lu', '返': 'fan', '回': 'hui', '主': 'zhu',
    '菜': 'cai', '单': 'dan', '终': 'zhong', '止': 'zhi', '重': 'zhong', '放': 'fang', '结': 'jie', '束': 'shu',
    '重': 'zhong', '放': 'fang', '主': 'zhu', '菜': 'cai', '单': 'dan', '关': 'guan', '于': 'yu', '帮': 'bang',
    '助': 'zhu', '键': 'jian', '盘': 'pan', '快': 'kuai', '捷': 'jie', '键': 'jian', '许': 'xu', '可': 'ke',
    '证': 'zheng', '更': 'geng', '新': 'xin', '历': 'li', '史': 'shi', '版': 'ban', '本': 'ben', '号': 'hao',
    
    # 添加游戏中常见的字符
    '店': 'dian', '长': 'zhang', '叔': 'shu', '母': 'mu', '父': 'fu', '哥': 'ge', '姐': 'jie', '弟': 'di', '妹': 'mei',
    '老': 'lao', '师': 'shi', '生': 'sheng', '学': 'xue', '校': 'xiao', '班': 'ban', '级': 'ji', '同': 'tong',
    '友': 'you', '朋': 'peng', '家': 'jia', '房': 'fang', '间': 'jian', '客': 'ke', '厅': 'ting', '卧': 'wo',
    '室': 'shi', '厨': 'chu', '卫': 'wei', '浴': 'yu', '阳': 'yang', '台': 'tai', '花': 'hua', '园': 'yuan',
    '树': 'shu', '草': 'cao', '花': 'hua', '鸟': 'niao', '鱼': 'yu', '虫': 'chong', '猫': 'mao', '狗': 'gou',
    '天': 'tian', '地': 'di', '山': 'shan', '水': 'shui', '火': 'huo', '风': 'feng', '雨': 'yu', '雪': 'xue',
    '云': 'yun', '星': 'xing', '月': 'yue', '阳': 'yang', '光': 'guang', '影': 'ying', '色': 'se', '白': 'bai',
    '黑': 'hei', '红': 'hong', '绿': 'lv', '蓝': 'lan', '黄': 'huang', '紫': 'zi', '粉': 'fen', '灰': 'hui',
    '春': 'chun', '夏': 'xia', '秋': 'qiu', '冬': 'dong', '早': 'zao', '晚': 'wan', '上': 'shang', '下': 'xia',
    '左': 'zuo', '右': 'you', '前': 'qian', '后': 'hou', '里': 'li', '外': 'wai', '东': 'dong', '西': 'xi',
    '南': 'nan', '北': 'bei', '中': 'zhong', '央': 'yang', '边': 'bian', '角': 'jiao', '处': 'chu', '所': 'suo',
    '年': 'nian', '月': 'yue', '日': 'ri', '时': 'shi', '分': 'fen', '秒': 'miao', '刻': 'ke', '钟': 'zhong',
    '表': 'biao', '时': 'shi', '候': 'hou', '等': 'deng', '待': 'dai', '等': 'deng', '等': 'deng', '来': 'lai',
    '去': 'qu', '到': 'dao', '从': 'cong', '向': 'xiang', '往': 'wang', '走': 'zou', '跑': 'pao', '跳': 'tiao',
    '飞': 'fei', '游': 'you', '爬': 'pa', '坐': 'zuo', '站': 'zhan', '躺': 'tang', '睡': 'shui', '醒': 'xing',
    '看': 'kan', '听': 'ting', '说': 'shuo', '话': 'hua', '讲': 'jiang', '告': 'gao', '诉': 'su', '问': 'wen',
    '答': 'da', '应': 'ying', '叫': 'jiao', '喊': 'han', '哭': 'ku', '笑': 'xiao', '唱': 'chang', '跳': 'tiao',
    '舞': 'wu', '画': 'hua', '写': 'xie', '读': 'du', '学': 'xue', '教': 'jiao', '练': 'lian', '习': 'xi',
    '工': 'gong', '作': 'zuo', '活': 'huo', '动': 'dong', '运': 'yun', '动': 'dong', '游': 'you', '戏': 'xi',
    '玩': 'wan', '乐': 'le', '趣': 'qu', '兴': 'xing', '趣': 'qu', '爱': 'ai', '好': 'hao', '喜': 'xi', '欢': 'huan',
    '讨': 'tao', '厌': 'yan', '恨': 'hen', '怕': 'pa', '紧': 'jin', '张': 'zhang', '放': 'fang', '松': 'song',
    '安': 'an', '全': 'quan', '危': 'wei', '险': 'xian', '平': 'ping', '安': 'an', '健': 'jian', '康': 'kang',
    '病': 'bing', '痛': 'tong', '累': 'lei', '饿': 'e', '渴': 'ke', '饱': 'bao', '满': 'man', '空': 'kong',
    '多': 'duo', '少': 'shao', '很': 'hen', '非': 'fei', '常': 'chang', '特': 'te', '别': 'bie', '特': 'te',
    '殊': 'shu', '普': 'pu', '通': 'tong', '一': 'yi', '般': 'ban', '正': 'zheng', '常': 'chang', '异': 'yi',
    '常': 'chang', '奇': 'qi', '怪': 'guai', '神': 'shen', '秘': 'mi', '明': 'ming', '白': 'bai', '清': 'qing',
    '楚': 'chu', '模': 'mo', '糊': 'hu', '复': 'fu', '杂': 'za', '简': 'jian', '单': 'dan', '容': 'rong',
    '易': 'yi', '困': 'kun', '难': 'nan', '麻': 'ma', '烦': 'fan', '方': 'fang', '便': 'bian', '舒': 'shu',
    '服': 'fu', '舒': 'shu', '适': 'shi', '美': 'mei', '丽': 'li', '漂': 'piao', '亮': 'liang', '好': 'hao',
    '看': 'kan', '难': 'nan', '看': 'kan', '丑': 'chou', '陋': 'lou',
    
    # 游戏特定角色名和地名
    '辉': 'hui', '夜': 'ye', '葛': 'ge', '城': 'cheng', '余': 'yu', '洛': 'luo', '琛': 'chen', '神': 'shen',
    '魔': 'mo', '妖': 'yao', '精': 'jing', '灵': 'ling', '仙': 'xian', '佛': 'fo', '神': 'shen', '鬼': 'gui',
    '怪': 'guai', '兽': 'shou', '龙': 'long', '凤': 'feng', '麒': 'qi', '麟': 'lin', '虎': 'hu', '狮': 'shi',
    '象': 'xiang', '马': 'ma', '牛': 'niu', '羊': 'yang', '猪': 'zhu', '鸡': 'ji', '鸭': 'ya', '鹅': 'e',
    
    # 动作和状态
    '补': 'bu', '漏': 'lou', '缺': 'que', '失': 'shi', '错': 'cuo', '误': 'wu', '对': 'dui', '正': 'zheng',
    '确': 'que', '准': 'zhun', '精': 'jing', '确': 'que', '细': 'xi', '致': 'zhi', '粗': 'cu', '糙': 'cao',
    '完': 'wan', '成': 'cheng', '结': 'jie', '束': 'shu', '停': 'ting', '止': 'zhi', '暂': 'zan', '停': 'ting',
    '继': 'ji', '续': 'xu', '坚': 'jian', '持': 'chi', '放': 'fang', '弃': 'qi', '努': 'nu', '力': 'li',
    '尝': 'chang', '试': 'shi', '测': 'ce', '试': 'shi', '检': 'jian', '验': 'yan', '验': 'yan', '证': 'zheng',
    
    # 情感和关系
    '爱': 'ai', '恋': 'lian', '情': 'qing', '感': 'gan', '心': 'xin', '意': 'yi', '思': 'si', '想': 'xiang',
    '念': 'nian', '记': 'ji', '忆': 'yi', '忘': 'wang', '记': 'ji', '得': 'de', '失': 'shi', '去': 'qu',
    '获': 'huo', '得': 'de', '收': 'shou', '获': 'huo', '失': 'shi', '败': 'bai', '成': 'cheng', '功': 'gong',
    '胜': 'sheng', '利': 'li', '败': 'bai', '北': 'bei', '输': 'shu', '赢': 'ying', '赚': 'zhuan', '赔': 'pei',
    
    # 数量和程度
    '些': 'xie', '点': 'dian', '批': 'pi', '堆': 'dui', '群': 'qun', '队': 'dui', '组': 'zu', '班': 'ban',
    '级': 'ji', '层': 'ceng', '段': 'duan', '级': 'ji', '别': 'bie', '类': 'lei', '种': 'zhong', '样': 'yang',
    '式': 'shi', '型': 'xing', '款': 'kuan', '件': 'jian', '条': 'tiao', '根': 'gen', '支': 'zhi', '只': 'zhi',
    '头': 'tou', '个': 'ge', '位': 'wei', '名': 'ming', '人': 'ren', '次': 'ci', '遍': 'bian', '回': 'hui',
    '趟': 'tang', '场': 'chang', '局': 'ju', '轮': 'lun', '届': 'jie', '期': 'qi', '季': 'ji', '度': 'du',
    
    # 游戏中的动作
    '选': 'xuan', '择': 'ze', '决': 'jue', '定': 'ding', '判': 'pan', '断': 'duan', '思': 'si', '考': 'kao',
    '想': 'xiang', '象': 'xiang', '梦': 'meng', '见': 'jian', '遇': 'yu', '见': 'jian', '碰': 'peng', '到': 'dao',
    '找': 'zhao', '寻': 'xun', '求': 'qiu', '搜': 'sou', '索': 'suo', '发': 'fa', '现': 'xian', '探': 'tan',
    '索': 'suo', '调': 'tiao', '查': 'cha', '研': 'yan', '究': 'jiu', '分': 'fen', '析': 'xi', '总': 'zong',
    '结': 'jie', '归': 'gui', '纳': 'na', '整': 'zheng', '理': 'li', '收': 'shou', '拾': 'shi', '打': 'da',
    '扫': 'sao', '清': 'qing', '洁': 'jie', '干': 'gan', '净': 'jing', '脏': 'zang', '乱': 'luan', '整': 'zheng',
    '齐': 'qi', '规': 'gui', '整': 'zheng', '标': 'biao', '准': 'zhun', '正': 'zheng', '规': 'gui', '合': 'he',    '法': 'fa', '违': 'wei', '法': 'fa', '犯': 'fan', '罪': 'zui', '错': 'cuo', '误': 'wu',
    
    # 添加从日志中发现的缺失字符
    '不': 'bu', '且': 'qie', '临': 'lin', '为': 'wei', '久': 'jiu', '么': 'me', '之': 'zhi', '也': 'ye', 
    '书': 'shu', '了': 'le', '事': 'shi', '交': 'jiao', '什': 'shen', '今': 'jin', '他': 'ta', '代': 'dai', 
    '以': 'yi', '们': 'men', '会': 'hui', '但': 'dan', '你': 'ni', '倒': 'dao', '假': 'jia', '做': 'zuo', 
    '共': 'gong', '其': 'qi', '再': 'zai', '况': 'kuang', '刚': 'gang', '包': 'bao', '半': 'ban', 
    '印': 'yin', '变': 'bian', '吗': 'ma', '吧': 'ba', '呢': 'ne', '味': 'wei', '和': 'he', '咖': 'ka', 
    '品': 'pin', '哈': 'ha', '哦': 'o', '唉': 'ai', '啊': 'a', '啡': 'fei', '啦': 'la', '啧': 'ze', 
    '喝': 'he', '嗯': 'en', '嘛': 'ma', '因': 'yin', '太': 'tai', '她': 'ta', '姑': 'gu', '娘': 'niang', 
    '子': 'zi', '孔': 'kong', '实': 'shi', '就': 'jiu', '尽': 'jin', '居': 'ju', '差': 'cha', '己': 'ji', 
    '当': 'dang', '怀': 'huai', '怎': 'zen', '惜': 'xi', '我': 'wo', '扰': 'rao', '把': 'ba', '抱': 'bao', 
    '指': 'zhi', '按': 'an', '挺': 'ting', '撒': 'sa', '改': 'gai', '故': 'gu', '旁': 'pang', '最': 'zui', 
    '有': 'you', '果': 'guo', '架': 'jia', '概': 'gai', '歉': 'qian', '毕': 'bi', '没': 'mei', '深': 'shen', 
    '然': 'ran', '照': 'zhao', '留': 'liu', '疑': 'yi', '百': 'bai', '的': 'de', '真': 'zhen', '瞒': 'man', 
    '知': 'zhi', '突': 'tu', '竟': 'jing', '算': 'suan', '粮': 'liang', '约': 'yue', '纪': 'ji', '经': 'jing', 
    '而': 'er', '聊': 'liao', '至': 'zhi', '虽': 'sui', '要': 'yao', '解': 'jie', '让': 'rang', '该': 'gai', 
    '请': 'qing', '谁': 'shei', '谎': 'huang', '谓': 'wei', '起': 'qi', '轻': 'qing', '迎': 'ying', 
    '还': 'hai', '这': 'zhe', '迭': 'die', '道': 'dao', '那': 'na', '都': 'dou', '门': 'men', '随': 'sui', 
    '需': 'xu', '食': 'shi',
    
    # 符号映射 - 删除所有中文符号
    '—': '', '－': '', '–': '', '《': '', '》': '', '「': '', '」': '', '『': '', '』': '', '（': '', '）': '', '【': '', '】': '',
    '，': '', '。': '', '；': '', '：': '', '！': '', '？': '', '、': '', '·': '', '…': '', '～': '', '〈': '', '〉': '',
    '"': '', '"': '', ''': '', ''': '', '〔': '', '〕': '', '※': '', '△': '', '▲': '', '◆': '', '★': '', '☆': '',
}

def chinese_to_pinyin(text: str) -> str:
    """将中文字符转换为拼音"""
    result = ""
    unknown_chars = set()
    
    for char in text:
        if char in CHINESE_TO_PINYIN:
            result += CHINESE_TO_PINYIN[char]
        elif '\u4e00' <= char <= '\u9fff':  # 其他中文字符
            # 对于没有在字典中的中文字符，记录下来
            unknown_chars.add(char)
            result += char  # 先保留原字符
        else:
            result += char
    
    # 返回结果和未知字符集合
    return result, unknown_chars

def normalize_filename(filename: str) -> str:
    """
    标准化文件名：
    - 中文汉字换成拼音
    - 删除中文符号
    - 删除空格
    - 保留数字、英文和英文符号
    """
    # 获取文件名和扩展名
    name, ext = os.path.splitext(filename)
    
    # 转换中文字符
    normalized_name, unknown_chars = chinese_to_pinyin(name)
    
    # 删除空格
    normalized_name = normalized_name.replace(' ', '')
    
    # 只保留字母、数字、下划线、连字符、点号
    normalized_name = re.sub(r'[^\w\-\.]', '', normalized_name)
    
    return normalized_name + ext, unknown_chars

def scan_audio_files(base_path: str, log_file=None) -> tuple:
    """扫描音频文件夹，查找包含中文字符的文件名和文件夹名并生成重命名映射"""
    file_rename_mapping = {}
    folder_rename_mapping = {}
    all_unknown_chars = set()
    
    def log_print(message):
        print(message)
        if log_file:
            log_file.write(message + '\n')
    
    if not os.path.exists(base_path):
        log_print(f"警告: 路径不存在: {base_path}")
        return file_rename_mapping, folder_rename_mapping, all_unknown_chars
    
    log_print(f"正在扫描: {base_path}")
    
    # 先收集所有需要重命名的文件夹，按深度排序（深度大的先处理）
    folders_to_rename = []
    
    for root, dirs, files in os.walk(base_path):
        # 检查当前目录下的文件夹
        for dir_name in dirs:
            has_chinese = any('\u4e00' <= char <= '\u9fff' for char in dir_name)
            if has_chinese:
                dir_path = os.path.join(root, dir_name)
                relative_dir_path = os.path.relpath(dir_path, base_path)
                
                # 生成新的文件夹名
                new_dir_name, unknown_chars = normalize_filename(dir_name)
                new_relative_dir_path = os.path.join(os.path.dirname(relative_dir_path), new_dir_name)
                
                # 记录未知字符
                all_unknown_chars.update(unknown_chars)
                
                # 计算文件夹深度
                depth = relative_dir_path.count(os.sep)
                folders_to_rename.append((depth, relative_dir_path, new_relative_dir_path, unknown_chars))
    
    # 按深度降序排序，深层文件夹先处理
    folders_to_rename.sort(key=lambda x: x[0], reverse=True)
    
    # 添加文件夹重命名映射
    for depth, old_path, new_path, unknown_chars in folders_to_rename:
        folder_rename_mapping[old_path.replace('\\', '/')] = new_path.replace('\\', '/')
        log_print(f"  发现中文文件夹: {old_path} -> {new_path}")
        if unknown_chars:
            log_print(f"    包含未知字符: {', '.join(unknown_chars)}")
    
    # 扫描文件（需要考虑文件夹重命名后的路径）
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.endswith(('.mp3', '.flac', '.wav', '.ogg')):
                # 检查文件名是否包含中文字符
                has_chinese = any('\u4e00' <= char <= '\u9fff' for char in file)
                
                if has_chinese:
                    original_path = os.path.join(root, file)
                    relative_path = os.path.relpath(original_path, base_path)
                    
                    # 生成新的文件名
                    new_filename, unknown_chars = normalize_filename(file)
                    
                    # 计算新的相对路径（考虑文件夹重命名）
                    old_dir_path = os.path.dirname(relative_path)
                    new_dir_path = old_dir_path
                    
                    # 应用文件夹重命名映射
                    for old_folder, new_folder in folder_rename_mapping.items():
                        old_folder_norm = old_folder.replace('/', os.sep)
                        new_folder_norm = new_folder.replace('/', os.sep)
                        if old_dir_path.startswith(old_folder_norm):
                            new_dir_path = old_dir_path.replace(old_folder_norm, new_folder_norm, 1)
                            break
                    
                    new_relative_path = os.path.join(new_dir_path, new_filename)
                    
                    # 记录未知字符
                    all_unknown_chars.update(unknown_chars)
                    
                    # 添加到映射中
                    file_rename_mapping[relative_path.replace('\\', '/')] = new_relative_path.replace('\\', '/')
                    log_print(f"  发现中文文件: {relative_path} -> {new_relative_path}")
                    
                    if unknown_chars:
                        log_print(f"    包含未知字符: {', '.join(unknown_chars)}")
    
    return file_rename_mapping, folder_rename_mapping, all_unknown_chars

def rename_folders(base_path: str, folder_rename_mapping: Dict[str, str], dry_run: bool = True, log_file=None):
    """重命名文件夹"""
    renamed_folders = []
    
    def log_print(message):
        print(message)
        if log_file:
            log_file.write(message + '\n')
    
    # 按深度降序排序，确保深层文件夹先重命名
    sorted_folders = sorted(folder_rename_mapping.items(), 
                           key=lambda x: x[0].count('/'), reverse=True)
    
    for old_path, new_path in sorted_folders:
        old_full_path = os.path.join(base_path, old_path.replace('/', os.sep))
        new_full_path = os.path.join(base_path, new_path.replace('/', os.sep))
        
        if os.path.exists(old_full_path):
            if not dry_run:
                # 确保父目录存在
                os.makedirs(os.path.dirname(new_full_path), exist_ok=True)
                
                # 重命名文件夹
                shutil.move(old_full_path, new_full_path)
                renamed_folders.append((old_path, new_path))
                log_print(f"重命名文件夹: {old_path} -> {new_path}")
            else:
                log_print(f"[预览] 将重命名文件夹: {old_path} -> {new_path}")
        else:
            log_print(f"警告: 文件夹不存在: {old_full_path}")
    
    return renamed_folders

def rename_files(base_path: str, rename_mapping: Dict[str, str], dry_run: bool = True, log_file=None):
    """重命名文件"""
    renamed_files = []
    
    def log_print(message):
        print(message)
        if log_file:
            log_file.write(message + '\n')
    
    for old_path, new_path in rename_mapping.items():
        old_full_path = os.path.join(base_path, old_path.replace('/', os.sep))
        new_full_path = os.path.join(base_path, new_path.replace('/', os.sep))
        
        if os.path.exists(old_full_path):
            if not dry_run:
                # 确保目标目录存在
                os.makedirs(os.path.dirname(new_full_path), exist_ok=True)
                
                # 重命名文件
                shutil.move(old_full_path, new_full_path)
                renamed_files.append((old_path, new_path))
                log_print(f"重命名: {old_path} -> {new_path}")
            else:
                log_print(f"[预览] 将重命名: {old_path} -> {new_path}")
        else:
            log_print(f"警告: 文件不存在: {old_full_path}")
    
    return renamed_files

def update_rpy_files(game_path: str, file_rename_mapping: Dict[str, str], folder_rename_mapping: Dict[str, str], dry_run: bool = True, log_file=None):
    """更新rpy文件中的音频文件引用"""
    updated_files = []
    
    if not os.path.exists(game_path):
        msg = f"警告: 游戏路径不存在: {game_path}"
        print(msg)
        if log_file:
            log_file.write(msg + "\n")
        return updated_files
    
    # 查找所有rpy文件
    rpy_files = []
    for root, dirs, files in os.walk(game_path):
        for file in files:
            if file.endswith('.rpy'):
                rpy_files.append(os.path.join(root, file))
    
    msg = f"找到 {len(rpy_files)} 个rpy文件"
    print(msg)
    if log_file:
        log_file.write(msg + "\n")
    
    # 合并所有重命名映射（文件夹重命名会影响文件路径）
    all_rename_mapping = {}
    
    # 先添加文件重命名映射
    all_rename_mapping.update(file_rename_mapping)
    
    # 然后处理文件夹重命名对现有文件路径的影响
    for old_folder, new_folder in folder_rename_mapping.items():
        # 对于所有不在文件重命名映射中的文件，如果它们在被重命名的文件夹中，也需要更新路径
        for old_file_path, new_file_path in list(all_rename_mapping.items()):
            if old_file_path.startswith(old_folder + '/'):
                # 更新文件路径以反映文件夹重命名
                updated_new_path = new_file_path.replace(old_folder, new_folder, 1)
                all_rename_mapping[old_file_path] = updated_new_path
    
    # 为文件夹重命名添加映射（处理引用整个文件夹的情况）
    for old_folder, new_folder in folder_rename_mapping.items():
        all_rename_mapping[old_folder] = new_folder
    
    for rpy_file in rpy_files:
        try:
            with open(rpy_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # 替换音频文件引用
            for old_path, new_path in all_rename_mapping.items():
                # 处理不同的引用格式
                patterns = [
                    f'"{old_path}"',
                    f"'{old_path}'",
                    f'"{old_path.replace(".flac", ".mp3")}"',  # 处理flac到mp3的转换
                    f"'{old_path.replace('.flac', '.mp3')}'",
                    f'audio/{old_path}',  # 可能包含audio/前缀
                    f'sound/{old_path}',  # 可能包含sound/前缀
                ]
                
                replacements = [
                    f'"{new_path}"',
                    f"'{new_path}'",
                    f'"{new_path.replace(".flac", ".mp3")}"',
                    f"'{new_path.replace('.flac', '.mp3')}'",
                    f'audio/{new_path}',
                    f'sound/{new_path}',
                ]
                
                for pattern, replacement in zip(patterns, replacements):
                    if pattern in content:
                        content = content.replace(pattern, replacement)
                        msg = f"  替换: {pattern} -> {replacement}"
                        print(msg)
                        if log_file:
                            log_file.write(msg + "\n")
            
            # 如果内容有变化，保存文件
            if content != original_content:
                if not dry_run:
                    with open(rpy_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    updated_files.append(rpy_file)
                    msg = f"更新文件: {rpy_file}"
                    print(msg)
                    if log_file:
                        log_file.write(msg + "\n")
                else:
                    msg = f"[预览] 将更新文件: {rpy_file}"
                    print(msg)
                    if log_file:
                        log_file.write(msg + "\n")
                    
        except Exception as e:
            msg = f"处理文件时出错 {rpy_file}: {e}"
            print(msg)
            if log_file:
                log_file.write(msg + "\n")
    
    return updated_files

def main():
    # 配置路径 - 从transfer文件夹的角度设置相对路径
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_path = os.path.dirname(script_dir)  # 上一级目录
    audio_path = os.path.join(base_path, "TheWhiteNightInLateSummer", "game", "audio")
    sound_path = os.path.join(base_path, "TheWhiteNightInLateSummer", "game", "sound")
    game_path = os.path.join(base_path, "TheWhiteNightInLateSummer", "game")
    
    # 创建日志文件
    log_file_path = os.path.join(script_dir, "rename_log.txt")
    
    print("=== 音频文件重命名工具 ===")
    print(f"脚本位置: {script_dir}")
    print(f"基础路径: {base_path}")
    print(f"音频路径: {audio_path}")
    print(f"音效路径: {sound_path}")
    print(f"游戏路径: {game_path}")
    print(f"日志文件: {log_file_path}")
    
    with open(log_file_path, 'w', encoding='utf-8') as log_file:
        log_file.write("=== 音频文件重命名工具日志 ===\n")
        log_file.write(f"运行时间: {os.path.basename(__file__)}\n")
        log_file.write(f"脚本位置: {script_dir}\n")
        log_file.write(f"基础路径: {base_path}\n")
        log_file.write(f"音频路径: {audio_path}\n")
        log_file.write(f"音效路径: {sound_path}\n")
        log_file.write(f"游戏路径: {game_path}\n\n")
        
        # 第一步：扫描audio和sound文件夹中的中文文件名
        print("\n第一步：扫描音频文件夹中的中文文件名和文件夹名...")
        log_file.write("第一步：扫描音频文件夹中的中文文件名和文件夹名...\n")
        
        audio_file_mapping, audio_folder_mapping, audio_unknown = scan_audio_files(audio_path, log_file)
        print(f"音频文件夹找到 {len(audio_file_mapping)} 个中文文件名，{len(audio_folder_mapping)} 个中文文件夹名")
        log_file.write(f"音频文件夹找到 {len(audio_file_mapping)} 个中文文件名，{len(audio_folder_mapping)} 个中文文件夹名\n")
        
        print("扫描音效文件夹中的中文文件名和文件夹名...")
        log_file.write("扫描音效文件夹中的中文文件名和文件夹名...\n")
        
        sound_file_mapping, sound_folder_mapping, sound_unknown = scan_audio_files(sound_path, log_file)
        print(f"音效文件夹找到 {len(sound_file_mapping)} 个中文文件名，{len(sound_folder_mapping)} 个中文文件夹名")
        log_file.write(f"音效文件夹找到 {len(sound_file_mapping)} 个中文文件名，{len(sound_folder_mapping)} 个中文文件夹名\n")
        
        # 合并映射和未知字符
        all_file_mapping = {**audio_file_mapping, **sound_file_mapping}
        all_folder_mapping = {**audio_folder_mapping, **sound_folder_mapping}
        all_unknown_chars = audio_unknown.union(sound_unknown)
        
        print(f"总共找到 {len(all_file_mapping)} 个需要重命名的文件，{len(all_folder_mapping)} 个需要重命名的文件夹")
        log_file.write(f"总共找到 {len(all_file_mapping)} 个需要重命名的文件，{len(all_folder_mapping)} 个需要重命名的文件夹\n")
        
        # 显示未知字符
        if all_unknown_chars:
            unknown_msg = f"发现 {len(all_unknown_chars)} 个未知中文字符: {', '.join(sorted(all_unknown_chars))}"
            print(f"\n警告: {unknown_msg}")
            log_file.write(f"\n警告: {unknown_msg}\n")
            
            # 生成待添加的字典条目
            missing_chars_file = os.path.join(script_dir, "missing_characters.txt")
            with open(missing_chars_file, 'w', encoding='utf-8') as f:
                f.write("# 以下字符需要添加到CHINESE_TO_PINYIN字典中:\n")
                for char in sorted(all_unknown_chars):
                    f.write(f"'{char}': '',  # 请填写拼音\n")
            print(f"未知字符列表已保存到: {missing_chars_file}")
            log_file.write(f"未知字符列表已保存到: {missing_chars_file}\n")
        
        if not all_file_mapping and not all_folder_mapping:
            print("没有找到包含中文字符的音频文件或文件夹")
            log_file.write("没有找到包含中文字符的音频文件或文件夹\n")
            return
        
        # 保存重命名映射到JSON文件
        mapping_file = os.path.join(script_dir, "rename_mapping.json")
        mapping_data = {
            "files": all_file_mapping,
            "folders": all_folder_mapping
        }
        with open(mapping_file, 'w', encoding='utf-8') as f:
            json.dump(mapping_data, f, ensure_ascii=False, indent=2)
        print(f"重命名映射已保存到: {mapping_file}")
        log_file.write(f"重命名映射已保存到: {mapping_file}\n")
        
        # 预览模式 - 只显示总结信息，详细信息写入日志
        print("\n=== 预览模式 ===")
        log_file.write("\n=== 预览模式 ===\n")
        print("即将进行的重命名操作:")
        log_file.write("即将进行的重命名操作:\n")
        
        if all_folder_mapping:
            print(f"\n文件夹: {len(all_folder_mapping)} 个文件夹将被重命名")
            log_file.write(f"\n文件夹: {len(all_folder_mapping)} 个文件夹将被重命名\n")
            if audio_folder_mapping:
                print(f"  音频文件夹: {len(audio_folder_mapping)} 个")
                rename_folders(audio_path, audio_folder_mapping, dry_run=True, log_file=log_file)
            if sound_folder_mapping:
                print(f"  音效文件夹: {len(sound_folder_mapping)} 个")
                rename_folders(sound_path, sound_folder_mapping, dry_run=True, log_file=log_file)
        
        if all_file_mapping:
            print(f"\n文件: {len(all_file_mapping)} 个文件将被重命名")
            log_file.write(f"\n文件: {len(all_file_mapping)} 个文件将被重命名\n")
            if audio_file_mapping:
                print(f"  音频文件: {len(audio_file_mapping)} 个")
                rename_files(audio_path, audio_file_mapping, dry_run=True, log_file=log_file)
            if sound_file_mapping:
                print(f"  音效文件: {len(sound_file_mapping)} 个")
                rename_files(sound_path, sound_file_mapping, dry_run=True, log_file=log_file)
        
        print("\n即将更新的rpy文件:")
        log_file.write("\n即将更新的rpy文件:\n")
        update_rpy_files(game_path, all_file_mapping, all_folder_mapping, dry_run=True, log_file=log_file)
        
        print(f"\n详细信息已保存到日志文件: {log_file_path}")
        
        # 询问是否执行
        response = input("\n是否执行重命名操作? (y/N): ")
        if response.lower() == 'y':
            print("\n第二步：执行重命名操作...")
            log_file.write("\n第二步：执行重命名操作...\n")
            
            # 先重命名文件夹
            if all_folder_mapping:
                print("重命名文件夹...")
                log_file.write("重命名文件夹...\n")
                
                if audio_folder_mapping:
                    print("  重命名音频文件夹...")
                    log_file.write("  重命名音频文件夹...\n")
                    rename_folders(audio_path, audio_folder_mapping, dry_run=False, log_file=log_file)
                
                if sound_folder_mapping:
                    print("  重命名音效文件夹...")
                    log_file.write("  重命名音效文件夹...\n")
                    rename_folders(sound_path, sound_folder_mapping, dry_run=False, log_file=log_file)
            
            # 再重命名文件
            if all_file_mapping:
                print("重命名文件...")
                log_file.write("重命名文件...\n")
                
                if audio_file_mapping:
                    print("  重命名音频文件...")
                    log_file.write("  重命名音频文件...\n")
                    rename_files(audio_path, audio_file_mapping, dry_run=False, log_file=log_file)
                
                if sound_file_mapping:
                    print("  重命名音效文件...")
                    log_file.write("  重命名音效文件...\n")
                    rename_files(sound_path, sound_file_mapping, dry_run=False, log_file=log_file)
            
            print("\n第三步：更新rpy文件...")
            log_file.write("\n第三步：更新rpy文件...\n")
            update_rpy_files(game_path, all_file_mapping, all_folder_mapping, dry_run=False, log_file=log_file)
            
            print("\n操作完成!")
            log_file.write("\n操作完成!\n")
            print(f"重命名映射文件保存在: {mapping_file}")
            print(f"详细日志保存在: {log_file_path}")
        else:
            print("操作取消")
            log_file.write("操作取消\n")

if __name__ == "__main__":
    main()
