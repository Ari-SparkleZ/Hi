import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

st.set_page_config(page_title="Cobweb Plot Explorer", layout="centered")
st.title("고정점 반복법 시각화")
st.write("반복함수 g(x)를 직접 입력하고, cobweb plot과 반복값 변화를 확인합니다.")

st.subheader("입력")
expr = st.text_input("반복함수 g(x)", value="(x+2)/3")
expr = expr.replace("^", "**")

x0 = st.number_input("초기값 x0", value=0.0, format="%.6f")
n_iter = st.slider("반복 횟수", min_value=1, max_value=80, value=12)
xmin = st.number_input("그래프 x 최소값", value=-5.0, format="%.2f")
xmax = st.number_input("그래프 x 최대값", value=5.0, format="%.2f")
tol = st.number_input("수렴 판정 기준 tol", value=1e-6, format="%.8f")

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

        x_grid = np.linspace(xmin, xmax, 800)
        y_grid = np.array([g(v) for v in x_grid], dtype=float)

        fig, ax = plt.subplots(figsize=(8, 8))
        ax.plot(x_grid, y_grid, label="y = g(x)")
        ax.plot(x_grid, x_grid, "--", label="y = x")

        x = x0
        for _ in range(n_iter):
            y = float(g(x))
            ax.plot([x, x], [x, y], "g-", lw=1.4)
            ax.plot([x, y], [y, y], "g-", lw=1.4)
            x = y

        ax.scatter([x0], [x0], color="red", zorder=5, label="start")
        ax.set_title("Cobweb Plot of Fixed-Point Iteration")
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.grid(True, alpha=0.3)
        ax.legend()

        vals = np.array(xs, dtype=float)
        vmin = np.min(vals)
        vmax = np.max(vals)
        span = max(vmax - vmin, 1.0)
        pad = 0.35 * span

        low = min(vmin - pad, xmin)
        high = max(vmax + pad, xmax)

        ax.set_xlim(low, high)
        ax.set_ylim(low, high)
        ax.set_aspect("equal", adjustable="box")

        plt.tight_layout()
        st.subheader("Cobweb plot")
        st.pyplot(fig)

    except Exception as e:
        st.error(f"오류 발생: {e}")