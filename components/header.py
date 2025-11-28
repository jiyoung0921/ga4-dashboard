"""ヘッダーヒーローコンポーネント - Modern Design"""
import streamlit as st
from datetime import datetime
from typing import Optional


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
                        font-size: 0.75rem;
                        font-weight: 600;
                        text-transform: uppercase;
                        letter-spacing: 0.1em;
                        opacity: 0.8;
                        margin-bottom: 8px;
                    ">Analytics Dashboard</div>
                    <div class="hero-title">📊 {scope_label}</div>
                </div>
                <div style="text-align: right;">
                    <div style="
                        font-size: 0.75rem;
                        opacity: 0.7;
                        margin-bottom: 4px;
                    ">最終更新</div>
                    <div style="
                        font-size: 0.9rem;
                        font-weight: 600;
                    ">{current_time}</div>
                </div>
            </div>
            <div class="hero-meta">
                <span class="hero-chip">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                        <line x1="16" y1="2" x2="16" y2="6"></line>
                        <line x1="8" y1="2" x2="8" y2="6"></line>
                        <line x1="3" y1="10" x2="21" y2="10"></line>
                    </svg>
                    {start_display} 〜 {end_display}
                </span>
                <span class="hero-chip">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
                        <circle cx="12" cy="10" r="3"></circle>
                    </svg>
                    {scope_label}
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_section_header(icon: str, title: str, subtitle: Optional[str] = None) -> None:
    """セクションヘッダーを描画"""
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
                width: 48px;
                height: 48px;
                border-radius: 14px;
                background: linear-gradient(135deg, rgba(124, 106, 239, 0.15) 0%, rgba(255, 140, 90, 0.1) 100%);
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 1.5rem;
            ">{icon}</div>
            <div>
                <div style="
                    font-family: 'Plus Jakarta Sans', 'Inter', sans-serif;
                    font-size: 1.25rem;
                    font-weight: 700;
                    color: #1A1A2E;
                ">{title}</div>
                {subtitle_html}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_stat_card(value: str, label: str, icon: str, trend: Optional[str] = None, trend_positive: bool = True) -> None:
    """統計カードを描画"""
    trend_html = ""
    if trend:
        trend_color = "#059669" if trend_positive else "#DC2626"
        trend_bg = "rgba(16, 185, 129, 0.1)" if trend_positive else "rgba(239, 68, 68, 0.1)"
        arrow = "↑" if trend_positive else "↓"
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
            ">{arrow} {trend}</div>
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
        ">
            <div style="
                display: flex;
                justify-content: space-between;
                align-items: flex-start;
                margin-bottom: 16px;
            ">
                <div style="
                    width: 44px;
                    height: 44px;
                    border-radius: 12px;
                    background: linear-gradient(135deg, rgba(124, 106, 239, 0.12) 0%, rgba(255, 140, 90, 0.08) 100%);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 1.25rem;
                ">{icon}</div>
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
