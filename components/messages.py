"""ステータスメッセージ用の共通コンポーネント"""
from __future__ import annotations

from textwrap import dedent
from typing import Optional, Any

import streamlit as st

from components.icons import Icons

VARIANT_STYLES = {
    "info": {
        "bg": "#F1F5FF",
        "border": "#C7D2FE",
        "color": "#1E3A8A",
        "icon": Icons.info,
    },
    "warning": {
        "bg": "#FFF9E6",
        "border": "#F6E3B4",
        "color": "#8A4B0F",
        "icon": Icons.alert_circle,
    },
    "error": {
        "bg": "#FEECEC",
        "border": "#F5B5B5",
        "color": "#972D2D",
        "icon": Icons.x_circle,
    },
    "success": {
        "bg": "#ECFDF3",
        "border": "#B7F0D8",
        "color": "#1B7C4A",
        "icon": Icons.check_circle,
    },
}


def render_message(text: str, variant: str = "info", container: Optional[Any] = None) -> None:
    """Lucideアイコン付きのステータスメッセージを描画"""
    style = VARIANT_STYLES.get(variant, VARIANT_STYLES["info"])
    icon_svg = style["icon"](16, style["color"])
    content_html = text.replace("\n", "<br />")
    html = dedent(
        f"""
        <div style="
            display: flex;
            gap: 10px;
            align-items: flex-start;
            border-radius: 14px;
            padding: 12px 14px;
            border: 1px solid {style['border']};
            background: {style['bg']};
            color: {style['color']};
            font-size: 0.9rem;
            line-height: 1.5;
        ">
            <span style="display: inline-flex; padding-top: 2px;">{icon_svg}</span>
            <span style="flex: 1;">{content_html}</span>
        </div>
        """
    )
    target = container if container is not None else st
    target.markdown(html, unsafe_allow_html=True)

