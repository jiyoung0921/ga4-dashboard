# GA4 Analytics Dashboard

Google Analytics 4（GA4）と Google Search Console（GSC）を横断的に分析できるダッシュボードです。非エンジニアでもセットアップと運用ができるよう、これまでの経緯と手順を整理しました。

---

## 1. これまでの歩み

1. **初期構築（フェーズ1〜3）**
   - Streamlit で骨組みを作成
   - GA4 API から主要 KPI／トラフィックを取得
   - 期間・モードをサイドバーで切り替えられるように

2. **機能拡張（フェーズ4〜5）**
   - 自然言語で質問できる「対話アシスタント」を追加
   - GSC と連携し、SEO タブでクエリ別の指標を可視化
   - サイト領域（USCPA・MBA・CIA・CISA・CFE・IFRS）を切り替えて分析可能に

3. **UI/UX リファイン（2025年11月時点）**
   - GA4 カラー（オレンジ系）を基調に統一
   - KPI カードに前期間比較・週次推移ボタンを追加
   - イベントタブを「記事 × イベント」の分析に特化
   - チャットに代表質問ボタンを表示し、入力補助を実装

---

## 2. 必要なもの

- **OS**: macOS / Windows いずれも可
- **Python**: 3.10 以上を推奨（3.11 で動作確認済み）
- **その他**: `pip`, 仮想環境ツール（`venv` 推奨）、Streamlit

> 注: 現在は Python 3.9 向けの互換パッチを同梱していますが、Google 製ライブラリが 3.9 をサポート外としているため、3.10 以上にアップグレードしてください。

---

## 3. セットアップ手順

1. **プロジェクトを取得**
   - Git 管理している場合は `git clone` を実行
   - ZIP で受け取った場合は任意のフォルダに展開し、Cursor などで開く

   ```bash
   git clone <repository-url>
   cd claude-code
   ```

2. **仮想環境の作成と有効化**
   ```bash
   python -m venv .venv
   # macOS / Linux
   source .venv/bin/activate
   # Windows（PowerShell）
   .\.venv\Scripts\Activate.ps1
   ```

3. **依存ライブラリのインストール**
   ```bash
   pip install -r requirements.txt
   ```

4. **Streamlit のシークレット設定**
   `.streamlit/secrets.toml` を作成し、以下を記入します。

   ```toml
   ga4_property_id = "249786227"         # GA4 プロパティ ID
   gsc_site_url    = "sc-domain:abitus.co.jp"  # GSC のプロパティ（ドメインの場合）

   [google_cloud]
   type = "service_account"
   project_id = "..."
   private_key_id = "..."
   private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
   client_email = "service-account@project.iam.gserviceaccount.com"
   client_id = "..."
   auth_uri = "https://accounts.google.com/o/oauth2/auth"
   token_uri = "https://oauth2.googleapis.com/token"
   auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
   client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/..."
   ```

   - GA4/GSC で利用するサービスアカウントの JSON をコピーし、`private_key` の改行を `\n` に置き換えてください。
   - GA4 側ではサービスアカウントに「閲覧者」権限を付与、GSC では「フル」権限を付与する必要があります。

5. **アプリの起動**
   ```bash
   streamlit run app.py
   ```
   ブラウザが自動で開きます。開かない場合は `http://localhost:8501` を手動で開いてください。

---

## 4. 画面の見方と使い方

### サイドバー
- **モード選択**（ダッシュボード／対話アシスタント）
- **期間**（プリセットまたはカスタム）
- **サイト領域**（USCPA / MBA / CIA / CISA / CFE / IFRS）
- GA4 / GSC の接続状況が表示されます

### ダッシュボードモード
1. **ヒーローヘッダー**: 選択したサイト領域と期間、最終更新日時を表示
2. **KPI カード**: セッション数 + 各 CV イベント（資料請求など）をカード表示
   - 「週次推移を見る」ボタン → 過去8週間の週次データをグラフと表で確認
3. **タブ構成**
   - 概要（主要 KPI と日別トラフィック）
   - 流入元（チャネル・ソース・ランディングページ）
   - デバイス（カテゴリ別の比較や時系列）
   - 記事別イベント分析（イベント総数 TOP5、イベント別の記事 TOP5を表示）
   - リアルタイム（アクティブユーザー、人気ページ）
   - UTM 分析（キャンペーン別指標）
   - SEO（GSC データ × GA4 データの統合）

### 対話アシスタント
- よく使う質問をボタンで表示 → クリックすると入力欄に自動セット
- 「資料請求 今月どれくらい？」等の自然言語で質問可能
- グラフや表を含む回答にも対応

---

## 5. トラブルシューティング

| 症状 | 主な原因 | 対処 |  
|------|----------|------|
| 403 Access denied | サービスアカウントに GA4/GSC 権限が無い | 各管理画面でサービスアカウントを追加し、閲覧権限を付与 |
| `importlib.metadata` エラー | Python 3.9 系の既知問題 | `pip install -r requirements.txt` 再実行、または Python 3.10 以上にアップグレード |
| GSC データが空 | `gsc_site_url` が未設定/形式違い | `.streamlit/secrets.toml` を確認。例：`sc-domain:abitus.co.jp` |
| 記事別イベントが空 | フィルタに該当する URL がない | 期間・領域を調整。GA4で出力されるパス（`/www-abitus-co-jp/...`）が含まれるか確認 |
| `use_container_width` 警告 | Streamlit API の非推奨機能 | すべて `width="stretch"` へ置き換え済み |

---

## 6. Windows への移行手順

1. Cursor を同じアカウントでログイン
2. プロジェクト全体を Windows にコピー（または Git で `clone`）
3. Python 3.11 をインストールし、仮想環境を作成
4. `pip install -r requirements.txt` を実行
5. `.streamlit/secrets.toml` を転記
6. `streamlit run app.py` で動作確認

必要であれば README を更新して宛先（部署名など）を書き添えると、他メンバーへの引き継ぎも容易です。

---

## 7. HubSpot 連携の展望

- HubSpot API（Private App Token）を利用すれば、フォーム送信やウェビナー申込、参加状況などを取得してダッシュボードに表示できます。
- 実装する場合は `modules/hubspot_client.py` のようなラッパーを作成し、Secrets にトークンを保持。GA4 のイベントと照合することでキャンペーンごとの商談状況も追跡可能です。
- 詳細要件が決まり次第、タスクを分割して対応しましょう。

---

## 8. 補足情報

- `modules/ga4_client.py`: GA4 Data API の呼び出しロジック。領域フィルタやイベント集計を一括で実施。
- `components/`: Streamlit の UI コンポーネント（ヘッダー、ダッシュボード、チャットなど）
- `assets/styles.css`: カスタムテーマ。オレンジ基調の SaaS ライクなデザインを定義。
- `utils/config.py`: サイト領域ごとの設定（CV イベント一覧、URL プレフィックスなど）

---

不明点や改善要望があれば、issue やメモにまとめておくと後続の開発がスムーズになります。


