"""サイドバーコンポーネント"""
import streamlit as st
from datetime import datetime, timedelta
from typing import Tuple, Optional
from utils.config import get_site_scope_options


def render_sidebar() -> Tuple[str, str, str, str]:
    """サイドバーをレンダリングして設定値を返す"""
    st.sidebar.title("⚙️ 設定")
    st.sidebar.markdown(
        """
        <div class="ux-tip-card">
            <div class="ux-tip-title">迷ったときのおすすめ設定</div>
            <p style="margin-bottom:0;">最初に「過去30日間」を表示しています。どの期間で見るか悩む場合はひとまずこの設定で状況を確認できます。</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # モード選択
    mode = st.sidebar.radio(
        "モード選択",
        ["ダッシュボード", "対話アシスタント"],
        key="mode_selection"
    )
    
    st.sidebar.divider()
    
    # データソース接続状態
    st.sidebar.subheader("💾 データソース")
    ga4_connected = 'ga4_client' in st.session_state and st.session_state.ga4_client is not None
    gsc_connected = 'gsc_client' in st.session_state and st.session_state.gsc_client is not None

    st.sidebar.markdown(
        f"- GA4: {'接続済み ✅' if ga4_connected else '未接続 ⚠️'}"
    )
    st.sidebar.markdown(
        f"- GSC: {'接続済み ✅' if gsc_connected else '未接続（任意）'}"
    )
    with st.sidebar.expander("接続ガイド（必要なときだけ開く）"):
        st.sidebar.write("GA4/GSC 連携に問題がある場合は README の「セットアップ手順」を参照してください。")
    
    st.sidebar.divider()
    
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
    
    st.sidebar.divider()
    
    # 情報
    st.sidebar.success("🎯 推奨: 期間プリセットは『過去30日間』が最もバランス良くトレンドを把握できます。")
    st.sidebar.caption("データは最大48時間の遅延がある可能性があります。")
    
    st.sidebar.divider()
    
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

