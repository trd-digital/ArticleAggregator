import streamlit as st
import json
import os

# Function to load articles from JSON file
@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_articles(json_file="articles.json"):
    if os.path.exists(json_file):
        with open(json_file, 'r') as f:
            articles = json.load(f)
        return articles
    else:
        return []

# Set the page title
st.title("Real Estate News Dashboard")

# Load articles from the JSON file
articles = load_articles()

st.write(f"Showing **{len(articles)}** articles (unfiltered).")

# Loop through and display each article
for article in articles:
    # Get publication information; default to "Boston Globe" if not provided
    publication = article.get("publication", "Boston Globe")
    
    # Display the headline with a small caption for publication and AI notice.
    st.markdown(f"### {article.get('hed', 'No Title')}")
    st.caption(f"Outlet: {publication}")
    
    # Optionally, display the subhead if available
    if article.get("subhead"):
        st.markdown(f"**{article.get('subhead')}**")
    
    # Display the publication date
    st.write(f"**Publication Date:** {article.get('pub_date', 'Unknown')}")
    
    # Display a snippet of the article content (first 300 characters)
    content_snippet = article.get("content", "")[:300] + "..."
    st.write(content_snippet)
    
    # Optionally, you can display the classification scores in small text
    if "classifications" in article:
        classifications = article["classifications"]
        # Format classifications as "Label: score" pairs, comma-separated.
        class_text = ", ".join([f"{label}: {score:.2f}" for label, score in classifications.items()])
        st.caption(f"Classifications: {class_text} -- AI-generated classification")
    
    # Provide a link to the full article
    st.markdown(f"[Read full article]({article.get('url')})")
    
    st.markdown("---")
