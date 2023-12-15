import yfinance as yf
import streamlit as st
from assistant_methods import get_account, get_account_portfolio_history, get_account_configurations, get_all_positions, \
    get_all_order, create_order, get_historical_bars, get_historical_quotes, get_news_articles, coder
import plotly.graph_objs as go
from assistant import InvestmentAdvisor, files
from datetime import datetime, timedelta
from execbox import execbox
import pandas as pd


def format_number(number):
    try:
        number = float(number)
        if number >= 1_000_000_000_000:
            return f"${number / 1_000_000_000_000:.2f}T"
        elif number >= 1_000_000_000:
            return f"${number / 1_000_000_000:.2f}B"
        elif number >= 1_000_000:
            return f"${number / 1_000_000:.2f}M"
        elif number >= 1_000:
            return f"${number / 1_000:.2f}K"
        elif 0 < number < 1:
            return f"{number * 100:.2f}%"
        else:
            return f"${number:.2f}"
    except (ValueError, TypeError):
        return "N/A"


def home_search():
    get_news_articles(start=None, end=None, sort='desc', symbols=None, limit=10, include_content=False,
                      exclude_contentless=False, page_token=None)

    with st.expander("Search", expanded=False):
        with st.form("input_form"):
            symbols = st.text_input('Enter stock symbol (e.g., AAPL)', max_chars=10)
            submitted = st.form_submit_button("Submit")

        if submitted:
            # Set the start date to the first day of the current year
            start_datey = datetime(datetime.now().year, 1, 1).date()
            start_datem = datetime.now().date() - timedelta(days=30)
            start_datew = datetime.now().date() - timedelta(days=7)
            start_datewn = datetime.now().date() - timedelta(days=1)
            # Set the end date to today's date
            end_date = datetime.now().date()

            # Fetch the data
            datay = get_historical_bars(symbols=symbols, timeframe='1M', start=start_datey, end=end_date, limit=1000,
                                        adjustment=None, raw=None, feed="iex", currency="USD")

            df = datay
            df.index = pd.to_datetime(df.index)  # Convert the 't' column to datetime for proper plotting

            # Create the candlestick chart
            fig = go.Figure(data=[go.Candlestick(x=df.index,
                                                 open=df['Open'],
                                                 high=df['High'],
                                                 low=df['Low'],
                                                 close=df['Close'])])
            # __________________________________________________________________________________________________________________
            # Customize the layout to match the screenshot
            fig.update_layout(title=f'Candlestick Chart for {symbols}', xaxis_title='Date', yaxis_title='Price',
                              xaxis_rangeslider_visible=False, height=300, width=800)

            datam = get_historical_bars(symbols=symbols, timeframe='16H', start=start_datem, end=end_date, limit=1000,
                                        adjustment=None, raw=None, feed="iex", currency="USD")

            df = datam
            df.index = pd.to_datetime(df.index)  # Convert the 't' column to datetime for proper plotting

            # Create the candlestick chart
            fig1 = go.Figure(data=[go.Candlestick(x=df.index,
                                                  open=df['Open'],
                                                  high=df['High'],
                                                  low=df['Low'],
                                                  close=df['Close'])])

            # Customize the layout to match the screenshot
            fig1.update_layout(title=f'Candlestick Chart for {symbols}', xaxis_title='Date', yaxis_title='Price',
                               xaxis_rangeslider_visible=False, height=300, width=800)
            # ___________________________________________________________________________________________________________________

            dataw = get_historical_bars(symbols=symbols, timeframe='8H', start=start_datew, end=end_date, limit=1000,
                                        adjustment=None, raw=None, feed="iex", currency="USD")

            df = dataw
            df.index = pd.to_datetime(df.index)  # Convert the 't' column to datetime for proper plotting

            # Create the candlestick chart
            fig2 = go.Figure(data=[go.Candlestick(x=df.index,
                                                  open=df['Open'],
                                                  high=df['High'],
                                                  low=df['Low'],
                                                  close=df['Close'])])

            # Customize the layout to match the screenshot
            fig2.update_layout(title=f'Candlestick Chart for {symbols}', xaxis_title='Date', yaxis_title='Price',
                               xaxis_rangeslider_visible=False, height=300, width=800)
            # ___________________________________________________________________________________________________________________
            stock = get_historical_bars(symbols=symbols, timeframe='15Min', start=start_datewn, end=None, limit=1000,
                                        adjustment=None, raw=None, feed="iex", currency="USD")

            df = stock
            df.index = pd.to_datetime(df.index)  # Convert the 't' column to datetime for proper plotting

            # Create the candlestick chart
            fig3 = go.Figure(data=[go.Candlestick(x=df.index,
                                                  open=df['Open'],
                                                  high=df['High'],
                                                  low=df['Low'],
                                                  close=df['Close'])])

            # Customize the layout to match the screenshot
            fig3.update_layout(title=f'Candlestick Chart for {symbols}', xaxis_title='Date', yaxis_title='Price',
                               xaxis_rangeslider_visible=False, height=300, width=800)

            # ____________________________________________________________________________________________________________________
            news = get_news_articles(start=start_datewn, end=None, sort='desc', symbols=None, limit=50,
                                     include_content=True,
                                     exclude_contentless=False, page_token=None)
            # Convert news data to DataFrame
            news_df = pd.DataFrame(news['news'])

            # Adding a column for combined headline and URL in Markdown format
            news_df['headline_link'] = news_df.apply(lambda row: f"[{row['headline']}]({row['url']})", axis=1)

            # Display the clickable links in Streamlit, 3 at a time
            st.write("### News Articles")
            for i in range(0, len(news_df), 3):
                batch = news_df['headline_link'].iloc[i:i + 3]
                for link in batch:
                    st.markdown(link, unsafe_allow_html=True)

                # Check if there are more articles to display
                if i + 3 < len(news_df):
                    if st.button(f'Show more news', key=i):
                        continue
                    else:
                        break
            # ___________________________________________________________________________________________________________________
            stock = yf.Ticker(symbols)
            stock = stock.info
            # Create 7 columns
            colm1, colm2, colm3, colm4, colm5, colm6, colm7 = st.columns(7)

            with colm1:
                st.markdown(f"###### Cap: {format_number(stock.get('marketCap', 'N/A'))}")
                st.markdown(f"###### Value: {format_number(stock.get('enterpriseValue', 'N/A'))}")

            with colm2:
                st.markdown(f"###### Trailing PE: {stock.get('trailingPE', 'N/A')}")
                st.markdown(f"###### Forward PE: {stock.get('forwardPE', 'N/A')}")

            with colm3:
                st.markdown(f"###### Previous Close: {format_number(stock.get('previousClose', 'N/A'))}")
                st.markdown(f"###### Open: {format_number(stock.get('open', 'N/A'))} ")

            with colm4:
                st.markdown(f"###### Day Low: {format_number(stock.get('dayLow', 'N/A'))}")
                st.markdown(f"###### Day High: {format_number(stock.get('dayHigh', 'N/A'))}")

            with colm5:
                st.markdown(f"###### Profit Margins: {format_number(stock.get('profitMargins', 'N/A'))}")
                st.markdown(f"###### Trailing PEG Ratio: {stock.get('trailingPegRatio', 'N/A')}")

            with colm6:
                st.markdown(f"###### 52 Week Low: {format_number(stock.get('fiftyTwoWeekLow', 'N/A'))}")
                st.markdown(f"###### 52 Week High: {format_number(stock.get('fiftyTwoWeekHigh', 'N/A'))}")

            with colm7:
                st.markdown(f"###### Volume: {format_number(stock.get('volume', 'N/A'))}")
                st.markdown(f"###### Average Volume: {format_number(stock.get('averageVolume', 'N/A'))}")

            with st.container():
                tab1, tab2, tab3, tab4 = st.tabs(['Year', 'Month', 'Week', 'Day'])
                with tab1:
                    st.plotly_chart(fig, use_container_width=True)
                with tab2:
                    st.plotly_chart(fig1, use_container_width=True)
                with tab3:
                    st.plotly_chart(fig2, use_container_width=True)
                with tab4:
                    st.plotly_chart(fig3, use_container_width=True)

            colmu1, colmu2 = st.columns(2)
            with colmu1:
                st.write(f"###### Gross Profits: {format_number(stock.get('grossProfits', 'N/A'))}")
                st.write(f"###### Free Cashflow: {format_number(stock.get('freeCashflow', 'N/A'))} ")
                st.write(f"###### Operating Cashflow: {format_number(stock.get('operatingCashflow', 'N/A'))}")
                st.write(f"###### Earnings Growth: {format_number(stock.get('earningsGrowth', 'N/A'))}")

            with colmu2:
                st.write(f"###### Revenue Growth: {format_number(stock.get('revenueGrowth', 'N/A'))}")
                st.write(f"###### Gross Margins: {format_number(stock.get('grossMargins', 'N/A'))}")
                st.write(f"###### EBITDA Margins: {format_number(stock.get('ebitdaMargins', 'N/A'))}")
                st.write(f"###### Operating Margins: {format_number(stock.get('operatingMargins', 'N/A'))}")

            st.write('___')

            colms1, colms2, colms3, colms4, colms5, = st.columns(5)

            with colms1:
                st.write('Audit Risk')
                st.write(f"{stock.get('auditRisk', 'N/A')}")

            with colms2:
                st.write('Board Risk')
                st.write(f"{stock.get('boardRisk', 'N/A')}")

            with colms3:
                st.write('Compensation Risk')
                st.write(f"{stock.get('compensationRisk', 'N/A')}")

            with colms4:
                st.write('Shareholder Rights Risk')
                st.write(f"{stock.get('shareHolderRightsRisk', 'N/A')}")

            with colms5:
                st.write('Overall Risk')
                st.write(f"{stock.get('overallRisk', 'N/A')}")
            st.write('___')

            co1, co2, = st.columns(2)
            with co1:
                st.write(
                    f"Address: {stock.get('address1', 'N/A')}, {stock.get('city', 'N/A')}, {stock.get('state', 'N/A')} {stock.get('zip', 'N/A')}")
                st.write(f"Full Time Employees: {stock.get('fullTimeEmployees', 'N/A')}")
                st.write(f"Phone: {stock.get('phone', 'N/A')}")

            with co2:
                st.write(f"Website: {stock.get('website', 'N/A')}")
                st.write(f"Industry: {stock.get('industry', 'N/A')}")
                st.write(f"Sector: {stock.get('sector', 'N/A')}")
            st.write("---")

            st.markdown("<h3 style='text-align: center;'>Business Summary</h3>", unsafe_allow_html=True)
            st.write(stock.get('longBusinessSummary', 'N/A'))
            st.write("---")

            st.markdown("<h3 style='text-align: center;'>Company Leadership</h3>", unsafe_allow_html=True)
            company_officers = stock.get('companyOfficers', [])
            if company_officers:
                for officer in company_officers:
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write(f"**{officer.get('title', 'N/A')}:**")
                        st.write(f"**{officer.get('name', 'N/A')}**")
                    with col2:
                        st.write(f"- Age: {officer.get('age', 'N/A')}")
                        st.write(f"- Year Born: {officer.get('yearBorn', 'N/A')}")
                    with col3:
                        st.write(f"- Fiscal Year: {officer.get('fiscalYear', 'N/A')}")
                        st.write(f"- Total Pay: {officer.get('totalPay', 'N/A')} USD")

                    col4, col5 = st.columns(2)
                    with col4:
                        st.write(f"- Exercised Value: {officer.get('exercisedValue', 'N/A')} USD")
                    with col5:
                        st.write(f"- Unexercised Value: {officer.get('unexercisedValue', 'N/A')} USD")
                    st.write("---")  # Separator line for readability
            else:
                st.write("No company leadership data available.")


def display_quotes_data():
    with st.expander("Search Quotes", expanded=False):
        with st.form("input"):
            symbol = st.text_input('Enter stock symbol (e.g., AAPL)', max_chars=10)
            start_date = st.date_input('Start date')
            end_date = st.date_input('End date')
            submitted = st.form_submit_button("Submit")

        if submitted:
            # Fetch auction data
            auction_data = get_historical_quotes(symbols=symbol, start=start_date, end=end_date)

            # Check if 'quotes' key and the specific symbol are present in the data
            if 'quotes' in auction_data and symbol in auction_data['quotes']:
                processed_data = []
                for record in auction_data['quotes'][symbol]:
                    # Process each record
                    # Example: Extracting ask price, bid price, and timestamp
                    processed_data.append({
                        'Ask Price': record.get('ap', None),
                        'Bid Price': record.get('bp', None),
                        'Timestamp': pd.to_datetime(record.get('t', '')).strftime('%Y-%m-%d %H:%M:%S'),
                        'Auction trade size': record.get('s', None)
                        # Add more fields as needed
                    })

                df = pd.DataFrame(processed_data)
                st.dataframe(df)
            else:
                st.error(f"No quote data available for symbol '{symbol}'.")


def display_order_data(order_data):
    # Define the columns you expect to display
    expected_columns = ['symbol', 'qty', 'filled_qty', 'filled_avg_price', 'order_type', 'side', 'status', 'created_at']

    # Create a DataFrame from the data
    df = pd.DataFrame.from_records(order_data, columns=expected_columns)

    # Handling missing columns
    missing_columns = [col for col in expected_columns if col not in df.columns]
    if missing_columns:
        print(f"Warning: Missing columns in the data: {missing_columns}")

    # Display the DataFrame in the app
    st.dataframe(df)


def convert_timestamps(timestamps):
    return [datetime.fromtimestamp(ts) for ts in timestamps]


def format_change(change):
    """Format the change in price as a percentage with appropriate color."""
    change_percent = float(change) * 100
    color = "red" if change_percent < 0 else "green"
    return f'<span style="color: {color};">{change_percent:.2f}%</span>'


def display_account_data():
    st.markdown(f"<h2 style='text-align: center;'>Portfolio Management</h2>", unsafe_allow_html=True)

    # Account data retrieval would be done here
    account_data = get_account()
    config = get_account_configurations()
    all_open_pos = get_all_positions()
    account_his_m = get_account_portfolio_history(period="3M", timeframe="1D")
    account_his_d = get_account_portfolio_history(period="1D", timeframe="1Min")
    account_his_w = get_account_portfolio_history(period="1W", timeframe="15Min")
    # Convert timestamps to readable dates for plotting
    dates_w = convert_timestamps(account_his_w['timestamp'])
    dates_m = convert_timestamps(account_his_m['timestamp'])
    dates_d = convert_timestamps(account_his_d['timestamp'])

    # Create DataFrames for the portfolio history
    df_w = pd.DataFrame({
        'Date': dates_w,
        'Equity': account_his_w['equity'],
        'Profit/Loss': account_his_w['profit_loss']
    }).set_index('Date')

    df_m = pd.DataFrame({
        'Date': dates_m,
        'Equity': account_his_m['equity'],
        'Profit/Loss': account_his_m['profit_loss']
    }).set_index('Date')

    df_d = pd.DataFrame({
        'Date': dates_d,
        'Equity': account_his_d['equity'],
        'Profit/Loss': account_his_d['profit_loss']
    }).set_index('Date')

    col1, col2, col3, col4, = st.columns(4)
    with col1:
        st.markdown(
            f"<div style='text-align: center;'><span style='font-size: 0.75em;'>Equity</span><br><span style='font-size: 1.25em;'>${account_data['equity']}</span></div>",
            unsafe_allow_html=True)
    with col2:
        st.markdown(
            f"<div style='text-align: center;'><span style='font-size: 0.75em;'>Buying Power</span><br><span style='font-size: 1.25em;'>${account_data['buying_power']}</span></div>",
            unsafe_allow_html=True)
    with col3:
        st.markdown(
            f"<div style='text-align: center;'><span style='font-size: 0.75em;'>Initial Margin</span><br><span style='font-size: 1.25em;'>${account_data['initial_margin']}</span></div>",
            unsafe_allow_html=True)
    with col4:
        st.markdown(
            f"<div style='text-align: center;'><span style='font-size: 0.75em;'>Maintenance Margin</span><br><span style='font-size: 1.25em;'>${account_data['maintenance_margin']}</span></div>",
            unsafe_allow_html=True)

    with st.expander("Account Overview", expanded=False):
        metrics_html = f"""
               <style>
                   .metric {{ display: flex; flex-direction: column;  }}
                   .metric .label {{ font-size: 0.75em; }}
                   .metric .value {{ font-size: 1.25em; }}
               </style>
               <div class="metric">
                   <span class="label">Account Number</span>
                   <span class="value">{account_data['account_number']}</span>
               </div>
               <div class="metric">
                   <span class="label">Status</span>
                   <span class="value">{account_data['status']}</span>
               </div>
               <div class="metric">
                   <span class="label">Pattern Day Trader</span>
                   <span class="value">{"Yes" if account_data['pattern_day_trader'] else "No"}</span>
               </div>
               <div class="metric">
                   <span class="label">Shorting Enabled</span>
                   <span class="value">{"Yes" if account_data['shorting_enabled'] else "No"}</span>
               </div>
               <div class="metric">
                   <span class="label">DTBP Check</span>
                   <span class="value">{config['dtbp_check']}</span>
                </div>
               <div class="metric">
                   <span class="label">Trade Confirm Email</span>
                   <span class="value">{config['trade_confirm_email']}</span>
                </div>
               <div class="metric">
                   <span class="label">Suspend Trade </span>
                   <span class="value">{config['suspend_trade']}</span>
               </div>
               <div class="metric">
                   <span class="label">No Shorting</span>
                   <span class="value">{config['no_shorting']}</span>
               </div>
               <div class="metric">
                   <span class="label">Fractional Trading</span>
                   <span class="value">{config['fractional_trading']}</span>
                </div>
               <div class="metric">
                   <span class="label">Max Margin Multiplier  </span>
                   <span class="value">{config['max_margin_multiplier']}</span>
                </div>
               <div class="metric">
                   <span class="label">pdt_check</span>
                   <span class="value">{config['pdt_check']}</span> 
                </div>
               <div class="metric">
                   <span class="label">PTP No Exception Entry</span>
                   <span class="value">{config['ptp_no_exception_entry']}</span>
               """
        st.markdown(metrics_html, unsafe_allow_html=True)

    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=df_d.index, y=df_d['Equity'], mode='lines', name='Equity'))
    fig1.update_layout(
        plot_bgcolor='black',
        xaxis=dict(
            showline=True,
            showgrid=True,
            showticklabels=True,
            linecolor='rgb(204, 204, 204)',
            linewidth=2,
            ticks='outside',
            tickfont=dict(
                family='Arial',
                size=12,
                color='rgb(204, 204, 204)',
            ),
        ),
        yaxis=dict(
            showgrid=True,
            zeroline=True,
            showline=True,
            showticklabels=True,
        ),
        autosize=True,
        margin=dict(
            autoexpand=True,
            l=100,
            r=20,
            t=110,
        ),
        showlegend=True
    )

    # Hiding x-axis ticks and labels
    fig1.update_xaxes(showticklabels=True)

    # Hiding y-axis ticks and labels
    fig1.update_yaxes(showticklabels=True)

    # Plotting the equity chart using Plotly for a more customized look
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_m.index, y=df_m['Equity'], mode='lines', name='Equity'))
    fig.update_layout(
        plot_bgcolor='black',
        xaxis=dict(
            showline=True,
            showgrid=True,
            showticklabels=True,
            linecolor='rgb(204, 204, 204)',
            linewidth=2,
            ticks='outside',
            tickfont=dict(
                family='Arial',
                size=12,
                color='rgb(204, 204, 204)',
            ),
        ),
        yaxis=dict(
            showgrid=True,
            zeroline=True,
            showline=True,
            showticklabels=True,
        ),
        autosize=True,
        margin=dict(
            autoexpand=True,
            l=100,
            r=20,
            t=110,
        ),
        showlegend=True
    )

    # Hiding x-axis ticks and labels
    fig.update_xaxes(showticklabels=True)

    # Hiding y-axis ticks and labels
    fig.update_yaxes(showticklabels=True)

    # Plotting the equity chart using Plotly for a more customized look
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(x=df_w.index, y=df_w['Equity'], mode='lines', name='Equity'))
    fig3.update_layout(
        plot_bgcolor='black',
        xaxis=dict(
            showline=True,
            showgrid=True,
            showticklabels=True,
            linecolor='rgb(204, 204, 204)',
            linewidth=2,
            ticks='outside',
            tickfont=dict(
                family='Arial',
                size=12,
                color='rgb(204, 204, 204)',
            ),
        ),
        yaxis=dict(
            showgrid=True,
            zeroline=True,
            showline=True,
            showticklabels=True,
        ),
        autosize=True,
        margin=dict(
            autoexpand=True,
            l=100,
            r=20,
            t=110,
        ),
        showlegend=True
    )

    # Hiding x-axis ticks and labels
    fig3.update_xaxes(showticklabels=True)

    # Hiding y-axis ticks and labels
    fig3.update_yaxes(showticklabels=True)

    # Creating tabs for daily, monthly, and yearly charts

    tab1, tab2, tab3 = st.tabs(["Daily", "Weekly", "Monthly"])
    with tab1:
        st.plotly_chart(fig1, use_container_width=True)
    with tab2:
        st.plotly_chart(fig3, use_container_width=True)
    with tab3:
        st.plotly_chart(fig, use_container_width=True)

    # Convert your positions data to a pandas DataFrame
    df = pd.DataFrame(all_open_pos)
    with st.expander("All Open Positions", expanded=False):
        st.dataframe(df)

    df = df.drop(
        columns=['asset_id', 'exchange', 'asset_class', 'asset_marginable', 'unrealized_plpc', 'unrealized_intraday_pl',
                 'unrealized_intraday_plpc', 'qty_available', 'lastday_price'])

    # Rename columns to match the desired headers
    df.rename(columns={
        'symbol': 'Asset',
        'current_price': 'Price',
        'qty': 'Quantity',
        'market_value': 'Market Value',
        'cost_basis': 'Cost Basis',
        'unrealized_pl': 'Total Profit',
        'change_today': 'Change',
        'avg_entry_price': 'Avg. Price',
    }, inplace=True)

    # Format the 'Change' column first before combining
    df['Change'] = df['Change'].apply(format_change)

    # Combine 'Asset' and 'Change' into one column
    df['Assets'] = df.apply(lambda x: f"{x['Asset']} {x['Change']}", axis=1)

    # Now you can drop the original 'Asset' and 'Change' columns if they are not needed
    df.drop(['Asset', 'Change'], axis=1, inplace=True)

    # Define the new column order with 'Assets' as the first column
    column_order = ['Assets', 'Price', 'Avg. Price', 'Total Profit', 'Market Value', 'Cost Basis', 'Quantity']
    df = df[column_order]

    # Display the DataFrame as a table in Streamlit using markdown for HTML rendering
    st.markdown(df.to_html(escape=False), unsafe_allow_html=True)

    # Assuming orders is a DataFrame with the data
    orders = pd.DataFrame(get_all_order('all'))

    # Renaming columns as per the mapping
    orders.rename(columns={
        'symbol': 'Asset',
        'order_type': 'Order',  # or 'side' if that's what is meant by 'Order'
        'qty': 'Quantity',
        'filled_avg_price': 'Average Cost',
        'notional': 'Notional',
        # 'amount': 'Amount', # Assuming you have logic to calculate 'Amount'
        'status': 'Status'
    }, inplace=True)

    # Selecting only the required columns
    orders = orders[['Asset', 'Order', 'Quantity', 'Average Cost', 'Notional', 'Status']]

    selected_columns = ['Asset', 'Order', 'Quantity', 'Average Cost', 'Notional', 'Status']  # Add 'Amount' if necessary
    orders = orders[selected_columns]

    # Display the DataFrame in Streamlit
    st.dataframe(orders)

    if 'show_sidebar' not in st.session_state:
        st.session_state.show_sidebar = True

        # Toggle button in the main page
    if st.button('Toggle Sidebar'):
        st.session_state.show_sidebar = not st.session_state.show_sidebar

        # Display sidebar content based on toggle state
    if st.session_state.show_sidebar:
        with st.sidebar.expander("Make a Trade", expanded=False):
            with st.form("order_form"):
                # Input fields for trade orders
                symbol = st.text_input('Symbol', max_chars=30)
                side = st.selectbox('Side', ['buy', 'sell'])
                order_type = st.selectbox('Type', ['market', 'limit', 'stop', 'stop_limit', 'trailing_stop'])
                time_in_force = st.selectbox('Time in Force', ['day', 'gtc', 'opg', 'cls', 'ioc', 'fok'])

                # Allow user to choose between specifying Qty or Notional
                qty_or_notional = st.radio("Specify by", ["Quantity", "Notional"])
                if qty_or_notional == "Quantity":
                    qty = st.number_input('Quantity (Qty)', min_value=0, step=1)
                    notional = None
                else:
                    notional = st.number_input('Notional', min_value=0.0, format='%f')
                    qty = None

                if order_type == 'limit' or order_type == 'stop_limit':
                    limit_price = st.number_input('Limit Price', min_value=0.01, format='%f')  # set a minimum value
                else:
                    limit_price = None
                if order_type in ['stop', 'stop_limit']:
                    stop_price = st.number_input('Stop Price', min_value=0.01, format='%f')  # set a minimum value
                else:
                    stop_price = None
                if order_type == 'trailing_stop':
                    trail_price = st.number_input('Trail Price', min_value=0.0, format='%f')
                else:
                    trail_price = None
                if order_type == 'trailing_stop':
                    trail_percent = st.number_input('Trail Percent', min_value=0.1, step=0.1, format='%f')
                else:
                    trail_percent = None  # Default to None if not a trailing stop order

                client_order_id = st.text_input('Client Order ID', max_chars=20)
                order_class = st.selectbox('Order Class', ['', 'simple', 'bracket', 'oco', 'oto'])

                submit_order = st.form_submit_button("Submit Order")

    if submit_order:
        # Validate trail_percent for trailing stop orders
        if order_type == 'trailing_stop' and (trail_percent is None or trail_percent < 0.1):
            st.sidebar.error('Trail percent must be greater than or equal to 0.1 for trailing stop orders')
        payload = {
            "side": side,
            "type": order_type,
            "time_in_force": time_in_force,
            "symbol": symbol,
            "qty": qty,
            "notional": notional,
            "stop_price": stop_price,
            "limit_price": limit_price,
            "trail_price": trail_price,
            "trail_percent": trail_percent,
            "client_order_id": client_order_id,
            "order_class": order_class,

        }
        create_order(payload
                     )

        st.sidebar.success('Order Submitted!')

    with st.form("Feed"):
        status = st.selectbox('Select Feed', options=['open', 'closed', 'all'], index=0)
        submitted = st.form_submit_button("Submit")

    if submitted:
        orders = get_all_order(status)
        st.dataframe(orders)


# __________________________________________________________________________________________________
def display_home_page():
    home_search()


def display_AI():
    advisor = InvestmentAdvisor()
    files()
    if prompt := st.chat_input("How can I help you?"):
        advisor.process_user_message(prompt)


def display_coder():
    with st.expander("Quantitative trading", expanded=False):
        execbox(line_numbers=True, height=450, )

        if 'code' not in st.session_state:
            st.session_state.code = None
        if 'response' not in st.session_state:
            st.session_state.response = None

        with st.form("send"):
            query = st.text_area(label="TRY- 'Keltner Channel & MACD Strategy: Buy when the price closes above the upper Keltner Channel, and the MACD is bullish. Short when the price closes below the lower Keltner Channel, and the MACD is bearish.'")
            submitted = st.form_submit_button("Submit")

        if submitted:
            # Run the coder function and store the result in session state
            st.session_state.response, st.session_state.code = coder(query)

        if st.session_state.response:
            st.write(st.session_state.response)
        if st.session_state.code:
            st.code(st.session_state.code)
