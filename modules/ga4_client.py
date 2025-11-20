"""GA4 API クライアントモジュール"""
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    RunReportRequest,
    RunRealtimeReportRequest,
    Dimension,
    Metric,
    DateRange,
    Filter,
    FilterExpression,
    FilterExpressionList,
)
from typing import List, Dict, Optional, Any
import pandas as pd
from datetime import datetime, timedelta
from utils.auth import get_credentials
from utils.config import get_ga4_property_id
import streamlit as st


class GA4Client:
    """GA4 Data API クライアント"""
    
    def __init__(self):
        """初期化"""
        self.property_id = get_ga4_property_id()
        if not self.property_id:
            raise ValueError("GA4プロパティIDが設定されていません")
        
        credentials = get_credentials()
        if not credentials:
            raise ValueError("認証情報が取得できませんでした")
        
        self.client = BetaAnalyticsDataClient(credentials=credentials)
    
    def _build_site_scope_filter(self, site_scope: Optional[str]) -> Optional[FilterExpression]:
        """サイト領域のフィルターを構築"""
        if not site_scope:
            return None

        return FilterExpression(
            filter=Filter(
                field_name="customEvent:site_scope",
                string_filter=Filter.StringFilter(
                    match_type=Filter.StringFilter.MatchType.EXACT,
                    value=site_scope
                )
            )
        )


    def _merge_filters(self, *filters: Optional[FilterExpression]) -> Optional[FilterExpression]:
        expressions = [f for f in filters if f]
        if not expressions:
            return None
        if len(expressions) == 1:
            return expressions[0]
        return FilterExpression(and_group=FilterExpressionList(expressions=expressions))


    def run_report(
        self,
        dimensions: List[str],
        metrics: List[str],
        date_ranges: List[Dict[str, str]],
        dimension_filter: Optional[FilterExpression] = None,
        limit: Optional[int] = None
    ) -> pd.DataFrame:
        """レポートを実行してDataFrameを返す"""
        try:
            # ディメンションとメトリクスを設定
            dimension_list = [Dimension(name=dim) for dim in dimensions]
            metric_list = [Metric(name=metric) for metric in metrics]
            date_range_list = [
                DateRange(start_date=dr['start_date'], end_date=dr['end_date'])
                for dr in date_ranges
            ]
            
            # リクエストを作成
            request = RunReportRequest(
                property=f"properties/{self.property_id}",
                dimensions=dimension_list,
                metrics=metric_list,
                date_ranges=date_range_list,
                dimension_filter=dimension_filter,
                limit=limit
            )
            
            # レポートを実行
            response = self.client.run_report(request)
            
            # DataFrameに変換
            rows = []
            for row in response.rows:
                row_data = {}
                for i, dim_value in enumerate(row.dimension_values):
                    row_data[dimensions[i]] = dim_value.value
                for i, metric_value in enumerate(row.metric_values):
                    row_data[metrics[i]] = float(metric_value.value) if metric_value.value else 0.0
                rows.append(row_data)
            
            return pd.DataFrame(rows)
        
        except Exception as e:
            st.error(f"GA4レポートの取得に失敗しました: {str(e)}")
            return pd.DataFrame()
    
    def get_overview_metrics(self, start_date: str, end_date: str, site_scope: Optional[str] = None) -> Dict[str, float]:
        """概要メトリクスを取得"""
        dimensions = []
        metrics = [
            'sessions',
            'totalUsers',
            'screenPageViews',
            'bounceRate',
            'averageSessionDuration'
        ]
        
        df = self.run_report(
            dimensions=dimensions,
            metrics=metrics,
            date_ranges=[{'start_date': start_date, 'end_date': end_date}],
            dimension_filter=self._build_site_scope_filter(site_scope)
        )
        
        if df.empty:
            return {
                'sessions': 0,
                'totalUsers': 0,
                'screenPageViews': 0,
                'bounceRate': 0,
                'averageSessionDuration': 0
            }
        
        return df.iloc[0].to_dict()
    
    def get_daily_traffic(self, start_date: str, end_date: str, site_scope: Optional[str] = None) -> pd.DataFrame:
        """日別トラフィックを取得"""
        dimensions = ['date']
        metrics = ['sessions', 'totalUsers', 'screenPageViews']
        
        df = self.run_report(
            dimensions=dimensions,
            metrics=metrics,
            date_ranges=[{'start_date': start_date, 'end_date': end_date}],
            dimension_filter=self._build_site_scope_filter(site_scope)
        )
        
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')
        
        return df
    
    def get_traffic_source(self, start_date: str, end_date: str, site_scope: Optional[str] = None) -> pd.DataFrame:
        """流入元データを取得"""
        dimensions = ['sessionDefaultChannelGroup', 'sessionSource', 'sessionMedium']
        metrics = ['sessions']
        
        df = self.run_report(
            dimensions=dimensions,
            metrics=metrics,
            date_ranges=[{'start_date': start_date, 'end_date': end_date}],
            dimension_filter=self._build_site_scope_filter(site_scope),
            limit=100
        )
        
        return df
    
    def get_landing_pages(self, start_date: str, end_date: str, limit: int = 20, site_scope: Optional[str] = None) -> pd.DataFrame:
        """ランディングページデータを取得"""
        dimensions = ['landingPage']
        metrics = ['sessions', 'bounceRate', 'averageSessionDuration']
        
        df = self.run_report(
            dimensions=dimensions,
            metrics=metrics,
            date_ranges=[{'start_date': start_date, 'end_date': end_date}],
            dimension_filter=self._build_site_scope_filter(site_scope),
            limit=limit
        )
        
        return df
    
    def get_device_data(self, start_date: str, end_date: str, site_scope: Optional[str] = None) -> pd.DataFrame:
        """デバイスデータを取得"""
        dimensions = ['deviceCategory', 'date']
        metrics = ['sessions', 'bounceRate']
        
        df = self.run_report(
            dimensions=dimensions,
            metrics=metrics,
            date_ranges=[{'start_date': start_date, 'end_date': end_date}],
            dimension_filter=self._build_site_scope_filter(site_scope)
        )
        
        if not df.empty and 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')
        
        return df
    
    def get_events(self, start_date: str, end_date: str, limit: int = 20, site_scope: Optional[str] = None) -> pd.DataFrame:
        """イベントデータを取得"""
        dimensions = ['eventName', 'date']
        metrics = ['eventCount']
        
        df = self.run_report(
            dimensions=dimensions,
            metrics=metrics,
            date_ranges=[{'start_date': start_date, 'end_date': end_date}],
            dimension_filter=self._build_site_scope_filter(site_scope),
            limit=limit * 10  # 日付別になるので多めに取得
        )
        
        if not df.empty and 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')
        
        return df
    
    def get_realtime_data(self) -> Dict[str, Any]:
        """リアルタイムデータを取得"""
        try:
            request = RunRealtimeReportRequest(
                property=f"properties/{self.property_id}",
                dimensions=[Dimension(name="unifiedScreenName")],
                metrics=[Metric(name="activeUsers")],
                limit=10
            )
            
            response = self.client.run_realtime_report(request)
            
            # アクティブユーザー数を計算
            total_active_users = sum(
                float(row.metric_values[0].value) 
                for row in response.rows
            )
            
            # トップページを取得
            top_pages = []
            for row in response.rows[:10]:
                page = row.dimension_values[0].value
                users = float(row.metric_values[0].value)
                top_pages.append({'page': page, 'activeUsers': users})
            
            return {
                'activeUsers': total_active_users,
                'topPages': top_pages
            }
        
        except Exception as e:
            st.error(f"リアルタイムデータの取得に失敗しました: {str(e)}")
            return {'activeUsers': 0, 'topPages': []}
    
    def get_utm_data(self, start_date: str, end_date: str, site_scope: Optional[str] = None) -> pd.DataFrame:
        """UTMパラメータデータを取得"""
        dimensions = ['sessionCampaignName', 'sessionSource', 'sessionMedium']
        metrics = ['sessions', 'conversions']
        
        df = self.run_report(
            dimensions=dimensions,
            metrics=metrics,
            date_ranges=[{'start_date': start_date, 'end_date': end_date}],
            dimension_filter=self._build_site_scope_filter(site_scope),
            limit=100
        )
        
        return df
    
    def get_page_data(self, start_date: str, end_date: str, limit: int = 20, site_scope: Optional[str] = None) -> pd.DataFrame:
        """ページデータを取得（SEO統合用）"""
        dimensions = ['pagePath']
        metrics = ['sessions', 'screenPageViews', 'bounceRate', 'averageSessionDuration']
        
        df = self.run_report(
            dimensions=dimensions,
            metrics=metrics,
            date_ranges=[{'start_date': start_date, 'end_date': end_date}],
            dimension_filter=self._build_site_scope_filter(site_scope),
            limit=limit
        )
        
        return df

    def get_event_counts_by_names(
        self,
        start_date: str,
        end_date: str,
        event_names: List[str],
        site_scope: Optional[str] = None
    ) -> Dict[str, float]:
        """指定したイベント名のイベント数を取得"""
        if not event_names:
            return {}

        event_filter = FilterExpression(
            filter=Filter(
                field_name="eventName",
                in_list_filter=Filter.InListFilter(values=event_names)
            )
        )

        df = self.run_report(
            dimensions=['eventName'],
            metrics=['eventCount'],
            date_ranges=[{'start_date': start_date, 'end_date': end_date}],
            dimension_filter=self._merge_filters(
                self._build_site_scope_filter(site_scope),
                event_filter
            )
        )

        counts = {name: 0 for name in event_names}
        for _, row in df.iterrows():
            event_name = row.get('eventName')
            event_count = row.get('eventCount', 0)
            if event_name in counts:
                counts[event_name] = float(event_count)
        return counts

    def get_event_daily_series(
        self,
        start_date: str,
        end_date: str,
        event_name: str,
        site_scope: Optional[str] = None
    ) -> pd.DataFrame:
        """指定イベントの1日単位イベント数を取得"""
        event_filter = FilterExpression(
            filter=Filter(
                field_name="eventName",
                string_filter=Filter.StringFilter(
                    match_type=Filter.StringFilter.MatchType.EXACT,
                    value=event_name
                )
            )
        )

        df = self.run_report(
            dimensions=['date'],
            metrics=['eventCount'],
            date_ranges=[{'start_date': start_date, 'end_date': end_date}],
            dimension_filter=self._merge_filters(
                self._build_site_scope_filter(site_scope),
                event_filter
            )
        )

        if not df.empty and 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')
        return df

    def get_event_page_counts(
        self,
        start_date: str,
        end_date: str,
        site_scope: Optional[str] = None,
        event_names: Optional[List[str]] = None,
        page_prefixes: Optional[List[str]] = None,
        exclude_paths: Optional[List[str]] = None,
        limit: int = 500
    ) -> pd.DataFrame:
        """イベント×記事のイベント数を取得"""
        event_filter = None
        if event_names:
            event_filter = FilterExpression(
                filter=Filter(
                    field_name="eventName",
                    in_list_filter=Filter.InListFilter(values=event_names)
                )
            )

        page_filter = None
        if page_prefixes:
            or_filters = []
            for prefix in page_prefixes:
                or_filters.append(FilterExpression(
                    filter=Filter(
                        field_name="pagePath",
                        string_filter=Filter.StringFilter(
                            match_type=Filter.StringFilter.MatchType.CONTAINS,
                            value=prefix
                        )
                    )
                ))
            if or_filters:
                page_filter = FilterExpression(or_group=FilterExpressionList(expressions=or_filters))

        exclude_filter = []
        if exclude_paths:
            for pattern in exclude_paths:
                exclude_filter.append(FilterExpression(
                    filter=Filter(
                        field_name="pagePath",
                        string_filter=Filter.StringFilter(
                            match_type=Filter.StringFilter.MatchType.CONTAINS,
                            value=pattern
                        )
                    )
                ))
 
        df = self.run_report(
            dimensions=['pagePath', 'eventName'],
            metrics=['eventCount'],
            date_ranges=[{'start_date': start_date, 'end_date': end_date}],
            dimension_filter=self._merge_filters(
                self._build_site_scope_filter(site_scope),
                event_filter,
                page_filter,
                FilterExpression(not_expression=FilterExpression(or_group=FilterExpressionList(expressions=exclude_filter))) if exclude_filter else None
            ),
            limit=limit
        )
 
        return df

