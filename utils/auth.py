"""認証ヘルパーモジュール"""
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from typing import Optional, Dict, Any
from utils.config import get_service_account_info
import streamlit as st


def get_credentials() -> Optional[service_account.Credentials]:
    """サービスアカウントの認証情報を取得"""
    try:
        service_account_info = get_service_account_info()
        if not service_account_info:
            return None
        
        credentials = service_account.Credentials.from_service_account_info(
            service_account_info,
            scopes=[
                'https://www.googleapis.com/auth/analytics.readonly',
                'https://www.googleapis.com/auth/webmasters.readonly'
            ]
        )
        return credentials
    except Exception as e:
        st.error(f"認証情報の取得に失敗しました: {str(e)}")
        return None


