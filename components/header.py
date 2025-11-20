"""ヘッダーヒーローコンポーネント"""
import streamlit as st
from datetime import datetime
from typing import Optional


def render_header(site_scope: Optional[str], start_date: str, end_date: str) -> None:
    """ヒーローヘッダーを描画"""
    scope_label = site_scope if site_scope else "全サイト"
    start_display = datetime.strptime(start_date, "%Y-%m-%d").strftime("%Y年%m月%d日")
    end_display = datetime.strptime(end_date, "%Y-%m-%d").strftime("%Y年%m月%d日")

    st.markdown(
        f"""
        <div class="hero-banner">
            <div class="hero-title">サイト領域：{scope_label}</div>
            <div class="hero-meta">
                <span class="hero-chip">期間: {start_display} 〜 {end_display}</span>
                <span class="hero-chip">最終更新: {datetime.now().strftime('%Y/%m/%d %H:%M')}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
