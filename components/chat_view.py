"""チャットビューコンポーネント"""
import streamlit as st
import pandas as pd
from modules.ga4_client import GA4Client
from modules.gsc_client import GSCClient
from modules.query_parser import QueryParser
from modules.data_processor import DataProcessor
from modules.visualization import Visualization
from typing import Optional, Dict, Any
from utils.config import (
    get_event_alias_map,
    get_event_display_name
)
from datetime import datetime, timedelta


def initialize_chat_history():
    """チャット履歴を初期化"""
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []


def add_message(role: str, content: str, data: Optional[Any] = None):
    """メッセージを履歴に追加"""
    st.session_state.chat_history.append({
        'role': role,
        'content': content,
        'data': data
    })


EXAMPLE_QUESTIONS = [
    "USCPAの過去7日間のセッション数は？",
    "MBAの資料請求は今月どれくらい？",
    "USCPAのオンラインセミナー予約は先週何件？",
    "過去30日間で流入元トップ5は？",
    "USCPAのCV総数を直近30日で教えて",
    "今週と先週のセッション数を比較して",
    "MBAのカウンセリング予約の推移を教えて",
    "USCPAのイベント数トップ3は？",
    "今月の問合せ件数は？",
    "MBAのコンバージョン合計は？"
]


def _render_chat_tip():
    st.markdown(
        """
        <div class="ux-tip-card">
            <div class="ux-tip-title">まずは気軽に質問してみましょう</div>
            <p style="margin-bottom:0;">代表質問のボタンを押すだけでテンプレートが入力されます。最初の一歩を踏み出せるようにカード状に並べています。</p>
        </div>
        """,
        unsafe_allow_html=True
    )


def _calculate_previous_period(start_date: str, end_date: str) -> tuple[str, str]:
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    period_days = (end_dt - start_dt).days + 1
    prev_end = start_dt - timedelta(days=1)
    prev_start = prev_end - timedelta(days=period_days - 1)
    return prev_start.strftime("%Y-%m-%d"), prev_end.strftime("%Y-%m-%d")


def _detect_event_from_query(query: str) -> Optional[str]:
    alias_map = get_event_alias_map()
    for alias, event_name in alias_map.items():
        if alias in query:
            return event_name
    return None


def render_chat_view(ga4_client: GA4Client, gsc_client: Optional[GSCClient], start_date: str, end_date: str, site_scope: Optional[str]):
    """チャットビューをレンダリング"""
    st.header("💬 対話アシスタント")
    _render_chat_tip()
    
    initialize_chat_history()

    st.markdown("**よく使う質問例**")
    columns = st.columns(3)
    for idx, question in enumerate(EXAMPLE_QUESTIONS):
        col = columns[idx % 3]
        if col.button(question, key=f"example_q_{idx}"):
            st.session_state['chat_prefill'] = question
        if (idx % 3 == 2) and (idx != len(EXAMPLE_QUESTIONS) - 1):
            columns = st.columns(3)
    
    # チャット履歴を表示
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.chat_history:
            if message['role'] == 'user':
                with st.chat_message("user"):
                    st.write(message['content'])
            elif message['role'] == 'assistant':
                with st.chat_message("assistant"):
                    st.write(message['content'])
                    # データがある場合は表示
                    if message.get('data'):
                        data = message['data']
                        if isinstance(data, dict):
                            if 'graph' in data:
                                st.plotly_chart(data['graph'], width="stretch")
                            if 'table' in data:
                                st.dataframe(data['table'], width="stretch")
    
    # 質問入力
    chat_input_key = 'chat_user_input'
    prefill = st.session_state.pop('chat_prefill', None)
    if prefill:
        st.session_state[chat_input_key] = prefill
    user_query = st.chat_input("質問を入力してください（例: 過去7日間のセッション数は？）", key=chat_input_key)
    
    if user_query:
        # ユーザーメッセージを追加
        add_message('user', user_query)
        
        # 質問を解析
        parsed = QueryParser.parse_query(user_query)
        
        if not QueryParser.is_valid_query(parsed):
            response = "申し訳ございません。質問を理解できませんでした。期間を指定してください。"
            add_message('assistant', response)
            st.rerun()
        
        # 解析された期間を使用（指定されていない場合はデフォルト期間を使用）
        query_start_date = parsed['period'][0]
        query_end_date = parsed['period'][1]
        
        # 質問タイプに応じて処理
        query_type = QueryParser.get_query_type(parsed)
        response_data = {}

        detected_event = _detect_event_from_query(user_query)

        try:
            if detected_event:
                # イベント名が含まれる質問
                current_counts = ga4_client.get_event_counts_by_names(
                    query_start_date, query_end_date, [detected_event], site_scope
                )
                prev_start, prev_end = _calculate_previous_period(query_start_date, query_end_date)
                previous_counts = ga4_client.get_event_counts_by_names(
                    prev_start, prev_end, [detected_event], site_scope
                )
                current_value = current_counts.get(detected_event, 0)
                previous_value = previous_counts.get(detected_event, 0)
                diff = current_value - previous_value
                diff_percent = (diff / previous_value * 100) if previous_value else 0
                display_name = get_event_display_name(detected_event)

                response = (
                    f"{query_start_date}から{query_end_date}までの{display_name}件数は"
                    f" {int(current_value):,} 件です。"
                )
                if previous_value:
                    sign = '+' if diff >= 0 else ''
                    response += (
                        f" 前期間（{prev_start}〜{prev_end}）は {int(previous_value):,} 件で、"
                        f"差は {sign}{int(diff):,} 件（{sign}{diff_percent:.1f}%）でした。"
                    )

                response_data['table'] = pd.DataFrame([
                    {
                        '期間': f"{query_start_date}〜{query_end_date}",
                        '件数': int(current_value)
                    },
                    {
                        '期間': f"{prev_start}〜{prev_end}",
                        '件数': int(previous_value)
                    }
                ])

                add_message('assistant', response, response_data)
                st.rerun()

            if query_type == 'metric_only':
                # 指標のみの質問
                metric = parsed.get('metric')
                if metric:
                    metrics_data = ga4_client.get_overview_metrics(query_start_date, query_end_date, site_scope=site_scope)
                    metric_value = metrics_data.get(metric, 0)
                    metric_name_jp = metric_labels.get(metric, metric)
                    
                    if metric in rate_metrics:
                        response = f"{query_start_date}から{query_end_date}までの{metric_name_jp}は {metric_value * 100:.2f}% です。"
                    elif metric in duration_metrics:
                        minutes = int(metric_value // 60)
                        seconds = int(metric_value % 60)
                        response = f"{query_start_date}から{query_end_date}までの{metric_name_jp}は {minutes}分{seconds}秒 です。"
                    else:
                        response = f"{query_start_date}から{query_end_date}までの{metric_name_jp}は {int(metric_value):,} です。"
                else:
                    response = "指標を特定できませんでした。"
            
            elif query_type == 'dimension_metric':
                # ディメンションと指標の組み合わせ
                dimension = parsed.get('dimension')
                metric = parsed.get('metric')
                ranking = parsed.get('ranking', 10)
                
                def aggregate_metric(df: pd.DataFrame, group_col: str) -> Optional[pd.DataFrame]:
                    if metric not in df.columns:
                        return None
                    agg_func = 'mean' if metric in non_sum_metrics else 'sum'
                    aggregated = df.groupby(group_col)[metric].agg(agg_func).reset_index()
                    return aggregated.sort_values(metric, ascending=False)

                def prepare_display(df: pd.DataFrame):
                    display_df = df.copy()
                    y_axis_label = metric_labels.get(metric, metric)
                    if metric in rate_metrics:
                        display_df[metric] = display_df[metric] * 100
                        y_axis_label += "（%）"
                    elif metric in duration_metrics:
                        display_df[metric] = display_df[metric] / 60
                        y_axis_label += "（分）"
                    if metric in non_sum_metrics:
                        display_df[metric] = display_df[metric].round(2)
                    return display_df, y_axis_label

                if dimension == 'sessionSource':
                    # 流入元別データ
                    source_data = ga4_client.get_traffic_source(query_start_date, query_end_date, site_scope=site_scope)
                    if not source_data.empty:
                        source_summary = aggregate_metric(source_data, 'sessionSource')
                        if source_summary is None:
                            response = f"{metric_labels.get(metric, metric)}には対応していません。"
                        else:
                            source_summary = source_summary.head(ranking)
                            display_df, y_axis_label = prepare_display(source_summary)
                            response = f"流入元別{metric_labels.get(metric, metric)}のトップ{ranking}は以下の通りです。"
                            response_data['table'] = display_df
                            # グラフも作成
                            fig = Visualization.create_bar_chart(
                                display_df,
                                'sessionSource',
                                metric,
                                f"流入元別{metric_labels.get(metric, metric)}",
                                "流入元",
                                y_axis_label,
                                orientation='h'
                            )
                            response_data['graph'] = fig
                    else:
                        response = "データがありません。"
                
                elif dimension == 'sessionDefaultChannelGroup':
                    channel_data = ga4_client.get_traffic_source(query_start_date, query_end_date, site_scope=site_scope)
                    if not channel_data.empty:
                        channel_summary = aggregate_metric(channel_data, 'sessionDefaultChannelGroup')
                        if channel_summary is None:
                            response = f"{metric_labels.get(metric, metric)}には対応していません。"
                        else:
                            channel_summary = channel_summary.head(ranking)
                            display_df, y_axis_label = prepare_display(channel_summary)
                            response = f"チャネル別{metric_labels.get(metric, metric)}は以下の通りです。"
                            response_data['table'] = display_df
                            fig = Visualization.create_bar_chart(
                                display_df,
                                'sessionDefaultChannelGroup',
                                metric,
                                f"チャネル別{metric_labels.get(metric, metric)}",
                                "チャネル",
                                y_axis_label,
                                orientation='h'
                            )
                            response_data['graph'] = fig
                    else:
                        response = "データがありません。"

                elif dimension == 'deviceCategory':
                    # デバイス別データ
                    device_data = ga4_client.get_device_data(query_start_date, query_end_date, site_scope=site_scope)
                    if not device_data.empty:
                        device_summary = aggregate_metric(device_data, 'deviceCategory')
                        if device_summary is None:
                            response = f"{metric_labels.get(metric, metric)}には対応していません。"
                        else:
                            display_df, y_axis_label = prepare_display(device_summary)
                            response = f"デバイス別{metric_labels.get(metric, metric)}は以下の通りです。"
                            response_data['table'] = display_df
                            fig = Visualization.create_bar_chart(
                                display_df,
                                'deviceCategory',
                                metric,
                                f"デバイス別{metric_labels.get(metric, metric)}",
                                "デバイス",
                                y_axis_label
                            )
                            response_data['graph'] = fig
                    else:
                        response = "データがありません。"
                
                elif dimension == 'sessionCampaignName':
                    utm_data = ga4_client.get_utm_data(query_start_date, query_end_date, site_scope=site_scope)
                    if not utm_data.empty:
                        utm_summary = aggregate_metric(utm_data, 'sessionCampaignName')
                        if utm_summary is None:
                            response = f"{metric_labels.get(metric, metric)}には対応していません。"
                        else:
                            utm_summary = utm_summary.head(ranking)
                            display_df, y_axis_label = prepare_display(utm_summary)
                            response = f"キャンペーン別{metric_labels.get(metric, metric)}は以下の通りです。"
                            response_data['table'] = display_df
                            fig = Visualization.create_bar_chart(
                                display_df,
                                'sessionCampaignName',
                                metric,
                                f"キャンペーン別{metric_labels.get(metric, metric)}",
                                "キャンペーン",
                                y_axis_label,
                                orientation='h'
                            )
                            response_data['graph'] = fig
                    else:
                        response = "データがありません。"

                elif dimension == 'pagePath':
                    page_data = ga4_client.get_page_data(query_start_date, query_end_date, site_scope=site_scope)
                    if not page_data.empty:
                        page_summary = aggregate_metric(page_data, 'pagePath')
                        if page_summary is None:
                            response = f"{metric_labels.get(metric, metric)}には対応していません。"
                        else:
                            page_summary = page_summary.head(ranking)
                            display_df, y_axis_label = prepare_display(page_summary)
                            response = f"ページ別{metric_labels.get(metric, metric)}は以下の通りです。"
                            response_data['table'] = display_df
                            fig = Visualization.create_bar_chart(
                                display_df,
                                'pagePath',
                                metric,
                                f"ページ別{metric_labels.get(metric, metric)}",
                                "ページ",
                                y_axis_label,
                                orientation='h'
                            )
                            response_data['graph'] = fig
                    else:
                        response = "データがありません。"

                else:
                    response = f"ディメンション '{dimension}' にはまだ対応していません。"
            
            elif query_type == 'ranking':
                # ランキング質問
                metric = parsed.get('metric', 'sessions')
                ranking = parsed.get('ranking', 10)
                dimension = parsed.get('dimension')
                
                if dimension == 'sessionSource' or not dimension:
                    # 流入元ランキング
                    source_data = ga4_client.get_traffic_source(query_start_date, query_end_date, site_scope=site_scope)
                    if not source_data.empty:
                        source_summary = source_data.groupby('sessionSource')['sessions'].sum().reset_index()
                        source_summary = source_summary.sort_values('sessions', ascending=False).head(ranking)
                        
                        response = f"流入元トップ{ranking}は以下の通りです。"
                        response_data['table'] = source_summary
                        
                        fig = Visualization.create_bar_chart(
                            source_summary,
                            'sessionSource',
                            'sessions',
                            f"流入元トップ{ranking}",
                            "流入元",
                            "セッション数",
                            orientation='h'
                        )
                        response_data['graph'] = fig
                    else:
                        response = "データがありません。"
                else:
                    response = "このランキングにはまだ対応していません。"
            
            elif query_type == 'comparison':
                # 比較質問
                response = "比較機能は現在開発中です。"
            
            else:
                # 一般的な質問
                # 概要データを表示
                metrics_data = ga4_client.get_overview_metrics(query_start_date, query_end_date, site_scope=site_scope)
                daily_traffic = ga4_client.get_daily_traffic(query_start_date, query_end_date, site_scope=site_scope)
                
                response = f"{query_start_date}から{query_end_date}までの概要データです。"
                
                # グラフを作成
                if not daily_traffic.empty:
                    fig = Visualization.create_line_chart(
                        daily_traffic,
                        'date',
                        ['sessions', 'totalUsers', 'screenPageViews'],
                        "日別トラフィック",
                        "日付",
                        "数"
                    )
                    response_data['graph'] = fig
                    
                    # メトリクスも表示
                    metrics_df = pd.DataFrame([metrics_data])
                    response_data['table'] = metrics_df
            
            # アシスタントメッセージを追加
            add_message('assistant', response, response_data if response_data else None)
            st.rerun()
        
        except Exception as e:
            error_response = f"エラーが発生しました: {str(e)}"
            add_message('assistant', error_response)
            st.rerun()


