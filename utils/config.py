"""設定管理モジュール"""
import os
import streamlit as st
from typing import Optional, Dict, Any, List
import json


def get_ga4_property_id() -> Optional[str]:
    """GA4プロパティIDを取得"""
    if 'ga4_property_id' in st.secrets:
        return st.secrets['ga4_property_id']
    return os.getenv('GA4_PROPERTY_ID')


def get_gsc_site_url() -> Optional[str]:
    """GSCサイトURLを取得"""
    if 'gsc_site_url' in st.secrets:
        return st.secrets['gsc_site_url']
    return os.getenv('GSC_SITE_URL')


def get_service_account_info() -> Optional[Dict[str, Any]]:
    """サービスアカウント情報を取得"""
    # Streamlit Secretsから取得を試みる
    if 'google_cloud' in st.secrets:
        return dict(st.secrets['google_cloud'])
    
    # 環境変数から取得を試みる
    service_account_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    if service_account_path and os.path.exists(service_account_path):
        with open(service_account_path, 'r') as f:
            return json.load(f)
    
    return None


DATE_RANGE_PRESETS = {
    '過去7日間': 7,
    '過去30日間': 30,
    '過去90日間': 90,
    '今月': None,
    '先月': None,
}

SITE_SCOPE_OPTIONS = [
    {'label': 'USCPA', 'value': 'USCPA'},
    {'label': 'MBA', 'value': 'MBA'},
    {'label': 'CIA', 'value': 'CIA'},
    {'label': 'CISA', 'value': 'CISA'},
    {'label': 'CFE', 'value': 'CFE'},
    {'label': 'IFRS', 'value': 'IFRS'},
]

GA4_DIMENSION_OPTIONS = [
    {'label': '日付', 'value': 'date'},
    {'label': '流入元', 'value': 'sessionSource'},
    {'label': '流入チャネル', 'value': 'sessionDefaultChannelGroup'},
    {'label': 'キャンペーン', 'value': 'sessionCampaignName'},
    {'label': 'デバイス', 'value': 'deviceCategory'},
    {'label': 'ランディングページ', 'value': 'landingPage'},
    {'label': 'ページパス', 'value': 'pagePath'},
    {'label': 'イベント名', 'value': 'eventName'},
]

GA4_METRIC_OPTIONS = [
    {'label': 'セッション数', 'value': 'sessions'},
    {'label': 'ユーザー数', 'value': 'totalUsers'},
    {'label': 'ページビュー', 'value': 'screenPageViews'},
    {'label': 'イベント数', 'value': 'eventCount'},
    {'label': 'コンバージョン数', 'value': 'conversions'},
    {'label': '直帰率', 'value': 'bounceRate'},
    {'label': '平均セッション時間', 'value': 'averageSessionDuration'},
]

COMMON_CV_EVENTS = [
    'CV_資料請求',
    'CV_営業特別イベント予約',
    'CV_マーケティングイベント予約',
    'CV_カウンセリング予約',
    'CV_オンラインセミナー予約',
    'CV_オンライン体験予約',
    'CV_説明会動画',
    'CV_単位診断',
    'CV_問合せ',
    'CV_海外カウンセリング'
]

SITE_SCOPE_EVENT_MAP = {
    'USCPA': COMMON_CV_EVENTS,
    'MBA': [
        'CV_資料請求',
        'CV_営業特別イベント予約',
        'CV_マーケティングイベント予約',
        'CV_カウンセリング予約',
        'CV_オンラインセミナー予約',
        'CV_問合せ'
    ],
    'CIA': COMMON_CV_EVENTS,
    'CISA': COMMON_CV_EVENTS,
    'CFE': COMMON_CV_EVENTS,
    'IFRS': COMMON_CV_EVENTS,
}

EVENT_DISPLAY_MAP = {
    'CV_資料請求': '資料請求',
    'CV_営業特別イベント予約': '営業特別イベント予約',
    'CV_マーケティングイベント予約': 'マーケティングイベント予約',
    'CV_カウンセリング予約': 'カウンセリング予約',
    'CV_オンラインセミナー予約': 'オンラインセミナー予約',
    'CV_オンライン体験予約': 'オンライン体験予約',
    'CV_説明会動画': '説明会動画',
    'CV_単位診断': '単位診断',
    'CV_問合せ': '問合せ',
    'CV_海外カウンセリング': '海外カウンセリング'
}

EVENT_ALIAS_MAP = {
    '資料請求': 'CV_資料請求',
    '営業特別イベント予約': 'CV_営業特別イベント予約',
    '特別イベント予約': 'CV_営業特別イベント予約',
    'マーケティングイベント予約': 'CV_マーケティングイベント予約',
    'カウンセリング予約': 'CV_カウンセリング予約',
    'オンラインセミナー予約': 'CV_オンラインセミナー予約',
    'オンラインセミナー': 'CV_オンラインセミナー予約',
    'オンライン体験予約': 'CV_オンライン体験予約',
    'オンライン体験': 'CV_オンライン体験予約',
    '説明会動画': 'CV_説明会動画',
    '単位診断': 'CV_単位診断',
    '問合せ': 'CV_問合せ',
    '問い合わせ': 'CV_問合せ',
    '海外カウンセリング': 'CV_海外カウンセリング'
}

ARTICLE_PATH_PREFIXES = {
    'USCPA': [
        '/www-abitus-co-jp/information/uscpa/',
        '/www-abitus-co-jp/uscpablog/',
        '/www-abitus-co-jp/uscpa/',
        '/www-abitus-co-jp/column_voice/uscpa/',
        'https://www.abitus.co.jp/uscpa/',
        'https://www.abitus.co.jp/uscpablog/',
        'https://www.abitus.co.jp/information/uscpa/',
        'https://www.abitus.co.jp/column_voice/uscpa/'
    ],
    'MBA': [
        '/www-abitus-co-jp/information/mba/',
        '/www-abitus-co-jp/mbablog/',
        '/www-abitus-co-jp/mba/',
        '/www-abitus-co-jp/column_voice/mba/',
        'https://www.abitus.co.jp/mba/',
        'https://www.abitus.co.jp/mbablog/',
        'https://www.abitus.co.jp/information/mba/',
        'https://www.abitus.co.jp/column_voice/mba/'
    ],
    'CIA': [
        '/www-abitus-co-jp/information/cia/',
        '/www-abitus-co-jp/ciablog/',
        '/www-abitus-co-jp/cia/',
        '/www-abitus-co-jp/column_voice/cia/',
        'https://www.abitus.co.jp/cia/',
        'https://www.abitus.co.jp/ciablog/',
        'https://www.abitus.co.jp/information/cia/',
        'https://www.abitus.co.jp/column_voice/cia/'
    ],
    'CISA': [
        '/www-abitus-co-jp/information/cisa/',
        '/www-abitus-co-jp/cisablog/',
        '/www-abitus-co-jp/cisa/',
        '/www-abitus-co-jp/column_voice/cisa/',
        'https://www.abitus.co.jp/cisa/',
        'https://www.abitus.co.jp/cisablog/',
        'https://www.abitus.co.jp/information/cisa/',
        'https://www.abitus.co.jp/column_voice/cisa/'
    ],
    'CFE': [
        '/www-abitus-co-jp/information/cfe/',
        '/www-abitus-co-jp/cfeblog/',
        '/www-abitus-co-jp/cfe/',
        '/www-abitus-co-jp/column_voice/cfe/',
        'https://www.abitus.co.jp/cfe/',
        'https://www.abitus.co.jp/cfeblog/',
        'https://www.abitus.co.jp/information/cfe/',
        'https://www.abitus.co.jp/column_voice/cfe/'
    ],
    'IFRS': [
        '/www-abitus-co-jp/information/ifrs/',
        '/www-abitus-co-jp/ifrsblog/',
        '/www-abitus-co-jp/ifrs/',
        '/www-abitus-co-jp/column_voice/ifrs/',
        'https://www.abitus.co.jp/ifrs/',
        'https://www.abitus.co.jp/ifrsblog/',
        'https://www.abitus.co.jp/information/ifrs/',
        'https://www.abitus.co.jp/column_voice/ifrs/'
    ]
}


def get_date_range_presets() -> Dict[str, int]:
    """期間プリセットの定義"""
    return DATE_RANGE_PRESETS


def get_site_scope_options() -> List[Dict[str, Any]]:
    """サイト領域の選択肢"""
    return SITE_SCOPE_OPTIONS


def get_ga4_dimension_options() -> List[Dict[str, Any]]:
    """カスタムレポート用ディメンション選択肢"""
    return GA4_DIMENSION_OPTIONS


def get_ga4_metric_options() -> List[Dict[str, Any]]:
    """カスタムレポート用メトリクス選択肢"""
    return GA4_METRIC_OPTIONS


def get_cv_events_for_scope(site_scope: Optional[str]) -> List[str]:
    """サイト領域ごとのCVイベント一覧を取得"""
    if site_scope and site_scope in SITE_SCOPE_EVENT_MAP:
        return SITE_SCOPE_EVENT_MAP[site_scope]

    # すべての場合は全領域のユニークセット
    events = []
    for names in SITE_SCOPE_EVENT_MAP.values():
        events.extend(names)
    return sorted(set(events))


def get_event_alias_map() -> Dict[str, str]:
    """イベントエイリアスマッピングを取得"""
    return EVENT_ALIAS_MAP


def get_event_display_name(event_name: str) -> str:
    """イベント名の表示ラベルを取得"""
    return EVENT_DISPLAY_MAP.get(event_name, event_name)


def get_article_path_prefixes(site_scope: Optional[str]) -> List[str]:
    """サイト領域ごとの記事URLプレフィックス"""
    if site_scope and site_scope in ARTICLE_PATH_PREFIXES:
        return ARTICLE_PATH_PREFIXES[site_scope]
    prefixes = []
    for values in ARTICLE_PATH_PREFIXES.values():
        prefixes.extend(values)
    return prefixes


