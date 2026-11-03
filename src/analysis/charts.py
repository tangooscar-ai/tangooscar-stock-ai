import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

UP = "#26a69a"
DOWN = "#ef5350"
SPIKE = "#ffb300"

BULLISH = ["cdl_hammer", "cdl_bullish_engulfing", "cdl_bullish_harami", "cdl_morning_star"]
BEARISH = ["cdl_shooting_star", "cdl_bearish_engulfing", "cdl_bearish_harami", "cdl_evening_star"]
NEUTRAL = ["cdl_doji", "cdl_gap_up", "cdl_gap_down"]


def _pattern_points(data, names, price_col, factor):
    xs, ys, texts = [], [], []
    for _, row in data.iterrows():
        hits = [n.replace("cdl_", "").replace("_", " ") for n in names if row[n]]
        if hits:
            xs.append(row["date"])
            ys.append(row[price_col] * factor)
            texts.append(", ".join(hits))
    return xs, ys, texts


def _event_points(data, flag, price_col, factor, label):
    subset = data[data[flag]]
    xs = list(subset["date"])
    ys = list(subset[price_col] * factor)
    return xs, ys, [label] * len(xs)


def _marker_trace(points, name, symbol, color, size, visible=True):
    xs, ys, texts = points
    return go.Scatter(
        x=xs,
        y=ys,
        mode="markers",
        name=name,
        text=texts,
        hovertemplate="%{x}<br>%{text}<extra></extra>",
        marker=dict(symbol=symbol, size=size, color=color,
                    line=dict(width=1, color="white")),
        visible=visible,
    )


def build_chart(df, symbol, support=None, resistance=None, days=250, show_patterns=False):
    data = df.tail(days).reset_index(drop=True)
    x = data["date"]
    last_date = x.iloc[-1]

    fig = make_subplots(
        rows=4, cols=1, shared_xaxes=True, vertical_spacing=0.025,
        row_heights=[0.55, 0.15, 0.15, 0.15],
        subplot_titles=("", "Volume", "RSI (14)", "MACD (12, 26, 9)"),
    )

    fig.add_trace(go.Candlestick(
        x=x, open=data["open"], high=data["high"], low=data["low"],
        close=data["close"], name="Price",
        increasing_line_color=UP, decreasing_line_color=DOWN,
    ), row=1, col=1)

    for col, name, color in [("sma_20", "SMA 20", "#42a5f5"),
                             ("sma_50", "SMA 50", "#ffa726"),
                             ("sma_200", "SMA 200", "#ab47bc")]:
        fig.add_trace(go.Scatter(
            x=x, y=data[col], name=name, mode="lines",
            line=dict(width=1.3, color=color),
        ), row=1, col=1)

    for col, name in [("bb_upper", "Bollinger upper"), ("bb_lower", "Bollinger lower")]:
        fig.add_trace(go.Scatter(
            x=x, y=data[col], name=name, mode="lines", legendgroup="bb",
            line=dict(width=1, dash="dot", color="#9e9e9e"),
        ), row=1, col=1)

    for lv in resistance or []:
        fig.add_hline(
            y=lv["level"], line=dict(color=DOWN, width=1, dash="dash"),
            annotation_text=f"R {lv['level']:.2f} ({lv['distance_pct']:+.1f}%)",
            annotation_position="top left", row=1, col=1,
        )
    for lv in support or []:
        fig.add_hline(
            y=lv["level"], line=dict(color=UP, width=1, dash="dash"),
            annotation_text=f"S {lv['level']:.2f} ({lv['distance_pct']:+.1f}%)",
            annotation_position="bottom left", row=1, col=1,
        )

    events = [
        ("breakout_confirmed", "low", 0.99, "Breakout (heavy volume)", "triangle-up", "#00c853", 13),
        ("breakdown_confirmed", "high", 1.01, "Breakdown (heavy volume)", "triangle-down", "#d50000", 13),
        ("failed_breakout", "high", 1.01, "Failed breakout", "x", "#ff9800", 10),
        ("failed_breakdown", "low", 0.99, "Failed breakdown", "x", "#00bcd4", 10),
    ]
    for flag, price_col, factor, label, symbol_name, color, size in events:
        points = _event_points(data, flag, price_col, factor, label)
        fig.add_trace(_marker_trace(points, label, symbol_name, color, size), row=1, col=1)

    visible = True if show_patterns else "legendonly"
    patterns = [
        (BULLISH, "low", 0.985, "Bullish patterns", "diamond", UP),
        (BEARISH, "high", 1.015, "Bearish patterns", "diamond", DOWN),
        (NEUTRAL, "high", 1.012, "Neutral / gaps", "circle-open", "#bdbdbd"),
    ]
    for names, price_col, factor, label, symbol_name, color in patterns:
        points = _pattern_points(data, names, price_col, factor)
        fig.add_trace(_marker_trace(points, label, symbol_name, color, 9, visible), row=1, col=1)

    colors = []
    for _, r in data.iterrows():
        if r["volume_spike"]:
            colors.append(SPIKE)
        elif r["close"] >= r["open"]:
            colors.append(UP)
        else:
            colors.append(DOWN)
    fig.add_trace(go.Bar(x=x, y=data["volume"], marker_color=colors, name="Volume"), row=2, col=1)
    fig.add_trace(go.Scatter(
        x=x, y=data["volume_avg_20"], name="Volume avg 20", mode="lines",
        line=dict(width=1.2, color="#fafafa"),
    ), row=2, col=1)

    fig.add_trace(go.Scatter(
        x=x, y=data["rsi_14"], name="RSI 14", mode="lines",
        line=dict(width=1.3, color="#ce93d8"),
    ), row=3, col=1)
    for level in (70, 30):
        fig.add_hline(y=level, line=dict(color="#9e9e9e", width=1, dash="dash"), row=3, col=1)
    fig.update_yaxes(range=[0, 100], row=3, col=1)

    hist_colors = [UP if v >= 0 else DOWN for v in data["macd_hist"].fillna(0)]
    fig.add_trace(go.Bar(x=x, y=data["macd_hist"], marker_color=hist_colors,
                         name="MACD histogram"), row=4, col=1)
    fig.add_trace(go.Scatter(x=x, y=data["macd"], name="MACD", mode="lines",
                             line=dict(width=1.2, color="#42a5f5")), row=4, col=1)
    fig.add_trace(go.Scatter(x=x, y=data["macd_signal"], name="Signal", mode="lines",
                             line=dict(width=1.2, color="#ffa726")), row=4, col=1)

    all_days = pd.bdate_range(x.iloc[0], x.iloc[-1]).strftime("%Y-%m-%d")
    missing = sorted(set(all_days) - set(x))
    fig.update_xaxes(rangebreaks=[dict(bounds=["sat", "mon"]), dict(values=missing)])
    fig.update_xaxes(rangeslider_visible=False)
    fig.update_xaxes(
        rangeselector=dict(bgcolor="#37474f", font=dict(color="white"), buttons=[
            dict(count=1, label="1M", step="month", stepmode="backward"),
            dict(count=3, label="3M", step="month", stepmode="backward"),
            dict(count=6, label="6M", step="month", stepmode="backward"),
            dict(step="all", label="All"),
        ]),
        row=1, col=1,
    )
    fig.update_layout(
        template="plotly_dark",
        height=950,
        title=dict(text=f"{symbol} daily chart (data to {last_date}, delayed)", y=0.98),
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="top", y=-0.07, x=0),
        margin=dict(l=50, r=30, t=90, b=190),
    )
    fig.add_annotation(
        text="Source: Yahoo Finance via yfinance, about 15 minutes delayed. "
             "Research view, not investment advice.",
        xref="paper", yref="paper", x=0, y=-0.22, showarrow=False,
        font=dict(size=11),
    )
    fig.update_yaxes(title_text="Price (Rs)", row=1, col=1)
    return fig