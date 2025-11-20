"""ダッシュボードビューコンポーネント"""
import streamlit as st
import pandas as pd
from modules.ga4_client import GA4Client
from modules.gsc_client import GSCClient
from modules.data_processor import DataProcessor
from modules.visualization import Visualization
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Tuple, Any
from utils.config import get_cv_events_for_scope, get_event_display_name, get_article_path_prefixes

UX_TAB_TIPS = {
    "overview": {
        "title": "目標との差がひと目で分かる",
        "message": "前の期間を仮の目標にして可視化しています。あとどれくらい伸ばせば良いかすぐ確認できます。"
    },
    "traffic": {
        "title": "強みと課題を同時に把握",
        "message": "好調なチャネルと注意が必要なチャネルを並べて表示し、次の打ち手を考えやすくしています。"
    },
    "device": {
        "title": "注目すべきデバイスを絞り込み",
        "message": "直帰率が高いデバイスを警告し、優先度の高い改善領域が一目で分かります。"
    },
    "event": {
        "title": "次に追うべき記事が見つかる",
        "message": "イベント別に記事を順位付けしているので、成果につながるコンテンツをすぐ特定できます。"
    },
    "realtime": {
        "title": "更新の速さを明示",
        "message": "ボタンひとつで即座に更新できることを示し、気軽に最新状況を確認できるようにしています。"
    },
    "utm": {
        "title": "成果と課題を比較しやすく",
        "message": "勝ち筋のキャンペーンと改善候補を同じ画面で見せ、意思決定をサポートします。"
    },
    "seo": {
        "title": "検索データの裏付けを同時表示",
        "message": "GA4とGSCの指標を合わせて表示し、『なぜこの動きになったのか』を納得して判断できます。"
    }
}


@st.cache_data(ttl=300, hash_funcs={GA4Client: lambda client: client.property_id})  # 5分間キャッシュ
def get_overview_metrics_cached(ga4_client: GA4Client, start_date: str, end_date: str, site_scope: Optional[str]):
    """概要メトリクスを取得（キャッシュ付き）"""
    return ga4_client.get_overview_metrics(start_date, end_date, site_scope=site_scope)


@st.cache_data(ttl=300, hash_funcs={GA4Client: lambda client: client.property_id})
def get_daily_traffic_cached(ga4_client: GA4Client, start_date: str, end_date: str, site_scope: Optional[str]):
    """日別トラフィックを取得（キャッシュ付き）"""
    df = ga4_client.get_daily_traffic(start_date, end_date, site_scope)
    if not df.empty and 'date' in df.columns:
        df = df.sort_values('date')
    return df


@st.cache_data(ttl=300, hash_funcs={GA4Client: lambda client: client.property_id})
def get_event_counts_cached(
    ga4_client: GA4Client,
    start_date: str,
    end_date: str,
    event_names: Tuple[str, ...],
    site_scope: Optional[str]
):
    """イベント数を取得（キャッシュ付き）"""
    return ga4_client.get_event_counts_by_names(start_date, end_date, list(event_names), site_scope)


def _calculate_previous_period(start_date: str, end_date: str) -> tuple[str, str]:
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    period_days = (end_dt - start_dt).days + 1
    prev_end = start_dt - timedelta(days=1)
    prev_start = prev_end - timedelta(days=period_days - 1)
    return prev_start.strftime("%Y-%m-%d"), prev_end.strftime("%Y-%m-%d")


def _format_metric_value(metric: str, value: Optional[float]) -> str:
    if value is None:
        return "-"
    if metric == 'bounceRate':
        return f"{value * 100:.1f}%"
    if metric == 'averageSessionDuration':
        minutes = int(value // 60)
        seconds = int(value % 60)
        return f"{minutes}:{seconds:02d}"
    return f"{int(value):,}"


def _format_delta(metric: str, current: float, previous: float) -> tuple[str, str]:
    if previous is None:
        return "", ""
    delta = current - previous
    if metric == 'bounceRate':
        delta_pct = delta * 100
    elif metric == 'averageSessionDuration':
        delta_pct = (delta / previous * 100) if previous else 0
    else:
        delta_pct = (delta / previous * 100) if previous else 0

    direction = "positive" if delta_pct >= 0 else "negative"
    sign = "+" if delta_pct >= 0 else ""
    if metric == 'bounceRate':
        delta_text = f"{sign}{delta_pct:.1f}pt"
    else:
        delta_text = f"{sign}{delta_pct:.1f}%"
    return delta_text, direction


def _render_tab_tip(key: str) -> None:
    tip = UX_TAB_TIPS.get(key)
    if not tip:
        return
    st.markdown(
        f"""
        <div class="ux-tip-card">
            <div class="ux-tip-title">{tip['title']}</div>
            <p style="margin-bottom:0;">{tip['message']}</p>
        </div>
        """,
        unsafe_allow_html=True
    )


def _calculate_goal_target(current: float, previous: Optional[float]) -> float:
    baseline = previous if previous and previous > 0 else current
    if baseline <= 0:
        baseline = 1
    return baseline * 1.1


def _render_goal_gradient_tracker(items: List[Dict[str, float]]) -> None:
    if not items:
        return
    st.subheader("🎯 目標勾配トラッカー")
    st.caption("前期間より10%アップを仮ターゲットにした進捗バーです。伸びしろの目安として使えます。")
    for item in items:
        current = item.get('current', 0) or 0
        target = item.get('target', 0) or 0
        if target <= 0:
            target = max(current, 1)
        progress = min(current / target, 1.0) if target else 0
        st.progress(
            progress,
            text=f"{item['label']} {int(current):,} / {int(target):,}"
        )


def _render_kpi_cards(cards: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    selected_card: Optional[Dict[str, Any]] = None
    chunk_size = 4
    for i in range(0, len(cards), chunk_size):
        chunk = cards[i:i + chunk_size]
        st.markdown('<div class="kpi-row">', unsafe_allow_html=True)
        cols = st.columns(len(chunk))
        for col, card in zip(cols, chunk):
            value_text = card['value_text']
            delta_text = card.get('delta_text', '')
            delta_class = card.get('delta_class', '')
            prev_text = card.get('previous_text', '')
            with col:
                st.markdown(
                    f"""
                    <div class="kpi-card">
                        <div class="kpi-label">{card['label']}</div>
                        <div class="kpi-value">{value_text}</div>
                        {f'<div class="kpi-prev">前期間: {prev_text}</div>' if prev_text else ''}
                        {f'<div class="kpi-delta {delta_class}">前期間比 {delta_text}</div>' if delta_text else ''}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                if st.button(
                    "週次推移を見る",
                    key=f"kpi_button_{card['id']}"
                ):
                    if selected_card is None:
                        selected_card = card
        st.markdown('</div>', unsafe_allow_html=True)
    return selected_card


def _aggregate_weekly(df: pd.DataFrame, value_column: str) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=['week_start', 'value'])
    series = df[['date', value_column]].copy()
    series = series.set_index('date')
    weekly = series.resample('W-MON', label='left', closed='left').sum().reset_index()
    weekly = weekly.rename(columns={'date': 'week_start', value_column: 'value'})
    weekly['week_label'] = weekly['week_start'].dt.strftime('%Y-%m-%d')
    return weekly


def _show_kpi_modal(card: Dict[str, Any], ga4_client: GA4Client, site_scope: Optional[str], end_date: str) -> None:
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    start_dt = end_dt - timedelta(days=55)  # 約8週間
    start_date = start_dt.strftime('%Y-%m-%d')
    end_str = end_dt.strftime('%Y-%m-%d')

    if card['metric_type'] == 'metric' and card['metric_key'] == 'sessions':
        df = ga4_client.get_daily_traffic(start_date, end_str, site_scope)
        value_column = 'sessions'
    elif card['metric_type'] == 'event':
        df = ga4_client.get_event_daily_series(start_date, end_str, card['metric_key'], site_scope)
        value_column = 'eventCount'
    else:
        df = pd.DataFrame()
        value_column = 'value'

    weekly = _aggregate_weekly(df, value_column)

    container = st.container()
    with container:
        st.markdown(
            f"""
            <div style="background: #FFFFFF; border-radius: 18px; padding: 24px; box-shadow: 0 24px 48px -32px rgba(47,42,38,0.45); margin-bottom: 24px;">
                <h3 style="margin-top:0;">{card['label']}の週次推移</h3>
            """,
            unsafe_allow_html=True
        )
        if weekly.empty:
            st.info("データがありません")
        else:
            fig = Visualization.create_bar_chart(
                weekly,
                'week_label',
                'value',
                f"{card['label']}の週次推移",
                "週開始日",
                "件数"
            )
            st.plotly_chart(fig, width="stretch")
            st.dataframe(
                weekly[['week_label', 'value']].rename(columns={'week_label': '週', 'value': '件数'}),
                width="stretch"
            )
        st.markdown("</div>", unsafe_allow_html=True)

        if st.button("閉じる", key=f"close_modal_{card['id']}"):
            container.empty()


def render_overview_tab(ga4_client: GA4Client, start_date: str, end_date: str, site_scope: Optional[str]):
    """概要タブをレンダリング"""
    st.header("📊 概要")
    _render_tab_tip("overview")
    
    # メトリクスを取得
    metrics = get_overview_metrics_cached(ga4_client, start_date, end_date, site_scope)
    prev_start, prev_end = _calculate_previous_period(start_date, end_date)
    previous_metrics = get_overview_metrics_cached(ga4_client, prev_start, prev_end, site_scope)
    daily_traffic = get_daily_traffic_cached(ga4_client, start_date, end_date, site_scope)
 
    event_names = get_cv_events_for_scope(site_scope)
    event_tuple = tuple(event_names)
    current_events = get_event_counts_cached(ga4_client, start_date, end_date, event_tuple, site_scope)
    previous_events = get_event_counts_cached(ga4_client, prev_start, prev_end, event_tuple, site_scope)

    cards = []
    # セッション数カード
    current_sessions = metrics.get('sessions', 0)
    previous_sessions = previous_metrics.get('sessions', 0) if previous_metrics else None
    session_delta_text, session_delta_class = _format_delta('sessions', current_sessions, previous_sessions)
    cards.append({
        'label': 'セッション数',
        'value_text': _format_metric_value('sessions', current_sessions),
        'previous_text': _format_metric_value('sessions', previous_sessions) if previous_sessions is not None else '',
        'delta_text': session_delta_text,
        'delta_class': session_delta_class,
        'id': 'metric_sessions',
        'metric_type': 'metric',
        'metric_key': 'sessions'
    })

    for event_name in event_names:
        current_value = current_events.get(event_name, 0)
        previous_value = previous_events.get(event_name, 0) if previous_events else None
        delta_text, delta_class = _format_delta('sessions', current_value, previous_value)
        display_name = get_event_display_name(event_name)
        cards.append({
            'label': display_name,
            'value_text': f"{int(current_value):,}",
            'previous_text': f"{int(previous_value):,}" if previous_value is not None else '',
            'delta_text': delta_text,
            'delta_class': delta_class,
            'id': f"event_{event_name}",
            'metric_type': 'event',
            'metric_key': event_name
        })

    selected_card = _render_kpi_cards(cards)
    if selected_card:
        st.session_state['kpi_modal'] = {
            'card': selected_card,
            'end_date': end_date,
            'site_scope': site_scope
        }

    modal_info = st.session_state.pop('kpi_modal', None)
    if modal_info:
        _show_kpi_modal(
            modal_info['card'],
            ga4_client,
            modal_info['site_scope'],
            modal_info['end_date']
        )

    progress_items: List[Dict[str, float]] = []
    progress_items.append({
        'label': 'セッション数',
        'current': current_sessions,
        'target': _calculate_goal_target(current_sessions, previous_sessions)
    })
    for event_name in event_names:
        current_value = current_events.get(event_name, 0)
        previous_value = previous_events.get(event_name, 0) if previous_events else 0
        progress_items.append({
            'label': get_event_display_name(event_name),
            'current': current_value,
            'target': _calculate_goal_target(current_value, previous_value)
        })
    _render_goal_gradient_tracker(progress_items)

    st.divider()
    
    # 日別トラフィックトレンド
    if not daily_traffic.empty:
        st.subheader("📈 日別トラフィックトレンド")
        fig = Visualization.create_line_chart(
            daily_traffic,
            'date',
            ['sessions', 'totalUsers', 'screenPageViews'],
            "日別トラフィック",
            "日付",
            "数"
        )
        st.plotly_chart(fig, width="stretch")
        
        # データテーブル
        with st.expander("データを表示"):
            st.dataframe(daily_traffic, width="stretch")
    else:
        st.info("データがありません")


def render_traffic_source_tab(ga4_client: GA4Client, start_date: str, end_date: str, site_scope: Optional[str]):
    """流入元タブをレンダリング"""
    st.header("🌐 流入元")
    _render_tab_tip("traffic")
    
    # チャネルグループ別データ
    source_data = ga4_client.get_traffic_source(start_date, end_date, site_scope=site_scope)
    
    if not source_data.empty:
        # チャネルグループ別の集計
        if 'sessionDefaultChannelGroup' in source_data.columns:
            channel_group = source_data.groupby('sessionDefaultChannelGroup')['sessions'].sum().reset_index()
            channel_group = channel_group.sort_values('sessions', ascending=False)
            
            st.subheader("📊 チャネルグループ別セッション数")
            fig = Visualization.create_bar_chart(
                channel_group,
                'sessionDefaultChannelGroup',
                'sessions',
                "チャネルグループ別セッション数",
                "チャネルグループ",
                "セッション数",
                orientation='h'
            )
            st.plotly_chart(fig, width="stretch")

            st.subheader("⚖️ チャネル健全性ビュー")
            col_success, col_risk = st.columns(2)
            top_channels = channel_group.head(5)
            weak_channels = channel_group.sort_values('sessions', ascending=True).head(5)
            with col_success:
                st.caption("まずは好調チャネルを基準にして、他チャネルの位置づけを把握できます。")
                st.dataframe(top_channels, width="stretch")
            with col_risk:
                st.caption("セッションが少ないチャネルは早めに手当てできるよう別枠で表示しています。")
                st.dataframe(weak_channels, width="stretch")
        
        # 参照元/メディア別データ
        st.subheader("📋 参照元/メディア別データ")
        if 'sessionSource' in source_data.columns and 'sessionMedium' in source_data.columns:
            source_medium = source_data.groupby(['sessionSource', 'sessionMedium'])['sessions'].sum().reset_index()
            source_medium = source_medium.sort_values('sessions', ascending=False).head(20)
            st.dataframe(source_medium, width="stretch")
        
        # ランディングページ
        st.subheader("🪧 ランディングページ")
        landing_pages = ga4_client.get_landing_pages(start_date, end_date, limit=10, site_scope=site_scope)
        if not landing_pages.empty:
            st.dataframe(landing_pages, width="stretch")
    else:
        st.info("データがありません")


def render_device_tab(ga4_client: GA4Client, start_date: str, end_date: str, site_scope: Optional[str]):
    """デバイスタブをレンダリング"""
    st.header("📱 デバイス")
    _render_tab_tip("device")
    
    device_data = ga4_client.get_device_data(start_date, end_date, site_scope=site_scope)
    
    if not device_data.empty:
        # デバイスカテゴリ別の集計
        if 'deviceCategory' in device_data.columns:
            device_summary = device_data.groupby('deviceCategory').agg({
                'sessions': 'sum',
                'bounceRate': 'mean'
            }).reset_index()
            
            st.subheader("📊 デバイスカテゴリ別セッション数")
            fig = Visualization.create_bar_chart(
                device_summary,
                'deviceCategory',
                'sessions',
                "デバイスカテゴリ別セッション数",
                "デバイス",
                "セッション数"
            )
            st.plotly_chart(fig, width="stretch")
            
            st.subheader("📊 デバイスカテゴリ別直帰率")
            fig2 = Visualization.create_bar_chart(
                device_summary,
                'deviceCategory',
                'bounceRate',
                "デバイスカテゴリ別直帰率",
                "デバイス",
                "直帰率"
            )
            st.plotly_chart(fig2, width="stretch")

            st.subheader("⚠️ 注意すべきデバイス")
            riskiest = device_summary.sort_values('bounceRate', ascending=False).head(1)
            if not riskiest.empty:
                row = riskiest.iloc[0]
                st.warning(
                    f"直帰率が最も高いデバイスは **{row['deviceCategory']}** ({row['bounceRate']*100:.1f}%) です。"
                )
            
            # 時系列データ
            if 'date' in device_data.columns:
                st.subheader("📈 デバイス別時系列トレンド")
                fig3 = go.Figure()
                colors = ['#5B4FDB', '#4A90E2', '#50C878']
                for i, device in enumerate(device_data['deviceCategory'].unique()):
                    device_df = device_data[device_data['deviceCategory'] == device].sort_values('date')
                    fig3.add_trace(go.Scatter(
                        x=device_df['date'],
                        y=device_df['sessions'],
                        mode='lines+markers',
                        name=device,
                        line=dict(width=2, color=colors[i % len(colors)]),
                        marker=dict(size=6)
                    ))
                fig3.update_layout(
                    title="デバイス別セッション数トレンド",
                    xaxis_title="日付",
                    yaxis_title="セッション数",
                    hovermode='x unified',
                    template='plotly_white',
                    font=dict(family="Noto Sans JP, Roboto, sans-serif"),
                    height=400
                )
                st.plotly_chart(fig3, width="stretch")
    else:
        st.info("データがありません")


def render_event_tab(ga4_client: GA4Client, start_date: str, end_date: str, site_scope: Optional[str]):
    """イベントタブをレンダリング（記事別分析）"""
    st.header("📰 記事別イベント分析")
    _render_tab_tip("event")
 
    event_names = get_cv_events_for_scope(site_scope)
    event_data = ga4_client.get_event_page_counts(
        start_date,
        end_date,
        site_scope=None,
        event_names=event_names,
        limit=1000
    )
 
    if event_data.empty:
        st.info("データがありません")
        return
 
    event_data['eventCount'] = event_data['eventCount'].astype(float)
    event_data = event_data.rename(columns={'pagePath': 'pagePath', 'eventName': 'eventName'})
 
    page_series = event_data['pagePath'].astype(str)
    prefixes = get_article_path_prefixes(site_scope)
    filtered = event_data.copy()
    mask_applied = False
    if prefixes:
        mask = pd.Series(False, index=event_data.index)
        for prefix in prefixes:
            mask = mask | page_series.str.contains(prefix, na=False)
        if mask.any():
            filtered = event_data[mask]
            mask_applied = True
    if not mask_applied:
        abitus_mask = page_series.str.contains("abitus.co.jp", case=False, na=False)
        if abitus_mask.any():
            filtered = event_data[abitus_mask]
            mask_applied = True
    if mask_applied:
        event_data = filtered
    else:
        st.info("アビタス（abitus.co.jp）に紐づく記事データが見つかりません。期間やサイト領域を変更してみてください。")
        return
 
    exclude_patterns = [
        '/thank',
        '/thanks',
        'request_thanks',
        'thank-you',
        'thankyou',
        '/lp-pathmake-co-jp/',
        'pathmake',
        '(not set)'
    ]
    filtered = event_data.copy()
    for pattern in exclude_patterns:
        filtered = filtered[~filtered['pagePath'].astype(str).str.contains(pattern, na=False)]
    event_data = filtered
 
    if event_data.empty:
        st.info("記事に該当するデータがありません")
        return
 
    with st.expander("生データ（参考）"):
        st.dataframe(event_data.head(30), width="stretch")
 
    overall = (
        event_data.groupby('pagePath')['eventCount']
        .sum()
        .reset_index()
        .sort_values('eventCount', ascending=False)
        .head(5)
    )
 
    st.subheader("イベント総数が多い記事 TOP5")
    if overall.empty:
        st.info("データがありません")
    else:
        display_overall = overall.rename(columns={'pagePath': '記事URL', 'eventCount': 'イベント総数'})
        st.dataframe(display_overall, width="stretch")
 
    st.subheader("イベント別 記事 TOP5")
    if event_names:
        display_mapping = {get_event_display_name(name): name for name in event_names}
        selected_display = st.selectbox("イベントを選択", list(display_mapping.keys()))
        selected_event = display_mapping[selected_display]
    else:
        st.info("イベント設定がありません")
        return
 
    event_df = (
        event_data[event_data['eventName'] == selected_event]
        .sort_values('eventCount', ascending=False)
        .head(5)
    )
 
    if event_df.empty:
        st.info("該当イベントのデータがありません")
        return
 
    display_df = event_df[['pagePath', 'eventCount']].rename(
        columns={'pagePath': '記事URL', 'eventCount': 'イベント数'}
    )
    st.dataframe(display_df, width="stretch")
 
 
@st.cache_data(ttl=30, hash_funcs={GA4Client: lambda client: client.property_id})  # 30秒間キャッシュ
def get_realtime_data_cached(ga4_client: GA4Client):
    """リアルタイムデータを取得（30秒キャッシュ）"""
    return ga4_client.get_realtime_data()


def render_realtime_tab(ga4_client: GA4Client, site_scope: Optional[str]):
    """リアルタイムタブをレンダリング"""
    st.header("⚡ リアルタイム")
    _render_tab_tip("realtime")
    
    # リアルタイムデータを取得（30秒キャッシュ）
    realtime_data = get_realtime_data_cached(ga4_client)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            "アクティブユーザー数",
            f"{int(realtime_data.get('activeUsers', 0)):,}",
            delta=None
        )
    
    # 過去30分間のページビューは別途実装が必要
    with col2:
        st.metric(
            "過去30分間のページビュー",
            "---",
            delta=None,
            help="この機能は今後実装予定です"
        )
    
    st.divider()
    
    # トップページ
    st.subheader("🔥 リアルタイムトップページ")
    top_pages = realtime_data.get('topPages', [])
    if top_pages:
        top_pages_df = pd.DataFrame(top_pages)
        st.dataframe(top_pages_df, width="stretch")
    else:
        st.info("データがありません")
    
    # 自動更新
    if st.button("🔄 更新"):
        get_realtime_data_cached.clear()
        st.rerun()


def render_utm_tab(ga4_client: GA4Client, start_date: str, end_date: str, site_scope: Optional[str]):
    """UTMタブをレンダリング"""
    st.header("📢 UTMパラメータ")
    _render_tab_tip("utm")
    
    utm_data = ga4_client.get_utm_data(start_date, end_date, site_scope=site_scope)
    
    if not utm_data.empty:
        st.subheader("📊 UTMパラメータ別データ")
        st.dataframe(utm_data, width="stretch")
        
        # キャンペーン別セッション数
        if 'sessionCampaignName' in utm_data.columns:
            campaign_data = utm_data.groupby('sessionCampaignName')['sessions'].sum().reset_index()
            campaign_data = campaign_data.sort_values('sessions', ascending=False).head(20)
            
            st.subheader("📈 キャンペーン別セッション数")
            fig = Visualization.create_bar_chart(
                campaign_data,
                'sessionCampaignName',
                'sessions',
                "キャンペーン別セッション数",
                "キャンペーン",
                "セッション数",
                orientation='h'
            )
            st.plotly_chart(fig, width="stretch")
    else:
        st.info("データがありません")


def render_seo_tab(ga4_client: GA4Client, gsc_client: Optional[GSCClient], start_date: str, end_date: str, site_scope: Optional[str]):
    """SEOタブをレンダリング"""
    st.header("🔍 SEO")
    _render_tab_tip("seo")
    
    if gsc_client is None:
        st.warning("Google Search Consoleが接続されていません。")
        return
    
    # GSCデータを取得
    query_data = gsc_client.get_query_data(start_date, end_date, limit=50)
    gsc_page_data = gsc_client.get_page_data(start_date, end_date, limit=50)
    
    # GA4データを取得
    ga4_page_data = ga4_client.get_page_data(start_date, end_date, limit=50, site_scope=site_scope)
    
    # データを統合
    if not gsc_page_data.empty and not ga4_page_data.empty:
        merged_data = DataProcessor.merge_ga4_gsc_data(
            ga4_page_data,
            gsc_page_data,
            ga4_url_column='pagePath',
            gsc_url_column='page'
        )
        
        st.subheader("📊 ページ別SEOパフォーマンス")
        st.dataframe(merged_data.head(20), width="stretch")
    else:
        st.info("データがありません")
    
    # 検索クエリデータ
    if not query_data.empty:
        st.subheader("🔎 検索クエリ別データ")
        query_data_sorted = query_data.sort_values('clicks', ascending=False).head(20)
        st.dataframe(query_data_sorted, width="stretch")
        
        # クリック数トップ10
        st.subheader("📈 クリック数トップ10")
        fig = Visualization.create_bar_chart(
            query_data_sorted.head(10),
            'query',
            'clicks',
            "クリック数トップ10",
            "検索クエリ",
            "クリック数",
            orientation='h'
        )
        st.plotly_chart(fig, width="stretch")


def render_dashboard_view(ga4_client: GA4Client, gsc_client: Optional[GSCClient], start_date: str, end_date: str, site_scope: Optional[str]):
    """ダッシュボードビューをレンダリング"""
    # タブを作成
    tabs = st.tabs([
        "概要", "流入元", "デバイス", "イベント", "リアルタイム", "UTM", "SEO"
    ])
    
    with tabs[0]:
        render_overview_tab(ga4_client, start_date, end_date, site_scope)
    
    with tabs[1]:
        render_traffic_source_tab(ga4_client, start_date, end_date, site_scope)
    
    with tabs[2]:
        render_device_tab(ga4_client, start_date, end_date, site_scope)
    
    with tabs[3]:
        render_event_tab(ga4_client, start_date, end_date, site_scope)
    
    with tabs[4]:
        render_realtime_tab(ga4_client, site_scope)
    
    with tabs[5]:
        render_utm_tab(ga4_client, start_date, end_date, site_scope)
    
    with tabs[6]:
        render_seo_tab(ga4_client, gsc_client, start_date, end_date, site_scope)

