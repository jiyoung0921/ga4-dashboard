"""ダッシュボードビューコンポーネント（Phase 1: 簡素化）"""
import streamlit as st
import pandas as pd
from modules.ga4_client import GA4Client
from modules.gsc_client import GSCClient
from modules.data_processor import DataProcessor
from modules.visualization import Visualization
from datetime import datetime, timedelta
import re
from typing import Optional, List, Dict, Tuple, Any
from textwrap import dedent
from components.icons import Icons
from components.messages import render_message
from utils.config import (
    get_cv_events_for_scope,
    get_event_display_name,
    get_article_path_prefixes,
    get_site_scope_options
)


@st.cache_data(ttl=300, hash_funcs={GA4Client: lambda client: client.property_id})  # 5分間キャッシュ
def get_overview_metrics_cached(ga4_client: GA4Client, start_date: str, end_date: str, site_scope: Optional[str]):
    """概要メトリクスを取得（キャッシュ付き）"""
    return ga4_client.get_overview_metrics(start_date, end_date, site_scope=site_scope)


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


@st.cache_data(ttl=300, hash_funcs={GA4Client: lambda client: client.property_id})
def get_event_sources_by_scope_cached(
    ga4_client: GA4Client,
    start_date: str,
    end_date: str
) -> pd.DataFrame:
    """サイト領域ごとのイベント参照元サマリ"""
    rows: List[pd.DataFrame] = []
    for option in get_site_scope_options():
        scope = option['value']
        event_names = get_cv_events_for_scope(scope)
        df = ga4_client.get_event_source_summary(
            start_date,
            end_date,
            site_scope=scope,
            event_names=event_names,
            limit=300
        )
        if df.empty:
            continue
        df['eventCount'] = df['eventCount'].astype(float)
        agg = (
            df.groupby('sessionSourceMedium')['eventCount']
            .sum()
            .reset_index()
            .sort_values('eventCount', ascending=False)
            .head(10)
        )
        agg['siteScope'] = scope
        rows.append(agg)
    if rows:
        return pd.concat(rows, ignore_index=True)
    return pd.DataFrame(columns=['sessionSourceMedium', 'eventCount', 'siteScope'])


SUBHEADER_ICON_COLOR = "#7C6AEF"


def _render_subsection_heading(icon_svg: str, text: str) -> None:
    """Lucideアイコン付きのサブヘッダーを描画"""
    st.markdown(
        f"""
        <div style="
            display: flex;
            align-items: center;
            gap: 10px;
            margin: 1.25rem 0 0.75rem;
        ">
            <span style="
                width: 32px;
                height: 32px;
                border-radius: 10px;
                background: rgba(124, 106, 239, 0.12);
                display: inline-flex;
                align-items: center;
                justify-content: center;
            ">{icon_svg}</span>
            <span style="
                font-size: 1rem;
                font-weight: 700;
                color: #2D3748;
            ">{text}</span>
        </div>
        """,
        unsafe_allow_html=True
    )


USCPA_SOURCE_PATTERNS = [
    {"label": "Google広告 (google / cpc)", "pattern": r"google\s*/\s*cpc"},
    {"label": "Yahoo広告 (yahoo / cpc)", "pattern": r"yahoo\s*/\s*cpc"},
    {"label": "Facebook広告 (facebook / banner)", "pattern": r"facebook\s*/\s*banner"},
    {"label": "Facebook海外 (facebook_foreign / banner)", "pattern": r"facebook_foreign\s*/\s*banner"},
    {"label": "アフィリエイト", "pattern": r"aff"},
    {"label": "Google自然検索 (google / organic)", "pattern": r"google\s*/\s*organic"},
    {"label": "Yahoo自然検索 (yahoo / organic)", "pattern": r"yahoo\s*/\s*organic"},
    {"label": "ダイレクト", "pattern": r"direct"},
    {"label": "リファラル", "pattern": r"referral"}
]

USCPA_COMBINED_PATTERN = "(" + "|".join(pattern['pattern'] for pattern in USCPA_SOURCE_PATTERNS) + ")"


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


def _render_event_source_summary(ga4_client: GA4Client, start_date: str, end_date: str) -> None:
    summary_df = get_event_sources_by_scope_cached(ga4_client, start_date, end_date)
    if summary_df.empty:
        render_message("参照元別のイベントデータがありません。")
        return
    summary_df = summary_df.rename(columns={
        'sessionSourceMedium': '参照元/メディア',
        'eventCount': 'イベント数',
        'siteScope': 'サイト領域'
    })
    _render_subsection_heading(
        Icons.layers(18, SUBHEADER_ICON_COLOR),
        "サイト領域別 イベント参照元（上位）"
    )
    st.dataframe(summary_df[['サイト領域', '参照元/メディア', 'イベント数']], width="stretch")


def _render_uscpa_source_breakdown(ga4_client: GA4Client, start_date: str, end_date: str) -> None:
    source_data = ga4_client.get_traffic_source(start_date, end_date, site_scope="USCPA")
    if source_data.empty:
        render_message("USCPAの参照元データがありません。")
        return
    source_data = source_data.copy()
    source_data['sourceMedium'] = (
        source_data['sessionSource'].fillna('(not set)').astype(str)
        + " / " +
        source_data['sessionMedium'].fillna('(not set)').astype(str)
    )
    source_data['sessions'] = source_data['sessions'].astype(float)

    summary_rows = []
    for pattern_conf in USCPA_SOURCE_PATTERNS:
        regex = re.compile(pattern_conf['pattern'], re.IGNORECASE)
        mask = source_data['sourceMedium'].apply(lambda val: bool(regex.search(val)))
        total = source_data.loc[mask, 'sessions'].sum()
        summary_rows.append({
            'カテゴリ': pattern_conf['label'],
            'セッション数': int(total)
        })

    summary_df = pd.DataFrame(summary_rows).sort_values('セッション数', ascending=False)

    combined_mask = source_data['sourceMedium'].str.contains(USCPA_COMBINED_PATTERN, case=False, regex=True)
    detail_df = (
        source_data.loc[combined_mask, ['sourceMedium', 'sessions']]
        .rename(columns={'sourceMedium': '参照元/メディア', 'sessions': 'セッション数'})
        .sort_values('セッション数', ascending=False)
    )

    _render_subsection_heading(
        Icons.map_pin(18, SUBHEADER_ICON_COLOR),
        "USCPA 参照元/メディア別セッション"
    )
    st.dataframe(summary_df, width="stretch")
    if not detail_df.empty:
        st.caption("一致した参照元/メディアの詳細")
        st.dataframe(detail_df, width="stretch")


def _render_kpi_cards(cards: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    selected_card: Optional[Dict[str, Any]] = None
    chunk_size = 4
    for i in range(0, len(cards), chunk_size):
        chunk = cards[i:i + chunk_size]
        cols = st.columns(len(chunk))
        for col, card in zip(cols, chunk):
            value_text = card['value_text']
            delta_text = card.get('delta_text', '')
            delta_class = card.get('delta_class', '')
            prev_text = card.get('previous_text', '')
            with col:
                card_html = dedent(
                    f"""
                    <div class="kpi-card">
                        <div class="kpi-card__meta">
                            <div class="kpi-label">{card['label']}</div>
                            <div class="kpi-chip">{card.get('chip_text', '')}</div>
                        </div>
                        <div class="kpi-value">{value_text}</div>
                        <div class="kpi-divider"></div>
                        <div class="kpi-prev">前期間: {prev_text if prev_text else '-'}</div>
                        {f'<div class="kpi-delta {delta_class}">{delta_text}</div>' if delta_text else ''}
                    </div>
                    """
                ).strip()
                st.markdown(card_html, unsafe_allow_html=True)
                if st.button(
                    "週次推移を見る",
                    key=f"kpi_button_{card['id']}"
                ):
                    if selected_card is None:
                        selected_card = card
    return selected_card


def _render_kpi_cards_with_breakdown(
    cards: List[Dict[str, Any]],
    ga4_client: GA4Client,
    start_date: str,
    end_date: str,
    site_scope: Optional[str]
) -> Optional[Dict[str, Any]]:
    """KPIカードをレンダリング（週次推移＋参照元ブレークダウンボタン付き）"""
    selected_card: Optional[Dict[str, Any]] = None
    chunk_size = 4
    
    for i in range(0, len(cards), chunk_size):
        chunk = cards[i:i + chunk_size]
        cols = st.columns(len(chunk))
        for col, card in zip(cols, chunk):
            value_text = card['value_text']
            delta_text = card.get('delta_text', '')
            delta_class = card.get('delta_class', '')
            prev_text = card.get('previous_text', '')
            with col:
                card_html = dedent(
                    f"""
                    <div class="kpi-card">
                        <div class="kpi-card__meta">
                            <div class="kpi-label">{card['label']}</div>
                            <div class="kpi-chip">{card.get('chip_text', '')}</div>
                        </div>
                        <div class="kpi-value">{value_text}</div>
                        <div class="kpi-divider"></div>
                        <div class="kpi-prev">前期間: {prev_text if prev_text else '-'}</div>
                        {f'<div class="kpi-delta {delta_class}">{delta_text}</div>' if delta_text else ''}
                    </div>
                    """
                ).strip()
                st.markdown(card_html, unsafe_allow_html=True)
                
                # ボタン行（2カラム）
                btn_col1, btn_col2 = st.columns(2)
                with btn_col1:
                    if st.button(
                        "📈 週次推移",
                        key=f"kpi_button_{card['id']}",
                        use_container_width=True
                    ):
                        if selected_card is None:
                            selected_card = card
                
                with btn_col2:
                    # CVイベントの場合のみ参照元ボタンを表示
                    if card['metric_type'] == 'event':
                        if st.button(
                            "🔍 参照元",
                            key=f"breakdown_button_{card['id']}",
                            use_container_width=True
                        ):
                            st.session_state['breakdown_modal'] = {
                                'card': card,
                                'start_date': start_date,
                                'end_date': end_date,
                                'site_scope': site_scope
                            }
    
    # 参照元ブレークダウンモーダルの表示
    breakdown_info = st.session_state.pop('breakdown_modal', None)
    if breakdown_info:
        _show_event_source_breakdown(
            breakdown_info['card'],
            ga4_client,
            breakdown_info['start_date'],
            breakdown_info['end_date'],
            breakdown_info['site_scope']
        )
    
    return selected_card


def _show_event_source_breakdown(
    card: Dict[str, Any],
    ga4_client: GA4Client,
    start_date: str,
    end_date: str,
    site_scope: Optional[str]
) -> None:
    """イベントの参照元ブレークダウンを表示"""
    event_name = card.get('metric_key')
    if not event_name:
        return
    
    container = st.container()
    with container:
        _render_subsection_heading(
            Icons.share_2(18, SUBHEADER_ICON_COLOR),
            f"{card['label']}の参照元内訳"
        )
        
        # イベントの参照元別データを取得
        df = ga4_client.get_event_source_summary(
            start_date,
            end_date,
            site_scope=site_scope,
            event_names=[event_name],
            limit=100
        )
        
        if df.empty:
            render_message("参照元データがありません")
        else:
            # 参照元/メディア別に集計
            df['eventCount'] = df['eventCount'].astype(float)
            source_summary = (
                df.groupby('sessionSourceMedium')['eventCount']
                .sum()
                .reset_index()
                .sort_values('eventCount', ascending=False)
                .head(10)
            )
            
            if source_summary.empty:
                render_message("参照元データがありません")
            else:
                # グラフ表示
                fig = Visualization.create_bar_chart(
                    source_summary,
                    'sessionSourceMedium',
                    'eventCount',
                    f"{card['label']}の参照元別発生数",
                    "参照元/メディア",
                    "イベント数",
                    orientation='h'
                )
                st.plotly_chart(fig, width="stretch")
                
                # テーブル表示
                display_df = source_summary.rename(columns={
                    'sessionSourceMedium': '参照元/メディア',
                    'eventCount': 'イベント数'
                })
                st.dataframe(display_df, width="stretch")
                
                # 合計
                total = source_summary['eventCount'].sum()
                st.caption(f"合計: {int(total):,} 件")
        
        if st.button("閉じる", key=f"close_breakdown_{card['id']}"):
            container.empty()


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
        _render_subsection_heading(
            Icons.line_chart(18, SUBHEADER_ICON_COLOR),
            f"{card['label']}の週次推移"
        )
        if weekly.empty:
            render_message("データがありません")
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

        if st.button("閉じる", key=f"close_modal_{card['id']}"):
            container.empty()


def render_overview_tab(ga4_client: GA4Client, start_date: str, end_date: str, site_scope: Optional[str]):
    """概要タブをレンダリング（Phase 1: 流入元・UTM情報を統合）"""
    from components.header import render_section_header
    render_section_header("overview", "概要")
    
    # メトリクスを取得
    metrics = get_overview_metrics_cached(ga4_client, start_date, end_date, site_scope)
    prev_start, prev_end = _calculate_previous_period(start_date, end_date)
    previous_metrics = get_overview_metrics_cached(ga4_client, prev_start, prev_end, site_scope)

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
        'chip_text': '主要指標',
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
            'chip_text': 'CV',
            'id': f"event_{event_name}",
            'metric_type': 'event',
            'metric_key': event_name
        })

    # KPIカードをレンダリング（参照元ブレークダウンボタン付き）
    selected_card = _render_kpi_cards_with_breakdown(cards, ga4_client, start_date, end_date, site_scope)
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

    st.divider()

    # === 流入元情報（統合） ===
    _render_subsection_heading(
        Icons.share_2(18, SUBHEADER_ICON_COLOR),
        "チャネルグループ別セッション数"
    )
    source_data = ga4_client.get_traffic_source(start_date, end_date, site_scope=site_scope)
    if not source_data.empty and 'sessionDefaultChannelGroup' in source_data.columns:
        channel_group = source_data.groupby('sessionDefaultChannelGroup')['sessions'].sum().reset_index()
        channel_group = channel_group.sort_values('sessions', ascending=False)
        fig = Visualization.create_bar_chart(
            channel_group,
            'sessionDefaultChannelGroup',
            'sessions',
            "",
            "チャネルグループ",
            "セッション数",
            orientation='h'
        )
        st.plotly_chart(fig, width="stretch")
    else:
        render_message("チャネルグループデータがありません")

    st.divider()

    # === UTM/キャンペーン情報（統合） ===
    _render_subsection_heading(
        Icons.megaphone(18, SUBHEADER_ICON_COLOR),
        "キャンペーン別セッション数"
    )
    utm_data = ga4_client.get_utm_data(start_date, end_date, site_scope=site_scope)
    if not utm_data.empty and 'sessionCampaignName' in utm_data.columns:
        campaign_data = utm_data.groupby('sessionCampaignName')['sessions'].sum().reset_index()
        campaign_data = campaign_data.sort_values('sessions', ascending=False).head(10)
        # (not set)を除外
        campaign_data = campaign_data[campaign_data['sessionCampaignName'] != '(not set)']
        if not campaign_data.empty:
            fig = Visualization.create_bar_chart(
                campaign_data,
                'sessionCampaignName',
                'sessions',
                "",
                "キャンペーン",
                "セッション数",
                orientation='h'
            )
            st.plotly_chart(fig, width="stretch")
        else:
            render_message("有効なキャンペーンデータがありません")
    else:
        render_message("キャンペーンデータがありません")

    st.divider()

    # === イベント参照元サマリー ===
    _render_event_source_summary(ga4_client, start_date, end_date)

    # USCPA固有の参照元分析
    if site_scope == "USCPA":
        _render_uscpa_source_breakdown(ga4_client, start_date, end_date)


def _convert_landing_page_to_url(landing_page: str) -> str:
    """GA4のlandingPage形式をURLに変換
    例: /www-abitus-co-jp/lp/uscpa/ad8d → https://www.abitus.co.jp/lp/uscpa/ad8d
    """
    if not landing_page or landing_page == '(not set)':
        return ''
    
    # 先頭のスラッシュを除去
    path = landing_page.lstrip('/')
    
    # ドメイン部分を抽出して変換
    # /www-abitus-co-jp/path → https://www.abitus.co.jp/path
    parts = path.split('/', 1)
    domain_part = parts[0]
    rest_path = '/' + parts[1] if len(parts) > 1 else '/'
    
    # ハイフンをドットに変換してドメインを復元
    # www-abitus-co-jp → www.abitus.co.jp
    domain = domain_part.replace('-', '.')
    
    return f"https://{domain}{rest_path}"


def _render_landing_page_table(df: pd.DataFrame, page_col: str, count_col: str, title_col: str = None):
    """ランディングページのテーブルをタイトル＋リンクアイコン形式で表示"""
    
    if df.empty:
        render_message("データがありません")
        return
    
    # ヘッダー
    cols = st.columns([5, 1])
    cols[0].markdown("**ページ**")
    cols[1].markdown("**CV数**")
    
    st.markdown("<hr style='margin: 8px 0; border: none; border-top: 1px solid #E2E8F0;'>", unsafe_allow_html=True)
    
    for _, row in df.iterrows():
        landing_page = row[page_col]
        count = int(row[count_col])
        
        # ページタイトルがあれば使用、なければパスから生成
        if title_col and title_col in row and row[title_col] and row[title_col] != '(not set)':
            display_title = row[title_col]
            # タイトルが長すぎる場合は省略
            if len(display_title) > 60:
                display_title = display_title[:57] + '...'
        else:
            # パスから簡易タイトルを生成
            display_title = landing_page.split('/')[-1] if '/' in landing_page else landing_page
            if not display_title or display_title == '(not set)':
                display_title = landing_page
        
        url = _convert_landing_page_to_url(landing_page)
        
        cols = st.columns([5, 1])
        
        # タイトル＋リンクアイコン
        if url:
            link_icon = Icons.external_link(14, "#718096")
            cols[0].markdown(
                f"""<div style="display: flex; align-items: center; gap: 8px;">
                    <span style="font-size: 14px;">{display_title}</span>
                    <a href="{url}" target="_blank" rel="noopener noreferrer" 
                       style="display: inline-flex; text-decoration: none;" 
                       title="{url}">{link_icon}</a>
                </div>""",
                unsafe_allow_html=True
            )
        else:
            cols[0].markdown(f"<span style='font-size: 14px;'>{display_title}</span>", unsafe_allow_html=True)
        
        cols[1].markdown(f"<span style='font-size: 14px; font-weight: 600;'>{count:,}</span>", unsafe_allow_html=True)


def render_event_tab(ga4_client: GA4Client, start_date: str, end_date: str, site_scope: Optional[str]):
    """イベントタブをレンダリング（ランディングページ別CV分析）"""
    from components.header import render_section_header
    render_section_header("event", "ランディングページ別CV分析")
    
    st.caption("💡 どの記事（ランディングページ）からCVが発生したかを分析します")
 
    event_names = get_cv_events_for_scope(site_scope)
    
    # ランディングページ×CVイベント×ページタイトルのデータを取得
    event_data = ga4_client.get_cv_by_landing_page_with_title(
        start_date,
        end_date,
        site_scope=site_scope,
        event_names=event_names,
        limit=1000
    )
 
    if event_data.empty:
        render_message("データがありません。期間を広げてみてください。", "warning")
        return
 
    event_data['eventCount'] = event_data['eventCount'].astype(float)
    
    # (not set)やサンクスページを除外
    exclude_patterns = ['(not set)', '(none)', 'thank', 'pathmake']
    
    page_series = event_data['landingPage'].astype(str).str.lower()
    mask = ~page_series.str.contains('|'.join(exclude_patterns), case=False, na=False, regex=True)
    event_data = event_data[mask]
 
    if event_data.empty:
        render_message("フィルタ後のデータがありません。期間を広げてみてください。", "warning")
        return
 
    with st.expander("生データ（参考）", expanded=False):
        st.write(f"取得件数: {len(event_data)} 件")
        st.dataframe(event_data.head(30), use_container_width=True)
    
    # ページタイトルのマッピングを作成（landingPage → pageTitle）
    title_map = event_data.groupby('landingPage')['pageTitle'].first().to_dict()
 
    # CV総数が多いランディングページ TOP10
    overall = (
        event_data.groupby('landingPage')['eventCount']
        .sum()
        .reset_index()
        .sort_values('eventCount', ascending=False)
        .head(10)
    )
    # ページタイトルを追加
    overall['pageTitle'] = overall['landingPage'].map(title_map)
 
    _render_subsection_heading(
        Icons.bar_chart_3(18, SUBHEADER_ICON_COLOR),
        "CV総数が多いランディングページ TOP10"
    )
    _render_landing_page_table(overall, 'landingPage', 'eventCount', 'pageTitle')
    
    # グラフも表示（タイトルを使用）
    if not overall.empty:
        chart_df = overall.copy()
        chart_df['displayLabel'] = chart_df.apply(
            lambda r: (r['pageTitle'][:30] + '...' if len(str(r['pageTitle'])) > 30 else r['pageTitle']) 
                      if r['pageTitle'] and r['pageTitle'] != '(not set)' 
                      else r['landingPage'].split('/')[-1],
            axis=1
        )
        fig = Visualization.create_bar_chart(
            chart_df.head(10),
            'displayLabel',
            'eventCount',
            "",
            "ランディングページ",
            "CV数",
            orientation='h'
        )
        st.plotly_chart(fig, use_container_width=True)
 
    st.divider()
    
    # イベント別のランディングページ TOP10
    _render_subsection_heading(
        Icons.target(18, SUBHEADER_ICON_COLOR),
        "イベント別 ランディングページ TOP10"
    )
    if event_names:
        display_mapping = {get_event_display_name(name): name for name in event_names}
        selected_display = st.selectbox("CVイベントを選択", list(display_mapping.keys()))
        selected_event = display_mapping[selected_display]
    else:
        render_message("イベント設定がありません")
        return
 
    event_df = (
        event_data[event_data['eventName'] == selected_event]
        .sort_values('eventCount', ascending=False)
        .head(10)
    )
 
    if event_df.empty:
        render_message("該当イベントのデータがありません")
        return
 
    _render_landing_page_table(event_df, 'landingPage', 'eventCount', 'pageTitle')
    
    # グラフ
    if not event_df.empty:
        chart_df = event_df.copy()
        chart_df['displayLabel'] = chart_df.apply(
            lambda r: (r['pageTitle'][:30] + '...' if len(str(r['pageTitle'])) > 30 else r['pageTitle']) 
                      if r['pageTitle'] and r['pageTitle'] != '(not set)' 
                      else r['landingPage'].split('/')[-1],
            axis=1
        )
        fig = Visualization.create_bar_chart(
            chart_df.head(10),
            'displayLabel',
            'eventCount',
            f"{selected_display}のランディングページ別CV数",
            "ランディングページ",
            "CV数",
            orientation='h'
        )
        st.plotly_chart(fig, use_container_width=True)
 


def render_seo_tab(ga4_client: GA4Client, gsc_client: Optional[GSCClient], start_date: str, end_date: str, site_scope: Optional[str]):
    """SEOタブをレンダリング"""
    from components.header import render_section_header
    render_section_header("seo", "SEO")
    
    if gsc_client is None:
        render_message("Google Search Consoleが接続されていません。", "warning")
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
        
        _render_subsection_heading(
            Icons.search(18, SUBHEADER_ICON_COLOR),
            "ページ別SEOパフォーマンス"
        )
        st.dataframe(merged_data.head(20), width="stretch")
    else:
        render_message("データがありません")
    
    # 検索クエリデータ
    if not query_data.empty:
        _render_subsection_heading(
            Icons.search(18, SUBHEADER_ICON_COLOR),
            "検索クエリ別データ"
        )
        query_data_sorted = query_data.sort_values('clicks', ascending=False).head(20)
        st.dataframe(query_data_sorted, width="stretch")
        
        # クリック数トップ10
        _render_subsection_heading(
            Icons.trending_up(18, SUBHEADER_ICON_COLOR),
            "クリック数トップ10"
        )
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


def render_dashboard_view(
    ga4_client: GA4Client,
    gsc_client: Optional[GSCClient],
    start_date: str,
    end_date: str,
    site_scope: Optional[str]
):
    """ダッシュボードビューをレンダリング（Phase 1: 簡素化）"""
    # タブを作成（概要・イベント・SEOの3タブに集約）
    tabs = st.tabs([
        "概要", "イベント", "SEO"
    ])
    
    with tabs[0]:
        render_overview_tab(ga4_client, start_date, end_date, site_scope)
    
    with tabs[1]:
        render_event_tab(ga4_client, start_date, end_date, site_scope)
    
    with tabs[2]:
        render_seo_tab(ga4_client, gsc_client, start_date, end_date, site_scope)

