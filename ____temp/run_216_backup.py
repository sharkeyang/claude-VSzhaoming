# -*- coding: utf-8 -*-
"""运行216分支概率表生成（指向备份数据）"""
import sys, os
sys.stdout.reconfigure(encoding='utf-8')
os.chdir(r'D:\@VSwork\VS昭明计划VBA优化')
os.environ['PROJ'] = r'D:\@VSwork\VS昭明计划VBA优化'
import importlib.util
spec = importlib.util.spec_from_file_location('g', '____temp/gen_180_prob_table.py')
g = importlib.util.module_from_spec(spec)
g.DATA_DIR = r'D:\@VSwork\VS昭明计划VBA优化\昭明算展\谕组日_备份_20260804'
g.PROJ = r'D:\@VSwork\VS昭明计划VBA优化'
g.INPUT_PATH = g.DATA_DIR
spec.loader.exec_module(g)
g.main()