import streamlit as st
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Page config
st.set_page_config(
    page_title="AWS Samples Repository Explorer",
    page_icon="📦",
    layout="wide"
)

# Load data efficiently
@st.cache_data
def load_data():
    with open('aws_samples_repos.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    # Convert to DataFrame immediately and optimize dtypes
    df = pd.DataFrame(data['repositories'])
    # Optimize memory by using appropriate dtypes
    df['stars'] = df['stars'].astype('int32')
    df['category'] = df['category'].astype('category')
    df['uncategorized'] = df['uncategorized'].astype('bool')
    return {
        'total_repositories': data['total_repositories'],
        'uncategorized_count': data.get('uncategorized_count', 0),
        'df': df
    }

data = load_data()
df = data['df']

# Sidebar
st.sidebar.title("📦 AWS Samples Explorer")
st.sidebar.markdown(f"**Total Repositories:** {data['total_repositories']}")
st.sidebar.markdown(f"**Uncategorized:** {data.get('uncategorized_count', 0)}")

# Navigation
page = st.sidebar.radio(
    "Navigate",
    ["🏠 Overview", "🔍 Search & Filter", "📊 Analytics", "⭐ Top Repositories", "📂 By Category", "🔗 Quick Links"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### Filters")
selected_categories = st.sidebar.multiselect(
    "Categories",
    options=sorted(df['category'].unique()),
    default=[]
)

min_stars = st.sidebar.slider("Minimum Stars", 0, int(df['stars'].max()), 0)

# Apply filters
filtered_df = df.copy()
if selected_categories:
    filtered_df = filtered_df[filtered_df['category'].isin(selected_categories)]
filtered_df = filtered_df[filtered_df['stars'] >= min_stars]

# Main content
if page == "🏠 Overview":
    st.title("AWS Samples Repository Explorer")
    st.markdown("Explore and discover repositories from the AWS Samples organization")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Repos", len(filtered_df))
    with col2:
        st.metric("Categories", filtered_df['category'].nunique())
    with col3:
        st.metric("Total Stars", f"{filtered_df['stars'].sum():,}")
    with col4:
        st.metric("Avg Stars", f"{filtered_df['stars'].mean():.0f}")
    
    st.markdown("---")
    
    # Category distribution
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Repositories by Category")
        cat_counts = filtered_df['category'].value_counts()
        fig = px.pie(
            values=cat_counts.values,
            names=cat_counts.index,
            title="Distribution"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Top 10 Categories by Stars")
        cat_stars = filtered_df.groupby('category')['stars'].sum().sort_values(ascending=False).head(10)
        fig = px.bar(
            x=cat_stars.values,
            y=cat_stars.index,
            orientation='h',
            labels={'x': 'Total Stars', 'y': 'Category'}
        )
        fig.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
    
    # Recent popular repos
    st.subheader("🌟 Highly Starred Repositories")
    top_repos = filtered_df.nlargest(10, 'stars')[['name', 'category', 'stars', 'description']]
    st.dataframe(top_repos, use_container_width=True, hide_index=True)

elif page == "🔍 Search & Filter":
    st.title("Search & Filter Repositories")
    
    search_term = st.text_input("🔎 Search by name or description", "")
    
    search_df = filtered_df.copy()
    if search_term:
        mask = (
            search_df['name'].str.contains(search_term, case=False, na=False) |
            search_df['description'].str.contains(search_term, case=False, na=False)
        )
        search_df = search_df[mask]
    
    st.markdown(f"**Found {len(search_df)} repositories**")
    
    # Sort options
    sort_by = st.selectbox("Sort by", ["Stars (High to Low)", "Stars (Low to High)", "Name (A-Z)", "Name (Z-A)"])
    
    if sort_by == "Stars (High to Low)":
        search_df = search_df.sort_values('stars', ascending=False)
    elif sort_by == "Stars (Low to High)":
        search_df = search_df.sort_values('stars', ascending=True)
    elif sort_by == "Name (A-Z)":
        search_df = search_df.sort_values('name')
    else:
        search_df = search_df.sort_values('name', ascending=False)
    
    # Paginate results for better performance
    results_per_page = 20
    total_results = len(search_df)
    total_pages = (total_results + results_per_page - 1) // results_per_page
    
    if total_results > 0:
        page_num = st.number_input("Page", min_value=1, max_value=max(1, total_pages), value=1, step=1)
        start_idx = (page_num - 1) * results_per_page
        end_idx = min(start_idx + results_per_page, total_results)
        
        st.markdown(f"Showing {start_idx + 1}-{end_idx} of {total_results} results")
        
        # Display only current page
        for _, repo in search_df.iloc[start_idx:end_idx].iterrows():
            with st.container():
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"### [{repo['name']}]({repo['url']})")
                    st.markdown(f"**Category:** {repo['category']}")
                    st.markdown(repo['description'] if repo['description'] else "_No description_")
                with col2:
                    st.metric("⭐ Stars", repo['stars'])
                st.markdown("---")
    else:
        st.info("No repositories found.")

elif page == "📊 Analytics":
    st.title("Repository Analytics")
    
    tab1, tab2, tab3 = st.tabs(["📈 Star Distribution", "📊 Category Analysis", "🔢 Statistics"])
    
    with tab1:
        st.subheader("Star Distribution")
        
        fig = px.histogram(
            filtered_df,
            x='stars',
            nbins=50,
            title="Distribution of Stars Across Repositories"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Box plot by category
        st.subheader("Stars by Category (Box Plot)")
        top_cats = filtered_df['category'].value_counts().head(10).index
        box_df = filtered_df[filtered_df['category'].isin(top_cats)]
        
        fig = px.box(
            box_df,
            x='category',
            y='stars',
            title="Star Distribution by Top 10 Categories"
        )
        fig.update_xaxes(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("Category Deep Dive")
        
        col1, col2 = st.columns(2)
        
        with col1:
            cat_stats = filtered_df.groupby('category').agg({
                'stars': ['count', 'sum', 'mean', 'max']
            }).round(0)
            cat_stats.columns = ['Count', 'Total Stars', 'Avg Stars', 'Max Stars']
            cat_stats = cat_stats.sort_values('Total Stars', ascending=False)
            st.dataframe(cat_stats, use_container_width=True)
        
        with col2:
            # Treemap
            fig = px.treemap(
                filtered_df,
                path=['category'],
                values='stars',
                title="Repository Stars by Category (Treemap)"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.subheader("Statistical Summary")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Median Stars", f"{filtered_df['stars'].median():.0f}")
            st.metric("Std Deviation", f"{filtered_df['stars'].std():.0f}")
        
        with col2:
            st.metric("75th Percentile", f"{filtered_df['stars'].quantile(0.75):.0f}")
            st.metric("90th Percentile", f"{filtered_df['stars'].quantile(0.90):.0f}")
        
        with col3:
            st.metric("Max Stars", f"{filtered_df['stars'].max():.0f}")
            st.metric("Min Stars", f"{filtered_df['stars'].min():.0f}")
        
        st.markdown("---")
        st.subheader("Detailed Statistics")
        st.dataframe(filtered_df['stars'].describe(), use_container_width=True)

elif page == "⭐ Top Repositories":
    st.title("Top Repositories")
    
    top_n = st.slider("Show top N repositories", 10, 100, 25)
    
    top_df = filtered_df.nlargest(top_n, 'stars')
    
    # Horizontal bar chart
    fig = px.bar(
        top_df.head(20),
        x='stars',
        y='name',
        orientation='h',
        color='category',
        title=f"Top {min(20, top_n)} Repositories by Stars",
        hover_data=['description']
    )
    fig.update_layout(height=600, yaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    st.subheader("Repository List")
    
    # Use dataframe display for better performance with large lists
    display_df = top_df[['name', 'category', 'stars', 'description', 'url']].copy()
    display_df['name'] = display_df.apply(lambda x: f"[{x['name']}]({x['url']})", axis=1)
    display_df = display_df.drop('url', axis=1)
    display_df.index = range(1, len(display_df) + 1)
    
    st.dataframe(
        display_df,
        use_container_width=True,
        column_config={
            "name": st.column_config.TextColumn("Repository", width="medium"),
            "category": st.column_config.TextColumn("Category", width="medium"),
            "stars": st.column_config.NumberColumn("⭐ Stars", width="small"),
            "description": st.column_config.TextColumn("Description", width="large")
        }
    )

elif page == "📂 By Category":
    st.title("Browse by Category")
    
    categories = sorted(filtered_df['category'].unique())
    selected_cat = st.selectbox("Select a category", categories)
    
    cat_df = filtered_df[filtered_df['category'] == selected_cat].sort_values('stars', ascending=False)
    
    # Add filter input
    filter_text = st.text_input("🔎 Filter repositories in this category", "", placeholder="Search by name or description...")
    
    if filter_text:
        mask = (
            cat_df['name'].str.contains(filter_text, case=False, na=False) |
            cat_df['description'].str.contains(filter_text, case=False, na=False)
        )
        cat_df = cat_df[mask]
    
    col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
    with col1:
        st.metric("Repositories", len(cat_df))
    with col2:
        st.metric("Total Stars", f"{cat_df['stars'].sum():,}")
    with col3:
        st.metric("Average Stars", f"{cat_df['stars'].mean():.0f}" if len(cat_df) > 0 else "0")
    with col4:
        expand_all = st.checkbox("Expand All", value=False)
    
    st.markdown("---")
    
    # Display repos in this category
    if len(cat_df) == 0:
        st.info("No repositories match your filter.")
    else:
        # Limit displayed repos for performance
        max_display = 100
        if len(cat_df) > max_display and not expand_all:
            st.warning(f"Showing first {max_display} of {len(cat_df)} repositories. Use filters to narrow results.")
            display_df = cat_df.head(max_display)
        else:
            display_df = cat_df
        
        for _, repo in display_df.iterrows():
            with st.expander(f"⭐ {repo['stars']} | {repo['name']}", expanded=expand_all):
                st.markdown(f"**Description:** {repo['description'] if repo['description'] else '_No description_'}")
                st.markdown(f"**URL:** [{repo['url']}]({repo['url']})")
                st.markdown(f"**Stars:** {repo['stars']}")

elif page == "🔗 Quick Links":
    st.title("Quick Links")
    
    st.markdown("### Generate Links for Your Use Case")
    
    use_case = st.selectbox(
        "What are you looking for?",
        [
            "Machine Learning & AI",
            "Serverless & Lambda",
            "Kubernetes & Containers",
            "Security & IAM",
            "Data & Analytics",
            "Infrastructure as Code",
            "All Repositories"
        ]
    )
    
    # Filter based on use case
    if use_case == "Machine Learning & AI":
        use_df = filtered_df[filtered_df['category'] == 'Machine Learning']
    elif use_case == "Serverless & Lambda":
        use_df = filtered_df[filtered_df['name'].str.contains('lambda|serverless|sam', case=False, na=False)]
    elif use_case == "Kubernetes & Containers":
        use_df = filtered_df[filtered_df['category'] == 'Containers']
    elif use_case == "Security & IAM":
        use_df = filtered_df[filtered_df['category'] == 'Security, Identity, & Compliance']
    elif use_case == "Data & Analytics":
        use_df = filtered_df[filtered_df['category'] == 'Analytics']
    elif use_case == "Infrastructure as Code":
        use_df = filtered_df[filtered_df['name'].str.contains('cdk|cloudformation|terraform', case=False, na=False)]
    else:
        use_df = filtered_df
    
    use_df = use_df.sort_values('stars', ascending=False)
    
    st.markdown(f"**Found {len(use_df)} repositories**")
    st.markdown("---")
    
    # Limit cards for performance
    max_cards = 50
    display_use_df = use_df.head(max_cards)
    
    if len(use_df) > max_cards:
        st.info(f"Showing top {max_cards} repositories by stars. Total found: {len(use_df)}")
    
    # Display as clickable cards
    cols = st.columns(3)
    for idx, (_, repo) in enumerate(display_use_df.iterrows()):
        with cols[idx % 3]:
            st.markdown(f"""
            <div style="padding: 10px; border: 1px solid #ddd; border-radius: 5px; margin-bottom: 10px;">
                <h4><a href="{repo['url']}" target="_blank">{repo['name']}</a></h4>
                <p><strong>⭐ {repo['stars']}</strong> | {repo['category']}</p>
                <p style="font-size: 0.9em;">{repo['description'][:100] if repo['description'] else 'No description'}...</p>
            </div>
            """, unsafe_allow_html=True)

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("Built with Streamlit 🎈")
