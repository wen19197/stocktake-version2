import streamlit as st
import re
import json
import os
from collections import Counter

# 存储文件路径
STORE_PATH = "stock_data.json"

# —— 持久化函数 —— #
def load_store():
    """从 JSON 文件读出 all_lists（列表字典）"""
    if os.path.exists(STORE_PATH):
        with open(STORE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        # JSON 里 quantity 是数字，code→qty
        return {name: Counter(counter) for name, counter in data.items()}
    return {}

def save_store(all_lists):
    """把 all_lists（Counter）写入 JSON 文件"""
    serializable = {name: dict(cnt) for name, cnt in all_lists.items()}
    with open(STORE_PATH, "w", encoding="utf-8") as f:
        json.dump(serializable, f, ensure_ascii=False, indent=2)

# 页面配置
st.set_page_config(page_title="多列表库存 AI 计算器", layout="centered")

# —— 初始化 Session State —— #
if 'all_lists' not in st.session_state:
    # 先尝试从文件加载；若不存在则用空字典
    st.session_state.all_lists = load_store()
if 'current_list' not in st.session_state:
    st.session_state.current_list = None
if 'history' not in st.session_state:
    st.session_state.history = []
if 'input_text' not in st.session_state:
    st.session_state.input_text = ""
if 'new_list_name' not in st.session_state:
    st.session_state.new_list_name = ""
if 'select_choice' not in st.session_state:
    st.session_state.select_choice = None
if 'search_code' not in st.session_state:
    st.session_state.search_code = ""

st.title("📦 多列表库存 AI 计算器（持久化）")

# —— 列表管理 & 创建（略，和之前示例相同） —— #
# ... （此处省略选择/创建列表 UI 及回调逻辑，保持不变） ...

# —— 假设此时 st.session_state.current_list 已指向一个已存在列表 —— #
current = st.session_state.current_list
counter = st.session_state.all_lists[current]

# —— 操作回调函数中，记得在每次修改 all_lists 后调用 save_store —— #
def add_to_total():
    # ... 之前的累加逻辑 ...
    save_store(st.session_state.all_lists)  # 持久化
def clear_all():
    # ... 清空逻辑 ...
    save_store(st.session_state.all_lists)
def undo():
    # ... 撤回逻辑 ...
    save_store(st.session_state.all_lists)
def create_new_list():
    # ... 新建列表逻辑 ...
    save_store(st.session_state.all_lists)

# —— 接着渲染输入框、按钮、表格 —— #
# ...（和之前示例保持一致）...
