import feedparser
import pandas as pd
import streamlit as st

# Lista de fontes RSS
RSS_FEEDS = [
    "https://g1.globo.com/rss/g1/economia/",
    "https://exame.com/feed/",
    "https://economia.estadao.com.br/rss/ultimas",
    "https://www.infomoney.com.br/feed/",
    "https://valor.globo.com/rss/",
    "https://www.creditcards.com/news/rss/",
    "https://www.forbes.com/finance/feed/"
]

# Função para buscar e processar as notícias de múltiplas fontes
def fetch_news_from_feeds(feeds):
    all_news = []
    for feed_url in feeds:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries:
            all_news.append({
                "title": entry.get("title", "Sem título"),
                "date": entry.get("published", "Data desconhecida"),
                "summary": entry.get("summary", "Sem resumo"),
                "link": entry.get("link", "Sem link")
            })
    return pd.DataFrame(all_news)

# Função para exibir as notícias no dashboard
def display_news(news_df):
    st.header("Notícias sobre Cartões de Crédito e Mercado de Crédito")
    for _, row in news_df.iterrows():
        st.markdown(f"### [{row['title']}]({row['link']})")
        st.markdown(f"**Data:** {row['date']}")
        st.markdown(f"**Resumo:** {row['summary']}")
        st.write("---")

# Dashboard
def main():
    st.title("Dashboard de Notícias - Cartões de Crédito")
    st.sidebar.title("Configurações")

    # Atualização manual do feed
    if st.sidebar.button("Atualizar Notícias"):
        st.sidebar.write("Buscando as últimas notícias...")
        news_data = fetch_news_from_feeds(RSS_FEEDS)
        st.sidebar.success("Notícias atualizadas com sucesso!")
    else:
        news_data = fetch_news_from_feeds(RSS_FEEDS)

    # Exibir notícias no dashboard
    if not news_data.empty:
        display_news(news_data)
    else:
        st.write("Nenhuma notícia encontrada.")

# Executar o Streamlit
if __name__ == "__main__":
    st.set_page_config(layout="wide")
    main()
