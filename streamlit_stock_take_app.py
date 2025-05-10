import streamlit as st
import re
import csv
import io
from collections import Counter

# 页面配置
st.set_page_config(page_title="多列表库存 AI 计算器", layout="centered")

# 初始化：一个 dict 存所有列表，key 为列表名，value 为 Counter
if 'all_lists' not in st.session_state:
    st.session_state.all_lists = {}       # e.g. {'列表1': Counter(), '列表2': Counter(), ...}
if 'current_list' not in st.session_state:
    st.session_state.current_list = None  # 当前操作的列表名
if 'history' not in st.session_state:
    st.session_state.history = []         # 历史栈，用于 undo
if 'input_text' not in st.session_state:
    st.session_state.input_text = ""
if 'new_list_name' not in st.session_state:
    st.session_state.new_list_name = ""

st.title("📦 多列表库存 AI 计算器")

# —— 列表管理区 —— #
st.subheader("1️⃣ 选择或创建列表")
# 下拉选择已有列表
list_names = list(st.session_state.all_lists.keys())
choice = st.selectbox("请选择要操作的列表", ["— 新建列表 —"] + list_names, key="current_list")

# 如果选“新建列表”，提供文本框输入新名字
if choice == "— 新建列表 —":
    st.text_input("输入新列表名称", key="new_list_name", placeholder="比如 列表1")
    if st.button("🆕 创建新列表"):
        name = st.session_state.new_list_name.strip()
        if not name or name in st.session_state.all_lists:
            st.error("名称不能为空，且不能与已有列表重名")
        else:
            st.session_state.all_lists[name] = Counter()
            st.session_state.current_list = name
            st.success(f"✅ 已创建并切换到列表：{name}")
else:
    st.session_state.current_list = choice

# 如果还没选中任何列表，提示并 return
if not st.session_state.current_list:
    st.info("请先选择或创建一个列表，才能进行库存操作")
    st.stop()

current = st.session_state.current_list
counter = st.session_state.all_lists[current]

st.markdown(f"**当前列表：{current}**  （共 {len(counter)} 个不同 code）")
st.markdown("---")

# —— 核心功能区 —— #

def add_to_total():
    text = st.session_state.input_text
    matches = re.findall(r"(\S+)\s*([\d]*\.?\d+)", text)
    if not matches:
        st.warning("❗ 未匹配到 code+数量，请检查格式")
        return
    # 记录历史（备份整个 all_lists）
    st.session_state.history.append(st.session_state.all_lists.copy())
    for code, qty in matches:
        counter[code] += float(qty)
    st.session_state.input_text = ""
    st.success("已添加本轮数据")

def clear_all():
    st.session_state.history.append(st.session_state.all_lists.copy())
    st.session_state.all_lists[current] = Counter()
    st.success("已清空当前列表所有数据")

def undo():
    if st.session_state.history:
        st.session_state.all_lists = st.session_state.history.pop()
        st.success("已撤回上一步操作")
    else:
        st.warning("无可撤回的操作")

# 文本输入和按钮
st.text_area("📋 输入本轮库存列表", key="input_text", height=120,
             placeholder="格式：<code> <数量> 例：\nABC-1 3\nXYZ 2.5")
c1, c2, c3 = st.columns(3)
with c1:
    st.button("✅ 添加到当前列表", on_click=add_to_total)
with c2:
    st.button("🗑️ 清空当前列表", on_click=clear_all)
with c3:
    st.button("⏪ 撤回上一步", on_click=undo)

# 搜索某个 code
st.text_input("🔍 查询 code 数量", key="search_code", placeholder="输入 code 后回车")
if st.session_state.search_code:
    code = st.session_state.search_code.strip()
    qty = float(counter.get(code, 0))
    st.info(f"Code **{code}** 在列表 **{current}** 中的数量：**{qty}**")

# 排序展示
def sort_key(item):
    k, _ = item
    return (0, float(k)) if re.fullmatch(r'[\d\.]+', k) else (1, k)

if counter:
    st.subheader("📈 列表库存总览")
    rows = []
    for code, qty in sorted(counter.items(), key=sort_key):
        display_qty = int(qty) if qty == int(qty) else qty
        rows.append({"code": code, "quantity": display_qty})
    st.table(rows)
