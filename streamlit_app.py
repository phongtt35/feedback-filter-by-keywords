import streamlit as st
import pandas as pd
import re
import unicodedata
from io import BytesIO

def normalize_text(text):
    return unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('utf-8').lower()

def check_keywords(feedback, keywords):
    matches = []
    normalized_feedback = normalize_text(feedback)
    
    for keyword in keywords:
        normalized_keyword = normalize_text(keyword)
        if re.search(rf'\b{re.escape(normalized_keyword)}\b', normalized_feedback):
            matches.append(keyword)
    
    return matches

st.title('FPT Polytechnic - XLDL \n Lọc phản hồi cần lưu ý theo từ khóa')

keywords_input = st.text_input("Nhập từ khóa (ngăn cách bởi dấu phẩy)")
keywords_list = [kw.strip() for kw in keywords_input.split(',') if kw.strip()]

uploaded_file = st.file_uploader("Tải tệp Excel", type=["xlsx"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    
    if "Feedback" in df.columns:
        df["Matched Feedback"] = ""

        for i, row in df.iterrows():
            feedback = row["Feedback"]
            
            feedback_segments = [seg.strip() for seg in feedback.split('*') if seg.strip()]
            
            matched_segments = []
            for segment in feedback_segments:
                matches = check_keywords(segment, keywords_list)
                if matches:
                    matched_segments.append(f"{segment} (Matched: {', '.join(matches)})")
            
            if matched_segments:
                df.at[i, "Matched Feedback"] = "; ".join(matched_segments)

        matched_df = df[df["Matched Feedback"] != ""].copy()
        unmatched_df = df[df["Matched Feedback"] == ""].copy()

        st.dataframe(matched_df)

        if st.button("Tách feedback đã lọc"):
            output = BytesIO()

            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                matched_df.to_excel(writer, sheet_name="Cần lưu ý", index=False)
                unmatched_df.to_excel(writer, sheet_name="Còn lại", index=False)
            
            output.seek(0)
            processed_file = output.getvalue()

            st.download_button(label="Tải tệp đã tách",
                               data=processed_file,
                               file_name="processed_feedback.xlsx",
                               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    else:
        st.error("Tệp tải lên không có cột tên 'Feedback'")
