import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import plotly.express as px
import matplotlib.pyplot as plt
import altair as alt

# =============== SETTINGS ================
def settings():
    pd.options.display.float_format = '{:,.2f}'.format
    pd.options.display.max_columns = None
    pd.options.display.max_rows = None
    pd.set_option('display.expand_frame_repr', False)
    st.set_page_config(layout='wide')
    #locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
    plt.style.use('Solarize_Light2')

# =============== GETING DATA ================
def get_data(path):
    data = pd.read_csv(path)
    return data

def cleaning_data(data):
    data['date'] = pd.to_datetime(data['date'], format='%Y-%m-%d')
    data = data.sort_values(by='date').drop_duplicates(subset='id', keep='first')
    data = data.reset_index(drop=True)
    data['floors'] = round(data['floors'],1)
    data.loc[data['bedrooms'] == 33].replace({33: 3})
    return data

# =============== FEATURES ================
def ft_waterfront(data):
    data['waterfront'] = pd.Categorical(data['waterfront'])
    data['waterfront'] = data['waterfront'].cat.rename_categories({0: 'no', 1: 'yes'})
    return data

def ft_condition(data):
    data['condition'] = pd.Categorical(data['condition'])
    data['condition'] = data['condition'].cat.rename_categories(
        {1: 'bad', 2: 'fair', 3: 'average', 4: 'good', 5: 'excelent'})
    return data

def ft_view(data):
    data['view'] = pd.Categorical(data['view'])
    data['view'] = data['view'].cat.rename_categories({0: 'no view', 1: 'fair', 2: 'average', 3: 'good', 4: 'excelent'})
    return data

def ft_grade(data):
    data['grade'] = data['grade'].apply(lambda x: "poor" if x <= 3 else
    "fair" if x <= 5 else
    "average" if x <= 8 else
    "good" if x <= 10 else
    "excelent" if x <= 13 else 'na')
    data['grade'] = pd.Categorical(data['grade'])
    return data

def season(month, day):
    # ------ winter -----------
    # Dec and >= 21st
    if month == 12 and day >= 21:
        return 'winter'

    # Jan and Feb
    if month == 1 or month == 2:
        return 'winter'

    # Mar and < 21st
    if month == 3 and day < 21:
        return 'winter'

    # ------ Spring -----------

    # Mar and >= 21st
    if month == 3 and day >= 21:
        return 'spring'

    # Apr and May
    if month == 4 or month == 5:
        return 'spring'

    # Jun and < 21st
    if month == 6 and day < 21:
        return 'spring'

    # ------ Summer -----------

    # Jun and >= 21st
    if month == 6 and day >= 21:
        return 'summer'
    # Jul and Aug
    if month == 7 or month == 8:
        return 'summer'

    # Sep and < 23st
    if month == 9 and day < 23:
        return 'summer'

    # ------ Fall -----------

    # Jun and >= 23st
    if month == 9 and day >= 23:
        return 'fall'

    # Oct and Nov
    if month == 10 or month == 11:
        return 'fall'
    # Dec and <21st
    if month == 12 and day < 21:
        return 'fall'

def ft_season(data):
    data['day'] = pd.DatetimeIndex(data['date']).day
    data['month'] = pd.DatetimeIndex(data['date']).month
    data['season'] = data[['month', 'day']].apply(lambda x: season(month=x['month'], day=x['day']), axis=1)
    data.drop(columns=['month', 'day'], inplace=True)
    return data

def ft_bathrooms(data):
    df = pd.DataFrame(data['bathrooms'].astype(str).str.split('.', expand=True))
    data['complete_bathrooms'] = np.int64(df[0])
    data['half_bathroom'] = df[1]
    data['half_bathroom'] = data['half_bathroom'].apply(lambda x: "no" if x == "0" else "yes")
    data['half_bathroom'] = pd.Categorical(data['half_bathroom'])
    data = data.loc[data['complete_bathrooms'] != 0]
    data.drop(columns = ['bathrooms'],inplace = True)
    data = data.reset_index(drop=True)
    return data

def last_maintenance(built, renovated):
    if renovated == 0:
        return built
    else:
        return renovated

def ft_last_maintenance(data):
    data['last_maintenance'] = data[['yr_built', 'yr_renovated']].apply(
        lambda x: last_maintenance(built=x.yr_built, renovated=x.yr_renovated), axis=1)
    return data

def ft_price_sqft(data):
    data['price_sqft'] = round(data['price'] / data['sqft_living'],2)
    return data

def ft_regional_condition(data):
    df = data[['zipcode', 'condition']].groupby(['zipcode']).mean()
    df.rename(columns={'condition': 'regional_condition'}, inplace=True)
    data = data.merge(df, on='zipcode', how='left')
    return data

def ft_regional_price(data):
    df = data[['zipcode','price_sqft']].groupby(['zipcode']).mean()
    df.rename(columns = {'price_sqft':'regional_price_sqft'},inplace = True)
    data = data.merge(df,on='zipcode',how='left')
    data['expected_price'] = round(data['regional_price_sqft'] * data['sqft_living'], 2)
    data['profit'] = round(data['expected_price'] - data['price'],2)

    return data

def ft_buy(data):
    data['buy'] = data[['regional_price_sqft','price_sqft','regional_condition','condition','expected_price','price']].apply(lambda x: 'yes' if ((x['price_sqft']<x['regional_price_sqft']) & #sqft price bellow market
                                                                                                                       (x['regional_condition']<x['condition'])& # Regional Condition
                                                                                                                       ((x['expected_price']/x['price'])>1.6)) # Margin Profit greater than 60%
                                                                                                                    else 'no',axis = 1)
    return data

# =============== Data Frames ================
# filters the houses to buy
def ft_df_buy(data):
    data = data.loc[(data['buy'] == 'yes') & (data['condition'] != 'bad')].copy()
    print(data.columns)
    data = data[['id', 'date','season', 'price','expected_price','profit','price_sqft', 'regional_price_sqft',
        'complete_bathrooms', 'half_bathroom', 'bedrooms', 'floors', 'sqft_living', 'sqft_above','sqft_basement', 'sqft_lot',
       'view', 'condition', 'grade','waterfront', 'yr_built', 'yr_renovated','last_maintenance', 'zipcode', 'lat', 'long']]
    data = data.reset_index(drop = True)
    return data

# =============== Graphic Models ================
def gr_model1(data,column):
    data['Quantity'] = 1
    chart_data = pd.DataFrame(data.groupby([column]).count()['Quantity'])
    chart_data = chart_data.reset_index()
    chart_data[chart_data.columns[0]] = pd.Categorical(chart_data[chart_data.columns[0]])
    title = f'{column.title()} Variable'
    st.markdown(f'<div style="text-align: center;"><b> {title} </b></div>', unsafe_allow_html=True)
    if (len(chart_data) <= 5):
        gr = alt.Chart(chart_data).mark_bar(size=50).encode(
            x=chart_data.columns[0],
            y=chart_data.columns[1],
            color=alt.Color(chart_data.columns[0],
            scale=alt.Scale(scheme='category10'),
            legend=None))
    elif (len(chart_data) > 5 and len(chart_data) < 10):
        gr = alt.Chart(chart_data).mark_bar(size=30).encode(
            x=chart_data.columns[0],
            y=chart_data.columns[1],
            color=alt.Color(chart_data.columns[0],
                            scale=alt.Scale(scheme='category10'),
                            legend=None))
    elif (len(chart_data) > 10 and len(chart_data) < 30):
        gr = alt.Chart(chart_data).mark_bar(size=20).encode(
            x=chart_data.columns[0],
            y=chart_data.columns[1],
            color=alt.Color(chart_data.columns[0],
                            scale=alt.Scale(scheme='category10'),
                            legend=None))
    else:
        gr = alt.Chart(chart_data).mark_bar().encode(
            x=chart_data.columns[0],
            y=chart_data.columns[1],
            color=alt.Color(chart_data.columns[0],
                            scale=alt.Scale(scheme='category20'),
                            legend=None))
    return st.altair_chart(gr, use_container_width=True)
def gr_model2(data,column,type):
    chart_data = data[[column,'price']]
    title = f'{column.title()} Vs Price ($)'
    if column == 'yr_built' or column == 'sqft_basement' :
        chart_data[chart_data.columns[0]] = pd.Categorical(chart_data[chart_data.columns[0]])
    if type == 'quality':
        st.markdown(f'<div style="text-align: center;"><b> {title} </b></div>', unsafe_allow_html=True)
        gr = alt.Chart(chart_data).mark_circle().encode(
            x=chart_data.columns[0],
            y=chart_data.columns[1],
            color=alt.Color(chart_data.columns[0],
                            scale=alt.Scale(scheme='category10'),
                            legend=None)
    )
    else:
        st.markdown(f'<div style="text-align: center;"><b> {title} </b></div>', unsafe_allow_html=True)
        gr = alt.Chart(chart_data).mark_circle().encode(
            x=chart_data.columns[0],
            y=chart_data.columns[1])
    return st.altair_chart(gr, theme="streamlit", use_container_width=True)
def gr_model3(data,column):
    fig = px.scatter_mapbox(data,
                            lat="lat",
                            lon="long",
                            color=column,
                            zoom=10)

    fig.update_layout(mapbox_style="open-street-map")
    fig.update_traces(marker={'size': 10})
    fig.update_layout(height=800, margin={"r": 0, "t": 0, "l": 0, "b": 0})
    return st.plotly_chart(fig,use_container_width=True)

# =============== TABS ================
def set_home(df, tab, data):
    with tab:
        st.title('🏠 House Rocket Info :rocket:')
        st.markdown(
            'House Rocket is a fictional company which make profit buying and selling Houses in King County (USA).')
        st.markdown('As the portfolio of houses are too large, is difficult to filter what are the good opportunity.')
        st.markdown('This app were built to help find the best opportunities using the **Businesses Criteria**.')
        st.info('Checkout the complete Repository on [Github](LINK)', icon="ℹ️")
        # =============== MARKER 1 ================
        st.header('**1. Objectives**')
        st.markdown('- Perform exploratory data analysis on properties available on dataset.')
        st.markdown('- Determine which properties should be purchased according to business criteria.')
        st.markdown('- Develop an online dashboard that can be accessed by the CEO from a mobile or computer.')

        # =============== MARKER 2 ================
        st.header('**2. Business Problem**')
        st.markdown('- What are the attributes that most impact the price of a property?')
        st.markdown('- Which property should the company have bought and for how much?')
        st.markdown('- Once the house was bought, when is the best moment to sell it and for how much?')
        st.markdown(" ")

        # =============== MARKER 3 ================
        st.header('**3. Business Assumptions**')
        st.markdown('- There may be typos in some records that must be dealt with/removed during data cleaning.')
        st.markdown('- There may be houses without a complete bathroom, those houses won’t be consider for buy')
        st.markdown('- The data available is only from Houses already sold between May 2014 to May 2015.')
        st.markdown('''- Seasons of the year:
    - Spring starts on March 21st.
    - Summer starts on June 21st.
    - Fall starts on September 23rd.
    - Winter starts on December 21st.''')
        st.markdown('- If the ‘yr_renovated’ is null, will be assumed that ‘yr_renovated’ = ‘yr_built‘')

        with st.expander('**The variable on original Dataset goes as follows:**'):
            st.markdown('''
            ### Columns Description
            
            | Variable | Description |
            | --- | --- |
            | id | Unique ID for each home sold |
            | date | Date of the home sale |
            | price | Price of each home sold |
            | bedrooms | Number of bedrooms |
            | bathrooms | Number of bathrooms, where .5 accounts for a room with a toilet but no shower |
            | sqft_living | Square footage of the apartments interior living space |
            | sqft_lot | Square footage of the land space |
            | floors | Number of floors |
            | waterfront | A dummy variable for whether the apartment was overlooking the waterfront or not |
            | view | An index from 0 to 4 of how good the view of the property was |
            | condition | An index from 1 to 5 on the condition of the apartment |
            | grade | An index from 1 to 13, where 1 - 3 falls short of building construction and design, 7 has an average level of construction and design, and 11 - 13 have a high quality level of construction and design. |
            | sqft_above | The square footage of the interior housing space that is above ground level |
            | sqft_basement | The square footage of the interior housing space that is below ground level |
            | yr_built | The year the house was initially built |
            | yr_renovated | The year of the house’s last renovation |
            | zipcode | What zipcode area the house is in |
            | lat | Lattitude |
            | long | Longitude |
            | sqft_living15 | The square footage of interior housing living space for the nearest 15 neighbors |
            | sqft_lot15 | The square footage of the land lots of the nearest 15 neighbors |
            ''')
        # =============== MARKER 4 ================
        st.header('**4. Business Criteria**')
        st.markdown('''- Business criteria to determine whether a property should be bought are:
    - Property price per square foot is bellow regional median.
    - Property condition is above regional median.
    - Profit margin should be greater than 10%''')

        # =============== MARKER 5 ================
        st.header('**5. Dat a Cleaning**')
        st.markdown("- Drop Duplicated ID's and keep first.")
        st.markdown("- Change Data Format to '%Y-%m-%d'.")
        st.markdown('- Check possible typing errors.')

        # =============== MARKER 6 ================
        st.header('**6. Feature Engeering**')
        st.markdown("- Create a variable _'season'_ of the year which the property was sold.")
        st.markdown("- Create a variable '_complete_bathrooms_' that are bathrooms with shower.")
        st.markdown("- Create a variable '_half_bathrooms_' that are bathrooms without shower.")
        st.markdown("- Create a variable '_price/sqft_lot_' that are bathrooms without shower.")
        st.markdown(
            "- Create a varible ‘_last_maintenance_’. If ‘_yr_renovate_’ is 0, then assume the _last_maintenance_ it’s the same as ‘_yr_built_’.")
        st.markdown(
            "- Use the **Columns Description Table** to convert the colunms 'View', 'Condition', 'Waterfront' and 'Grade' to categorical variables.")
        if st.checkbox('Show Categorical Variables'):
            st.dataframe(data.select_dtypes('category').describe().T, width=600)
    pass

def set_exploratory_analisys(data, tab):
    with tab:
        st.title('📈 Data Analisys')
        st.markdown(
            'This data were withdraw from Kagle and can be acessed in this [link](https://www.kaggle.com/datasets/harlfoxem/housesalesprediction).')
        # =============== MARKER 1 ================
        st.header("**1. Data Description**")
        st.markdown("We have used the Data Description available on Kaggle's source.")
        with st.expander('**Checkout the Columns Description Table:**'):
            st.markdown('''
            ### Columns Description

            | Variable | Description |
            | --- | --- |
            | id | Unique ID for each home sold |
            | date | Date of the home sale |
            | price | Price of each home sold |
            | bedrooms | Number of bedrooms |
            | bathrooms | Number of bathrooms, where .5 accounts for a room with a toilet but no shower |
            | sqft_living | Square footage of the apartments interior living space |
            | sqft_lot | Square footage of the land space |
            | floors | Number of floors |
            | waterfront | A dummy variable for whether the apartment was overlooking the waterfront or not |
            | view | An index from 0 to 4 of how good the view of the property was |
            | condition | An index from 1 to 5 on the condition of the apartment |
            | grade | An index from 1 to 13, where 1 - 3 falls short of building construction and design, 7 has an average level of construction and design, and 11 - 13 have a high quality level of construction and design. |
            | sqft_above | The square footage of the interior housing space that is above ground level |
            | sqft_basement | The square footage of the interior housing space that is below ground level |
            | yr_built | The year the house was initially built |
            | yr_renovated | The year of the house’s last renovation |
            | zipcode | What zipcode area the house is in |
            | lat | Lattitude |
            | long | Longitude |
            | sqft_living15 | The square footage of interior housing living space for the nearest 15 neighbors |
            | sqft_lot15 | The square footage of the land lots of the nearest 15 neighbors |
            
            ''')
        st.markdown(
            'For more information about **data cleaning** and **feature engeering**, check out the :house: Home Page.')

        # =============== MARKER 2 ================
        st.header('**2. Quantity Variables**')
        # =============== MARKER 2.1 ================
        st.markdown('### 2.1. Frequency Distribution on Bathrooms, Bedrooms and Floors')
        # =============== Graphics ================
        c1, c2, c3 = st.columns(3)
        with c1:
            gr_model1(data=data, column='bedrooms')
        with c2:
            gr_model1(data=data, column='complete_bathrooms')
        with c3:
            gr_model1(data=data, column='floors')

        st.markdown('#### Observations')
        st.markdown('- Most of houses has between 2 and 5 bedrooms (97,68%)')
        st.markdown('- Most of houses has between 1 and 3 bathrooms (98,13%)')
        st.markdown('- Most of houses has between 1 and 2 floors (96,36%)')

        # =============== MARKER 2.2 ================
        st.markdown('### 2.2. Time Series: Year Built, Year Renovated and Last Maintenance')

        gr_model1(data = data, column = 'yr_built')
        gr_model1(data=data.loc[data['yr_renovated']>0], column = 'yr_renovated')
        gr_model1(data=data, column='last_maintenance')

        st.markdown('#### Observations')
        st.markdown('- Of 21351, we have 906 reformed houses, which represents 4.24%.')
        st.markdown('- We had a peak of Renovated and Built houses on 2014.')
        st.markdown('- Of 21351 houses, we have 650 reformed or built houses in 2014, which represents 3.04%.')

        # =============== Graphics ================
        container1 = st.container()
        container2 = st.container()
        container3 = st.container()
        container4 = st.container()
        container5 = st.container()
        container6 = st.container()
        container7 = st.container()

        # =============== MARKER 3 ================
        with container1:
            st.header('**3. Quality Variables**')
            c1, c2, c3 = st.columns(3)
            with c1:
                gr_model1(data=data, column='view')
            with c2:
                gr_model1(data=data, column='condition')
            with c3:
                gr_model1(data=data, column='grade')
        with container2:
            c1, c2, c3 = st.columns(3)
            with c1:
                gr_model1(data=data, column='season')
            with c2:
                gr_model1(data=data, column='waterfront')
            with c3:
                gr_model1(data=data, column='half_bathroom')

            st.markdown('''#### Observations
- Most of Houses doesn't have View (90.15%)
- Most of Houses are in average, good or excelent conditions (99.13%)
- Most of Houses are in average or good grade (96.57%)
- Most of Houses were sold in Spring (31.50%).
- Most of Houses doesn't have waterfront (99.26%)
- Most of Houses have a Half Bathroom (69.00%)''')
        # =============== MARKER 4 ================
        with container3:
            st.header('**4. Variable Correlations**')
            st.header('**4.1. Quantity Variables**')
            c1, c2 = st.columns(2)
            with c1:
                gr_model2(data, column='sqft_living',type = None)
            with c2:
                gr_model2(data, column='sqft_lot',type = None)
        with container4:
            c1, c2 = st.columns(2)
            with c1:
                gr_model2(data=data.loc[data['sqft_basement']>0], column='sqft_basement',type = None)
            with c2:
                gr_model2(data, column='yr_built',type = None)
        # =============== MARKER 4.2 ================
        with container5:
            st.header('**4.2. Quality Variables**')
            c1, c2 = st.columns(2)
            with c1:
                gr_model2(data, column='view',type = 'quality')
            with c2:
                gr_model2(data, column='condition',type = 'quality')
        with container6:
            c1, c2 = st.columns(2)
            with c1:
                gr_model2(data, column='waterfront',type = 'quality')
            with c2:
                gr_model2(data, column='half_bathroom',type = 'quality')
        # =============== MARKER 4.3 ================
        with container7:
            st.header('**4.3. Correlation By Pearson**')
            fig, ax = plt.subplots()
            sns.heatmap(round(data[['sqft_living', 'sqft_lot', 'sqft_basement', 'bedrooms', 'complete_bathrooms', 'floors',
                              'yr_renovated', 'yr_built', 'last_maintenance', 'price']].corr(method='pearson'),2),
                        annot=True, ax=ax)
            st.write(fig)
            st.markdown('''#### Observations
- Price and sqft_living have a strong positive relation
- Complete Bathrooms also have a good positive relation, but it should happen because houses with more bathrooms, also have more sqft_living.)''')
    pass

def set_investment_suggest(df_buy,data, tab):

    with tab:
        container1 = st.container()
        container2 = st.container()

        with container1:
            st.title('📥 Investiment Suggestion')
            # Variables
            percent_buy = round((len(df_buy) / data.shape[0]) * 100, 2)
            profit = round((df_buy['expected_price'].sum() - df_buy['price'].sum()), 2)
            profit_str = str(round(profit / 100000, 2))
            profit_margin = str(round(((df_buy['expected_price'].mean() / df_buy['price'].mean()-1)*100), 2))
            value_invested  = round(df_buy['price'].sum(),2)
            value_invested_str = str(round(value_invested / 100000, 2))
            # =============== CARDS ================
            c1, c2, c3,c4,c5,c6 = st.columns(6)
            c1.metric(label="Total Houses", value=data.shape[0])
            c2.metric(label="House to Buy", value=len(df_buy))
            c3.metric(label="% of House to Buy", value=str(percent_buy) + "%")
            c4.metric(label = 'Invested Value',value ='$' + str(value_invested_str+'M'))
            c5.metric(label='Expected Profit', value='$' + profit_str + 'M')
            c6.metric(label = 'Average Profit Margin',value = profit_margin+'%')
            st.dataframe(df_buy.head(50), use_container_width=True)

        with container2:
            st.title('Suggestion Portfolio')
            st.markdown('')
            gr_model3(data = df_buy,column='profit')
    pass

if __name__ == '__main__':
    path = 'kc_house_data.csv'
    df = get_data(path)
    data = cleaning_data(df)
    settings()

    # =============== FEATURES ================
    data = ft_waterfront(data)
    data = ft_view(data)
    data = ft_bathrooms(data)
    data = ft_grade(data)
    data = ft_last_maintenance(data)
    data = ft_season(data)
    data = ft_price_sqft(data)
    data = ft_regional_price(data)
    data = ft_regional_condition(data)
    data = ft_buy(data)
    data = ft_condition(data)
    # =============== DATAFRAMES ================
    df_buy = ft_df_buy(data)

    # =============== DASHBOARD ================
    tabs = st.tabs(["🏠 Home", '📈 Data Analisys', "📥 Investiment Suggestion"])
    set_home(df=df, tab=tabs[0], data=data)
    set_exploratory_analisys(data, tabs[1])
    set_investment_suggest(data = data, df_buy= df_buy,tab =  tabs[2])
