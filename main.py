import streamlit as st
import difflib
import pandas as pd
from openai import OpenAI

# OpenAIクライアント（Streamlit Secrets）
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# テキスト読み込み
with open("hashimoto_transcript_raw.txt", "r", encoding="utf-8") as f:
    transcript_raw = f.read()

with open("hashimoto_transcript_cleaned.txt", "r", encoding="utf-8") as f:
    transcript_cleaned = f.read()

# 差分ログ生成
def extract_diff_log(original, cleaned):
    diff = list(difflib.ndiff(original.split(), cleaned.split()))
    corrections = []
    for i in range(len(diff)):
        if diff[i].startswith('- ') and i + 1 < len(diff) and diff[i + 1].startswith('+ '):
            corrections.append((diff[i][2:], diff[i + 1][2:]))
    return pd.DataFrame(corrections, columns=["元の言葉", "修正後の言葉"])

# タグ生成
def generate_tags(text):
    prompt = f"以下の文章にふさわしいタグを3?5個、日本語で出力してください：\n\n{text}"
    res = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "あなたはSEOに強い編集者です。"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.4,
        max_tokens=150
    )
    return res.choices[0].message.content.strip()

# 構成案生成
def generate_outline(text):
    prompt = f"以下の内容を3?5つの見出しでセクション構成に分けてください：\n\n{text}"
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

st.title("🧹 話し言葉 整形体験アプリ（自由入力OK）")

# ユーザー入力欄
user_input = st.text_area("🎤 あなたの話し言葉（文字起こしなど）を貼り付けてください", height=300,
                          placeholder="例：この剣士は甘棒で人なつっこい天子です。")

if st.button("🚀 整形してAIにかける"):
    if not user_input.strip():
        st.warning("何か入力してください。")
    else:
        # 整形処理
        transcript_raw = user_input
        transcript_cleaned = simple_clean(transcript_raw, {
            "剣士": "犬種", "甘棒": "甘えん坊", "天子": "犬種", "しけも": "しつけも",
            "個人さ": "個体差", "買い やすい": "買いやすい", "お 伝え": "お伝え",
            "お 出かけ": "お出かけ", "地は": "チワワ"
        })

        # 差分ログ表示
        st.markdown("## 📊 整形ログ")
        diff_df = extract_diff_log(transcript_raw, transcript_cleaned)
        st.dataframe(diff_df)

        # ChatGPT出力
        with st.spinner("ChatGPTでタグ・構成を処理中..."):
            tags_raw = generate_tags(transcript_raw)
            tags_clean = generate_tags(transcript_cleaned)
            outline_raw = generate_outline(transcript_raw)
            outline_clean = generate_outline(transcript_cleaned)

        # 比較表示
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("📝 整形前のタグ")
            st.code(tags_raw)
            st.subheader("🧱 整形前の構成案")
            st.markdown(outline_raw)

        with col2:
            st.subheader("📝 整形後のタグ")
            st.code(tags_clean)
            st.subheader("🧱 整形後の構成案")
            st.markdown(outline_clean)

        # 差分HTML表示
        st.markdown("## 🌈 差分ハイライト")
        diff_html = difflib.HtmlDiff().make_table(
            transcript_raw.split(), transcript_cleaned.split(),
            fromdesc="整形前", todesc="整形後", context=True, numlines=2
        )
        st.components.v1.html(diff_html, height=300, scrolling=True)
