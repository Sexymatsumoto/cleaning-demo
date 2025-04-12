# streamlit_cleaning_demo.py

import streamlit as st
import difflib
import pandas as pd
from openai import OpenAI

# OpenAIクライアント（secretsで設定）
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
def simple_clean(text: str, replacements: dict) -> str:
    for wrong, right in replacements.items():
        text = text.replace(wrong, right)
    return text.strip()

# 差分抽出
def extract_diff_log(original, cleaned):
    diff = list(difflib.ndiff(original.split(), cleaned.split()))
    corrections = []
    for i in range(len(diff)):
        if diff[i].startswith('- ') and i + 1 < len(diff) and diff[i + 1].startswith('+ '):
            corrections.append((diff[i][2:], diff[i + 1][2:]))
    return pd.DataFrame(corrections, columns=["元の言葉", "修正後の言葉"])

# GPTで要約生成
def generate_summary(text):
    prompt = f"以下の文章を100文字以内で要約してください：\n\n{text}"
    res = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "あなたはプロの編集者です。"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=100
    )
    return res.choices[0].message.content.strip()

# --- Streamlit UI ---
st.title("🧹 話し言葉 整形デモアプリ（整形前後のAI出力比較＋差分表示）")

default_input = "この剣士は甘棒で人なつっこい天子です。"
user_input = st.text_area("🎤 話し言葉を入力してください", value=default_input, height=200)

if st.button("🚀 整形前後で比較する"):
    with st.spinner("処理中..."):

        # 整形処理
        cleaned = simple_clean(user_input, replace_dict)

        # AIに要約依頼（整形前）
        summary_before = generate_summary(user_input)

        # AIに要約依頼（整形後）
        summary_after = generate_summary(cleaned)

        # 差分ログ作成
        diff_df = extract_diff_log(user_input, cleaned)

    st.subheader("✨ 整形前の要約（話し言葉のまま）")
    st.write(summary_before)

    st.subheader("🪄 整形後の要約（整った言葉）")
    st.write(summary_after)

    st.subheader("📝 整形ログ（どこがどう直されたか）")
    st.dataframe(diff_df)

