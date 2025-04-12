# streamlit_cleaning_demo_v2.py

import streamlit as st
import difflib
import pandas as pd
from openai import OpenAI
from html import escape

# OpenAIクライアント（secretsから取得）
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# 整形ルール辞書
replace_dict = {
    "剣士": "犬種",
    "甘棒": "甘えん坊",
    "天子": "犬種",
    "しけも": "しつけも",
    "個人さ": "個体差",
    "買い やすい": "買いやすい",
    "お 伝え": "お伝え",
    "お 出かけ": "お出かけ",
    "地は": "チワワ"
}

# 整形関数
def simple_clean(text, replacements):
    for wrong, right in replacements.items():
        text = text.replace(wrong, right)
    return text.strip()

# 差分HTML表示（単語単位）
def html_diff(a, b):
    differ = difflib.HtmlDiff(tabsize=2, wrapcolumn=80)
    return differ.make_table(a.split(), b.split(),
                             fromdesc="整形前（話し言葉）",
                             todesc="整形後（整った言葉）",
                             context=True, numlines=1)

# 差分ログ生成（表）
def extract_diff_log(original, cleaned):
    diff = list(difflib.ndiff(original.split(), cleaned.split()))
    corrections = []
    for i in range(len(diff)):
        if diff[i].startswith('- ') and i + 1 < len(diff) and diff[i + 1].startswith('+ '):
            corrections.append((diff[i][2:], diff[i + 1][2:]))
    return pd.DataFrame(corrections, columns=["元の言葉", "修正後の言葉"])

# タグ生成
def generate_tags(text, role):
    prompt = f"以下の文章にふさわしいタグを3〜5個、日本語で出力してください：\n\n{text}"
    res = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": role},
            {"role": "user", "content": prompt}
        ],
        temperature=0.4,
        max_tokens=150
    )
    return res.choices[0].message.content.strip()

# 構成案生成
def generate_outline(text):
    prompt = f"以下の内容を3〜5つの見出しでセクション構成に分けてください：\n\n{text}"
    res = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "あなたは優秀な構成ライターです。"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.4,
        max_tokens=200
    )
    return res.choices[0].message.content.strip()

# --- UI ---
st.title("🧹 話し言葉 → 整形 × AI出力比較 × 差分表示")

user_input = st.text_area("🎤 話し言葉（文字起こしなど）を貼ってください", height=200,
    value="この剣士は甘棒で人なつっこい天子です。")

if st.button("🚀 整形して比較！"):
    with st.spinner("整形中＆AI処理中..."):

        cleaned = simple_clean(user_input, replace_dict)
        diff_log = extract_diff_log(user_input, cleaned)

        # AI出力
        tags_before = generate_tags(user_input, "あなたはSEOに強い編集者です。")
        tags_after = generate_tags(cleaned, "あなたはSEOに強い編集者です。")

        outline_before = generate_outline(user_input)
        outline_after = generate_outline(cleaned)

        # 差分HTML生成
        diff_html = html_diff(user_input, cleaned)

    # 出力エリア
    st.subheader("📝 整形ログ（差分表）")
    st.dataframe(diff_log)

    st.subheader("🌈 差分ハイライト表示")
    st.components.v1.html(diff_html, height=250, scrolling=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🔸 整形前のタグ")
        st.code(tags_before)
        st.markdown("### 🪜 整形前の構成案")
        st.markdown(outline_before)

    with col2:
        st.markdown("### 🔹 整形後のタグ")
        st.code(tags_after)
        st.markdown("### 🧱 整形後の構成案")
        st.markdown(outline_after)
