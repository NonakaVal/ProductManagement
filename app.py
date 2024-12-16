import streamlit as st


st.set_page_config(page_title="collectorsguardian", page_icon="🎮", layout='wide')

# Navegação de páginas
home = st.Page("Pages/home.py", title="Home", icon=":material/home:", default=True)

products = st.Page("Pages/Products.py", title="Consultar Produtos", icon=":material/dashboard:")




log = st.Page("Pages/log.py", title="TestLog", icon="⚙️")


pg = st.navigation(
    {
        # "Controle": [], 
        # "Home" : [home],
        "": [home],
        "Produtos": [products,log]
      
        
    }
)

pg.run()

