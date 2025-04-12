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

# UI
st.title("  橋本さんの整形デモ：話し言葉 vs 整えた言葉")

col1, col2 = st.columns(2)
with col1:
    st.subheader("  整形前の話し言葉")
    st.text_area("整形前", transcript_raw, height=300)

with col2:
    st.subheader("  整形後の文章")
    st.text_area("整形後", transcript_cleaned, height=300)

if st.button("  ChatGPTでタグ・構成を比較！"):
    with st.spinner("AI処理中..."):
        tags_raw = generate_tags(transcript_raw)
        tags_clean = generate_tags(transcript_cleaned)
        outline_raw = generate_outline(transcript_raw)
        outline_clean = generate_outline(transcript_cleaned)

    st.markdown("##   タグの比較")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### 整形前")
        st.code(tags_raw)
    with c2:
        st.markdown("### 整形後")
        st.code(tags_clean)

    st.markdown("##   構成案の比較")
    c3, c4 = st.columns(2)
    with c3:
        st.markdown("### 整形前")
        st.markdown(outline_raw)
    with c4:
        st.markdown("### 整形後")
        st.markdown(outline_clean)

st.markdown("##   整形ログ（どこがどう変わったか）")
diff_df = extract_diff_log(transcript_raw, transcript_cleaned)
st.dataframe(diff_df)

st.markdown("##   差分ハイライト表示（HTML）")
with open("橋本さん_diff.html", "r", encoding="utf-8") as f:
    diff_html = f.read()
st.components.v1.html(diff_html, height=300, scrolling=True)
