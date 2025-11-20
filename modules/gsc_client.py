"""Google Search Console API クライアントモジュール"""
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from typing import List, Optional
import pandas as pd
from utils.auth import get_credentials
from utils.config import get_gsc_site_url
import streamlit as st


class GSCClient:
    """Google Search Console API クライアント"""
    
    def __init__(self):
        """初期化"""
        self.site_url = get_gsc_site_url()
        if not self.site_url:
            raise ValueError("GSCサイトURLが設定されていません")
        
        credentials = get_credentials()
        if not credentials:
            raise ValueError("認証情報が取得できませんでした")
        
        self.service = build('searchconsole', 'v1', credentials=credentials, cache_discovery=False)
    
    def get_search_analytics(
        self,
        start_date: str,
        end_date: str,
        dimensions: Optional[List[str]] = None,
        row_limit: int = 1000
    ) -> pd.DataFrame:
        """検索アナリティクスデータを取得"""
        try:
            if dimensions is None:
                dimensions = []
            
            request = {
                'startDate': start_date,
                'endDate': end_date,
                'dimensions': dimensions,
                'rowLimit': row_limit
            }
            
            response = self.service.searchanalytics().query(
                siteUrl=self.site_url,
                body=request
            ).execute()
            
            if 'rows' not in response:
                return pd.DataFrame()
            
            rows = []
            for row in response['rows']:
                row_data = {
                    'clicks': row.get('clicks', 0),
                    'impressions': row.get('impressions', 0),
                    'ctr': row.get('ctr', 0),
                    'position': row.get('position', 0)
                }
                
                # ディメンションを追加
                if 'keys' in row:
                    for i, key in enumerate(row['keys']):
                        if i < len(dimensions):
                            row_data[dimensions[i]] = key
                
                rows.append(row_data)
            
            return pd.DataFrame(rows)
        
        except HttpError as e:
            st.error(f"GSCデータの取得に失敗しました: {str(e)}")
            return pd.DataFrame()
        except Exception as e:
            st.error(f"予期しないエラーが発生しました: {str(e)}")
            return pd.DataFrame()
    
    def get_query_data(self, start_date: str, end_date: str, limit: int = 100) -> pd.DataFrame:
        """検索クエリデータを取得"""
        return self.get_search_analytics(
            start_date=start_date,
            end_date=end_date,
            dimensions=['query'],
            row_limit=limit
        )
    
    def get_page_data(self, start_date: str, end_date: str, limit: int = 100) -> pd.DataFrame:
        """ページデータを取得（SEO統合用）"""
        return self.get_search_analytics(
            start_date=start_date,
            end_date=end_date,
            dimensions=['page'],
            row_limit=limit
        )
    
    def get_country_data(self, start_date: str, end_date: str, limit: int = 50) -> pd.DataFrame:
        """国別データを取得"""
        return self.get_search_analytics(
            start_date=start_date,
            end_date=end_date,
            dimensions=['country'],
            row_limit=limit
        )
    
    def get_device_data(self, start_date: str, end_date: str) -> pd.DataFrame:
        """デバイス別データを取得"""
        return self.get_search_analytics(
            start_date=start_date,
            end_date=end_date,
            dimensions=['device']
        )


