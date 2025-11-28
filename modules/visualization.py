"""可視化モジュール - Modern Purple & Orange Theme"""
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from typing import Dict, List, Optional, Any
import streamlit as st


class Visualization:
    """可視化クラス - モダンダッシュボードテーマ"""
    
    # New color palette - Purple & Orange accent
    PRIMARY_COLOR = "#7C6AEF"
    SECONDARY_COLOR = "#A99BFF"
    ACCENT_COLOR = "#FF8C5A"
    
    # Chart colors - harmonious palette
    COLORS = [
        "#7C6AEF",  # Primary purple
        "#FF8C5A",  # Accent orange
        "#A99BFF",  # Light purple
        "#FFB088",  # Light orange
        "#5B4ACF",  # Deep purple
        "#E85A30",  # Deep orange
        "#B8ADFF",  # Pale purple
        "#6E6E8A",  # Neutral gray
        "#9E9EB8",  # Light gray
        "#4A3DB8",  # Dark purple
    ]
    
    # Gradient colors for area charts
    GRADIENT_PURPLE = ["rgba(124, 106, 239, 0.4)", "rgba(124, 106, 239, 0.05)"]
    GRADIENT_ORANGE = ["rgba(255, 140, 90, 0.4)", "rgba(255, 140, 90, 0.05)"]
    
    @staticmethod
    def _apply_base_layout(fig: go.Figure, title: str = "", x_title: str = "", y_title: str = "") -> go.Figure:
        """共通レイアウト設定"""
        fig.update_layout(
            title=dict(
                text=title,
                font=dict(
                    family="Plus Jakarta Sans, Inter, Noto Sans JP, sans-serif",
                    size=18,
                    color="#1A1A2E"
                ),
                x=0,
                xanchor="left"
            ),
            xaxis_title=x_title,
            yaxis_title=y_title,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            hovermode='x unified',
            hoverlabel=dict(
                bgcolor="white",
                font_size=13,
                font_family="Inter, Noto Sans JP, sans-serif",
                bordercolor="rgba(124, 106, 239, 0.2)"
            ),
            font=dict(
                family="Inter, Noto Sans JP, sans-serif",
                color="#1A1A2E",
                size=12
            ),
            legend=dict(
                bgcolor="rgba(255,255,255,0.9)",
                bordercolor="rgba(124, 106, 239, 0.1)",
                borderwidth=1,
                orientation="h",
                yanchor="bottom",
                y=1.02,
                x=0,
                font=dict(size=11)
            ),
            margin=dict(l=48, r=24, t=72, b=48)
        )
        
        # X軸スタイル
        fig.update_xaxes(
            showgrid=False,
            zeroline=False,
            showline=True,
            linewidth=1,
            linecolor="rgba(124, 106, 239, 0.1)",
            tickfont=dict(size=11, color="#6E6E8A")
        )
        
        # Y軸スタイル
        fig.update_yaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor="rgba(124, 106, 239, 0.06)",
            zeroline=False,
            showline=False,
            tickfont=dict(size=11, color="#6E6E8A")
        )
        
        # バーチャートのマーカー設定
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
        """折れ線グラフを作成（エリア塗りつぶし付き）"""
        fig = go.Figure()
        
        colors = Visualization.COLORS[:len(y_columns)]
        
        for i, y_col in enumerate(y_columns):
            # エリア塗りつぶし
            fig.add_trace(go.Scatter(
                x=df[x_column],
                y=df[y_col],
                mode='lines',
                name=y_col,
                line=dict(color=colors[i], width=2.5, shape='spline'),
                fill='tozeroy',
                fillcolor=f"rgba({int(colors[i][1:3], 16)}, {int(colors[i][3:5], 16)}, {int(colors[i][5:7], 16)}, 0.1)"
            ))
            
            # マーカーポイント
            fig.add_trace(go.Scatter(
                x=df[x_column],
                y=df[y_col],
                mode='markers',
                name=y_col,
                showlegend=False,
                marker=dict(
                    color='white',
                    size=8,
                    line=dict(color=colors[i], width=2)
                )
            ))
        
        fig = Visualization._apply_base_layout(fig, title, x_title, y_title)
        fig.update_layout(height=380)
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
        """棒グラフを作成（角丸・グラデーション風）"""
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
                marker=dict(
                    color=Visualization.PRIMARY_COLOR,
                    line=dict(width=0),
                    cornerradius=6
                ),
                hovertemplate='<b>%{y}</b><br>%{x:,.0f}<extra></extra>' if orientation == 'h' else '<b>%{x}</b><br>%{y:,.0f}<extra></extra>'
            ))
        
        fig = Visualization._apply_base_layout(fig, title, x_title, y_title)
        fig.update_layout(height=380)
        
        # 横棒グラフの場合はY軸を逆順に
        if orientation == 'h':
            fig.update_yaxes(autorange="reversed")
        
        return fig
    
    @staticmethod
    def create_pie_chart(
        df: pd.DataFrame,
        values_column: str,
        names_column: str,
        title: str
    ) -> go.Figure:
        """ドーナツチャートを作成"""
        if df.empty:
            return go.Figure()
        
        fig = go.Figure(data=[go.Pie(
            labels=df[names_column],
            values=df[values_column],
            hole=0.55,
            marker=dict(
                colors=Visualization.COLORS,
                line=dict(color='white', width=2)
            ),
            textposition='outside',
            textinfo='label+percent',
            textfont=dict(size=11),
            hovertemplate='<b>%{label}</b><br>%{value:,.0f} (%{percent})<extra></extra>'
        )])
        
        fig = Visualization._apply_base_layout(fig, title)
        fig.update_layout(
            height=380,
            showlegend=False,
            annotations=[dict(
                text='',
                x=0.5, y=0.5,
                font_size=14,
                showarrow=False
            )]
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
            marker=dict(
                color=[Visualization.PRIMARY_COLOR, Visualization.SECONDARY_COLOR, 
                       Visualization.ACCENT_COLOR, "#FFB088", "#B8ADFF"][:len(steps)],
                line=dict(width=0)
            ),
            connector=dict(line=dict(color="rgba(124, 106, 239, 0.2)", width=1))
        ))
        
        fig = Visualization._apply_base_layout(fig, title)
        fig.update_layout(height=420)
        
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
        
        # マーカースタイル
        fig.update_traces(
            marker=dict(
                line=dict(width=1, color='white'),
                opacity=0.8
            )
        )
        
        fig = Visualization._apply_base_layout(fig, title or "")
        fig.update_layout(height=380)
        
        return fig
    
    @staticmethod
    def create_area_chart(
        df: pd.DataFrame,
        x_column: str,
        y_columns: List[str],
        title: str,
        x_title: str = "",
        y_title: str = ""
    ) -> go.Figure:
        """エリアチャートを作成（スタック）"""
        fig = go.Figure()
        
        colors = Visualization.COLORS[:len(y_columns)]
        
        for i, y_col in enumerate(y_columns):
            fig.add_trace(go.Scatter(
                x=df[x_column],
                y=df[y_col],
                mode='lines',
                name=y_col,
                stackgroup='one',
                line=dict(width=0.5, color=colors[i]),
                fillcolor=f"rgba({int(colors[i][1:3], 16)}, {int(colors[i][3:5], 16)}, {int(colors[i][5:7], 16)}, 0.6)"
            ))
        
        fig = Visualization._apply_base_layout(fig, title, x_title, y_title)
        fig.update_layout(height=380)
        return fig
    
    @staticmethod
    def create_metric_card(value: Any, label: str, delta: Optional[Dict[str, Any]] = None) -> str:
        """メトリクスカード用のHTMLを生成"""
        delta_html = ""
        if delta:
            delta_value = delta.get('change_percent', 0)
            is_positive = delta.get('is_positive', True)
            delta_color = "#059669" if is_positive else "#DC2626"
            delta_bg = "rgba(16, 185, 129, 0.1)" if is_positive else "rgba(239, 68, 68, 0.1)"
            delta_symbol = "+" if is_positive else ""
            delta_html = f'''
                <span style="
                    color: {delta_color}; 
                    font-size: 0.8em;
                    font-weight: 600;
                    padding: 4px 10px;
                    border-radius: 999px;
                    background: {delta_bg};
                ">{delta_symbol}{delta_value:.1f}%</span>
            '''
        
        return f"""
        <div style="
            background: white; 
            padding: 24px; 
            border-radius: 16px; 
            box-shadow: 0 4px 20px rgba(124, 106, 239, 0.08);
            border: 1px solid rgba(124, 106, 239, 0.08);
            transition: all 0.3s ease;
        ">
            <div style="
                font-size: 0.8rem; 
                color: #6E6E8A; 
                margin-bottom: 12px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.05em;
            ">{label}</div>
            <div style="
                font-size: 2.25rem; 
                font-weight: 800; 
                color: #1A1A2E;
                font-family: 'Plus Jakarta Sans', sans-serif;
                line-height: 1.1;
                margin-bottom: 8px;
            ">{value}</div>
            {delta_html}
        </div>
        """
    
    @staticmethod
    def create_progress_bar(value: float, max_value: float, label: str) -> str:
        """プログレスバーHTMLを生成"""
        percentage = (value / max_value * 100) if max_value > 0 else 0
        
        return f"""
        <div style="margin-bottom: 16px;">
            <div style="
                display: flex;
                justify-content: space-between;
                margin-bottom: 8px;
                font-size: 0.85rem;
            ">
                <span style="color: #1A1A2E; font-weight: 600;">{label}</span>
                <span style="color: #6E6E8A;">{value:,.0f}</span>
            </div>
            <div style="
                height: 8px;
                background: rgba(124, 106, 239, 0.1);
                border-radius: 999px;
                overflow: hidden;
            ">
                <div style="
                    height: 100%;
                    width: {percentage}%;
                    background: linear-gradient(90deg, #7C6AEF 0%, #FF8C5A 100%);
                    border-radius: 999px;
                    transition: width 0.5s ease;
                "></div>
            </div>
        </div>
        """
