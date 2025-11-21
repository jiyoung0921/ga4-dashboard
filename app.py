"""GA4ダッシュボード メインアプリケーション"""
try:
    import importlib
    import importlib.metadata as _ilm  # type: ignore[attr-defined]
    if not hasattr(_ilm, "packages_distributions"):
        import importlib_metadata  # type: ignore
        _ilm.packages_distributions = importlib_metadata.packages_distributions
except Exception:  # pragma: no cover - best effort fallback
    try:
        import importlib
        import importlib_metadata  # type: ignore
        importlib.metadata = importlib_metadata  # type: ignore
    except Exception:
        pass

import streamlit as st
from modules.ga4_client import GA4Client
from modules.gsc_client import GSCClient
from components.sidebar import render_sidebar
from components.dashboard_view import render_dashboard_view
from components.chat_view import render_chat_view
from components.header import render_header
from utils.config import get_ga4_property_id, get_gsc_site_url
from pathlib import Path


# ページ設定
st.set_page_config(
    page_title="GA4 Analytics Dashboard",
    page_icon="assets/2025-11-21_00h52_14.png",
    layout="wide",
    initial_sidebar_state="expanded"
)


def load_local_css(path: Path) -> None:
    """ローカルのCSSを読み込む"""
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def initialize_clients():
    """GA4とGSCクライアントを初期化"""
    # GA4クライアント
    if 'ga4_client' not in st.session_state:
        try:
            ga4_property_id = get_ga4_property_id()
            if ga4_property_id:
                st.session_state.ga4_client = GA4Client()
            else:
                st.session_state.ga4_client = None
                st.error("GA4プロパティIDが設定されていません。")
        except Exception as e:
            st.session_state.ga4_client = None
            st.error(f"GA4クライアントの初期化に失敗しました: {str(e)}")
        else:
            if 'ga4_metadata' not in st.session_state:
                st.session_state.ga4_metadata = st.session_state.ga4_client.get_metadata_options()
    
    # GSCクライアント（オプション）
    if 'gsc_client' not in st.session_state:
        try:
            gsc_site_url = get_gsc_site_url()
            if gsc_site_url:
                st.session_state.gsc_client = GSCClient()
            else:
                st.session_state.gsc_client = None
        except Exception as e:
            st.session_state.gsc_client = None
            # GSCはオプションなのでエラーを表示しない
            pass

    if (
        st.session_state.get('ga4_client') is not None
        and not st.session_state.get('ga4_metadata')
    ):
        st.session_state.ga4_metadata = st.session_state.ga4_client.get_metadata_options()

    if 'custom_report_config' not in st.session_state:
        st.session_state.custom_report_config = {
            'dimensions': ['deviceCategory', 'eventName'],
            'metrics': ['eventCount'],
            'limit': 50
        }


def main():
    """メイン関数"""
    load_local_css(Path("assets/styles.css"))
    
    # クライアントを初期化
    initialize_clients()
    
    # サイドバーをレンダリング
    mode, start_date, end_date, site_scope = render_sidebar()
    
    # メインコンテンツ
    if st.session_state.ga4_client is None:
        st.error("""
        ## ⚠️ 設定が必要です
        
        GA4ダッシュボードを使用するには、以下の設定が必要です:
        
        1. **Streamlit Secretsの設定**
           - `.streamlit/secrets.toml` ファイルを作成
           - 以下の情報を設定:
             ```toml
             ga4_property_id = "YOUR_PROPERTY_ID"
             gsc_site_url = "sc-domain:yourdomain.com"  # オプション
             
             [google_cloud]
             type = "service_account"
             project_id = "your-project-id"
             private_key_id = "your-private-key-id"
             private_key = "-----BEGIN PRIVATE KEY-----\\n...\\n-----END PRIVATE KEY-----\\n"
             client_email = "your-service-account@your-project.iam.gserviceaccount.com"
             client_id = "your-client-id"
             auth_uri = "https://accounts.google.com/o/oauth2/auth"
             token_uri = "https://oauth2.googleapis.com/token"
             auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
             client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/..."
             ```
        
        2. **環境変数の設定（ローカル開発時）**
           - `GA4_PROPERTY_ID`: GA4プロパティID
           - `GSC_SITE_URL`: GSCサイトURL（オプション）
           - `GOOGLE_APPLICATION_CREDENTIALS`: サービスアカウントJSONキーファイルのパス
        
        詳細はREADME.mdを参照してください。
        """)
        return

    # ヒーローヘッダー
    render_header(site_scope, start_date, end_date)

    # モードに応じて表示
    if mode == "ダッシュボード":
        render_dashboard_view(
            st.session_state.ga4_client,
            st.session_state.gsc_client,
            start_date,
            end_date,
            site_scope,
            st.session_state.get('custom_report_config')
        )
    elif mode == "対話アシスタント":
        render_chat_view(
            st.session_state.ga4_client,
            st.session_state.gsc_client,
            start_date,
            end_date,
            site_scope
        )


if __name__ == "__main__":
    main()


