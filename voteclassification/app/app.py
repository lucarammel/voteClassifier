import streamlit as st


st.set_page_config(
    page_title="Devine pour qui tu vas voter !",
    page_icon=":envelope:",
)

st.title("Devine pour qui tu vas voter ! :envelope:")

st.markdown(
    """
# Introduction

Cette application est basée sur les travaux de recherche de Cagé et Piketty (2023) : 
[*Une histoire du conflit politique*](https://unehistoireduconflitpolitique.fr/). 

Toutes les données utilisées leur appartiennent et sont l'issu d'un travail de numérisation d'archives.

## Que fait cette application ?

Le but est de développer un petit modèle de machine learning afin de prédire en fonction de paramètres socio-géographiques, le vote d'un citoyen français ! :fr:

            """
)

st.markdown(
    """"
            Remplis ces critères afin de faire une prédiction ! 
            """
)


with st.form("my_form"):
    st.write("")
    slider_val = st.slider("", help="")
    checkbox_val = st.checkbox("", help="")

    submitted = st.form_submit_button("Envoyez !")
    if submitted:
        st.write("slider", slider_val, "checkbox", checkbox_val)

st.markdown("---")

st.markdown("Code source [github](https://github.com/lucarammel/voteclassifier)")
st.markdown("Auteur : [Lucas PEREIRA](https://github.com/lucarammel)")
