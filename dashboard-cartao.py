import feedparser
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from datetime import datetime, timedelta
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Configuração da página (mover para o início do código)
st.set_page_config(page_title="Análise de Notícias", layout="wide")

# Obter o ano atual e o mês atual
ano_atual = datetime.now().year
mes_atual = datetime.now().month

# Obter o primeiro e o último dia do mês atual
inicio_mes = datetime(ano_atual, mes_atual, 1)
fim_mes = datetime(ano_atual, mes_atual + 1, 1) - timedelta(days=1)

# Formatando as datas no formato YYYY-MM-DD
start_date = inicio_mes.strftime('%Y-%m-%d')
end_date = fim_mes.strftime('%Y-%m-%d')

# Função para obter a URL com o filtro de data (ano, start_date, end_date)
def obter_feed_url(base_url, ano=None, start_date=None, end_date=None):
    params = []
    if ano:
        params.append(f"ano={ano}")
    if start_date and end_date:
        params.append(f"start_date={start_date}")
        params.append(f"end_date={end_date}")
    
    # Se existirem parâmetros, adiciona à URL
    if params:
        return f"{base_url}?{'&'.join(params)}"
    return base_url

# Definindo os feeds com as URLs adaptadas para o ano e data dinâmica
RSS_FEEDS = [
    {"name": "G1 Economia", "url": "https://g1.globo.com/rss/g1/economia/"},
    {"name": "BCB - Notas técnicas", "url": "https://www.bcb.gov.br/api/feed/sitebcb/sitefeeds/notastecnicas"},
    {"name": "BCB - Notícias", "url": obter_feed_url("https://www.bcb.gov.br/api/feed/sitebcb/sitefeeds/noticias", ano=ano_atual)},
    {"name": "BCB - Notas imprensa", "url": obter_feed_url("https://www.bcb.gov.br/api/feed/sitebcb/sitefeeds/notasImprensa", ano=ano_atual)},
    {"name": "BCB - Estatísticas monetárias e de crédito", "url": "https://www.bcb.gov.br/api/feed/sitebcb/sitefeeds/historicomonetariascredito"},
    {"name": "Relatório de Pesquisa em Economia e Finanças", "url": "https://www.bcb.gov.br/api/feed/sitebcb/sitefeeds/relatorioeconofinancas"},
    {"name": "CreditCards.com", "url": "https://www.creditcards.com/news/rss/"},
    {"name": "Finsiders Brasil", "url": "https://finsidersbrasil.com.br/feed"},
]

# Exemplo: Configurar os feeds para pegar um intervalo de datas (ex: mês atual)
RSS_FEEDS_MES = [
    {"name": "BCB - Notícias", "url": obter_feed_url("https://www.bcb.gov.br/api/feed/sitebcb/sitefeeds/noticias", start_date=start_date, end_date=end_date)},
    {"name": "BCB - Notas imprensa", "url": obter_feed_url("https://www.bcb.gov.br/api/feed/sitebcb/sitefeeds/notasImprensa", start_date=start_date, end_date=end_date)},
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
        st.markdown(f"**Data:** {row['date']}")
        st.markdown(f"**Fonte:** {row['source']}")
        st.markdown(f"**Sentimento:** {row['sentiment']}")
        st.write("---")

# Função para exibir a distribuição das notícias
def display_distribution(news_df):
    st.header("Distribuição Temporal de Notícias")
    news_df['date_parsed'] = pd.to_datetime(news_df['date'], errors='coerce')
    news_df['date_parsed'] = news_df['date_parsed'].fillna(datetime.now())

    group_by = st.selectbox("Agrupar por:", ["Dia", "Semana", "Mês"])
    if group_by == "Dia":
        date_counts = news_df['date_parsed'].dt.date.value_counts().sort_index()
    elif group_by == "Semana":
        date_counts = news_df['date_parsed'].dt.to_period("W").value_counts().sort_index()
    else:
        date_counts = news_df['date_parsed'].dt.to_period("M").value_counts().sort_index()

    plt.figure(figsize=(10, 6))
    date_counts.plot(kind="bar", color="skyblue", alpha=0.7)
    plt.title("Distribuição de Notícias")
    plt.ylabel("Número de Notícias")
    plt.xlabel(group_by)
    plt.xticks(rotation=45)
    st.pyplot(plt)

    st.subheader("Nuvem de Palavras")
    all_text = " ".join(news_df["title"].fillna("") + " " + news_df["summary"].fillna(""))
    wordcloud = WordCloud(width=800, height=400, background_color="white").generate(all_text)
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    st.pyplot(plt)

# Função para exibir a análise de sentimentos das notícias
def display_sentiment_analysis(news_df):
    st.header("Análise de Sentimentos das Notícias")
    sentiment_counts = news_df["sentiment"].value_counts()
    st.bar_chart(sentiment_counts)

# Função para categorizar as notícias
categories = {
    "Cashback": ["cashback", "dinheiro de volta", "recompensas"],
    "Travel Rewards": ["milhas", "viagem", "aéreas"],
    "Crédito Corporativo": ["empresarial", "corporativo", "business"],
    "Fintechs": ["fintech", "bancos digitais", "plataformas"]
}

def categorize_news(news_df):
    category_counts = {cat: 0 for cat in categories}
    for _, row in news_df.iterrows():
        text = (row['title'] + " " + row['summary']).lower()
        for category, keywords in categories.items():
            if any(keyword in text for keyword in keywords):
                category_counts[category] += 1
    return category_counts

# Exibir as categorias no dashboard
def display_categories(news_df):
    st.subheader("Categorias de Notícias por Tema")
    categories = categorize_news(news_df)
    st.bar_chart(pd.DataFrame.from_dict(categories, orient='index', columns=["Quantidade"]))

# Função principal para criar o dashboard
def main():
    st.title("Dashboard de Notícias - Cartões de Crédito")
    
    news_data = fetch_news_from_feeds(RSS_FEEDS)

    if not news_data.empty:
        st.sidebar.header("Filtros")
        sources = st.sidebar.multiselect("Selecione a fonte", options=news_data["source"].unique(), default=news_data["source"].unique())
        start_date = st.sidebar.date_input("Data inicial", value=datetime(2023, 1, 1))
        end_date = st.sidebar.date_input("Data final", value=datetime.now())
        keywords = st.sidebar.text_area("Palavras-chave (separadas por vírgulas)", value="Digite o seu termo de busca")

        news_data["date_parsed"] = pd.to_datetime(news_data["date"], errors='coerce')
        filtered_data = news_data[
            (news_data["source"].isin(sources)) &  
            (news_data["date_parsed"].dt.date >= start_date) &  
            (news_data["date_parsed"].dt.date <= end_date)
        ]

        filtered_data["sentiment"] = filtered_data["summary"].apply(analyze_sentiment_vader)

        display_news(filtered_data)
        display_distribution(filtered_data)
        display_sentiment_analysis(filtered_data)
        display_categories(filtered_data)

# Executar o aplicativo
if __name__ == "__main__":
    main()
