"""ヘッダーヒーローコンポーネント - Soft Friendly Design with Lucide Icons"""
import streamlit as st
from datetime import datetime
from typing import Optional
from components.icons import Icons


def render_header(site_scope: Optional[str], start_date: str, end_date: str) -> None:
    """やさしい雰囲気のヒーローヘッダーを描画"""
    scope_label = site_scope if site_scope else "全サイト"
    start_display = datetime.strptime(start_date, "%Y-%m-%d").strftime("%Y年%m月%d日")
    end_display = datetime.strptime(end_date, "%Y-%m-%d").strftime("%Y年%m月%d日")
    current_time = datetime.now().strftime('%Y/%m/%d %H:%M')

    st.markdown(
        f"""
        <div class="hero-banner">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 14px;">
                <div>
                    <div style="
                        display: flex;
                        align-items: center;
                        gap: 6px;
                        font-size: 0.7rem;
                        font-weight: 600;
                        letter-spacing: 0.05em;
                        opacity: 0.9;
                        margin-bottom: 6px;
                    ">
                        {Icons.activity(12, "white")}
                        ANALYTICS DASHBOARD
                    </div>
                    <div class="hero-title">
                        {Icons.pie_chart(24, "white")}
                        {scope_label}
                    </div>
                </div>
                <div style="text-align: right;">
                    <div style="
                        display: flex;
                        align-items: center;
                        gap: 5px;
                        font-size: 0.7rem;
                        opacity: 0.75;
                        margin-bottom: 3px;
                        justify-content: flex-end;
                    ">
                        {Icons.refresh_cw(10, "white")}
                        最終更新
                    </div>
                    <div style="
                        font-size: 0.85rem;
                        font-weight: 600;
                    ">{current_time}</div>
                </div>
            </div>
            <div class="hero-meta">
                <span class="hero-chip">
                    {Icons.calendar_range(12, "white")}
                    {start_display} 〜 {end_display}
                </span>
                <span class="hero-chip">
                    {Icons.layers(12, "white")}
                    {scope_label}
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_section_header(icon_name: str, title: str, subtitle: Optional[str] = None) -> None:
    """セクションヘッダーを描画（アイコン名で指定）"""
    
    icon_map = {
        "overview": Icons.gauge(20, "#7C6AEF"),
        "traffic": Icons.share_2(20, "#7C6AEF"),
        "device": Icons.smartphone(20, "#7C6AEF"),
        "event": Icons.zap(20, "#7C6AEF"),
        "realtime": Icons.activity(20, "#7C6AEF"),
        "utm": Icons.megaphone(20, "#7C6AEF"),
        "seo": Icons.search(20, "#7C6AEF"),
        "chart": Icons.bar_chart_3(20, "#7C6AEF"),
        "users": Icons.users(20, "#7C6AEF"),
        "target": Icons.target(20, "#7C6AEF"),
        "trending": Icons.trending_up(20, "#7C6AEF"),
        "custom": Icons.sliders_horizontal(20, "#7C6AEF"),
    }
    
    icon_svg = icon_map.get(icon_name, Icons.bar_chart_3(20, "#7C6AEF"))
    subtitle_html = f'<div style="font-size: 0.8rem; color: #718096; margin-top: 3px;">{subtitle}</div>' if subtitle else ''
    
    st.markdown(
        f"""
        <div style="
            display: flex;
            align-items: center;
            gap: 14px;
            margin: 1.5rem 0 1.25rem;
        ">
            <div style="
                width: 44px;
                height: 44px;
                border-radius: 14px;
                background: linear-gradient(135deg, rgba(124, 106, 239, 0.1) 0%, rgba(255, 140, 90, 0.06) 100%);
                display: flex;
                align-items: center;
                justify-content: center;
            ">{icon_svg}</div>
            <div>
                <div style="
                    font-family: 'Quicksand', 'M PLUS Rounded 1c', sans-serif;
                    font-size: 1.15rem;
                    font-weight: 700;
                    color: #2D3748;
                ">{title}</div>
                {subtitle_html}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_stat_card(value: str, label: str, icon_name: str, trend: Optional[str] = None, trend_positive: bool = True) -> None:
    """統計カードを描画"""
    
    icon_map = {
        "sessions": Icons.users(18, "#7C6AEF"),
        "users": Icons.user_check(18, "#7C6AEF"),
        "pageviews": Icons.file_text(18, "#7C6AEF"),
        "events": Icons.zap(18, "#7C6AEF"),
        "conversions": Icons.target(18, "#7C6AEF"),
        "bounce": Icons.arrow_down_right(18, "#7C6AEF"),
        "duration": Icons.clock(18, "#7C6AEF"),
        "clicks": Icons.mouse_pointer_click(18, "#7C6AEF"),
        "trending_up": Icons.trending_up(18, "#48BB78"),
        "trending_down": Icons.trending_down(18, "#E53E3E"),
    }
    
    icon_svg = icon_map.get(icon_name, Icons.bar_chart_3(18, "#7C6AEF"))
    
    trend_html = ""
    if trend:
        trend_color = "#38A169" if trend_positive else "#E53E3E"
        trend_bg = "rgba(72, 187, 120, 0.12)" if trend_positive else "rgba(245, 101, 101, 0.12)"
        trend_icon = Icons.trending_up(10, trend_color) if trend_positive else Icons.trending_down(10, trend_color)
        trend_html = f'''
            <div style="
                display: inline-flex;
                align-items: center;
                gap: 3px;
                padding: 3px 8px;
                border-radius: 999px;
                background: {trend_bg};
                color: {trend_color};
                font-size: 0.7rem;
                font-weight: 600;
                margin-top: 6px;
            ">{trend_icon} {trend}</div>
        '''
    
    st.markdown(
        f"""
        <div style="
            background: white;
            border-radius: 16px;
            padding: 18px;
            box-shadow: 0 2px 8px rgba(124, 106, 239, 0.06);
            height: 100%;
        ">
            <div style="
                display: flex;
                justify-content: space-between;
                align-items: flex-start;
                margin-bottom: 12px;
            ">
                <div style="
                    width: 40px;
                    height: 40px;
                    border-radius: 12px;
                    background: linear-gradient(135deg, rgba(124, 106, 239, 0.1) 0%, rgba(255, 140, 90, 0.06) 100%);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                ">{icon_svg}</div>
            </div>
            <div style="
                font-size: 0.7rem;
                font-weight: 600;
                color: #718096;
                letter-spacing: 0.03em;
                margin-bottom: 6px;
            ">{label}</div>
            <div style="
                font-family: 'Quicksand', 'M PLUS Rounded 1c', sans-serif;
                font-size: 1.65rem;
                font-weight: 700;
                color: #2D3748;
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
        "up": Icons.trending_up(14, color),
        "down": Icons.trending_down(14, color),
        "users": Icons.users(14, color),
        "click": Icons.mouse_pointer_click(14, color),
        "target": Icons.target(14, color),
        "zap": Icons.zap(14, color),
    }
    
    icon_svg = icon_map.get(icon_name, Icons.bar_chart_3(14, color))
    
    st.markdown(
        f"""
        <div style="
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 10px 14px;
            background: rgba(124, 106, 239, 0.04);
            border-radius: 10px;
        ">
            <div style="
                width: 32px;
                height: 32px;
                border-radius: 8px;
                background: white;
                display: flex;
                align-items: center;
                justify-content: center;
                box-shadow: 0 2px 6px rgba(124, 106, 239, 0.06);
            ">{icon_svg}</div>
            <div>
                <div style="
                    font-family: 'Quicksand', 'M PLUS Rounded 1c', sans-serif;
                    font-size: 1rem;
                    font-weight: 700;
                    color: #2D3748;
                ">{value}</div>
                <div style="
                    font-size: 0.65rem;
                    color: #718096;
                    letter-spacing: 0.02em;
                ">{label}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
