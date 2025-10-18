import streamlit as st

st.title("🚀 Teste Streamlit")
st.write("Se você está vendo esta mensagem, o Streamlit está funcionando!")

nome = st.text_input("Digite seu nome:")
if nome:
    st.success(f"Olá, {nome}! 👋")
