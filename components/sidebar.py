"""サイドバーコンポーネント"""
import streamlit as st
from datetime import datetime, timedelta
from typing import Tuple
from utils.config import (
    get_site_scope_options,
    get_ga4_dimension_options,
    get_ga4_metric_options,
)


def render_sidebar() -> Tuple[str, str, str, str]:
    """サイドバーをレンダリングして設定値を返す"""
    st.sidebar.title("⚙️ 設定")
    
    # カスタムレポート設定
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
    
    with st.sidebar.expander("🔧 カスタムレポート設定", expanded=False):
        selected_dimensions = st.multiselect(
            "ディメンション",
            options=available_dimensions,
            default=current_config.get('dimensions', []),
            format_func=lambda value: _format(value, dimension_map),
            key="custom_dimensions_select"
        )
        selected_metrics = st.multiselect(
            "指標（必須）",
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
        st.caption("GA4のディメンション/指標から必要なものだけを選び、カスタムタブで確認できます。")
        st.session_state.custom_report_config = {
            'dimensions': selected_dimensions,
            'metrics': selected_metrics,
            'limit': limit_value
        }
    
    # モード選択
    mode = st.sidebar.radio(
        "モード選択",
        ["ダッシュボード", "対話アシスタント"],
        key="mode_selection"
    )
    
    # 期間選択
    st.sidebar.subheader("📅 期間選択")
    
    period_type = st.sidebar.radio(
        "期間タイプ",
        ["プリセット", "カスタム"],
        key="period_type"
    )
    
    today = datetime.now().date()
    start_date_obj = today - timedelta(days=6)
    end_date_obj = today
    
    if period_type == "プリセット":
        preset = st.sidebar.selectbox(
            "期間を選択",
            ["過去7日間", "過去30日間", "過去90日間", "今月", "先月"],
            key="period_preset"
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
        start_input = st.sidebar.date_input(
            "開始日",
            value=today - timedelta(days=7),
            key="start_date"
        )
        
        end_input = st.sidebar.date_input(
            "終了日",
            value=today,
            key="end_date"
        )
        
        start_date_obj = start_input
        end_date_obj = end_input
        
        if start_date_obj > end_date_obj:
            st.sidebar.warning("開始日が終了日より後になっています。日付を確認してください。")
            start_date_obj, end_date_obj = end_date_obj, start_date_obj
    
    start_date = start_date_obj.strftime('%Y-%m-%d')
    end_date = end_date_obj.strftime('%Y-%m-%d')
    
    # サイト領域選択
    st.sidebar.subheader("📂 サイト領域")
    site_scope_options = get_site_scope_options()
    site_scope_index = st.sidebar.selectbox(
        "サイト領域を選択",
        options=range(len(site_scope_options)),
        format_func=lambda idx: site_scope_options[idx]['label'],
        index=0,
        key="site_scope"
    )
    site_scope_value = site_scope_options[site_scope_index]['value']
    
    return mode, start_date, end_date, site_scope_value

