import streamlit as st



# Adicionar a imagem centralizada no início da página
st.markdown("""
<div style="text-align: center;">
    <img src="https://i.imgur.com/Ti4ILVw.png" style="width: 15%;"/>
</div>
            

            


""", unsafe_allow_html=True)
st.divider()

st.divider()

col1 , col2 = st.columns(2)

with col1:

    with st.expander("Paginas"):
        
        st.page_link("Pages/Products.py", label="Consultar Produtos", icon="📦")



with col2:


    with st.expander("Tabelas"):
        

        st.markdown("""
        [Tabela de produtos](https://docs.google.com/spreadsheets/d/11gOfqJdk1Q49MLDQA-DeEH7YiGIf_kWdkp6CORk8t4A/edit?usp=sharing)            

        [Tabela de Grupos](https://docs.google.com/spreadsheets/d/1aCRdnOEFD_x4NDSwj6SBfZXJBdPAEJjCvfX-n4PKCsE/edit?usp=sharing)
                    
        [Tabela de Vendas](https://docs.google.com/spreadsheets/d/128NJ71T3OcO9g2t28qvNoQn59JwHZ653a8ld5HInCyE/edit?usp=sharing)
                    
        [Tabela de Inside Sales](https://docs.google.com/spreadsheets/d/1egn82Gl_TvnF8JtVY164bKFsN8xtahr7n57P_SbtdYU/edit?usp=sharing)

        """, unsafe_allow_html=True)


