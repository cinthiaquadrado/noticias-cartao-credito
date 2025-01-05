import feedparser
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from datetime import datetime
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Configuração da página
st.set_page_config(page_title="Análise de Notícias", layout="wide")

# Fontes de RSS
RSS_FEEDS = [
    {"name": "Tecnologia", "url": "https://news.google.com/rss/headlines/section/topic/TECHNOLOGY?hl=pt-BR&gl=BR&ceid=BR:pt-150"},
    {"name": "Economia", "url": "https://news.google.com/rss/headlines/section/topic/BUSINESS?hl=pt-BR&gl=BR&ceid=BR:pt-150"},
    {"name": "Finanças", "url": "https://news.google.com/rss/headlines/section/topic/FINANCE?hl=pt-BR&gl=BR&ceid=BR:pt-150"},
]

# Função para buscar e processar as notícias
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

# Função para análise de sentimentos com VADER
def analyze_sentiment_vader(text):
    analyzer = SentimentIntensityAnalyzer()
    sentiment_score = analyzer.polarity_scores(text)
    if sentiment_score['compound'] > 0.05:
        return "Positivo"
    elif sentiment_score['compound'] < -0.05:
        return "Negativo"
    else:
        return "Neutro"

# Função para exibir as notícias no dashboard
def display_news(news_df):
    for _, row in news_df.iterrows():
        st.markdown(f"### [{row['title']}]({row['link']})")
        st.markdown(f"**Data:** {row['date']}  **Fonte:** {row['source']}  **Sentimento:** {row['sentiment']}")
        st.write("---")

# Função para exibir a distribuição das notícias
def display_distribution(news_df):
    st.header("Distribuição Temporal de Notícias")
    news_df['date_parsed'] = pd.to_datetime(news_df['date'], errors='coerce')
    news_df = news_df.dropna(subset=['date_parsed'])
    
    news_df['day'] = news_df['date_parsed'].dt.date
    date_counts = news_df['day'].value_counts().sort_index()
    
    date_counts.plot(kind="bar", color="skyblue", alpha=0.7)
    plt.title("Distribuição de Notícias por Dia")
    plt.xlabel("Data")
    plt.ylabel("Número de Notícias")
    plt.xticks(rotation=45)
    st.pyplot(plt)

    st.subheader("Nuvem de Palavras")
    all_text = " ".join(news_df["title"].fillna("") + " " + news_df["summary"].fillna(""))
    wordcloud = WordCloud(width=800, height=400, background_color="white").generate(all_text)
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    st.pyplot(plt)

# Função principal para criar o dashboard
def main():
    st.title("Dashboard de Notícias - Métodos de Pagamento")
    
    news_data = fetch_news_from_feeds(RSS_FEEDS)
    news_data["date_parsed"] = pd.to_datetime(news_data["date"], errors='coerce')

    # Filtros
    st.sidebar.header("Filtros")
    sources = st.sidebar.multiselect("Selecione a fonte", options=news_data["source"].unique(), default=news_data["source"].unique())
    start_date = st.sidebar.date_input("Data inicial", value=datetime(2023, 1, 1))
    end_date = st.sidebar.date_input("Data final", value=datetime.now())
    keywords = st.sidebar.text_area("Palavras-chave", value="")

    # Filtro por data e fonte
    filtered_data = news_data[(news_data["source"].isin(sources)) & 
                              (news_data["date_parsed"] >= start_date) & 
                              (news_data["date_parsed"] <= end_date)]

    # Filtro por palavras-chave
    if keywords:
        keyword_list = [kw.strip().lower() for kw in keywords.split(",")]
        filtered_data = filtered_data[ 
            filtered_data["title"].str.lower().str.contains("|".join(keyword_list)) |
            filtered_data["summary"].str.lower().str.contains("|".join(keyword_list))
        ]
    
    # Análise de sentimentos
    filtered_data["sentiment"] = filtered_data["title"].apply(analyze_sentiment_vader)
    filtered_data = filtered_data.sort_values(by="date_parsed", ascending=False)

    # Top 15 notícias
    top_news = filtered_data.head(15)

    # Abas no Streamlit
    tab1, tab2 = st.tabs(["Notícias", "Análise"])
    
    with tab1:
        display_news(top_news)
        display_distribution(filtered_data)

    with tab2:
        # Análise de Sentimentos
        sentiment_counts = filtered_data["sentiment"].value_counts()
        st.bar_chart(sentiment_counts)

if __name__ == "__main__":
    main()
