import streamlit as st
import re
from collections import Counter

# 页面配置
st.set_page_config(page_title="多列表库存 AI 计算器", layout="centered")

# —— 初始化 Session State —— #
if 'all_lists' not in st.session_state:
    st.session_state.all_lists = {}       # 存放所有列表: {列表名: Counter}
if 'current_list' not in st.session_state:
    st.session_state.current_list = None  # 当前选中的列表名
if 'history' not in st.session_state:
    st.session_state.history = []         # 用于撤回的历史栈，存放 all_lists 快照
if 'input_text' not in st.session_state:
    st.session_state.input_text = ""      # 本轮输入文本
if 'new_list_name' not in st.session_state:
    st.session_state.new_list_name = ""   # 新建列表名称
if 'select_choice' not in st.session_state:
    st.session_state.select_choice = None # 下拉框的选择值
if 'search_code' not in st.session_state:
    st.session_state.search_code = ""     # 查询用的 code

st.title("📦 多列表库存 AI 计算器")

# —— 1. 列表管理 —— #
st.subheader("1️⃣ 选择或创建列表")

def on_select_change():
    # 当你在下拉里选一个已有列表时，把它设置为 current_list
    st.session_state.current_list = st.session_state.select_choice

# 构造下拉选项
options = ["— 新建列表 —"] + list(st.session_state.all_lists.keys())
st.selectbox(
    "请选择要操作的列表",
    options,
    key="select_choice",
    on_change=on_select_change
)

# 新建列表回调
def create_new_list():
    name = st.session_state.new_list_name.strip()
    if not name:
        st.error("❗ 列表名称不能为空")
    elif name in st.session_state.all_lists:
        st.error("❗ 列表名已存在，请换一个")
    else:
        # 记录历史快照
        st.session_state.history.append({
            k: cnt.copy() for k, cnt in st.session_state.all_lists.items()
        })
        # 创建并切换
        st.session_state.all_lists[name] = Counter()
        st.session_state.current_list = name
        st.session_state.select_choice = name
        st.success(f"✅ 已创建并切换到列表：{name}")

# 如果选中新建
if st.session_state.select_choice == "— 新建列表 —":
    st.text_input(
        "输入新列表名称",
        key="new_list_name",
        placeholder="比如 列表1"
    )
    st.button("🆕 创建新列表", on_click=create_new_list)

# —— 校验：必须先有一个有效列表才能继续 —— #
current = st.session_state.current_list
if current not in st.session_state.all_lists:
    st.info("请先在上面新建或选择一个列表，然后再进行库存操作。")
    st.stop()

# 准备当前列表引用
counter = st.session_state.all_lists[current]
st.markdown(f"**当前列表：{current}**    已记录 {len(counter)} 个不同 code")
st.markdown("---")

# —— 2. 核心功能回调 —— #
def add_to_total():
    text = st.session_state.input_text
    matches = re.findall(r"(\S+)\s*([\d]*\.?\d+)", text)
    if not matches:
        st.warning("❗ 未检测到符合格式的 code+数量，请检查输入。")
        return
    # 记录历史
    st.session_state.history.append({
        k: cnt.copy() for k, cnt in st.session_state.all_lists.items()
    })
    # 累加
    for code, qty in matches:
        counter[code] += float(qty)
    st.session_state.input_text = ""
    st.success("✅ 本轮数据已累计")

def clear_all():
    st.session_state.history.append({
        k: cnt.copy() for k, cnt in st.session_state.all_lists.items()
    })
    st.session_state.all_lists[current] = Counter()
    st.success("🗑️ 已清空当前列表所有数据")

def undo():
    if st.session_state.history:
        st.session_state.all_lists = st.session_state.history.pop()
        st.success("⏪ 已撤回上一步操作")
    else:
        st.warning("⚠️ 无可撤回的操作")

# 文本输入与按钮
st.text_area(
    "📋 输入本轮库存列表",
    key="input_text",
    height=120,
    placeholder="格式：<code> <数量>\n示例：\nABC-123 5\nXYZ 6.3\nN11 .75"
)
c1, c2, c3 = st.columns(3)
with c1:
    st.button("✅ 添加到当前列表", on_click=add_to_total)
with c2:
    st.button("🗑️ 清空当前列表", on_click=clear_all)
with c3:
    st.button("⏪ 撤回上一步", on_click=undo)

st.markdown("---")

# —— 3. 查询功能 —— #
st.text_input(
    "🔍 查询某个 code 的数量",
    key="search_code",
    placeholder="输入 code 后回车"
)
if st.session_state.search_code:
    code = st.session_state.search_code.strip()
    qty = counter.get(code, 0.0)
    display_qty = int(qty) if qty == int(qty) else qty
    st.info(f"🔎 Code **{code}** 在列表 **{current}** 中的数量：**{display_qty}**")

# —— 排序展示 —— #
def sort_key(item):
    code, _ = item
    if re.fullmatch(r'[\d\.]+', code):
        return (0, float(code))
    else:
        return (1, code)

if counter:
    st.subheader("📈 当前列表库存总览")
    table = []
    for code, qty in sorted(counter.items(), key=sort_key):
        display_qty = int(qty) if qty == int(qty) else qty
        table.append({"code": code, "quantity": display_qty})
    st.table(table)
