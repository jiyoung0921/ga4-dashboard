"""ヘッダーヒーローコンポーネント - Modern Design with Lucide Icons"""
import streamlit as st
from datetime import datetime
from typing import Optional
from components.icons import Icons


def render_header(site_scope: Optional[str], start_date: str, end_date: str) -> None:
    """モダンなヒーローヘッダーを描画"""
    scope_label = site_scope if site_scope else "全サイト"
    start_display = datetime.strptime(start_date, "%Y-%m-%d").strftime("%Y年%m月%d日")
    end_display = datetime.strptime(end_date, "%Y-%m-%d").strftime("%Y年%m月%d日")
    current_time = datetime.now().strftime('%Y/%m/%d %H:%M')

    st.markdown(
        f"""
        <div class="hero-banner">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 16px;">
                <div>
                    <div style="
                        display: flex;
                        align-items: center;
                        gap: 8px;
                        font-size: 0.75rem;
                        font-weight: 600;
                        text-transform: uppercase;
                        letter-spacing: 0.1em;
                        opacity: 0.85;
                        margin-bottom: 8px;
                    ">
                        {Icons.activity(14, "white")}
                        Analytics Dashboard
                    </div>
                    <div class="hero-title" style="display: flex; align-items: center; gap: 12px;">
                        {Icons.pie_chart(28, "white")}
                        {scope_label}
                    </div>
                </div>
                <div style="text-align: right;">
                    <div style="
                        display: flex;
                        align-items: center;
                        gap: 6px;
                        font-size: 0.75rem;
                        opacity: 0.7;
                        margin-bottom: 4px;
                        justify-content: flex-end;
                    ">
                        {Icons.refresh_cw(12, "white")}
                        最終更新
                    </div>
                    <div style="
                        font-size: 0.9rem;
                        font-weight: 600;
                    ">{current_time}</div>
                </div>
            </div>
            <div class="hero-meta">
                <span class="hero-chip">
                    {Icons.calendar_range(14, "white")}
                    {start_display} 〜 {end_display}
                </span>
                <span class="hero-chip">
                    {Icons.layers(14, "white")}
                    {scope_label}
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_section_header(icon_name: str, title: str, subtitle: Optional[str] = None) -> None:
    """セクションヘッダーを描画（アイコン名で指定）"""
    
    # アイコンマッピング
    icon_map = {
        "overview": Icons.gauge(24, "#7C6AEF"),
        "traffic": Icons.share_2(24, "#7C6AEF"),
        "device": Icons.smartphone(24, "#7C6AEF"),
        "event": Icons.zap(24, "#7C6AEF"),
        "realtime": Icons.activity(24, "#7C6AEF"),
        "utm": Icons.megaphone(24, "#7C6AEF"),
        "seo": Icons.search(24, "#7C6AEF"),
        "chart": Icons.bar_chart_3(24, "#7C6AEF"),
        "users": Icons.users(24, "#7C6AEF"),
        "target": Icons.target(24, "#7C6AEF"),
        "trending": Icons.trending_up(24, "#7C6AEF"),
        "custom": Icons.sliders_horizontal(24, "#7C6AEF"),
    }
    
    icon_svg = icon_map.get(icon_name, Icons.bar_chart_3(24, "#7C6AEF"))
    subtitle_html = f'<div style="font-size: 0.85rem; color: #6E6E8A; margin-top: 4px;">{subtitle}</div>' if subtitle else ''
    
    st.markdown(
        f"""
        <div style="
            display: flex;
            align-items: center;
            gap: 16px;
            margin: 2rem 0 1.5rem;
        ">
            <div style="
                width: 52px;
                height: 52px;
                border-radius: 16px;
                background: linear-gradient(135deg, rgba(124, 106, 239, 0.12) 0%, rgba(255, 140, 90, 0.08) 100%);
                display: flex;
                align-items: center;
                justify-content: center;
                box-shadow: 0 4px 12px rgba(124, 106, 239, 0.1);
            ">{icon_svg}</div>
            <div>
                <div style="
                    font-family: 'Plus Jakarta Sans', 'Inter', sans-serif;
                    font-size: 1.35rem;
                    font-weight: 700;
                    color: #1A1A2E;
                ">{title}</div>
                {subtitle_html}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_stat_card(value: str, label: str, icon_name: str, trend: Optional[str] = None, trend_positive: bool = True) -> None:
    """統計カードを描画（アイコン名で指定）"""
    
    # アイコンマッピング
    icon_map = {
        "sessions": Icons.users(20, "#7C6AEF"),
        "users": Icons.user_check(20, "#7C6AEF"),
        "pageviews": Icons.file_text(20, "#7C6AEF"),
        "events": Icons.zap(20, "#7C6AEF"),
        "conversions": Icons.target(20, "#7C6AEF"),
        "bounce": Icons.arrow_down_right(20, "#7C6AEF"),
        "duration": Icons.clock(20, "#7C6AEF"),
        "clicks": Icons.mouse_pointer_click(20, "#7C6AEF"),
        "trending_up": Icons.trending_up(20, "#10B981"),
        "trending_down": Icons.trending_down(20, "#DC2626"),
    }
    
    icon_svg = icon_map.get(icon_name, Icons.bar_chart_3(20, "#7C6AEF"))
    
    trend_html = ""
    if trend:
        trend_color = "#059669" if trend_positive else "#DC2626"
        trend_bg = "rgba(16, 185, 129, 0.1)" if trend_positive else "rgba(239, 68, 68, 0.1)"
        trend_icon = Icons.trending_up(12, trend_color) if trend_positive else Icons.trending_down(12, trend_color)
        trend_html = f'''
            <div style="
                display: inline-flex;
                align-items: center;
                gap: 4px;
                padding: 4px 10px;
                border-radius: 999px;
                background: {trend_bg};
                color: {trend_color};
                font-size: 0.75rem;
                font-weight: 600;
                margin-top: 8px;
            ">{trend_icon} {trend}</div>
        '''
    
    st.markdown(
        f"""
        <div style="
            background: white;
            border-radius: 20px;
            padding: 24px;
            border: 1px solid rgba(124, 106, 239, 0.08);
            box-shadow: 0 4px 20px rgba(124, 106, 239, 0.06);
            height: 100%;
            transition: all 0.3s ease;
        ">
            <div style="
                display: flex;
                justify-content: space-between;
                align-items: flex-start;
                margin-bottom: 16px;
            ">
                <div style="
                    width: 48px;
                    height: 48px;
                    border-radius: 14px;
                    background: linear-gradient(135deg, rgba(124, 106, 239, 0.12) 0%, rgba(255, 140, 90, 0.08) 100%);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                ">{icon_svg}</div>
            </div>
            <div style="
                font-size: 0.8rem;
                font-weight: 600;
                color: #6E6E8A;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                margin-bottom: 8px;
            ">{label}</div>
            <div style="
                font-family: 'Plus Jakarta Sans', sans-serif;
                font-size: 2rem;
                font-weight: 800;
                color: #1A1A2E;
                line-height: 1.1;
            ">{value}</div>
            {trend_html}
        </div>
        """,
        unsafe_allow_html=True
    )


def render_mini_stat(value: str, label: str, icon_name: str, color: str = "#7C6AEF") -> None:
    """ミニ統計カードを描画"""
    
    icon_map = {
        "up": Icons.trending_up(16, color),
        "down": Icons.trending_down(16, color),
        "users": Icons.users(16, color),
        "click": Icons.mouse_pointer_click(16, color),
        "target": Icons.target(16, color),
        "zap": Icons.zap(16, color),
    }
    
    icon_svg = icon_map.get(icon_name, Icons.bar_chart_3(16, color))
    
    st.markdown(
        f"""
        <div style="
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 12px 16px;
            background: rgba(124, 106, 239, 0.04);
            border-radius: 12px;
            border: 1px solid rgba(124, 106, 239, 0.08);
        ">
            <div style="
                width: 36px;
                height: 36px;
                border-radius: 10px;
                background: white;
                display: flex;
                align-items: center;
                justify-content: center;
                box-shadow: 0 2px 8px rgba(124, 106, 239, 0.08);
            ">{icon_svg}</div>
            <div>
                <div style="
                    font-family: 'Plus Jakarta Sans', sans-serif;
                    font-size: 1.1rem;
                    font-weight: 700;
                    color: #1A1A2E;
                ">{value}</div>
                <div style="
                    font-size: 0.7rem;
                    color: #6E6E8A;
                    text-transform: uppercase;
                    letter-spacing: 0.03em;
                ">{label}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
