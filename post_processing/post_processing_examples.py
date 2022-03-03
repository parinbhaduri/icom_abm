# This file includes an assortment of example scripts for extracting and visualizing results from a completed ICoM ABM simulation object, "s"

import geopandas as pd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm
import contextily as ctx

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

##### See which histories are stored on the network
s.network._properties

#### Get history for total population
s.network.get_history('total_population')

### Get history for population of a particular block group
s.network.nodes[50].get_history('population')
s.network.get_node('240054015052').get_history('population')

### Get history for population of a particular block group
s.network.nodes[50].get_history('population')
s.network.get_node('240054015052').get_history('population')

### Get location history for a specific household agents
s.network.get_institution('all_hh_agents').components[25000].get_history('location')

### Get list of agents that reside in a specific block group
s.network.get_node('245101204002').hh_agents

##### Export final housing dataframe to geopackage
s.network.get_history('housing_bg_df')[-1].to_file(driver='ESRI Shapefile', filename="result_test.shp")

##### Plot initial population
s.network.get_history('housing_bg_df')[0].plot(column = 'population', cmap='OrRd', legend=True)

##### Plot initial population (with basemap)
df = s.network.get_history('housing_bg_df')[0]
ax = df.plot(column = 'population', cmap='OrRd', alpha=0.8, legend=True)
ctx.add_basemap(ax, source=ctx.providers.Stamen.TonerLite)

##### Plot final population
s.network.get_history('housing_bg_df')[-1].plot(column = 'population', cmap='OrRd', legend=True)

##### Plot population change
gdf = s.network.get_history('housing_bg_df')[-1]  # copy of final bg df
gdf['population_change'] = s.network.get_history('housing_bg_df')[-1]['population'] - s.network.get_history('housing_bg_df')[0]['population']
# normalize color
ax = gdf.plot(column = 'population', cmap='OrRd', alpha=0.8, legend=True)
ctx.add_basemap(ax, source=ctx.providers.Stamen.TonerLite)

##### Plot population change with divergent chloropleth map centered on 0
gdf = s.network.get_history('housing_bg_df')[-1]  # copy of final bg df
gdf['population_change'] = s.network.get_history('housing_bg_df')[-1]['population'] - s.network.get_history('housing_bg_df')[0]['population']
# normalize color
vmin, vmax, vcenter = gdf.population_change.min(), gdf.population_change.max(), 0
norm = TwoSlopeNorm(vmin=vmin, vcenter=vcenter, vmax=vmax)
# create a normalized colorbar
cmap = 'RdBu'
cbar = plt.cm.ScalarMappable(norm=norm, cmap=cmap)
# with normalization
ax = gdf.plot(column='population_change', cmap=cmap, alpha=0.8, norm=norm, legend=True)
ctx.add_basemap(ax, source=ctx.providers.Stamen.TonerLite)

#### Plot initial and final population side-by-side / multi-panel plot example (consistent scale)
# Get min, max, average for color scale
vmin = min(s.network.get_history('housing_bg_df')[0].population.min(), s.network.get_history('housing_bg_df')[-1].population.min())
vmax = min(s.network.get_history('housing_bg_df')[0].population.max(), s.network.get_history('housing_bg_df')[-1].population.max())
vcenter = np.mean([vmin, vmax])
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7))
s.network.get_history('housing_bg_df')[0].plot(column='population', vmin=vmin, vmax=vmax, cmap='OrRd', ax=ax1, legend=True)
s.network.get_history('housing_bg_df')[-1].plot(column='population', vmin=vmin, vmax=vmax, cmap='OrRd', ax=ax2, legend=True)

#### Scatterplot two columns of housing dataframe
df = pd.DataFrame(s.network.housing_bg_df)
df['population_change'] = df['population'] - df['pop1990']
df.plot(x='salesprice1993', y='population_change', style='o')

#### Scatterplot two columns of housing dataframe (with another column providing hues)
import seaborn
df = pd.DataFrame(s.network.housing_bg_df)
df['population_change'] = df['population'] - df['pop1990']
seaborn.relplot(data=df, x='salesprice1993', y='population_change', hue='average_income', aspect=1.61)

#### Scatterplot two columns of housing dataframe (with another column providing hues)
import seaborn
df = pd.DataFrame(s.network.housing_bg_df)
df['population_change_perc'] = (df['population'] - df['pop1990']) / df['pop1990']
seaborn.relplot(data=df, x='perc_fld_area', y='population_change_perc', hue='average_income', aspect=1.61)

#### Scatterplot two columns of housing dataframe (with another column providing hues)
import seaborn
df = pd.DataFrame(s.network.housing_bg_df)
df['price_change'] = df['new_price'] - df['salesprice1993']
seaborn.relplot(data=df, x='perc_fld_area', y='price_change', hue='average_income', aspect=1.61)

#### Plot metric in flood zone threshold over time
import seaborn as sns
column_names = ["Model Year", "Population Percentage Change in Flood Zone", "Flood Coefficient"]
years = []
pop_perc_change = []
price_perc_change = []
fld_coeff = -1000000
fld_coeff_list = []
for t in range(s.network.current_timestep_idx):
    df = s.network.get_history('housing_bg_df')[t]
    df_fld = df[(df.perc_fld_area >= df.perc_fld_area.quantile(.9))]
    pop_perc_change_fld = (df_fld.average_income.sum() - df_fld.mhi1990.sum()) / df_fld.mhi1990.sum()
    years.append(t+1)
    pop_perc_change.append(pop_perc_change_fld)
    fld_coeff_list.append(fld_coeff)
dict = {'Model Year': years,
        'Pop Perc Change Flood Zone': pop_perc_change,
        'Flood Coefficient': fld_coeff_list
        }
df = pd.DataFrame(dict)
df_append = pd.read_csv('temp_flood.csv', index_col=False)  # saved from a separate simulation and loaded in as csv
df = pd.concat([df,df_append],join='inner')
sns.lineplot(x='Model Year',
             y='Pop Perc Change Flood Zone',
             hue='Flood Coefficient',
             data=df)

#### Combine relevant housing dataframes (from each model run year) into a single dataframe and export to csv
first = True
for t in range(s.network.current_timestep_idx):
    df = s.network.get_history('housing_bg_df')[t]
    df = df[['GEOID','GISJOIN','new_price','population','occupied_units','available_units','demand_exceeds_supply',
           'perc_fld_area','mhi1990','salesprice1993','pop1990', 'average_income']]
    df['model_year'] = t+1
    if first:
        df_combined = df
        first = False
    else:
        df_combined = pd.concat([df_combined,df])

#### Read in output dataframe csv files, combine into single dataframe, and plot some results
runs_list = [0, -1000, -10000, -100000, -1000000] # [0, 0.25, 0.5, 0.75, 1.0]
first = True
for run_name in runs_list:
    df = pd.read_csv('./constance_runs/results_utility_simple_flood_utility_' + str(run_name) + '.csv')
    df['run_name'] = run_name
    if first:
        df_combined = df
        first = False
    else:
        df_combined = pd.concat([df_combined, df])
df_combined['flood_zone'] = "Not in Flood Zone"
df_combined.loc[(df_combined.perc_fld_area >= df_combined.perc_fld_area.quantile(.9)), 'flood_zone'] = "In Flood Zone"
# df_fld = df_combined[(df_combined.perc_fld_area >= df_combined.perc_fld_area.quantile(.9))]
# df_fld.loc[df_fld.pop_perc_change=='#DIV/0!', 'pop_perc_change'] = 1
# df_fld.pop_perc_change = df_fld.pop_perc_change.astype(float)
df_combined.loc[df_combined.average_income=='#DIV/0!', 'average_income'] = 1
df_combined.pop_perc_change = df_combined.average_income.astype(float)
import seaborn as sns
import matplotlib.pyplot as plt
fig, ax = plt.subplots()
ax.set_ylim(28000, 50000)
palette = sns.color_palette("mako_r", 5) # mako_r
sns.lineplot(x="model_year", y="average_income", hue="run_name", style="flood_zone", palette=palette, data=df_combined, estimator=np.median, ci = None)
plt.show()

#
runs_list = [0, 0.25, 0.5, 0.75, 1.0]
first = True
for run_name in runs_list:
    df = pd.read_csv('./constance_runs/results_utility_simple_avoidance_utility_' + str(run_name) + '.csv')
    df['run_name'] = run_name
    if first:
        df_combined = df
        first = False
    else:
        df_combined = pd.concat([df_combined, df])
df_fld = df_combined[(df_combined.perc_fld_area >= df_combined.perc_fld_area.quantile(.9))]
df_fld.loc[df_fld.pop_perc_change=='#DIV/0!', 'pop_perc_change'] = 1
df_fld['pop_perc_change'] = df_fld['pop_perc_change'].fillna(1)
df_fld.pop_perc_change = df_fld.pop_perc_change.astype(float)
import seaborn as sns
palette = sns.color_palette("rocket", 5)
sns.lineplot(x="model_year", y="pop_perc_change", hue="run_name", palette=palette, data=df_fld, ci=None)

# Add the text--for each line, find the end, annotate it with a label, and
# adjust the chart axes so that everything fits on.
import matplotlib.pyplot as plt
plt.style.use('ggplot')
fig, ax = plt.subplots()
# repeat sns.lineplot command here again
for line, name in zip(ax.lines, runs_list[::-1]):
    y = line.get_ydata()[-1]
    x = line.get_xdata()[-1]
    if not np.isfinite(y):
        y=next(reversed(line.get_ydata()[~line.get_ydata().mask]),float("nan"))
    if not np.isfinite(y) or not np.isfinite(x):
        continue
    text = ax.annotate(name,
               xy=(x, y),
               xytext=(0, 0),
               color=line.get_color(),
               xycoords=(ax.get_xaxis_transform(),
                 ax.get_yaxis_transform()),
               textcoords="offset points")
    text_width = (text.get_window_extent(
    fig.canvas.get_renderer()).transformed(ax.transData.inverted()).width)
    if np.isfinite(text_width):
        ax.set_xlim(ax.get_xlim()[0], text.xy[0] + text_width * 1.05)

#### Read in output dataframe csv files, combine into single dataframe, and plot some results
runs_list = [0, -500, -1000, -5000, -10000, -50000, -100000, -500000, -1000000, -5000000]

df = pd.read_csv('results_utility_-500000.csv')
df_combined = df
df_fld = df_combined[(df_combined.perc_fld_area >= df_combined.perc_fld_area.quantile(.9))]
df_fld.loc[df_fld.price_perc_change=='#DIV/0!', 'price_perc_change'] = 0
df_fld.pop_perc_change = df_fld.pop_perc_change.astype(float)
import seaborn as sns
sns.lineplot(x="model_year", y="population", hue="GEOID", data=df_combined, ci = None)
sns.lineplot(x="model_year", y="population", data=df_combined.groupby(['GEOID','model_year']).sum().reset_index(), ci = None)
sns.pointplot(data = df.groupby(['Name', 'Year']).mean().reset_index(),
              x='Year', y='Pts', hue='Name')
