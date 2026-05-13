#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PX4 安全检测报告前端服务
使用 Flask 提供 API，读取 output 目录中的报告文件
"""

from flask import Flask, jsonify, render_template
from pathlib import Path
import os
from datetime import datetime

app = Flask(__name__, 
            template_folder='templates',
            static_folder='static', 
            static_url_path='')

# 获取项目根目录
PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / "output"

# 支持的报告文件
REPORTS = {
    "agent4": {
        "name": "综合安全报告",
        "file": "agent4_report.md",
        "description": "整合Agent1/2/3的完整分析结果"
    },
    "agent1": {
        "name": "供应链分析",
        "file": "agent1_report.md",
        "description": "漏洞知识库匹配结果（27项漏洞）"
    },
    "agent2": {
        "name": "静态代码扫描",
        "file": "agent2_report.md",
        "description": "Flawfinder + Semgrep 检测结果（23项问题）"
    },
    "agent3": {
        "name": "动态仿真验证",
        "file": "agent3_report.md",
        "description": "仿真测试验证（3个关键漏洞）"
    }
}

@app.route('/')
def index():
    """默认页面 - 检测系统"""
    return render_template('detection.html')

@app.route('/reports')
def reports():
    """报告展示页面"""
    return render_template('index.html')

@app.route('/detection')
def detection():
    """检测系统页面（兼容旧URL）"""
    return render_template('detection.html')

@app.route('/api/reports')
def get_reports_list():
    """获取所有可用报告列表"""
    reports_info = {}
    for key, config in REPORTS.items():
        file_path = OUTPUT_DIR / config['file']
        reports_info[key] = {
            "name": config['name'],
            "description": config['description'],
            "exists": file_path.exists()
        }
    return jsonify(reports_info)

@app.route('/api/report/<report_id>')
def get_report(report_id):
    """读取指定报告内容"""
    if report_id not in REPORTS:
        return jsonify({"error": "报告不存在"}), 404
    
    file_path = OUTPUT_DIR / REPORTS[report_id]['file']
    
    if not file_path.exists():
        return jsonify({"error": f"文件不存在: {file_path}"}), 404
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return jsonify({
            "id": report_id,
            "name": REPORTS[report_id]['name'],
            "content": content,
            "file_path": str(file_path),
            "file_size": file_path.stat().st_size,
            "modified_time": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/status')
def get_status():
    """获取系统状态"""
    return jsonify({
        "output_dir": str(OUTPUT_DIR),
        "output_dir_exists": OUTPUT_DIR.exists(),
        "files_count": len(list(OUTPUT_DIR.glob('*'))) if OUTPUT_DIR.exists() else 0,
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    print(f"📁 输出目录: {OUTPUT_DIR}")
    print(f"✅ 如果看到上面的路径不对，请检查 project_root 设置")
    print(f"🌐 启动服务: http://127.0.0.1:5000")
    print(f"⚠️  按 Ctrl+C 停止服务\n")
    
    app.run(debug=True, host='127.0.0.1', port=5000)
