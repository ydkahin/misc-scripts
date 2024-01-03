import pandas as pd
import hvplot.pandas
import panel as pn

'''
This app generates a dashboard provided a csv from the letterboxd scraper that comes with it.
It requires the Panel python library
'''


films = pd.read_csv('./rich_example.csv') #replace the csv with export from the scraper
unique_years = sorted(films['film_year'].unique())

# Create a function to plot the distribution
def plot_distribution(film_year):
    
    filtered_films = films[films['film_year'] == film_year]
    

    filtered_films = films[films['film_year'] == film_year]    
    try:
        genres_list = [genre for genres in filtered_films['genres'] for genre in eval(genres)]
    except:
        genres_list = [genre for genres in filtered_films['genres'] for genre in genres]
    genres_df = pd.Series(genres_list).sort_values(ascending=True)
    
    
    user_rating_hist = filtered_films.hvplot.hist(
        'user_rating', 
        bins=10, 
        xlabel = 'User Rating',
        ylabel = 'counts',
        width=600, height=400, 
        title=f'User Rating Distribution of Watched Films from {film_year}')

    genres_hist = genres_df.value_counts().hvplot.barh(
        width=600, 
        color='teal',
        xlabel = 'Number of Films',
        height=400, 
        title=f'Genres Distribution of Watched Films from {film_year}')
    
    # Create a panel with the histograms
    panel = pn.Column(
        pn.Row(user_rating_hist, genres_hist)
    )
    # Display the panel
    return panel

# Create a slider for film_year
film_year_slider = pn.widgets.DiscreteSlider(
    name='Film Year',
    options=unique_years,
    value=unique_years[0],
    align='center'
)

# PANEL ROW No. 1
panel_row_1 = pn.interact(plot_distribution, film_year=film_year_slider)



#PANEL ROW No.2

year_count_hist = films['film_year'].value_counts().sort_index().hvplot.bar(
    xlabel='Film Year', 
    ylabel='counts',
    width=1200,
    height=400, 
    color='green',
    title='Year distribution of Watched Films',
    rot=90)


## Get the film year user rating average
user_mean_rating_by_year = films.groupby('film_year')['user_rating'].agg(['mean','size']).reset_index()

year_rating_hist = user_mean_rating_by_year.hvplot.bar(
    y='mean',
    x='film_year',
    color='size', colorbar=True, 
    clabel="Number of films", 
    cmap='Greens',
    ylim=(0, 5.5),
    height= 400,
    width=1200,
    bar_width= 1,
    ylabel='Average Rating (User)',
    xlabel='Film Year',
    title='User average rating through the years',
    rot=90
)


## put the second row together
panel_year = pn.Column(
    pn.Row(
        year_count_hist, 
        year_rating_hist
    )
)

layout = pn.Column(
    pn.Spacer(width=150),
    '# Film Stats',
    pn.Spacer(width=200),
    '## By Year (Use the slider below)',
    pn.Spacer(width=150),
    pn.Row(panel_row_1),
    pn.Spacer(height=50),
    '## This is for lifetime aggregate ',
    pn.Spacer(width=150),
    pn.Row(year_count_hist),
    pn.Spacer(height=150),
    pn.Row(year_rating_hist)
)



# Display the panel in the notebook
pn.extension()
layout.servable()