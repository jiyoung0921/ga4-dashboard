"""データ処理モジュール"""
import pandas as pd
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse


class DataProcessor:
    """データ処理クラス"""
    
    @staticmethod
    def normalize_url(url: str) -> str:
        """URLを正規化（末尾スラッシュの統一、クエリパラメータの除去など）"""
        if not url:
            return ''
        
        # パース
        parsed = urlparse(url)
        
        # パスを正規化（末尾スラッシュを統一）
        path = parsed.path
        if path and path != '/':
            path = path.rstrip('/')
        
        # 正規化されたURLを構築（スキームとホストは保持）
        normalized = f"{path}"
        if parsed.query:
            # クエリパラメータは保持する場合
            normalized += f"?{parsed.query}"
        
        return normalized
    
    @staticmethod
    def merge_ga4_gsc_data(
        ga4_df: pd.DataFrame,
        gsc_df: pd.DataFrame,
        ga4_url_column: str = 'pagePath',
        gsc_url_column: str = 'page'
    ) -> pd.DataFrame:
        """GA4とGSCのデータをURL単位でマージ"""
        if ga4_df.empty and gsc_df.empty:
            return pd.DataFrame()
        
        if ga4_df.empty:
            return gsc_df.copy()
        
        if gsc_df.empty:
            return ga4_df.copy()
        
        # URLを正規化
        ga4_df = ga4_df.copy()
        gsc_df = gsc_df.copy()
        
        ga4_df['normalized_url'] = ga4_df[ga4_url_column].apply(DataProcessor.normalize_url)
        gsc_df['normalized_url'] = gsc_df[gsc_url_column].apply(DataProcessor.normalize_url)
        
        # マージ
        merged_df = pd.merge(
            ga4_df,
            gsc_df,
            on='normalized_url',
            how='outer',
            suffixes=('_ga4', '_gsc')
        )
        
        # 元のURLカラムを統合
        if ga4_url_column in merged_df.columns:
            merged_df['page'] = merged_df[ga4_url_column].fillna(merged_df.get(gsc_url_column, ''))
        elif gsc_url_column in merged_df.columns:
            merged_df['page'] = merged_df[gsc_url_column]
        
        # 正規化URLカラムを削除
        if 'normalized_url' in merged_df.columns:
            merged_df = merged_df.drop(columns=['normalized_url'])
        
        return merged_df
    
    @staticmethod
    def aggregate_event_data(df: pd.DataFrame) -> pd.DataFrame:
        """イベントデータを集約（日付別からイベント別に）"""
        if df.empty or 'eventName' not in df.columns:
            return df
        
        # イベント名と日付でグループ化
        if 'date' in df.columns:
            grouped = df.groupby(['eventName', 'date']).agg({
                'eventCount': 'sum'
            }).reset_index()
        else:
            grouped = df.groupby('eventName').agg({
                'eventCount': 'sum'
            }).reset_index()
        
        return grouped
    
    @staticmethod
    def format_number(value: float, decimals: int = 0) -> str:
        """数値をフォーマット"""
        if pd.isna(value):
            return 'N/A'
        
        if value >= 1000000:
            return f"{value/1000000:.{decimals}f}M"
        elif value >= 1000:
            return f"{value/1000:.{decimals}f}K"
        else:
            return f"{value:.{decimals}f}"
    
    @staticmethod
    def format_percentage(value: float, decimals: int = 1) -> str:
        """パーセンテージをフォーマット"""
        if pd.isna(value):
            return 'N/A'
        return f"{value * 100:.{decimals}f}%"
    
    @staticmethod
    def format_duration(seconds: float) -> str:
        """秒数を時間形式にフォーマット"""
        if pd.isna(seconds):
            return 'N/A'
        
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m {secs}s"
        elif minutes > 0:
            return f"{minutes}m {secs}s"
        else:
            return f"{secs}s"
    
    @staticmethod
    def prepare_chart_data(df: pd.DataFrame, x_column: str, y_column: str) -> Dict:
        """チャート用データを準備"""
        if df.empty:
            return {'x': [], 'y': []}
        
        return {
            'x': df[x_column].tolist(),
            'y': df[y_column].tolist()
        }
    
    @staticmethod
    def filter_top_n(df: pd.DataFrame, metric_column: str, n: int = 10) -> pd.DataFrame:
        """トップNを取得"""
        if df.empty:
            return df
        
        return df.nlargest(n, metric_column)
    
    @staticmethod
    def calculate_comparison(current: float, previous: float) -> Dict[str, Any]:
        """比較データを計算"""
        if pd.isna(previous) or previous == 0:
            return {
                'change': current,
                'change_percent': 0,
                'is_positive': current >= 0
            }
        
        change = current - previous
        change_percent = (change / previous) * 100
        
        return {
            'change': change,
            'change_percent': change_percent,
            'is_positive': change >= 0
        }


