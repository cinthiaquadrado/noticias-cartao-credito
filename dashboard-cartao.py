import feedparser
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from datetime import datetime

# Lista de fontes RSS
RSS_FEEDS = [
    {"name": "G1 Economia", "url": "https://g1.globo.com/rss/g1/economia/"},
    {"name": "Exame", "url": "https://exame.com/feed/"},
    {"name": "Estadão Economia", "url": "https://economia.estadao.com.br/rss/ultimas"},
    {"name": "InfoMoney", "url": "https://www.infomoney.com.br/feed/"},
    {"name": "Valor Econômico", "url": "https://valor.globo.com/rss/"},
    {"name": "CreditCards.com", "url": "https://www.creditcards.com/news/rss/"},
    {"name": "Forbes Finance", "url": "https://www.forbes.com/finance/feed/"}
]

# Função para buscar e processar as notícias de múltiplas fontes
def fetch_news_from_feeds(feeds):
    all_news = []
    for feed in feeds:
        feed_data = feedparser.parse(feed["url"])
        for entry in feed_data.entries:
            all_news.append({
                "title": entry.get("title", "Sem título"),
                "date": entry.get("published", "Data desconhecida"),
                "summary": entry.get("summary", "Sem resumo"),
                "link": entry.get("link", "Sem link"),
                "source": feed["name"]
            })
    return pd.DataFrame(all_news)

# Função para exibir as notícias no dashboard
def display_news(news_df):
    st.header("Notícias sobre Cartões de Crédito e Mercado de Crédito")
    for _, row in news_df.iterrows():
        st.markdown(f"### [{row['title']}]({row['link']})")
        st.markdown(f"**Data:** {row['date']}")
        st.markdown(f"**Fonte:** {row['source']}")
        st.markdown(f"**Resumo:** {row['summary']}")
        st.write("---")

# Função para exibir a distribuição das notícias
def display_distribution(news_df):
    st.header("Distribuição Temporal de Notícias")
    news_df['date_parsed'] = pd.to_datetime(news_df['date'], errors='coerce')
    news_df['date_parsed'] = news_df['date_parsed'].fillna(datetime.now())  # Preenche datas inválidas com a data atual

    # Opções de agrupamento
    group_by = st.selectbox("Agrupar por:", ["Dia", "Semana", "Mês"])
    if group_by == "Dia":
        date_counts = news_df['date_parsed'].dt.date.value_counts().sort_index()
    elif group_by == "Semana":
        date_counts = news_df['date_parsed'].dt.to_period("W").value_counts().sort_index()
    else:  # Mês
        date_counts = news_df['date_parsed'].dt.to_period("M").value_counts().sort_index()

    # Exibir gráfico
    plt.figure(figsize=(10, 6))
    date_counts.plot(kind="bar", color="skyblue", alpha=0.7)
    plt.title("Distribuição de Notícias")
    plt.ylabel("Número de Notícias")
    plt.xlabel(group_by)
    plt.xticks(rotation=45)
    st.pyplot(plt)

# Função principal para criar o dashboard
def main():
    st.title("Dashboard de Notícias - Cartões de Crédito")
    st.sidebar.title("Configurações")

    # Atualizar feed de notícias
    st.sidebar.write("Buscando notícias...")
    news_data = fetch_news_from_feeds(RSS_FEEDS)

    if not news_data.empty:
        # Filtros no menu lateral
        st.sidebar.header("Filtros")
        sources = st.sidebar.multiselect("Selecione a fonte", options=news_data["source"].unique(), default=news_data["source"].unique())
        start_date = st.sidebar.date_input("Data inicial", value=datetime(2023, 1, 1))
        end_date = st.sidebar.date_input("Data final", value=datetime.now())

        # Aplicar filtros
        news_data["date_parsed"] = pd.to_datetime(news_data["date"], errors='coerce')
        filtered_data = news_data[
            (news_data["source"].isin(sources)) &
            (news_data["date_parsed"].dt.date >= start_date) &
            (news_data["date_parsed"].dt.date <= end_date)
        ]

        # Exibição de abas no dashboard
        tab1, tab2 = st.tabs(["Notícias", "Distribuição Temporal"])

        with tab1:
            if not filtered_data.empty:
                display_news(filtered_data)
            else:
                st.write("Nenhuma notícia encontrada para os filtros aplicados.")

        with tab2:
            if not filtered_data.empty:
                display_distribution(filtered_data)
            else:
                st.write("Nenhuma informação para exibir na distribuição temporal.")
    else:
        st.write("Não foi possível buscar as notícias.")

# Executar o Streamlit
if __name__ == "__main__":
    st.set_page_config(layout="wide")
    main()
