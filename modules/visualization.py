"""可視化モジュール"""
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from typing import Dict, List, Optional, Any
import streamlit as st


class Visualization:
    """可視化クラス"""
    
    # カラーパレット
    PRIMARY_COLOR = "#FF6F3C"
    SECONDARY_COLOR = "#FF9A3C"
    COLORS = [
        "#FF6F3C", "#FF9A3C", "#FFC46B", "#2A9D8F", "#264653",
        "#E76F51", "#F4A261", "#E9C46A", "#6D597A", "#4D908E"
    ]
    
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
        
        fig.update_layout(
            title=title,
            xaxis_title=x_title,
            yaxis_title=y_title,
            hovermode='x unified',
            template='plotly_white',
            font=dict(family="Noto Sans JP, Roboto, sans-serif"),
            height=400
        )
        
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
        
        fig = go.Figure()
        
        if color_column:
            fig = px.bar(
                df,
                x=x,
                y=y,
                color=color_column,
                orientation=orientation,
                title=title,
                color_discrete_sequence=Visualization.COLORS
            )
        else:
            fig.add_trace(go.Bar(
                x=x,
                y=y,
                orientation=orientation,
                marker_color=Visualization.PRIMARY_COLOR
            ))
            fig.update_layout(title=title)
        
        fig.update_layout(
            xaxis_title=x_title,
            yaxis_title=y_title,
            template='plotly_white',
            font=dict(family="Noto Sans JP, Roboto, sans-serif"),
            height=400
        )
        
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
        
        fig.update_layout(
            title=title,
            template='plotly_white',
            font=dict(family="Noto Sans JP, Roboto, sans-serif"),
            height=400
        )
        
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
        
        fig.update_layout(
            title=title,
            template='plotly_white',
            font=dict(family="Noto Sans JP, Roboto, sans-serif"),
            height=500
        )
        
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
        
        fig.update_layout(
            template='plotly_white',
            font=dict(family="Noto Sans JP, Roboto, sans-serif"),
            height=400
        )
        
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


