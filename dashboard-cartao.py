import feedparser
import pandas as pd
import streamlit as st
from datetime import datetime

# Função para buscar notícias de um feed RSS
def fetch_rss_news(feed_url):
    feed = feedparser.parse(feed_url)
    news = []
    for entry in feed.entries:
        news.append({
            "title": entry.title,
            "link": entry.link,
            "published": entry.published if "published" in entry else "Data desconhecida",
            "summary": entry.summary if "summary" in entry else "Sem resumo disponível"
        })
    return news

# Processar os dados em um DataFrame
def process_news_data(news, keywords):
    df = pd.DataFrame(news)

    # Converter a data para datetime (se possível)
    df["published"] = pd.to_datetime(df["published"], errors="coerce")

    # Filtrar notícias por palavras-chave
    keyword_filter = df["title"].str.contains("|".join(keywords), case=False, na=False) | \
                     df["summary"].str.contains("|".join(keywords), case=False, na=False)
    df = df[keyword_filter]

    # Ordenar por data mais recente
    df = df.sort_values("published", ascending=False)
    return df

# Criar um dashboard com Streamlit
def create_dashboard(news_df):
    st.title("Dashboard de Notícias sobre Cartões de Crédito")
    
    # Mostrar as últimas notícias
    st.header("Notícias Recentes")
    if not news_df.empty:
        for _, row in news_df.iterrows():
            st.subheader(row["title"])
            st.write(f"Publicado em: {row['published'].strftime('%Y-%m-%d %H:%M:%S')}" if pd.notnull(row["published"]) else "Data desconhecida")
            st.write(f"*Resumo:* {row['summary']}")
            st.write(f"[Leia mais]({row['link']})\n")
            st.markdown("---")  # Linha separadora entre notícias
    else:
        st.write("Nenhuma notícia encontrada para as palavras-chave selecionadas.")

    # Exibir dados em tabela
    st.header("Tabela de Notícias")
    st.dataframe(news_df)

# Fluxo principal
def main():
    st.sidebar.title("Configurações")
    st.sidebar.write("Escolha o feed RSS e defina palavras-chave.")

    # URL dos feeds RSS
    feeds = {
        "G1 Economia": "https://g1.globo.com/rss/g1/economia/",
        "Exame Negócios": "https://exame.com/feed/",
        "Estadão Economia": "https://economia.estadao.com.br/rss/ultimas"
    }

    # Seleção de feed no menu lateral
    feed_name = st.sidebar.selectbox("Selecionar feed", list(feeds.keys()))
    feed_url = feeds[feed_name]

    # Definir palavras-chave para filtragem
    default_keywords = ["cartão de crédito", "cartões de crédito", "mercado de crédito"]
    keywords = st.sidebar.text_input(
        "Palavras-chave (separadas por vírgula)", 
        value=", ".join(default_keywords)
    ).split(", ")

    st.sidebar.write(f"Buscando notícias do feed: {feed_name}")
    news = fetch_rss_news(feed_url)
    news_df = process_news_data(news, keywords)

    create_dashboard(news_df)

# Executar a aplicação
if __name__ == "__main__":
    st.set_page_config(layout="wide")
    main()
