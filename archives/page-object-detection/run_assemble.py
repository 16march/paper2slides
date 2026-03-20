#!/usr/bin/env python3
"""
步骤8：LaTeX文档组装
将所有页面的独立LaTeX片段组装成一个完整的可编译文档
"""

import os
from pathlib import Path
import re

def read_tex_file(filepath):
    """读取tex文件，提取文档中的实际内容"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取\begin{document}和\end{document}之间的内容
    match = re.search(r'\\begin{document}(.*?)\\end{document}', content, re.DOTALL)
    if match:
        return match.group(1).strip()
    return ""

def assemble_document(latex_dir):
    """组装完整的LaTeX文档"""
    # 按文件名排序（保证页面顺序）
    tex_files = sorted(Path(latex_dir).glob('*.tex'))
    
    # 收集所有内容
    contents = []
    for tex_file in tex_files:
        content = read_tex_file(tex_file)
        if content:
            contents.append(content)
            print(f"   ✅ 添加: {tex_file.name}")
    
    # 组装完整文档
    full_document = r'''\documentclass[11pt,a4paper,twocolumn]{article}
\usepackage[utf8]{inputenc}
\usepackage{graphicx}

\begin{document}

''' + '\n\n'.join(contents) + r'''

\end{document}
'''
    
    return full_document

if __name__ == '__main__':
    print("📑 步骤8：LaTeX文档组装...")
    
    latex_dir = 'test_output/latex_output_nougat'  # 使用Nougat版本
    output_file = 'test_output/final_output_nougat.tex'
    
    # 组装文档
    document = assemble_document(latex_dir)
    
    # 保存
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(document)
    
    print(f"\n✅ 步骤8完成！")
    print(f"   完整LaTeX文档保存为: {output_file}")
    print(f"   共组装了 {len(list(Path(latex_dir).glob('*.tex')))} 个片段")
