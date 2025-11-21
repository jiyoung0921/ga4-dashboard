"""可視化モジュール"""
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from typing import Dict, List, Optional, Any
import streamlit as st


class Visualization:
    """可視化クラス"""
    
    PRIMARY_COLOR = "#FF7A18"
    SECONDARY_COLOR = "#FF9F4C"
    COLORS = [
        "#FF7A18", "#F2B705", "#1AC6FF", "#8E8CFB", "#2EC4B6",
        "#FF9F4C", "#F8669E", "#6C8CF5", "#19B27D", "#FFD166"
    ]
    
    @staticmethod
    def _apply_base_layout(fig: go.Figure, title: str = "", x_title: str = "", y_title: str = "") -> go.Figure:
        fig.update_layout(
            title=title,
            xaxis_title=x_title,
            yaxis_title=y_title,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            hovermode='x unified',
            font=dict(family="SF Pro Display, SF Pro Text, Noto Sans JP, sans-serif", color="#1C1C1F"),
            title_font=dict(size=20, family="SF Pro Display, Noto Sans JP, sans-serif"),
            legend=dict(
                bgcolor="rgba(255,255,255,0.6)",
                bordercolor="rgba(0,0,0,0.05)",
                borderwidth=1,
                orientation="h",
                yanchor="bottom",
                y=1.02,
                x=0
            ),
            margin=dict(l=40, r=30, t=60, b=40)
        )
        fig.update_xaxes(showgrid=False, zeroline=False)
        fig.update_yaxes(showgrid=True, gridcolor="rgba(28,28,31,0.08)", zeroline=False)
        fig.update_traces(marker_line_width=0, selector=dict(type="bar"))
        return fig
    
    @staticmethod
    def create_line_chart(
        df: pd.DataFrame,
        x_column: str,
        y_columns: List[str],
        title: str,
        x_title: str = "",
        y_title: str = ""
    ) -> go.Figure:
        """折れ線グラフを作成"""
        fig = go.Figure()
        
        colors = Visualization.COLORS[:len(y_columns)]
        
        for i, y_col in enumerate(y_columns):
            fig.add_trace(go.Scatter(
                x=df[x_column],
                y=df[y_col],
                mode='lines+markers',
                name=y_col,
                line=dict(color=colors[i], width=2),
                marker=dict(size=6)
            ))
        
        fig.update_traces(line=dict(shape='spline'))
        fig = Visualization._apply_base_layout(fig, title, x_title, y_title)
        fig.update_layout(height=420)
        return fig
    
    @staticmethod
    def create_bar_chart(
        df: pd.DataFrame,
        x_column: str,
        y_column: str,
        title: str,
        x_title: str = "",
        y_title: str = "",
        orientation: str = 'v',
        color_column: Optional[str] = None
    ) -> go.Figure:
        """棒グラフを作成"""
        if df.empty:
            return go.Figure()
        
        if orientation == 'h':
            x = df[y_column]
            y = df[x_column]
            x_title, y_title = y_title, x_title
        else:
            x = df[x_column]
            y = df[y_column]
        
        if color_column:
            fig = px.bar(
                df,
                x=x,
                y=y,
                color=color_column,
                orientation=orientation,
                color_discrete_sequence=Visualization.COLORS
            )
        else:
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=x,
                y=y,
                orientation=orientation,
                marker_color=Visualization.PRIMARY_COLOR,
                marker=dict(line=dict(width=0))
            ))
        
        fig = Visualization._apply_base_layout(fig, title, x_title, y_title)
        fig.update_layout(height=420)
        return fig
    
    @staticmethod
    def create_pie_chart(
        df: pd.DataFrame,
        values_column: str,
        names_column: str,
        title: str
    ) -> go.Figure:
        """円グラフを作成"""
        if df.empty:
            return go.Figure()
        
        fig = go.Figure(data=[go.Pie(
            labels=df[names_column],
            values=df[values_column],
            hole=0.3,
            marker_colors=Visualization.COLORS
        )])
        
        fig = Visualization._apply_base_layout(fig, title)
        fig.update_layout(height=400)
        
        return fig
    
    @staticmethod
    def create_table(df: pd.DataFrame, title: str = "") -> pd.DataFrame:
        """テーブル用にDataFrameを準備"""
        return df.copy()
    
    @staticmethod
    def create_funnel_chart(
        steps: List[str],
        values: List[float],
        title: str = "コンバージョンファネル"
    ) -> go.Figure:
        """ファネルグラフを作成"""
        fig = go.Figure(go.Funnel(
            y=steps,
            x=values,
            textposition="inside",
            textinfo="value+percent initial",
            marker_color=Visualization.PRIMARY_COLOR
        ))
        
        fig = Visualization._apply_base_layout(fig, title)
        fig.update_layout(height=480)
        
        return fig
    
    @staticmethod
    def create_scatter_chart(
        df: pd.DataFrame,
        x_column: str,
        y_column: str,
        size_column: Optional[str] = None,
        color_column: Optional[str] = None,
        title: str = ""
    ) -> go.Figure:
        """散布図を作成"""
        if df.empty:
            return go.Figure()
        
        fig = px.scatter(
            df,
            x=x_column,
            y=y_column,
            size=size_column,
            color=color_column,
            title=title,
            color_discrete_sequence=Visualization.COLORS
        )
        
        fig = Visualization._apply_base_layout(fig, title or "")
        fig.update_layout(height=420)
        
        return fig
    
    @staticmethod
    def create_metric_card(value: Any, label: str, delta: Optional[Dict[str, Any]] = None) -> str:
        """メトリクスカード用のHTMLを生成"""
        delta_html = ""
        if delta:
            delta_value = delta.get('change_percent', 0)
            delta_color = "green" if delta.get('is_positive', True) else "red"
            delta_symbol = "+" if delta.get('is_positive', True) else ""
            delta_html = f'<span style="color: {delta_color}; font-size: 0.8em;">{delta_symbol}{delta_value:.1f}%</span>'
        
        return f"""
        <div style="background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <div style="font-size: 0.9em; color: #666; margin-bottom: 10px;">{label}</div>
            <div style="font-size: 2em; font-weight: bold; color: {Visualization.PRIMARY_COLOR};">{value}</div>
            {delta_html}
        </div>
        """


