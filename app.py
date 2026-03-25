import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go

st.set_page_config(
    page_title="Комплексний дашборд компаній",
    page_icon="📊",
    layout="wide"
)

st.markdown("""
<style>
.t1 {
    font-size: 34px;
    font-weight: 700;
    margin-bottom: 4px;
}
.t2 {
    font-size: 17px;
    color: #475569;
    margin-bottom: 18px;
}
.kartka {
    background-color: #f8fafc;
    padding: 16px;
    border-radius: 14px;
    border: 1px solid #e2e8f0;
    text-align: center;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}
.kartka h3 {
    margin: 0;
    font-size: 16px;
}
.kartka p {
    margin: 8px 0 0 0;
    font-size: 28px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="t1">📊 Комплексний дашборд “Фінанси + Медіа + Репутація”</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="t2">Об’єднання фінансових, медійних і публічних показників підприємств з розрахунком інтегрального рейтингу</div>',
    unsafe_allow_html=True
)

st.sidebar.header("Джерела даних")

financial_file = st.sidebar.file_uploader("Завантажте фінансовий CSV", type=["csv"])
media_file = st.sidebar.file_uploader("Завантажте медійний CSV", type=["csv"])
public_file = st.sidebar.file_uploader("Завантажте CSV публічного іміджу", type=["csv"])

use_demo = st.sidebar.checkbox(
    "Використати тестові дані",
    value=True if not (financial_file or media_file or public_file) else False
)

def create_demo_data():
    companies = [
        "ТОВ Альфа", "ТОВ Бета", "ПП Вектор", "ТОВ Горизонт", "ТОВ Дельта",
        "ПП Еталон", "ТОВ Жасмин", "ТОВ Зеніт", "ПП Імпульс", "ТОВ Кардинал"
    ]

    finance_df = pd.DataFrame({
        "Компанія": companies,
        "Дохід": [950, 780, 620, 1200, 560, 710, 860, 430, 990, 1100],
        "Прибуток": [220, 120, 80, 260, 60, 110, 140, 35, 180, 240],
        "Борг": [300, 420, 280, 500, 310, 260, 390, 150, 470, 520]
    })

    media_df = pd.DataFrame({
        "Компанія": companies,
        "Кількість_згадок": [120, 95, 65, 150, 80, 60, 110, 40, 135, 170],
        "Позитивні_згадки": [75, 40, 28, 85, 45, 22, 60, 18, 70, 92],
        "Негативні_згадки": [15, 25, 18, 20, 16, 14, 22, 10, 28, 26]
    })

    public_df = pd.DataFrame({
        "Компанія": companies,
        "Рейтинг_довіри": [82, 61, 58, 88, 55, 63, 69, 52, 74, 80],
        "Соціальна_активність": [76, 48, 44, 91, 50, 58, 67, 41, 72, 85],
        "Репутаційний_бал": [84, 57, 54, 89, 53, 60, 68, 45, 73, 81]
    })

    return finance_df, media_df, public_df

if use_demo:
    finance_df, media_df, public_df = create_demo_data()
else:
    if not (financial_file and media_file and public_file):
        st.warning("Завантажте всі три CSV-файли або увімкніть тестові дані.")
        st.stop()

    finance_df = pd.read_csv(financial_file)
    media_df = pd.read_csv(media_file)
    public_df = pd.read_csv(public_file)

required_finance = ["Компанія", "Дохід", "Прибуток", "Борг"]
required_media = ["Компанія", "Кількість_згадок", "Позитивні_згадки", "Негативні_згадки"]
required_public = ["Компанія", "Рейтинг_довіри", "Соціальна_активність", "Репутаційний_бал"]

missing_finance = [col for col in required_finance if col not in finance_df.columns]
missing_media = [col for col in required_media if col not in media_df.columns]
missing_public = [col for col in required_public if col not in public_df.columns]

if missing_finance:
    st.error(f"У фінансовому CSV немає стовпців: {', '.join(missing_finance)}")
    st.stop()

if missing_media:
    st.error(f"У медійному CSV немає стовпців: {', '.join(missing_media)}")
    st.stop()

if missing_public:
    st.error(f"У CSV публічного іміджу немає стовпців: {', '.join(missing_public)}")
    st.stop()

# Об'єднання таблиць
df = finance_df.merge(media_df, on="Компанія", how="inner").merge(public_df, on="Компанія", how="inner")

if df.empty:
    st.error("Після об’єднання таблиць немає спільних компаній.")
    st.stop()

# Розрахунок показників
df["Фінансовий_бал"] = (
    (df["Прибуток"] / (df["Дохід"] + 1)) * 100
    - (df["Борг"] / (df["Дохід"] + 1)) * 50
)

df["Медійний_бал"] = (
    (df["Позитивні_згадки"] * 2)
    - (df["Негативні_згадки"] * 1.5)
    + (df["Кількість_згадок"] * 0.2)
)

df["Публічний_бал"] = (
    df["Рейтинг_довіри"] * 0.4 +
    df["Соціальна_активність"] * 0.25 +
    df["Репутаційний_бал"] * 0.35
)

def normalize(series):
    min_val = series.min()
    max_val = series.max()
    if max_val == min_val:
        return pd.Series([50] * len(series), index=series.index)
    return ((series - min_val) / (max_val - min_val) * 100).round(2)

df["Фінансовий_бал_норм"] = normalize(df["Фінансовий_бал"])
df["Медійний_бал_норм"] = normalize(df["Медійний_бал"])
df["Публічний_бал_норм"] = normalize(df["Публічний_бал"])

st.sidebar.subheader("Ваги рейтингу")

w_fin = st.sidebar.slider("Вага фінансів", 0.0, 1.0, 0.4, 0.05)
w_media = st.sidebar.slider("Вага медіа", 0.0, 1.0, 0.3, 0.05)
w_public = st.sidebar.slider("Вага публічного іміджу", 0.0, 1.0, 0.3, 0.05)

weight_sum = w_fin + w_media + w_public
if weight_sum == 0:
    st.error("Сума ваг не може дорівнювати нулю.")
    st.stop()

w_fin /= weight_sum
w_media /= weight_sum
w_public /= weight_sum

df["Інтегральний_рейтинг"] = (
    df["Фінансовий_бал_норм"] * w_fin +
    df["Медійний_бал_норм"] * w_media +
    df["Публічний_бал_норм"] * w_public
).round(2)

def rating_level(value):
    if value < 40:
        return "Низький"
    elif value < 70:
        return "Середній"
    return "Високий"

df["Рівень_рейтингу"] = df["Інтегральний_рейтинг"].apply(rating_level)

selected_company = st.sidebar.selectbox("Оберіть компанію", ["Усі"] + sorted(df["Компанія"].tolist()))
selected_level = st.sidebar.selectbox("Фільтр за рівнем рейтингу", ["Усі", "Низький", "Середній", "Високий"])

filtered = df.copy()

if selected_company != "Усі":
    filtered = filtered[filtered["Компанія"] == selected_company]

if selected_level != "Усі":
    filtered = filtered[filtered["Рівень_рейтингу"] == selected_level]

total_companies = len(filtered)
avg_rating = round(filtered["Інтегральний_рейтинг"].mean(), 2) if not filtered.empty else 0
top_company = filtered.sort_values("Інтегральний_рейтинг", ascending=False).iloc[0]["Компанія"] if not filtered.empty else "—"
high_rating_count = (filtered["Рівень_рейтингу"] == "Високий").sum() if not filtered.empty else 0

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
        <div class="kartka">
            <h3>Кількість компаній</h3>
            <p>{total_companies}</p>
        </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
        <div class="kartka">
            <h3>Середній рейтинг</h3>
            <p>{avg_rating}</p>
        </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
        <div class="kartka">
            <h3>Лідер рейтингу</h3>
            <p style="font-size:20px;">{top_company}</p>
        </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
        <div class="kartka">
            <h3>Високий рейтинг</h3>
            <p>{high_rating_count}</p>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

st.subheader("Інтегральний рейтинг")

if not filtered.empty:
    avg_value = filtered["Інтегральний_рейтинг"].mean()

    gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=avg_value,
        title={"text": "Середній інтегральний рейтинг"},
        gauge={
            "axis": {"range": [0, 100]},
            "steps": [
                {"range": [0, 40], "color": "#fee2e2"},
                {"range": [40, 70], "color": "#fde68a"},
                {"range": [70, 100], "color": "#bbf7d0"}
            ],
            "threshold": {
                "line": {"color": "green", "width": 4},
                "thickness": 0.8,
                "value": avg_value
            }
        }
    ))
    st.plotly_chart(gauge, use_container_width=True)

st.markdown("---")

tab1, tab2, tab3 = st.tabs(["Фінанси", "Медіа", "Публічний імідж"])

with tab1:
    st.subheader("Фінансові показники")
    fin_cols = ["Компанія", "Дохід", "Прибуток", "Борг", "Фінансовий_бал_норм"]
    st.dataframe(filtered[fin_cols].sort_values("Фінансовий_бал_норм", ascending=False), use_container_width=True)

    if not filtered.empty:
        fig1, ax1 = plt.subplots(figsize=(10, 4))
        plot_df = filtered.sort_values("Фінансовий_бал_норм", ascending=False)
        ax1.bar(plot_df["Компанія"], plot_df["Фінансовий_бал_норм"])
        ax1.set_title("Фінансовий бал компаній")
        ax1.set_xlabel("Компанія")
        ax1.set_ylabel("Нормований бал")
        plt.xticks(rotation=45, ha="right")
        st.pyplot(fig1)

with tab2:
    st.subheader("Медійні показники")
    media_cols = ["Компанія", "Кількість_згадок", "Позитивні_згадки", "Негативні_згадки", "Медійний_бал_норм"]
    st.dataframe(filtered[media_cols].sort_values("Медійний_бал_норм", ascending=False), use_container_width=True)

    if not filtered.empty:
        fig2, ax2 = plt.subplots(figsize=(10, 4))
        plot_df = filtered.sort_values("Медійний_бал_норм", ascending=False)
        ax2.bar(plot_df["Компанія"], plot_df["Медійний_бал_норм"])
        ax2.set_title("Медійний бал компаній")
        ax2.set_xlabel("Компанія")
        ax2.set_ylabel("Нормований бал")
        plt.xticks(rotation=45, ha="right")
        st.pyplot(fig2)

with tab3:
    st.subheader("Показники публічного іміджу")
    public_cols = ["Компанія", "Рейтинг_довіри", "Соціальна_активність", "Репутаційний_бал", "Публічний_бал_норм"]
    st.dataframe(filtered[public_cols].sort_values("Публічний_бал_норм", ascending=False), use_container_width=True)

    if not filtered.empty:
        fig3, ax3 = plt.subplots(figsize=(10, 4))
        plot_df = filtered.sort_values("Публічний_бал_норм", ascending=False)
        ax3.bar(plot_df["Компанія"], plot_df["Публічний_бал_норм"])
        ax3.set_title("Бал публічного іміджу")
        ax3.set_xlabel("Компанія")
        ax3.set_ylabel("Нормований бал")
        plt.xticks(rotation=45, ha="right")
        st.pyplot(fig3)

st.markdown("---")

st.subheader("Зведена таблиця рейтингу")

summary_cols = [
    "Компанія",
    "Фінансовий_бал_норм",
    "Медійний_бал_норм",
    "Публічний_бал_норм",
    "Інтегральний_рейтинг",
    "Рівень_рейтингу"
]

st.dataframe(
    filtered[summary_cols].sort_values("Інтегральний_рейтинг", ascending=False),
    use_container_width=True
)

st.markdown("---")
st.caption("Навчальний вебзастосунок для комплексного оцінювання компаній")
