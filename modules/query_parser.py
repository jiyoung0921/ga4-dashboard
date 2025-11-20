"""質問解析モジュール（ルールベース）"""
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta


class QueryParser:
    """質問解析クラス（正規表現とキーワードマッチングベース）"""
    
    # 期間パターン
    PERIOD_PATTERNS = {
        r'過去(\d+)日間': lambda m: ('days', int(m.group(1))),
        r'過去(\d+)日': lambda m: ('days', int(m.group(1))),
        r'(\d+)日間': lambda m: ('days', int(m.group(1))),
        r'(\d+)日': lambda m: ('days', int(m.group(1))),
        r'今週': lambda m: ('week', 'current'),
        r'先週': lambda m: ('week', 'previous'),
        r'今月': lambda m: ('month', 'current'),
        r'先月': lambda m: ('month', 'previous'),
        r'過去30日間': lambda m: ('days', 30),
        r'過去7日間': lambda m: ('days', 7),
        r'過去90日間': lambda m: ('days', 90),
    }
    
    # 指標キーワード
    METRIC_KEYWORDS = {
        'セッション数': 'sessions',
        'セッション': 'sessions',
        'ユーザー数': 'totalUsers',
        'ユーザー': 'totalUsers',
        'ページビュー': 'screenPageViews',
        'PV': 'screenPageViews',
        '直帰率': 'bounceRate',
        '平均セッション時間': 'averageSessionDuration',
        'セッション時間': 'averageSessionDuration',
        'コンバージョン数': 'conversions',
        'コンバージョン': 'conversions',
        'イベント数': 'eventCount',
        'イベント': 'eventCount',
    }
    
    # ディメンションキーワード
    DIMENSION_KEYWORDS = {
        '流入元': 'sessionSource',
        'ソース': 'sessionSource',
        'チャネル': 'sessionDefaultChannelGroup',
        'デバイス': 'deviceCategory',
        'ページ': 'pagePath',
        '地域': 'country',
        'ブラウザ': 'browser',
        'UTM': 'sessionCampaignName',
        'キャンペーン': 'sessionCampaignName',
    }
    
    # ランキングキーワード
    RANKING_KEYWORDS = {
        r'トップ(\d+)': lambda m: int(m.group(1)),
        r'上位(\d+)': lambda m: int(m.group(1)),
        r'ワースト(\d+)': lambda m: (-int(m.group(1)), True),  # 負の値でワーストを表現
        r'下位(\d+)': lambda m: (-int(m.group(1)), True),
    }
    
    # 比較キーワード
    COMPARISON_KEYWORDS = {
        '比較': True,
        '比べ': True,
        '対比': True,
    }
    
    @staticmethod
    def parse_period(query: str) -> Optional[Tuple[str, str]]:
        """期間を解析して開始日と終了日を返す"""
        today = datetime.now().date()
        
        # パターンマッチング
        for pattern, handler in QueryParser.PERIOD_PATTERNS.items():
            match = re.search(pattern, query)
            if match:
                period_type, value = handler(match)
                
                if period_type == 'days':
                    days = max(1, int(value))
                    end_date = today
                    start_date = today - timedelta(days=days - 1)
                    return (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
                
                elif period_type == 'week':
                    if value == 'current':
                        # 今週（月曜日から日曜日）
                        days_since_monday = today.weekday()
                        start_date = today - timedelta(days=days_since_monday)
                        end_date = today
                        return (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
                    elif value == 'previous':
                        # 先週
                        days_since_monday = today.weekday()
                        end_date = today - timedelta(days=days_since_monday + 1)
                        start_date = end_date - timedelta(days=6)
                        return (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
                
                elif period_type == 'month':
                    if value == 'current':
                        # 今月
                        start_date = today.replace(day=1)
                        end_date = today
                        return (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
                    elif value == 'previous':
                        # 先月
                        first_of_this_month = today.replace(day=1)
                        last_of_previous_month = first_of_this_month - timedelta(days=1)
                        start_date = last_of_previous_month.replace(day=1)
                        end_date = last_of_previous_month
                        return (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
        
        # デフォルト: 過去7日間
        end_date = today
        start_date = today - timedelta(days=6)
        return (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
    
    @staticmethod
    def parse_metric(query: str) -> Optional[str]:
        """指標を解析"""
        for keyword, metric in QueryParser.METRIC_KEYWORDS.items():
            if keyword in query:
                return metric
        return None
    
    @staticmethod
    def parse_dimension(query: str) -> Optional[str]:
        """ディメンションを解析"""
        for keyword, dimension in QueryParser.DIMENSION_KEYWORDS.items():
            if keyword in query:
                return dimension
        return None
    
    @staticmethod
    def parse_ranking(query: str) -> Optional[int]:
        """ランキングを解析（トップNなど）"""
        for pattern, handler in QueryParser.RANKING_KEYWORDS.items():
            match = re.search(pattern, query)
            if match:
                result = handler(match)
                if isinstance(result, tuple):
                    return abs(result[0])  # ワーストの場合は絶対値
                return result
        return None
    
    @staticmethod
    def parse_comparison(query: str) -> bool:
        """比較要求を解析"""
        for keyword in QueryParser.COMPARISON_KEYWORDS.keys():
            if keyword in query:
                return True
        return False
    
    @staticmethod
    def parse_query(query: str) -> Dict[str, any]:
        """質問を解析して構造化データを返す"""
        result = {
            'period': QueryParser.parse_period(query),
            'metric': QueryParser.parse_metric(query),
            'dimension': QueryParser.parse_dimension(query),
            'ranking': QueryParser.parse_ranking(query),
            'comparison': QueryParser.parse_comparison(query),
            'original_query': query
        }
        
        return result
    
    @staticmethod
    def is_valid_query(parsed: Dict[str, any]) -> bool:
        """解析結果が有効かチェック"""
        # 期間が取得できれば最低限有効
        return parsed.get('period') is not None
    
    @staticmethod
    def get_query_type(parsed: Dict[str, any]) -> str:
        """質問タイプを判定"""
        if parsed.get('comparison'):
            return 'comparison'
        elif parsed.get('ranking'):
            return 'ranking'
        elif parsed.get('dimension') and parsed.get('metric'):
            return 'dimension_metric'
        elif parsed.get('metric'):
            return 'metric_only'
        else:
            return 'general'


