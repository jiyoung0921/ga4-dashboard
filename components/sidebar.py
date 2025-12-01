"""サイドバーコンポーネント - Elegant Radio Button Design（Phase 1: 簡素化）"""
import streamlit as st
from datetime import datetime, timedelta
from typing import Tuple
from utils.config import get_site_scope_options
from components.icons import Icons
from components.messages import render_message


def render_sidebar() -> Tuple[str, str, str, str]:
    """上品なサイドバーをレンダリングして設定値を返す"""
    
    # サイドバーヘッダー
    st.sidebar.markdown(
        f"""
        <div style="
            padding: 6px 0 20px;
            border-bottom: 1px solid #E2E8F0;
            margin-bottom: 20px;
        ">
            <div style="
                display: flex;
                align-items: center;
                gap: 10px;
            ">
                <div style="
                    width: 40px;
                    height: 40px;
                    border-radius: 12px;
                    background: linear-gradient(135deg, #7C6AEF 0%, #9D8FFF 50%, #FFB088 100%);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: white;
                    box-shadow: 0 4px 12px rgba(124, 106, 239, 0.25);
                ">{Icons.bar_chart_3(20, "white")}</div>
                <div>
                    <div style="
                        font-family: 'Quicksand', 'M PLUS Rounded 1c', sans-serif;
                        font-size: 1rem;
                        font-weight: 700;
                        color: #2D3748;
                    ">GA4 Dashboard</div>
                    <div style="
                        font-size: 0.65rem;
                        color: #718096;
                        letter-spacing: 0.03em;
                    ">Analytics Suite</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # モード選択
    st.sidebar.markdown(
        f"""
        <div style="
            font-size: 0.7rem;
            font-weight: 600;
            color: #FF8C5A;
            letter-spacing: 0.04em;
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            gap: 6px;
        ">
            {Icons.layout_dashboard(14, "#FF8C5A")}
            モード
        </div>
        """,
        unsafe_allow_html=True
    )
    
    mode = st.sidebar.radio(
        "モード選択",
        ["ダッシュボード", "対話アシスタント"],
        key="mode_radio",
        label_visibility="collapsed"
    )
    
    st.sidebar.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    
    # 期間選択
    st.sidebar.markdown(
        f"""
        <div style="
            font-size: 0.7rem;
            font-weight: 600;
            color: #FF8C5A;
            letter-spacing: 0.04em;
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            gap: 6px;
        ">
            {Icons.calendar_days(14, "#FF8C5A")}
            期間
        </div>
        """,
        unsafe_allow_html=True
    )
    
    period_type = st.sidebar.radio(
        "期間タイプ",
        ["プリセット", "カスタム"],
        key="period_type_radio",
        label_visibility="collapsed",
        horizontal=True
    )
    
    today = datetime.now().date()
    start_date_obj = today - timedelta(days=6)
    end_date_obj = today
    
    if period_type == "プリセット":
        preset = st.sidebar.selectbox(
            "期間を選択",
            ["過去7日間", "過去30日間", "過去90日間", "今月", "先月"],
            key="period_preset",
            label_visibility="collapsed"
        )
        
        if preset == "過去7日間":
            start_date_obj = today - timedelta(days=6)
            end_date_obj = today
        elif preset == "過去30日間":
            start_date_obj = today - timedelta(days=29)
            end_date_obj = today
        elif preset == "過去90日間":
            start_date_obj = today - timedelta(days=89)
            end_date_obj = today
        elif preset == "今月":
            start_date_obj = today.replace(day=1)
            end_date_obj = today
        elif preset == "先月":
            first_of_this_month = today.replace(day=1)
            last_of_previous_month = first_of_this_month - timedelta(days=1)
            start_date_obj = last_of_previous_month.replace(day=1)
            end_date_obj = last_of_previous_month
    else:
        col1, col2 = st.sidebar.columns(2)
        with col1:
            start_input = st.date_input(
                "開始",
                value=today - timedelta(days=7),
                key="start_date"
            )
        with col2:
            end_input = st.date_input(
                "終了",
                value=today,
                key="end_date"
            )
        
        start_date_obj = start_input
        end_date_obj = end_input
        
        if start_date_obj > end_date_obj:
            render_message("開始日が終了日より後です", "warning", container=st.sidebar)
            start_date_obj, end_date_obj = end_date_obj, start_date_obj
    
    start_date = start_date_obj.strftime('%Y-%m-%d')
    end_date = end_date_obj.strftime('%Y-%m-%d')
    
    st.sidebar.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    
    # サイト領域選択
    st.sidebar.markdown(
        f"""
        <div style="
            font-size: 0.7rem;
            font-weight: 600;
            color: #FF8C5A;
            letter-spacing: 0.04em;
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            gap: 6px;
        ">
            {Icons.layers(14, "#FF8C5A")}
            サイト領域
        </div>
        """,
        unsafe_allow_html=True
    )
    
    site_scope_options = get_site_scope_options()
    site_scope_index = st.sidebar.selectbox(
        "サイト領域を選択",
        options=range(len(site_scope_options)),
        format_func=lambda idx: site_scope_options[idx]['label'],
        index=0,
        key="site_scope",
        label_visibility="collapsed"
    )
    site_scope_value = site_scope_options[site_scope_index]['value']
    
    st.sidebar.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
    
    # フッター
    st.sidebar.markdown(
        f"""
        <div style="
            position: fixed;
            bottom: 0;
            left: 0;
            width: 220px;
            padding: 14px 20px;
            background: linear-gradient(180deg, transparent 0%, white 30%);
            border-top: 1px solid #E2E8F0;
        ">
            <div style="
                display: flex;
                align-items: center;
                gap: 8px;
                font-size: 0.7rem;
                color: #A0AEC0;
            ">
                {Icons.wifi(12, "#48BB78")}
                <span style="color: #48BB78; font-weight: 600;">GA4 接続中</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    return mode, start_date, end_date, site_scope_value
