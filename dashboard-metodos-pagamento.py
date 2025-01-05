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
    {"name": "Finanças", "url": "https://news.google.com/rss/headlines/section/topic/FINANCE?hl=pt-BR&gl=BR&ceid=BR:pt-150"},
    {"name": "Tecnologia", "url": "https://news.google.com/rss/headlines/section/topic/TECHNOLOGY?hl=pt-BR&gl=BR&ceid=BR:pt-150"},
    {"name": "Economia", "url": "https://news.google.com/rss/headlines/section/topic/BUSINESS?hl=pt-BR&gl=BR&ceid=BR:pt-150"}
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

# Função para exibir a distribuição temporal das notícias
def display_distribution(news_df):
    # Distribuição temporal por dia, mês e ano
    news_df['date_parsed'] = pd.to_datetime(news_df['date'], errors='coerce')
    news_df = news_df.dropna(subset=['date_parsed'])
    
    # Extrair dia, mês, ano
    news_df['day'] = news_df['date_parsed'].dt.date
    news_df['month'] = news_df['date_parsed'].dt.to_period('M')
    news_df['year'] = news_df['date_parsed'].dt.to_period('Y')

    # Controle de seleção de distribuição
    distribution_type = st.selectbox("Selecione a distribuição", ("Dia", "Mês", "Ano"))

    # Gráfico de distribuição selecionada
    if distribution_type == "Dia":
        day_counts = news_df['day'].value_counts().sort_index()
        title = "Distribuição de Notícias por Dia"
        xlabel = "Data"
        ylabel = "Número de Notícias"
        day_counts.plot(kind="bar", color="skyblue", alpha=0.7)
        
    elif distribution_type == "Mês":
        month_counts = news_df['month'].value_counts().sort_index()
        title = "Distribuição de Notícias por Mês"
        xlabel = "Mês"
        ylabel = "Número de Notícias"
        month_counts.plot(kind="bar", color="orange", alpha=0.7)
        
    else:
        year_counts = news_df['year'].value_counts().sort_index()
        title = "Distribuição de Notícias por Ano"
        xlabel = "Ano"
        ylabel = "Número de Notícias"
        year_counts.plot(kind="bar", color="green", alpha=0.7)

    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    st.pyplot(plt)

# Função para gerar a nuvem de palavras com base na palavra-chave
def generate_wordcloud(news_df, keywords):
    # Filtrar as notícias por palavras-chave
    if keywords:
        keyword_list = [kw.strip().lower() for kw in keywords.split(",")]
        filtered_df = news_df[
            news_df["title"].str.lower().str.contains("|".join(keyword_list)) |
            news_df["summary"].str.lower().str.contains("|".join(keyword_list))
        ]
    else:
        filtered_df = news_df

    # Criar a nuvem de palavras
    all_text = " ".join(filtered_df["title"].fillna("") + " " + filtered_df["summary"].fillna(""))
    wordcloud = WordCloud(width=800, height=400, background_color="white").generate(all_text)
    
    st.subheader("Nuvem de Palavras")
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    st.pyplot(plt)

# Função principal para criar o dashboard
def main():
    st.title("Dashboard de Notícias - Métodos de Pagamento")
    
    # Carregar notícias
    news_data = fetch_news_from_feeds(RSS_FEEDS)
    news_data["date_parsed"] = pd.to_datetime(news_data["date"], errors='coerce')

    # Filtros
    st.sidebar.header("Filtros")
    sources = st.sidebar.multiselect("Selecione a fonte", options=news_data["source"].unique(), default=news_data["source"].unique())
    start_date = st.sidebar.date_input("Data inicial", value=datetime(2023, 1, 1))
    end_date = st.sidebar.date_input("Data final", value=datetime.now())
    keywords = st.sidebar.text_area("Palavras-chave", value="")

    # Convertendo start_date e end_date para datetime
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    # Garantindo que news_data["date_parsed"] esteja no formato correto
    news_data["date_parsed"] = pd.to_datetime(news_data["date"], errors='coerce')

    # Aplicar filtro
    filtered_data = news_data[
        (news_data["source"].isin(sources)) &  
        (news_data["date_parsed"] >= start_date) &  
        (news_data["date_parsed"] <= end_date)
    ]

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

    # Top notícias
    top_news = filtered_data.head(30)

    # Abas no Streamlit
    tab1, tab2 = st.tabs(["Notícias", "Análise"])
    
    with tab1:
        display_news(top_news)

    with tab2:
        display_distribution(filtered_data)
        generate_wordcloud(filtered_data, keywords)  # Passando a palavra-chave para a função
        display_sentiment_analysis(filtered_data)

if __name__ == "__main__":
    main()

