import streamlit as st
from streamlit_option_menu import option_menu
from apps import exploracao, momentum, value, multiFactor, recomendacao  # import your app modules here

st.set_page_config(page_title="Factor Investing Case", layout="wide")

apps = [
    {"func": exploracao.app, "title": "Exploração | Live API", "icon": "graph-up"},
    {"func": momentum.app, "title": "Momentum | Estático", "icon": "chevron-bar-expand"},
    {"func": value.app, "title": "Value & Size | Estático", "icon": "journal-arrow-up"},
    {"func": multiFactor.app, "title": "Multi Fator | Estático", "icon": "diagram-3"},
    {"func": recomendacao.app, "title": "Raciocínio", "icon": "code"}
]

titles = [app["title"] for app in apps]
titles_lower = [title.lower() for title in titles]
icons = [app["icon"] for app in apps]

params = st.experimental_get_query_params()

if "page" in params:
    default_index = int(titles_lower.index(params["page"][0].lower()))
else:
    default_index = 0

with st.sidebar:
    selected = option_menu(
        "Factor Investing",
        options=titles,
        icons=icons,
        menu_icon="menu-button-fill",
        default_index=default_index,
    )

    st.sidebar.markdown("---")

for app in apps:
    if app["title"] == selected:
        app["func"]()
        break
