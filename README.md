# House Rocket

House Rocket is a fictional company which make profit buying and selling Houses in King County (USA).

# Objectives

- Perform exploratory data analysis on properties available on dataset.
- Determine which properties should be purchased according to business criteria.
- Develop an online [dashboard](https://zameromjairo-house-rocket-dashboard-fgfvox.streamlit.app) that can be accessed by the CEO from a mobile or computer.

# 1. Business Problem

- What are the attributes that most impact the price of a property?
- Which property should the company have bought and for how much?
- Once the house was bought, when is the best moment to sell it and for how much?

# 2. **Business Assumptions**

- There may be typos in some records that must be dealt with/removed during data cleaning.
- There may be houses without a complete bathroom, those houses won’t be consider for buy
- The data available is only from Houses already sold between May 2014 to May 2015.
- Seasons of the year:
    - Spring starts on March 21st
    - Summer starts on June 21st
    - Fall starts on September 23rd
    - Winter starts on December 21st
- If the ‘yr_renovated’ is null, will be assumed that ‘yr_renovated’ = ‘yr_built‘
- Business criteria to determine whether a property should be bought are:
    - Property price per square foot is bellow regional median.
    - Property condition is above regional median.
    - Profit margin should be greater than 50%
- The variable on original Dataset goes as follows:
    
    
    | Variable | Description |
    | --- | --- |
    | id  | Unique ID for each home sold |
    | date  | Date of the home sale |
    | price  | Price of each home sold |
    | bedrooms  | Number of bedrooms |
    | bathrooms  | Number of bathrooms, where we have decimal as .5, accounts for a room with a toilet but no shower |
    | sqft_living  | Square footage of the apartments interior living space |
    | sqft_lot  | Square footage of the land space |
    | floors  | Number of floors |
    | waterfront  | A dummy variable for whether the apartment was overlooking the waterfront or not |
    | view  | An index from 0 to 4 of how good the view of the property was |
    | condition  | An index from 1 to 5 on the condition of the apartment |
    | grade  | An index from 1 to 13, where 1 - 3 falls short of building construction and design, 7 has an average level of construction and design, and 11 - 13 have a high quality level of construction and design. |
    | sqft_above  | The square footage of the interior housing space that is above ground level |
    | sqft_basement  | The square footage of the interior housing space that is below ground level |
    | yr_built  | The year the house was initially built |
    | yr_renovated  | The year of the house’s last renovation |
    | zipcode  | What zipcode area the house is in |
    | lat  | Lattitude |
    | long  | Longitude |
    | sqft_living15  | The square footage of interior housing living space for the nearest 15 neighbors |
    | sqft_lot15  | The square footage of the land lots of the nearest 15 neighbors |

# 3. Solution Strategy

1. Understand the business model
2. Understand the business problem
3. Data Collect
4. Data Cleaning
5. Data Filtering
6. Feature Engineering
    1. Create new variables as:
        - Season of the year which the property was sold
        - bathrooms with shower (complete bathrooms)
        - bathrooms without shower (half bathrooms)
        - ‘**last_maintenance’,** If ‘yr_renovate’ is 0, then assume the last_maintenance it’s the same as ‘yr_built’
7. Exploratory Analysis
8. Insights
9. Conclusion
10. Dashboard Deploy
    1. House Rocket Guide
    2. Statistic Insights
    3. Buying Suggestion
    

# 4. Data Insights

- The number of properties built with basements decreased 50% after the 80s.
- The price per square foot on properties with water view are 30% more expensive than properties that don't.
- The properties sold on summer are 20% more expensive than properties that were sold on winter.
- The further into the past we look in relation to the date of construction, the greater the proportion of renovated properties

# 5. Business Results

There are 21,351 available properties. Based on business criteria, 214 selected properties should be bought by House Rocket resulting on a US$730.86M profit.

Necessary Investment: US$935.07M

Estimated Revenue: US$1,665.65M

Estimated Profit: US$730.86M

Estimated Margin: 78.16%

# 6. Conclusion

The objective of this project was to create a online dashboard for the House Rocket's CEO. Deploying the dashboard on Streamlit platform which provides the CEO access from anywhere, facilitating data visualization and business decisions.

# 7. Next Steps

- Determine which season of the year would be the best to execute a sale.
- Implement a Machine Learning algorithm to define selling prices and increase revenue.

# 7. References

- Dataset House Sales in King County (USA) from [Kaggle](https://www.kaggle.com/harlfoxem/housesalesprediction)
- Variables meaning on [Kaggle discussion](https://www.kaggle.com/harlfoxem/housesalesprediction/discussion/207885)
- Python from Zero to DS lessons on [Youtube](https://www.youtube.com/watch?v=1xXK_z9M6yk&list=PLZlkyCIi8bMprZgBsFopRQMG_Kj1IA1WG&ab_channel=SejaUmDataScientist)
