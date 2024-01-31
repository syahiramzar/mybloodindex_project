import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from datetime import datetime
import requests
import numpy as np
import seaborn as sns

def myblood_dataviz():

    donations_my = pd.read_csv('/home/ubuntu/refined_df/donations_my.csv')
    donations_my['date'] = pd.to_datetime(donations_my['date'], format='%Y-%m-%d')
    donations_state = pd.read_csv('/home/ubuntu/refined_df/donations_state.csv')
    donations_state['date'] = pd.to_datetime(donations_state['date'], format='%Y-%m-%d')
    returning_donor = pd.read_csv('/home/ubuntu/refined_df/returning_donor.csv')

    daily_2024 = donations_my.loc[donations_my['date'].dt.year == 2024].set_index('date').copy()
    daily_2024['cumsum'] = daily_2024['daily'].cumsum()

    daily_2023 = donations_my.loc[donations_my['date'].dt.year == 2023].set_index('date').copy()
    daily_2023['cumsum'] = daily_2023['daily'].cumsum()

    last_date = daily_2024.index.values[-1]  # find the latest date in datasets
    one_year = np.timedelta64(365, 'D')
    one_yearns = one_year.astype('timedelta64[ns]')
    samedate_lastyear = last_date - one_yearns  # minus one year

    cum_24 = daily_2024['cumsum'].values[-1]  # cumulative values in total 2024 so far
    cum_23 = daily_2023.at[samedate_lastyear, 'cumsum']

    last_value = (daily_2024['daily'].values[-1])
    pctdiff_lastyear = (cum_24 - cum_23) / cum_23 * 100
    pctdiff_yesterday = (last_value - (daily_2024['daily'].values[-2])) / (daily_2024['daily'].values[-2]) * 100

    df_values = pd.DataFrame([[last_date,last_value,pctdiff_yesterday, pctdiff_lastyear]],columns=['last_date','last_value','pctdiff_yesterday','pctdiff_lastyear'])
    df_values.to_csv('/home/ubuntu/key_values.csv', index=False)

    def relative(input):
        if input > 0:
            return "higher"
        if input < 0:
            return "lower"

    # chart 1 - daily donation

    fig1, axs = plt.subplots(nrows=2, figsize=(8, 12), constrained_layout=True)

    axs[0].plot(daily_2024.index, daily_2024['daily'])
    axs[0].set_title(f'(C1) 2024 Malaysia Blood Donation Index, as of {str(last_date)[:10]}: \n New daily donations = {last_value}, ({pctdiff_yesterday:.2f}% {relative(pctdiff_yesterday)} than the previous day)')

    axs[1].plot(daily_2024.index, daily_2024['cumsum'])
    axs[1].set_title(f'Cumulative Daily Donations \n As of {str(last_date)[:10]}: {cum_24}, \u2248 {pctdiff_lastyear:.2f}% {relative(pctdiff_lastyear)} than last year (same date)')

    def my_format_function(x, pos=None):
        x = mdates.num2date(x)
        if pos == 0:
            fmt = '%d\n%b\n%Y'
        else:
            fmt = '%d'
        label = x.strftime(fmt)

        return label
    formatter = my_format_function

    for ax in axs.flat:
        ax.xaxis.set_major_formatter(formatter)
        ax.xaxis.set_minor_locator(mdates.DayLocator())
        ax.xaxis.set_minor_formatter(mdates.DateFormatter('%d'))

    fig1.savefig('/home/ubuntu/plots/chart1.png', bbox_inches='tight')

    # chart 2 - 2024 new+returning donor by state

    state_2024 = donations_state.loc[donations_state['date'].dt.year == 2024].set_index('date').copy()
    state_donor = state_2024.loc[:, ['state', 'daily', 'donations_new', 'donations_returning', 'year']]
    state_donor_grp = state_donor.groupby(['state', 'year']).sum().sort_values(by=['daily'], ascending=False).reset_index().set_index('state')

    donor_state_bar = state_donor_grp.loc[:, ['donations_new', 'donations_returning']].copy()
    donor_state_bar.rename(columns={'donations_new': 'New Donors','donations_returning': 'Returning Donors'}, inplace=True)

    fig2, ax = plt.subplots(figsize=(35,25))

    bottom = np.zeros(len(donor_state_bar))
    for i, col in enumerate(donor_state_bar.columns):
      ax.bar(donor_state_bar.index, donor_state_bar[col], bottom=bottom, label=col)
      bottom += np.array(donor_state_bar[col])

    totals = donor_state_bar.sum(axis=1)

    y_offset = 50
    for i, total in enumerate(totals):
      ax.text(totals.index[i], total + y_offset, round(total), ha='center', weight='bold',size=25)

    y_offset = -250
    for bar in ax.patches:
      ax.text(
          bar.get_x() + bar.get_width() / 2,
          bar.get_height() + bar.get_y() + y_offset,
          round(bar.get_height()),
          ha='center', color='w', weight='bold', size=22 )

    ax.text(totals.index[7], totals['W.P. Kuala Lumpur'] * 0.6, f'* Data updated as of {str(last_date)[:10]}. \n'
                                                                 f'\n'
                                                                 f'** The data for W.P. Kuala Lumpur may be higher than \n'
                                                                 f'the actual donor counts (and Selangor lower) due to \n'
                                                                 f'data from mobile campaigns around Selangor and \n'
                                                                 f'Putrajaya being recorded as data for W.P. Kuala Lumpur.',size=26)

    ax.text(totals.index[7], totals['W.P. Kuala Lumpur'] * 0.45, f'*** Red colored text represents daily new donations:\n'
                                                                 f'T = total new donations ({str(last_date)[:10]}),\n'
                                                                 f'N = from new donors,\n'
                                                                 f'R = from returning donors', size=26, color='r')

    temp_latest_donor = state_2024.loc[last_date, ['state', 'daily', 'donations_new', 'donations_returning']].reset_index().set_index('state')
    temp_latest_donor.drop(columns=['date'], inplace=True)
    latest_donor = temp_latest_donor.reindex(donor_state_bar.index)

    for label, row in latest_donor.iterrows():
        total = row.iloc[0]
        new = row.iloc[1]
        returning = row.iloc[2]
        ax.text(label, totals[label] + 1300, f'T = +{total}', ha='center', weight='bold', color='r', size=22)
        ax.text(label, totals[label] + 1000, f'(N = +{new},', ha='center', color='r', size=22)
        ax.text(label, totals[label] + 700, f'R = +{returning})', ha='center', color='r', size=22)

    ax.set_title('(C2) 2024 : Cumulative Daily Blood Donations (by States)', fontsize=40)
    ax.legend(fontsize=30)
    ax.tick_params(axis='both', labelsize=20)
    ax.set_ylim(0, totals['W.P. Kuala Lumpur']+2000)

    fig2.savefig('/home/ubuntu/plots/chart2.png', bbox_inches='tight')

    # chart 3 - trends over the years

    temp_yearly_my = donations_my.loc[:, ['date', 'daily']].copy().set_index('date')
    monthly_my = temp_yearly_my.resample('MS').sum()
    yearly_my = temp_yearly_my.resample('YS').sum()

    fig3, axs = plt.subplots(nrows=2, ncols=1, figsize=(20,8), sharex=True)
    axs[0].plot(monthly_my.index, monthly_my['daily'])
    axs[1].plot(yearly_my.index, yearly_my['daily'])
    axs[0].xaxis.set_minor_formatter(mdates.DateFormatter('%Y'))
    for ax in axs.flat:
        ax.grid(which='both', axis='x', linestyle='--')
        ax.xaxis.set_minor_locator(mdates.YearLocator())

    temp_lowest = monthly_my.copy().reset_index()
    temp_lowest['year'] = temp_lowest['date'].dt.year
    temp_lowest2 = temp_lowest[['daily', 'year']].groupby('year').min().reset_index()
    temp_lowest2['marker'] = 1

    temp_lowest3 = pd.merge(temp_lowest, temp_lowest2, on=['year', 'daily'], how='left')
    lowest_month_inyear = temp_lowest3[(temp_lowest3['marker']) == 1][temp_lowest.columns].reset_index()
    lowest_month_inyear['month'] = lowest_month_inyear['date'].dt.strftime("%b")

    axs[0].scatter(lowest_month_inyear['date'],lowest_month_inyear['daily'], c='red')
    axs[0].axvline(pd.Timestamp('2020-03-01'), color='r', linestyle='--', alpha=0.4)
    axs[0].axvline(pd.Timestamp('2021-11-01'), color='r', linestyle='--', alpha=0.4)
    axs[0].text(x=pd.Timestamp('2020-03-01'), y=-4000, s='C-19 MCO\nStart', fontdict=dict(color='red', size=8), horizontalalignment='center')
    axs[0].text(x=pd.Timestamp('2021-11-01'), y=-4000, s='C-19 MCO\nEnd', fontdict=dict(color='red', size=8), horizontalalignment='center')

    axs[0].set_ylim(2000)


    for i in range(lowest_month_inyear.shape[0]):
     axs[0].text(x=lowest_month_inyear.date[i], y=lowest_month_inyear.daily[i]-3000, s=lowest_month_inyear.month[i],
              fontdict=dict(color='black', size=9))

    axs[0].set_title(f'(C3) Malaysia Blood Donation Trend, as of {str(last_date)[:10]}: \n \nMonthly trend', loc='left')
    axs[1].set_title(f'Yearly trend', loc='left')

    fig3.savefig('/home/ubuntu/plots/chart3.png', bbox_inches='tight')

    # chart 4 - stacked bar

    temp_bar = donations_state.groupby(['year', 'state'])  # temp df
    temp_bar2 = temp_bar['daily'].sum().reset_index()

    color = px.colors.qualitative.Prism
    color.extend(['rgb(239, 85, 59)', 'rgb(0, 204, 150)'])
    color_state = dict(zip(temp_bar2["state"].unique(), color)) #set each state with unique color

    pivot_c4s = pd.pivot_table(temp_bar2, values='daily', index='year', columns=['state'])
    fig4 = px.bar(pivot_c4s, x=pivot_c4s.index, y=pivot_c4s.columns, color='state', color_discrete_map=color_state,
                  barmode="stack", title=f'(C4) Malaysia Total Yearly Blood Donation (by States): 2006-Current',
                  labels={"value": "Total", "year": "Year", "state": "State"}, width=2000, height=1300)
    fig4.update_layout(font=dict(size=19),
                       legend=dict(traceorder="reversed", yanchor="top", y=0.7, xanchor="left", x=1.01,
                                   font=dict(size=20, color="black")))

    fig4.add_annotation(x=0.03, y=0.95, xref='paper', yref='paper', xanchor='left', yanchor='top', align='left',
                        showarrow=False, font=dict(size=18, color="black"), bgcolor="white", opacity=0.85,
                        text=f'a) Data updated as of {str(last_date)[:10]}.'
                             f'<br><br>b) No data recorded for Pulau Pinang prior to 2014.'
                             f'<br><br>c) Total donations for Kelantan in 2017 (not visible) is 35.'
                             f'<br><br>d) Total donations for Perak in 2006 & 2007 (not visible) is 53.'
                             f'<br><br>e) Refer C2 for in-depth year 2024.')

    fig4.write_html("/home/ubuntu/plots/chart4.html")
    fig4.write_image("/home/ubuntu/plots/chart4.png")

    #chart 5

    temp_bar3 = donations_state.groupby(['state'])  # temp df
    state_total = temp_bar3[['daily', 'donations_returning']].sum().reset_index()
    state_total['state_proportion_total'] = state_total['daily'] / state_total['daily'].sum() * 100
    state_total['color'] = color
    state_total.rename(columns={'daily':'total_donations'}, inplace=True)
    state_total.sort_values('state_proportion_total', ascending=False, inplace=True)
    color1 = state_total['color'].tolist()


    state_total['returning_don_pct'] = state_total['donations_returning'] / state_total['total_donations'] * 100
    state_pctreturning_bar = state_total[['state', 'returning_don_pct', 'color']]

    fig5 = make_subplots(rows=1, cols=2, specs=[[{}, {}]], shared_xaxes=False, shared_yaxes=True, horizontal_spacing=0)

    fig5.add_trace(go.Bar(x=state_total['state_proportion_total'],
                         y=state_total['state'],
                         text=state_total['state_proportion_total'].map('{:,.2f}'.format),
                         textposition='inside',
                         orientation='h',
                         width=0.7,
                         showlegend=False,
                         marker_color = color1),
                         1, 1) # 1,1 represents row 1 column 1 in the plot grid

    fig5.add_trace(go.Bar(x=state_pctreturning_bar['returning_don_pct'],
                         y=state_pctreturning_bar['state'],
                         text=state_pctreturning_bar['returning_don_pct'].map('{:,.2f}'.format),
                         textposition='inside',
                         orientation='h',
                         width=0.7,
                         showlegend=False,
                         marker_color = color1),
                         1, 2) # 1,2 represents row 1 column 2 in the plot grid

    fig5.update_xaxes(showticklabels=True,title_text="State % Proportion (Based on Total Donations in Malaysia)", row=1, col=1, range=[40,0])
    fig5.update_xaxes(showticklabels=True,title_text="% of Returning Donors (Based on Total Donations in Each State)", row=1, col=2)

    fig5.add_annotation(x=0, y=1.02, xref='paper', yref='paper', xanchor='left', yanchor='top', align='left',
                        showarrow=False, font=dict(size=15, color="black"),
                        text=f'<b>Data updated as of {str(last_date)[:10]}.</b>')

    fig5.update_layout(title_text="(C5) Malaysia Total Donations (by State): 2006-Current",
                      width=1500,
                      height=1200,
                      font=dict(size=14),
                      title_x=0.5,
                      xaxis1={'side': 'bottom'},
                      xaxis2={'side': 'bottom'},)

    fig5.write_image("/home/ubuntu/plots/chart5.png")

    # chart 6 - heatmap of returning donors based on group age (first visited)

    returning_age_grp = returning_donor.groupby(by=["age_group_first_visit", "visit_freq"]).size().reset_index()
    returning_age_grp['pct'] = returning_age_grp[0] / len(returning_donor['donor_id']) * 100
    returning_age_grp.rename(columns={0: 'amount'}, inplace=True)
    returning_age_grp["visit_freq"] = returning_age_grp["visit_freq"].astype(pd.api.types.CategoricalDtype(categories=["11-higher", "9-11", "6-8", "3-5", "2"]))
    pivot_c6 = pd.pivot_table(returning_age_grp, values='pct', index='visit_freq', columns='age_group_first_visit', observed=False)

    sns.set(font_scale=1.3)
    fig6, ax = plt.subplots(figsize=(20,12))
    ax = sns.heatmap(pivot_c6, cmap="crest", annot=True, fmt=".2", linewidth=.5)
    ax.set(xlabel='Donor Age Group (When First Visited)', ylabel='Total Visits')
    ax.set_title(f'(C6) Heatmap of Returning Donors (Based on Age When Started Donating):\n'
                 f'2013-Current (Data updated as of {str(last_date)[:10]})\n\n'
                 f'% calculated based on total "returning donors" (person who has donated at least twice)', loc = "center")

    fig6.savefig('/home/ubuntu/plots/chart6.png', bbox_inches='tight')

    # chart 7 - heatmap of returning donors based on group age (current age)

    returning_age_grp2 = returning_donor.groupby(by=["age_group_current", "visit_freq"]).size().reset_index()
    returning_age_grp2['pct'] = returning_age_grp2[0] / len(returning_donor['donor_id']) * 100
    returning_age_grp2.rename(columns={0: 'amount'}, inplace=True)
    returning_age_grp2["visit_freq"] = returning_age_grp2["visit_freq"].astype(pd.api.types.CategoricalDtype(categories=["11-higher", "9-11", "6-8", "3-5", "2"]))
    pivot_c7 = pd.pivot_table(returning_age_grp2, values='pct', index='visit_freq', columns='age_group_current', observed=False)

    sns.set(font_scale=1.3)
    fig7, ax = plt.subplots(figsize=(20,12))
    ax = sns.heatmap(pivot_c7, cmap=sns.cubehelix_palette(as_cmap=True), annot=True, fmt=".2", linewidth=.5)
    ax.set(xlabel='Donor Age Group (Current Age)', ylabel='Total Visits')
    ax.set_title(f'(C7) Heatmap of Returning Donors (Based on Current Age):\n'
                 f'2013-Current (Data updated as of {str(last_date)[:10]})\n\n'
                 f'% calculated based on total "returning donors" (person who has donated at least twice)', loc = "center")

    fig7.savefig('/home/ubuntu/plots/chart7.png', bbox_inches='tight')