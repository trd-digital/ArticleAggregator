import streamlit as st
import json
import os
from bs4 import BeautifulSoup
from datetime import datetime

# @st.cache_data(ttl=300)

def clean_text(html_content):
    # Parse HTML, extract text, and escape dollar signs
    text = BeautifulSoup(html_content, "html.parser").get_text(separator=" ", strip=True)
    return text.replace("$", "\$")


def load_articles(json_file="articles.json"):
    """Load articles from JSON and add a datetime object for sorting."""
    if os.path.exists(json_file):
        with open(json_file, 'r') as f:
            articles = json.load(f)
        # Convert ISO publication dates to datetime objects for sorting.
        # Also, each article should have a raw_pub_date (if stored by your scraper).
        for article in articles:
            if article.get("pub_date"):
                try:
                    article["pub_date_dt"] = datetime.fromisoformat(article["pub_date"])
                except Exception as e:
                    article["pub_date_dt"] = None
            else:
                article["pub_date_dt"] = None
        return articles
    else:
        return []

# Load articles
articles = load_articles()

st.title("Real Estate News Dashboard")
st.write(f"Showing **{len(articles)}** articles.")

# Sidebar: Filtering and sorting options.
st.sidebar.header("Filters & Sorting Options")

# Filter by Outlet: Get unique outlets from the JSON.
outlets = sorted(list({article.get("Outlet", "Unknown") for article in articles}))
selected_outlet = st.sidebar.selectbox("Filter by Outlet", ["All"] + outlets)

# Sorting: Option dropdown and order.
sort_option = st.sidebar.selectbox("Sort Articles By", ["Publication Date", "Outlet", "Classification Score"])
sort_order = st.sidebar.radio("Sort Order", ["Descending", "Ascending"])

# If sorting by classification score, choose a category.
classification_category = None
if sort_option == "Classification Score":
    classification_keys = set()
    for article in articles:
        for key in article.get("classifications", {}).keys():
            classification_keys.add(key)
    classification_keys = sorted(list(classification_keys))
    if classification_keys:
        classification_category = st.sidebar.selectbox("Select Classification Category", classification_keys)
    else:
        st.sidebar.info("No classification data available.")

# Apply outlet filtering.
if selected_outlet != "All":
    articles = [article for article in articles if article.get("Outlet", "Unknown") == selected_outlet]

# Sorting logic.
if sort_option == "Publication Date":
    articles = sorted(
        articles,
        key=lambda a: a.get("pub_date_dt") or datetime.min,
        reverse=(sort_order == "Descending")
    )
elif sort_option == "Outlet":
    articles = sorted(
        articles,
        key=lambda a: a.get("Outlet", ""),
        reverse=(sort_order == "Descending")
    )
elif sort_option == "Classification Score" and classification_category:
    articles = sorted(
        articles,
        key=lambda a: a.get("classifications", {}).get(classification_category, 0),
        reverse=(sort_order == "Descending")
    )

# Display each article with the updated UI.
for article in articles:
    # Headline in bold.
    st.markdown(f"**{article.get('hed', 'No Title')}**")
    
    # Subhead in italic (if available).
    if article.get("subhead"):
        st.markdown(f"*{article.get('subhead')}*")
    
    # Display the raw publication date.
    st.write(f"Published on: {article.get('raw_pub_date', 'Unknown')}")
    
    # Show a snippet (first 300 characters) of the article content.
    snippet = article.get("content", "")[:300] + "..."
    st.write(snippet)
    
    # "Read More" expander to reveal full content and additional details.
    with st.expander("Read More"):
        st.markdown("**Full Article:**")
        # Clean the content before displaying
        full_text = clean_text(article.get("content", "No content available"))
        st.write(full_text)
        if "classifications" in article:
            class_text = ", ".join([f"{label}: {score:.2f}" for label, score in article["classifications"].items()])
            st.caption(f"Classifications (AI-generated): {class_text}")

    
    st.markdown("---")
