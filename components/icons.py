"""Lucide Icons - SVG アイコンライブラリ"""

# アイコンサイズのデフォルト値
DEFAULT_SIZE = 20
DEFAULT_STROKE_WIDTH = 1.75

def _svg_wrapper(path: str, size: int = DEFAULT_SIZE, stroke_width: float = DEFAULT_STROKE_WIDTH, color: str = "currentColor") -> str:
    """SVG ラッパー"""
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round">{path}</svg>'''


class Icons:
    """Lucide Icons コレクション"""
    
    # ===== ダッシュボード・分析系 =====
    @staticmethod
    def bar_chart_3(size: int = DEFAULT_SIZE, color: str = "currentColor") -> str:
        """棒グラフアイコン（3本）"""
        return _svg_wrapper(
            '<path d="M3 3v18h18"/><path d="M18 17V9"/><path d="M13 17V5"/><path d="M8 17v-3"/>',
            size, color=color
        )
    
    @staticmethod
    def trending_up(size: int = DEFAULT_SIZE, color: str = "currentColor") -> str:
        """上昇トレンド"""
        return _svg_wrapper(
            '<polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/>',
            size, color=color
        )
    
    @staticmethod
    def trending_down(size: int = DEFAULT_SIZE, color: str = "currentColor") -> str:
        """下降トレンド"""
        return _svg_wrapper(
            '<polyline points="22 17 13.5 8.5 8.5 13.5 2 7"/><polyline points="16 17 22 17 22 11"/>',
            size, color=color
        )
    
    @staticmethod
    def pie_chart(size: int = DEFAULT_SIZE, color: str = "currentColor") -> str:
        """円グラフ"""
        return _svg_wrapper(
            '<path d="M21.21 15.89A10 10 0 1 1 8 2.83"/><path d="M22 12A10 10 0 0 0 12 2v10z"/>',
            size, color=color
        )
    
    @staticmethod
    def activity(size: int = DEFAULT_SIZE, color: str = "currentColor") -> str:
        """アクティビティ（心拍線）"""
        return _svg_wrapper(
            '<polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>',
            size, color=color
        )
    
    @staticmethod
    def line_chart(size: int = DEFAULT_SIZE, color: str = "currentColor") -> str:
        """折れ線グラフ"""
        return _svg_wrapper(
            '<path d="M3 3v18h18"/><path d="m19 9-5 5-4-4-3 3"/>',
            size, color=color
        )
    
    @staticmethod
    def gauge(size: int = DEFAULT_SIZE, color: str = "currentColor") -> str:
        """ゲージ"""
        return _svg_wrapper(
            '<path d="m12 14 4-4"/><path d="M3.34 19a10 10 0 1 1 17.32 0"/>',
            size, color=color
        )
    
    # ===== ナビゲーション・UI系 =====
    @staticmethod
    def layout_dashboard(size: int = DEFAULT_SIZE, color: str = "currentColor") -> str:
        """ダッシュボードレイアウト"""
        return _svg_wrapper(
            '<rect width="7" height="9" x="3" y="3" rx="1"/><rect width="7" height="5" x="14" y="3" rx="1"/><rect width="7" height="9" x="14" y="12" rx="1"/><rect width="7" height="5" x="3" y="16" rx="1"/>',
            size, color=color
        )
    
    @staticmethod
    def message_circle(size: int = DEFAULT_SIZE, color: str = "currentColor") -> str:
        """メッセージ（チャット）"""
        return _svg_wrapper(
            '<path d="M7.9 20A9 9 0 1 0 4 16.1L2 22Z"/>',
            size, color=color
        )
    
    @staticmethod
    def bot(size: int = DEFAULT_SIZE, color: str = "currentColor") -> str:
        """ボット・AI"""
        return _svg_wrapper(
            '<path d="M12 8V4H8"/><rect width="16" height="12" x="4" y="8" rx="2"/><path d="M2 14h2"/><path d="M20 14h2"/><path d="M15 13v2"/><path d="M9 13v2"/>',
            size, color=color
        )
    
    @staticmethod
    def sparkles(size: int = DEFAULT_SIZE, color: str = "currentColor") -> str:
        """スパークル（AI・魔法）"""
        return _svg_wrapper(
            '<path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/><path d="M5 3v4"/><path d="M19 17v4"/><path d="M3 5h4"/><path d="M17 19h4"/>',
            size, color=color
        )
    
    @staticmethod
    def settings(size: int = DEFAULT_SIZE, color: str = "currentColor") -> str:
        """設定（歯車）"""
        return _svg_wrapper(
            '<path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/><circle cx="12" cy="12" r="3"/>',
            size, color=color
        )
    
    @staticmethod
    def sliders_horizontal(size: int = DEFAULT_SIZE, color: str = "currentColor") -> str:
        """スライダー（調整）"""
        return _svg_wrapper(
            '<line x1="21" x2="14" y1="4" y2="4"/><line x1="10" x2="3" y1="4" y2="4"/><line x1="21" x2="12" y1="12" y2="12"/><line x1="8" x2="3" y1="12" y2="12"/><line x1="21" x2="16" y1="20" y2="20"/><line x1="12" x2="3" y1="20" y2="20"/><line x1="14" x2="14" y1="2" y2="6"/><line x1="8" x2="8" y1="10" y2="14"/><line x1="16" x2="16" y1="18" y2="22"/>',
            size, color=color
        )
    
    # ===== 日付・時間系 =====
    @staticmethod
    def calendar_days(size: int = DEFAULT_SIZE, color: str = "currentColor") -> str:
        """カレンダー（日付入り）"""
        return _svg_wrapper(
            '<rect width="18" height="18" x="3" y="4" rx="2" ry="2"/><line x1="16" x2="16" y1="2" y2="6"/><line x1="8" x2="8" y1="2" y2="6"/><line x1="3" x2="21" y1="10" y2="10"/><path d="M8 14h.01"/><path d="M12 14h.01"/><path d="M16 14h.01"/><path d="M8 18h.01"/><path d="M12 18h.01"/><path d="M16 18h.01"/>',
            size, color=color
        )
    
    @staticmethod
    def calendar_range(size: int = DEFAULT_SIZE, color: str = "currentColor") -> str:
        """カレンダー（範囲）"""
        return _svg_wrapper(
            '<rect width="18" height="18" x="3" y="4" rx="2" ry="2"/><line x1="16" x2="16" y1="2" y2="6"/><line x1="8" x2="8" y1="2" y2="6"/><line x1="3" x2="21" y1="10" y2="10"/><path d="M17 14h-6"/><path d="M13 18H7"/><path d="M7 14h.01"/><path d="M17 18h.01"/>',
            size, color=color
        )
    
    @staticmethod
    def clock(size: int = DEFAULT_SIZE, color: str = "currentColor") -> str:
        """時計"""
        return _svg_wrapper(
            '<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>',
            size, color=color
        )
    
    # ===== 場所・領域系 =====
    @staticmethod
    def map_pin(size: int = DEFAULT_SIZE, color: str = "currentColor") -> str:
        """マップピン"""
        return _svg_wrapper(
            '<path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/>',
            size, color=color
        )
    
    @staticmethod
    def globe(size: int = DEFAULT_SIZE, color: str = "currentColor") -> str:
        """地球儀"""
        return _svg_wrapper(
            '<circle cx="12" cy="12" r="10"/><line x1="2" x2="22" y1="12" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>',
            size, color=color
        )
    
    @staticmethod
    def building_2(size: int = DEFAULT_SIZE, color: str = "currentColor") -> str:
        """ビル"""
        return _svg_wrapper(
            '<path d="M6 22V4a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v18Z"/><path d="M6 12H4a2 2 0 0 0-2 2v6a2 2 0 0 0 2 2h2"/><path d="M18 9h2a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2h-2"/><path d="M10 6h4"/><path d="M10 10h4"/><path d="M10 14h4"/><path d="M10 18h4"/>',
            size, color=color
        )
    
    @staticmethod
    def layers(size: int = DEFAULT_SIZE, color: str = "currentColor") -> str:
        """レイヤー"""
        return _svg_wrapper(
            '<polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/>',
            size, color=color
        )
    
    # ===== ユーザー・イベント系 =====
    @staticmethod
    def users(size: int = DEFAULT_SIZE, color: str = "currentColor") -> str:
        """ユーザー複数"""
        return _svg_wrapper(
            '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
            size, color=color
        )
    
    @staticmethod
    def user_check(size: int = DEFAULT_SIZE, color: str = "currentColor") -> str:
        """ユーザー確認"""
        return _svg_wrapper(
            '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><polyline points="16 11 18 13 22 9"/>',
            size, color=color
        )
    
    @staticmethod
    def mouse_pointer_click(size: int = DEFAULT_SIZE, color: str = "currentColor") -> str:
        """クリック"""
        return _svg_wrapper(
            '<path d="m9 9 5 12 1.8-5.2L21 14Z"/><path d="M7.2 2.2 8 5.1"/><path d="m5.1 8-2.9-.8"/><path d="M14 4.1 12 6"/><path d="m6 12-1.9 2"/>',
            size, color=color
        )
    
    @staticmethod
    def zap(size: int = DEFAULT_SIZE, color: str = "currentColor") -> str:
        """稲妻（イベント）"""
        return _svg_wrapper(
            '<polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>',
            size, color=color
        )
    
    @staticmethod
    def target(size: int = DEFAULT_SIZE, color: str = "currentColor") -> str:
        """ターゲット（コンバージョン）"""
        return _svg_wrapper(
            '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>',
            size, color=color
        )
    
    @staticmethod
    def rocket(size: int = DEFAULT_SIZE, color: str = "currentColor") -> str:
        """ロケット"""
        return _svg_wrapper(
            '<path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 0 0 0-2.91-.09z"/><path d="m12 15-3-3a22 22 0 0 1 2-3.95A12.88 12.88 0 0 1 22 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 0 1-4 2z"/><path d="M9 12H4s.55-3.03 2-4c1.62-1.08 5 0 5 0"/><path d="M12 15v5s3.03-.55 4-2c1.08-1.62 0-5 0-5"/>',
            size, color=color
        )
    
    # ===== デバイス系 =====
    @staticmethod
    def smartphone(size: int = DEFAULT_SIZE, color: str = "currentColor") -> str:
        """スマートフォン"""
        return _svg_wrapper(
            '<rect width="14" height="20" x="5" y="2" rx="2" ry="2"/><path d="M12 18h.01"/>',
            size, color=color
        )
    
    @staticmethod
    def tablet(size: int = DEFAULT_SIZE, color: str = "currentColor") -> str:
        """タブレット"""
        return _svg_wrapper(
            '<rect width="16" height="20" x="4" y="2" rx="2" ry="2"/><line x1="12" x2="12.01" y1="18" y2="18"/>',
            size, color=color
        )
    
    @staticmethod
    def monitor(size: int = DEFAULT_SIZE, color: str = "currentColor") -> str:
        """モニター（デスクトップ）"""
        return _svg_wrapper(
            '<rect width="20" height="14" x="2" y="3" rx="2" ry="2"/><line x1="8" x2="16" y1="21" y2="21"/><line x1="12" x2="12" y1="17" y2="21"/>',
            size, color=color
        )
    
    # ===== 流入元・SEO系 =====
    @staticmethod
    def share_2(size: int = DEFAULT_SIZE, color: str = "currentColor") -> str:
        """シェア（流入元）"""
        return _svg_wrapper(
            '<circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" x2="15.42" y1="13.51" y2="17.49"/><line x1="15.41" x2="8.59" y1="6.51" y2="10.49"/>',
            size, color=color
        )
    
    @staticmethod
    def search(size: int = DEFAULT_SIZE, color: str = "currentColor") -> str:
        """検索"""
        return _svg_wrapper(
            '<circle cx="11" cy="11" r="8"/><line x1="21" x2="16.65" y1="21" y2="16.65"/>',
            size, color=color
        )
    
    @staticmethod
    def external_link(size: int = DEFAULT_SIZE, color: str = "currentColor") -> str:
        """外部リンク"""
        return _svg_wrapper(
            '<path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" x2="21" y1="14" y2="3"/>',
            size, color=color
        )
    
    @staticmethod
    def link(size: int = DEFAULT_SIZE, color: str = "currentColor") -> str:
        """リンク"""
        return _svg_wrapper(
            '<path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/>',
            size, color=color
        )
    
    # ===== ステータス系 =====
    @staticmethod
    def check_circle(size: int = DEFAULT_SIZE, color: str = "currentColor") -> str:
        """チェック（成功）"""
        return _svg_wrapper(
            '<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/>',
            size, color=color
        )
    
    @staticmethod
    def alert_circle(size: int = DEFAULT_SIZE, color: str = "currentColor") -> str:
        """警告"""
        return _svg_wrapper(
            '<circle cx="12" cy="12" r="10"/><line x1="12" x2="12" y1="8" y2="12"/><line x1="12" x2="12.01" y1="16" y2="16"/>',
            size, color=color
        )
    
    @staticmethod
    def wifi(size: int = DEFAULT_SIZE, color: str = "currentColor") -> str:
        """接続中"""
        return _svg_wrapper(
            '<path d="M5 13a10 10 0 0 1 14 0"/><path d="M8.5 16.5a5 5 0 0 1 7 0"/><path d="M2 8.82a15 15 0 0 1 20 0"/><line x1="12" x2="12.01" y1="20" y2="20"/>',
            size, color=color
        )
    
    # ===== その他 =====
    @staticmethod
    def file_text(size: int = DEFAULT_SIZE, color: str = "currentColor") -> str:
        """ドキュメント"""
        return _svg_wrapper(
            '<path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><polyline points="14 2 14 8 20 8"/><line x1="16" x2="8" y1="13" y2="13"/><line x1="16" x2="8" y1="17" y2="17"/><line x1="10" x2="8" y1="9" y2="9"/>',
            size, color=color
        )
    
    @staticmethod
    def megaphone(size: int = DEFAULT_SIZE, color: str = "currentColor") -> str:
        """メガホン（キャンペーン）"""
        return _svg_wrapper(
            '<path d="m3 11 18-5v12L3 13v-2z"/><path d="M11.6 16.8a3 3 0 1 1-5.8-1.6"/>',
            size, color=color
        )
    
    @staticmethod
    def arrow_up_right(size: int = DEFAULT_SIZE, color: str = "currentColor") -> str:
        """右上矢印"""
        return _svg_wrapper(
            '<line x1="7" x2="17" y1="17" y2="7"/><polyline points="7 7 17 7 17 17"/>',
            size, color=color
        )
    
    @staticmethod
    def arrow_down_right(size: int = DEFAULT_SIZE, color: str = "currentColor") -> str:
        """右下矢印"""
        return _svg_wrapper(
            '<line x1="7" x2="17" y1="7" y2="17"/><polyline points="17 7 17 17 7 17"/>',
            size, color=color
        )
    
    @staticmethod
    def chevron_right(size: int = DEFAULT_SIZE, color: str = "currentColor") -> str:
        """右シェブロン"""
        return _svg_wrapper(
            '<polyline points="9 18 15 12 9 6"/>',
            size, color=color
        )
    
    @staticmethod
    def refresh_cw(size: int = DEFAULT_SIZE, color: str = "currentColor") -> str:
        """リフレッシュ"""
        return _svg_wrapper(
            '<path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"/><path d="M21 3v5h-5"/><path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"/><path d="M8 16H3v5"/>',
            size, color=color
        )

