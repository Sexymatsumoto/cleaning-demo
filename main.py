import streamlit as st
import difflib
import pandas as pd
from openai import OpenAI

# 整形ルール辞書ベースのクリーン関数
def simple_clean(text: str, replacements: dict) -> str:
    for wrong, right in replacements.items():
        text = text.replace(wrong, right)
    return text.strip()

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

# OpenAIクライアント（Streamlit Secrets）
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Streamlit UI
st.title("  話し言葉 整形体験アプリ（整形確認付き）")

# ユーザー入力欄
user_input = st.text_area("  あなたの話し言葉（文字起こし）を入力してください", height=300,
                          placeholder="例：この剣士は甘棒で人なつっこい天子です。")

replace_dict = {
    "端元": "橋本",
    "橋元": "橋本",
    "きょいと総定": "共栄塗装店",
    "ケルフェア": "ケルヒャー",
    "アマドイ": "雨どい",
    "トリオン": "塗料",
    "京江徒藻店": "共栄塗装店",
    "本日も装点": "共栄塗装店",
    "総店": "共栄塗装店",
    "きょいと装点": "共栄塗装店",
    "京米途奏店": "共栄塗装店",
    "キョウェトソーテン": "共栄塗装店",
    "京江逃走店": "共栄塗装店",
    "京江逸操店": "共栄塗装店",
    "京江戸総店": "共栄塗装店",
    "京江逸総店": "共栄塗装店",
    "教育途層店": "共栄塗装店",
    "京江都総店": "共栄塗装店",
    "京江戸装店": "共栄塗装店",
    "京江途奏店": "共栄塗装店",
    "教育と創展": "共栄塗装店",
    "教育と送店": "共栄塗装店",
    "京江塗装店": "共栄塗装店",
    "京栄塗装": "共栄塗装店",
    "教育塗装店": "共栄塗装店",
    "教衛トソーテン": "共栄塗装店",
    "教育と商店": "共栄塗装店",
    "教衛": "共栄",
    "教存": "共栄",
    "京都蒼天橋本": "共栄塗装店",
    "教会塗装店": "共栄塗装店",
    "公務店": "工務店"
}


if st.button("  整形してAIにかける"):
    if not user_input.strip():
        st.warning("? 入力が空です。文字起こしを貼り付けてください。")
    else:
        # 整形処理
        transcript_raw = user_input
        transcript_cleaned = simple_clean(transcript_raw, replace_dict)

        st.markdown("###   整形前後の一部（確認用）")
        st.code("整形前：\n" + transcript_raw[:100])
        st.code("整形後：\n" + transcript_cleaned[:100])

        # 差分ログ表示
        st.markdown("##   整形ログ")
        diff_df = extract_diff_log(transcript_raw, transcript_cleaned)
        if diff_df.empty:
            st.warning("? 整形ログが空です。置換される対象がない可能性があります。")
        else:
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
            st.subheader("  整形前のタグ")
            st.code(tags_raw)
            st.subheader("  整形前の構成案")
            st.markdown(outline_raw)

        with col2:
            st.subheader("  整形後のタグ")
            st.code(tags_clean)
            st.subheader("  整形後の構成案")
            st.markdown(outline_clean)

        # 差分HTML表示
        st.markdown("##   差分ハイライト")
        diff_html = difflib.HtmlDiff().make_table(
            transcript_raw.split(), transcript_cleaned.split(),
            fromdesc="整形前", todesc="整形後", context=True, numlines=2
        )
        st.components.v1.html(diff_html, height=300, scrolling=True)
