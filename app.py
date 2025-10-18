import streamlit as st
import numpy as np
import pandas as pd

st.set_page_config(page_title="Comparação Econômica SLB vs Diesel", layout="centered")

st.title("💡 Comparação Econômica: Sistema com Bateria de Segunda Vida (SLB) vs Diesel")

st.markdown("Insira abaixo todos os parâmetros e clique em **Calcular** para comparar os cenários.")

# ----------------------------
st.header("🔧 Parâmetros Econômicos Comuns")
col1, col2 = st.columns(2)
with col1:
    taxa_desc = st.number_input("Taxa de desconto real (% a.a.)", 0.0, 20.0, 8.0)
with col2:
    inflacao = st.number_input("Inflação (% a.a.)", 0.0, 20.0, 4.0)

# ----------------------------
st.header("⚡ Dados de Consumo")
col1, col2 = st.columns(2)
with col1:
    potencia = st.number_input("Potência média (kW)", 0.0, 1000.0, 10.0)
with col2:
    horas_dia = st.number_input("Tempo de uso (h/dia)", 0.0, 24.0, 10.0)
energia_anual = potencia * horas_dia * 365

# ----------------------------
st.header("⛽ Sistema Diesel")
col1, col2 = st.columns(2)
with col1:
    capex_diesel = st.number_input("CAPEX do gerador (R$)", 0.0, 2_000_000.0, 100_000.0)
    preco_diesel = st.number_input("Preço do diesel (R$/L)", 0.0, 20.0, 6.0)
with col2:
    sfc = st.number_input("Consumo específico (L/kWh)", 0.1, 1.0, 0.35)
    manut_diesel = st.number_input("Manutenção anual (R$/ano)", 0.0, 100_000.0, 5_000.0)

# ----------------------------
st.header("🔋 Sistema SLB + PV")
col1, col2 = st.columns(2)
with col1:
    capex_pv = st.number_input("CAPEX PV (R$)", 0.0, 2_000_000.0, 80_000.0)
    capex_slb = st.number_input("CAPEX Bateria (R$)", 0.0, 2_000_000.0, 50_000.0)
with col2:
    opex_slb = st.number_input("Manutenção sistema (R$/ano)", 0.0, 100_000.0, 3_000.0)
    capacidade_ini = st.number_input("Capacidade inicial da bateria (kWh)", 0.0, 2_000.0, 100.0)

taxa_desgaste = st.number_input("Taxa de desgaste (% perda de capacidade/ano)", 0.0, 20.0, 3.0, step=0.1)
vida_util = st.number_input("Vida útil do projeto (anos)", 1, 50, 10)

# ----------------------------
# Botão de cálculo
calcular = st.button("🚀 Calcular Comparação")

if calcular:
    st.divider()
    st.subheader("📈 Resultados da Simulação")

    # Cálculos diesel
    litros_ano = energia_anual * sfc
    custo_diesel_ano = litros_ano * preco_diesel
    opex_diesel = custo_diesel_ano + manut_diesel

    # SLB – degradação linear
    anos = np.arange(0, vida_util + 1)
    soh = np.maximum(100 - taxa_desgaste * anos, 0)  # não deixar negativo
    soh_final = soh[-1]

    # Custos acumulados (sem desconto por enquanto)
    npc_diesel = capex_diesel + opex_diesel * vida_util
    npc_slb = capex_pv + capex_slb + opex_slb * vida_util

    # ---- Resultados
    st.metric("Demanda anual", f"{energia_anual:,.0f} kWh/ano")
    st.metric("Consumo de Diesel", f"{litros_ano:,.0f} L/ano")
    st.metric("SOH final da bateria", f"{soh_final:.1f}%")

    st.divider()
    col1, col2 = st.columns(2)
    col1.metric("Custo total Diesel (R$)", f"{npc_diesel:,.0f}")
    col2.metric("Custo total SLB+PV (R$)", f"{npc_slb:,.0f}")

    if npc_slb < npc_diesel:
        st.success("✅ O sistema **SLB + PV** é mais econômico no horizonte escolhido.")
    else:
        st.error("⚠️ O sistema **Diesel** ainda é mais econômico neste cenário.")

    # ---- Gráfico SOH
    st.subheader("🔋 Degradação da Bateria")
    df = pd.DataFrame({"Ano": anos, "SOH (%)": soh})
    st.line_chart(df.set_index("Ano"), use_container_width=True)

    # ---- Tabela resumo
    st.subheader("📊 Resumo numérico")
    tabela = {
        "Ano": anos,
        "SOH (%)": soh,
        "Energia útil (kWh)": capacidade_ini * soh / 100,
    }
    df_tab = pd.DataFrame(tabela)
    st.dataframe(df_tab)

    st.download_button(
        "Baixar resultados (CSV)",
        data=df_tab.to_csv(index=False).encode("utf-8"),
        file_name="comparacao_SLB_vs_Diesel.csv",
        mime="text/csv",
    )
