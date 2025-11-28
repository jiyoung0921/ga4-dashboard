"""サイドバーコンポーネント - Modern Design with Lucide Icons"""
import streamlit as st
from datetime import datetime, timedelta
from typing import Tuple
from utils.config import (
    get_site_scope_options,
    get_ga4_dimension_options,
    get_ga4_metric_options,
)
from components.icons import Icons


def render_sidebar() -> Tuple[str, str, str, str]:
    """モダンなサイドバーをレンダリングして設定値を返す"""
    
    # サイドバーヘッダー
    st.sidebar.markdown(
        f"""
        <div style="
            padding: 8px 0 24px;
            border-bottom: 1px solid rgba(124, 106, 239, 0.1);
            margin-bottom: 24px;
        ">
            <div style="
                display: flex;
                align-items: center;
                gap: 12px;
            ">
                <div style="
                    width: 44px;
                    height: 44px;
                    border-radius: 14px;
                    background: linear-gradient(135deg, #7C6AEF 0%, #FF8C5A 100%);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: white;
                ">{Icons.bar_chart_3(22, "white")}</div>
                <div>
                    <div style="
                        font-family: 'Plus Jakarta Sans', sans-serif;
                        font-size: 1.1rem;
                        font-weight: 700;
                        color: #1A1A2E;
                    ">GA4 Dashboard</div>
                    <div style="
                        font-size: 0.7rem;
                        color: #6E6E8A;
                        text-transform: uppercase;
                        letter-spacing: 0.05em;
                    ">Analytics Suite</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # モード選択（アイコン付き）
    st.sidebar.markdown(
        f"""
        <div style="
            font-size: 0.7rem;
            font-weight: 600;
            color: #6E6E8A;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            gap: 6px;
        ">
            {Icons.layout_dashboard(14, "#6E6E8A")}
            モード
        </div>
        """,
        unsafe_allow_html=True
    )
    
    mode = st.sidebar.radio(
        "モード選択",
        ["ダッシュボード", "対話アシスタント"],
        key="mode_selection",
        label_visibility="collapsed"
    )
    
    st.sidebar.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    
    # 期間選択
    st.sidebar.markdown(
        f"""
        <div style="
            font-size: 0.7rem;
            font-weight: 600;
            color: #6E6E8A;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            gap: 6px;
        ">
            {Icons.calendar_days(14, "#6E6E8A")}
            期間
        </div>
        """,
        unsafe_allow_html=True
    )
    
    period_type = st.sidebar.radio(
        "期間タイプ",
        ["プリセット", "カスタム"],
        key="period_type",
        horizontal=True,
        label_visibility="collapsed"
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
            st.sidebar.warning("⚠️ 開始日が終了日より後です")
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
            color: #6E6E8A;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            gap: 6px;
        ">
            {Icons.layers(14, "#6E6E8A")}
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
    
    st.sidebar.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)
    
    # カスタムレポート設定（折りたたみ）
    metadata = st.session_state.get('ga4_metadata', {})
    default_dimension_options = get_ga4_dimension_options()
    default_metric_options = get_ga4_metric_options()
    dimension_map = {opt['value']: opt['label'] for opt in default_dimension_options}
    metric_map = {opt['value']: opt['label'] for opt in default_metric_options}
    
    available_dimensions = metadata.get('dimensions') or [opt['value'] for opt in default_dimension_options]
    available_metrics = metadata.get('metrics') or [opt['value'] for opt in default_metric_options]
    
    current_config = st.session_state.get('custom_report_config', {
        'dimensions': ['deviceCategory', 'eventName'],
        'metrics': ['eventCount'],
        'limit': 50
    })
    
    def _format(value: str, mapping: dict) -> str:
        return mapping.get(value, value)
    
    with st.sidebar.expander("⚙️ カスタムレポート", expanded=False):
        selected_dimensions = st.multiselect(
            "ディメンション",
            options=available_dimensions,
            default=current_config.get('dimensions', []),
            format_func=lambda value: _format(value, dimension_map),
            key="custom_dimensions_select"
        )
        selected_metrics = st.multiselect(
            "指標",
            options=available_metrics,
            default=current_config.get('metrics', []),
            format_func=lambda value: _format(value, metric_map),
            key="custom_metrics_select"
        )
        limit_value = st.number_input(
            "取得件数",
            min_value=1,
            max_value=250,
            value=current_config.get('limit', 50),
            step=1
        )
        st.caption("カスタムタブで確認できます")
        st.session_state.custom_report_config = {
            'dimensions': selected_dimensions,
            'metrics': selected_metrics,
            'limit': limit_value
        }
    
    # フッター
    st.sidebar.markdown(
        f"""
        <div style="
            position: fixed;
            bottom: 0;
            left: 0;
            width: 240px;
            padding: 16px 24px;
            background: linear-gradient(180deg, transparent 0%, white 20%);
            border-top: 1px solid rgba(124, 106, 239, 0.08);
        ">
            <div style="
                display: flex;
                align-items: center;
                gap: 8px;
                font-size: 0.75rem;
                color: #9E9EB8;
            ">
                {Icons.wifi(14, "#10B981")}
                <span style="color: #10B981; font-weight: 500;">GA4 接続中</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    return mode, start_date, end_date, site_scope_value
