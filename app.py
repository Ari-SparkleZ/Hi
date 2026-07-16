import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.colors import LinearSegmentedColormap
import pandas as pd

st.set_page_config(page_title="Cobweb Plot Explorer", layout="centered")
st.title("고정점 반복법 시각화")
st.write("반복함수 g(x)를 입력하면 cobweb plot과 반복값 변화를 확인할 수 있습니다.")

if "expr" not in st.session_state:
    st.session_state.expr = "(x+2)/3"
if "x0" not in st.session_state:
    st.session_state.x0 = 0.0
if "n_iter" not in st.session_state:
    st.session_state.n_iter = 20
if "tol" not in st.session_state:
    st.session_state.tol = 1e-6
if "xgrid_min" not in st.session_state:
    st.session_state.xgrid_min = -5.0
if "xgrid_max" not in st.session_state:
    st.session_state.xgrid_max = 5.0
if "zoom_center" not in st.session_state:
    st.session_state.zoom_center = 0.0
if "zoom_factor" not in st.session_state:
    st.session_state.zoom_factor = 1.0
if "base_half" not in st.session_state:
    st.session_state.base_half = 5.0

st.subheader("입력")
expr = st.text_input("반복함수 g(x)", key="expr")
x0 = st.number_input("초기값 x0", key="x0", format="%.6f")
n_iter = st.slider("반복 횟수", min_value=1, max_value=500, key="n_iter")
tol = st.number_input("수렴 판정 기준 tol", key="tol", format="%.8f")

xgrid_min = st.slider("그래프 x축 최소(함수 계산용)", min_value=-100.0, max_value=100.0, key="xgrid_min", step=0.5)
xgrid_max = st.slider("그래프 x축 최대(함수 계산용)", min_value=-100.0, max_value=100.0, key="xgrid_max", step=0.5)

zoom_center = st.slider("확대 중심", min_value=-10.0, max_value=10.0, key="zoom_center", step=0.1)
zoom_factor = st.slider("확대 배율", min_value=1.0, max_value=50.0, key="zoom_factor", step=0.5)
base_half = st.slider("기본 폭", min_value=0.001, max_value=10.0, key="base_half", step=0.001)

expr = expr.replace("^", "**")

allowed_names = {
    "np": np,
    "sin": np.sin,
    "cos": np.cos,
    "tan": np.tan,
    "sqrt": np.sqrt,
    "exp": np.exp,
    "log": np.log,
    "abs": abs,
    "pi": np.pi,
    "e": np.e
}

def g(x):
    return eval(expr, {"__builtins__": {}}, {**allowed_names, "x": x})

if st.button("실행"):
    try:
        if xgrid_min >= xgrid_max:
            st.error("x축 최소값은 최대값보다 작아야 합니다.")
            st.stop()

        xs = [float(x0)]
        errors = [np.nan]

        for _ in range(n_iter):
            x_next = float(g(xs[-1]))
            xs.append(x_next)
            errors.append(abs(xs[-1] - xs[-2]))

        df = pd.DataFrame({
            "n": range(len(xs)),
            "x_n": xs,
            "abs_error": errors
        })

        st.subheader("반복값 표")
        st.dataframe(df, use_container_width=True)

        converged = any(e < tol for e in errors[1:])
        if converged:
            st.success(f"설정한 기준 tol={tol} 아래로 내려가 수렴하는 양상이 보입니다.")
        else:
            st.warning("설정한 반복 횟수 안에서는 수렴이 뚜렷하게 확인되지 않았습니다.")

        st.subheader("오차 변화")
        err_df = pd.DataFrame({
            "n": range(1, len(errors)),
            "abs_error": errors[1:]
        })
        st.line_chart(err_df.set_index("n"))

        x_grid = np.linspace(xgrid_min, xgrid_max, 1200)
        y_vals = []
        for v in x_grid:
            try:
                y_vals.append(float(g(v)))
            except Exception:
                y_vals.append(np.nan)
        y_grid = np.array(y_vals, dtype=float)

        fig, ax = plt.subplots(figsize=(8, 8))
        ax.plot(x_grid, y_grid, label="y = g(x)")
        ax.plot(x_grid, x_grid, "--", label="y = x")

        x = x0
        for _ in range(n_iter):
            y = float(g(x))
            ax.plot([x, x], [x, y], "g-", lw=1.3)
            ax.plot([x, y], [y, y], "g-", lw=1.3)
            x = y

        ax.scatter([x0], [x0], color="red", zorder=5, label="start")
        ax.set_title("Cobweb Plot of Fixed-Point Iteration")
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.grid(True, alpha=0.3)
        ax.legend()

        zoom_half = base_half / zoom_factor
        low = zoom_center - zoom_half
        high = zoom_center + zoom_half

        vals = np.array(xs, dtype=float)
        vmin = np.min(vals)
        vmax = np.max(vals)
        span = max(vmax - vmin, 1.0)
        pad = 0.12 * span

        low = min(low, vmin - pad)
        high = max(high, vmax + pad)

        ax.set_xlim(low, high)
        ax.set_ylim(low, high)
        ax.set_aspect("equal", adjustable="box")

        y_mark = low + 0.04 * (high - low)
        ax.hlines(y_mark, low, high, colors="gray", linestyles=":", alpha=0.6)

        cmap = LinearSegmentedColormap.from_list(
            "blue_purple_pink",
            ["#1e40ff", "#8b00ff", "#ff3fbf"]
        )
        norm = mcolors.Normalize(vmin=0, vmax=max(len(xs) - 1, 1))
        point_colors = [cmap(norm(i)) for i in range(len(xs))]

        ax.scatter(
            xs,
            [y_mark] * len(xs),
            c=point_colors,
            s=60,
            zorder=6,
            edgecolors="black",
            linewidths=0.3
        )

        for i, xval in enumerate(xs):
            ax.annotate(
                f"{i}",
                (xval, y_mark),
                textcoords="offset points",
                xytext=(0, 7),
                ha="center",
                fontsize=8,
                color="black"
            )

        ax.spines["bottom"].set_visible(True)
        ax.spines["left"].set_visible(True)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.xaxis.set_ticks_position("bottom")
        ax.yaxis.set_ticks_position("left")
        ax.tick_params(axis="x", bottom=True, labelbottom=True)
        ax.tick_params(axis="y", left=True, labelleft=True)

        plt.tight_layout()
        st.subheader("Cobweb plot")
        st.pyplot(fig)

    except Exception as e:
        st.error(f"오류 발생: {e}")