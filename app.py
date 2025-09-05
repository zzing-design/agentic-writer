import streamlit as st
import time
import pandas as pd
import os

# ----------------- 配置 -----------------
import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel(model_name="gemini-pro")


# Prompt 模板
STRUCTURE_PROMPT = """
你是一个专业写作顾问，请根据以下主题生成一个五段式写作结构。
每段包含一个小标题和一句简短提示。

主题：{theme}

输出格式：
1. [标题]：提示语
2. ...
"""

SUBTASK_PROMPT = """
你是我的AI写作助手，请根据以下段落标题和主题写出100字以内的段落，并说明你的写作理由。

主题：{theme}
段落标题：{heading}
"""

# ----------------- 函数 -----------------
from openai import RateLimitError, APIError

def call_gemini(prompt):
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"⚠️ Gemini 出错：{str(e)}"


def parse_structure(response_text):
    lines = response_text.strip().split("\n")
    parsed = []
    for line in lines:
        if "." in line:
            title = line.split(".")[1].split("：")[0].strip()
            hint = line.split("：")[-1].strip()
            parsed.append({"title": title, "hint": hint})
    return parsed

# ----------------- UI 入口 -----------------
st.title("📘 Agentic AI 写作系统原型")
st.write("输入主题，生成结构，逐段协同编辑")

# Session 存储
if "structure" not in st.session_state:
    st.session_state.structure = []
if "theme" not in st.session_state:
    st.session_state.theme = ""

# ----------------- 输入主题 → 生成结构 -----------------
st.subheader("1️⃣ 输入主题")
theme = st.text_input("请输入写作主题：", value=st.session_state.theme)

if st.button("生成写作结构"):
    st.session_state.theme = theme
    with st.spinner("AI 正在生成写作结构..."):
        prompt = STRUCTURE_PROMPT.format(theme=theme)
        response = call_gemini(prompt)
        st.session_state.structure = parse_structure(response)
        st.success("结构生成完成！")

# ----------------- 显示结构 & 子任务入口 -----------------
if st.session_state.structure:
    st.subheader("2️⃣ 写作结构 & 协作编辑")
    for idx, section in enumerate(st.session_state.structure):
        with st.expander(f"📌 第{idx+1}段：{section['title']}"):
            st.write(f"提示：{section['hint']}")
            if st.button(f"生成建议内容 - 第{idx+1}段"):
                prompt = SUBTASK_PROMPT.format(theme=st.session_state.theme, heading=section['title'])
                with st.spinner("AI 正在生成建议内容..."):
                    ai_text = call_openai(prompt)
                    st.session_state[f"ai_text_{idx}"] = ai_text
                    st.success("生成完成")
            if f"ai_text_{idx}" in st.session_state:
                st.markdown("**AI建议内容：**")
                st.info(st.session_state[f"ai_text_{idx}"])
                user_edit = st.text_area("你的修改版本：", key=f"edit_{idx}")

# ----------------- 数据记录（可选） -----------------
# 可在后续加入 csv 保存日志，例如写入每段修改内容、点击时间等。

# ----------------- 汇总功能（可选） -----------------
# 可添加按钮将全部段落内容组合展示或导出。

st.markdown("---")
st.caption("📊 Prototype v0.1 by Nyxien")