import json
import assistant_methods as am

from openai import OpenAI

API_KEY = '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'
client = OpenAI(api_key=API_KEY)


def handle_required_action(thread_id, run_id, required_action):
    tool_outputs = []
    if required_action and required_action.type == 'submit_tool_outputs':
        for call in required_action.submit_tool_outputs.tool_calls:
            if call.function.name == 'getAccount':
                output = am.get_account()
                if not isinstance(output, str):
                    output = json.dumps(output)
                tool_outputs.append({
                    "tool_call_id": call.id,
                    "output": output
                })
            elif call.function.name == 'createOrder':
                order_args = json.loads(call.function.arguments)
                output = am.create_order(order_args)
                if not isinstance(output, str):
                    output = json.dumps(output)
                tool_outputs.append({
                    "tool_call_id": call.id,
                    "output": output
                })
            elif call.function.name == 'getAllOrders':
                order_params = json.loads(call.function.arguments) if call.function.arguments else {}
                output = am.get_all_order(order_params)
                if not isinstance(output, str):
                    output = json.dumps(output)
                tool_outputs.append({
                    "tool_call_id": call.id,
                    "output": output
                })
            elif call.function.name == 'cancelAllOrders':
                output = am.cancel_all_orders()
                if not isinstance(output, str):
                    output = json.dumps(output)
                tool_outputs.append({
                    "tool_call_id": call.id,
                    "output": output
                })
            elif call.function.name == 'getOrderById':
                # Assuming getOrderById needs an 'order_id' argument
                order_id = json.loads(call.function.arguments).get('order_id')
                output = am.get_order_by_id(order_id)
                if not isinstance(output, str):
                    output = json.dumps(output)
                tool_outputs.append({
                    "tool_call_id": call.id,
                    "output": output
                })

            elif call.function.name == 'replaceOrderById':
                # Parse the arguments for replaceOrderById
                replace_args = json.loads(call.function.arguments)
                order_id = replace_args.get('order_id')
                # Remove order_id from replace_args as it's a path parameter, not a body parameter
                del replace_args['order_id']
                output = am.replace_order_by_id(order_id, replace_args)
                if not isinstance(output, str):
                    output = json.dumps(output)
                tool_outputs.append({
                    "tool_call_id": call.id,
                    "output": output
                })

            elif call.function.name == 'getAllPositions':
                output = am.get_all_positions()
                if not isinstance(output, str):
                    output = json.dumps(output)
                tool_outputs.append({
                    "tool_call_id": call.id,
                    "output": output
                })

            elif call.function.name == 'closeAllPositions':
                # Check if 'cancel_orders' argument is provided
                close_args = json.loads(call.function.arguments) if call.function.arguments else {}
                cancel_orders = close_args.get('cancel_orders', False)
                output = am.close_all_positions(cancel_orders)
                if not isinstance(output, str):
                    output = json.dumps(output)
                tool_outputs.append({
                    "tool_call_id": call.id,
                    "output": output
                })

            elif call.function.name == 'getOpenPosition':
                # Parse the arguments for getOpenPosition
                symbol_or_asset_id = json.loads(call.function.arguments).get('symbol_or_asset_id')
                output = am.get_open_position(symbol_or_asset_id)
                if not isinstance(output, str):
                    output = json.dumps(output)
                tool_outputs.append({
                    "tool_call_id": call.id,
                    "output": output
                })
            elif call.function.name == 'getHistoricalAuctions':  # Add this branch for the new method
                # Parse the arguments for getHistoricalAuctions
                arguments = json.loads(call.function.arguments)
                symbols = arguments.get('symbols')
                start = arguments.get('start')
                end = arguments.get('end')
                limit = arguments.get('limit', 1000)
                asof = arguments.get('asof')
                feed = arguments.get('feed')
                currency = arguments.get('currency', 'USD')

                # Call the get_historical_auctions function
                output = am.get_historical_auctions(symbols, start, end, limit, asof, feed, currency)
                if not isinstance(output, str):
                    output = json.dumps(output)
                tool_outputs.append({
                    "tool_call_id": call.id,
                    "output": output
                })

            elif call.function.name == 'closePosition':
                # Parse the arguments for closePosition
                args = json.loads(call.function.arguments)
                symbol_or_asset_id = args.get('symbol_or_asset_id')
                qty = args.get('qty', None)
                percentage = args.get('percentage', None)
                output = am.close_position(symbol_or_asset_id, qty, percentage)
                if not isinstance(output, str):
                    output = json.dumps(output)
                tool_outputs.append({
                    "tool_call_id": call.id,
                    "output": output
                })

            elif call.function.name == 'getAccountPortfolioHistory':
                # Parse the arguments for getAccountPortfolioHistory
                history_args = json.loads(call.function.arguments) if call.function.arguments else {}
                output = am.get_account_portfolio_history(**history_args)
                if not isinstance(output, str):
                    output = json.dumps(output)
                tool_outputs.append({
                    "tool_call_id": call.id,
                    "output": output
                })

            elif call.function.name == 'getAllWatchlists':
                output = am.get_all_watchlists()
                if not isinstance(output, str):
                    output = json.dumps(output)
                tool_outputs.append({
                    "tool_call_id": call.id,
                    "output": output
                })

            elif call.function.name == 'createWatchlist':
                # Parse the arguments for createWatchlist
                watchlist_args = json.loads(call.function.arguments)
                name = watchlist_args.get('name')
                symbols = watchlist_args.get('symbols', [])
                output = am.create_watchlist(name, symbols)
                if not isinstance(output, str):
                    output = json.dumps(output)
                tool_outputs.append({
                    "tool_call_id": call.id,
                    "output": output
                })

            elif call.function.name == 'getWatchlistById':
                # Parse the arguments for getWatchlistById
                watchlist_id = json.loads(call.function.arguments).get('watchlist_id')
                output = am.get_watchlist_by_id(watchlist_id)
                if not isinstance(output, str):
                    output = json.dumps(output)
                tool_outputs.append({
                    "tool_call_id": call.id,
                    "output": output
                })

            elif call.function.name == 'updateWatchlistById':
                # Parse the arguments for updateWatchlistById
                update_args = json.loads(call.function.arguments)
                watchlist_id = update_args.get('watchlist_id')
                name = update_args.get('name')
                symbols = update_args.get('symbols', [])
                output = am.update_watchlist_by_id(watchlist_id, name, symbols)
                if not isinstance(output, str):
                    output = json.dumps(output)
                tool_outputs.append({
                    "tool_call_id": call.id,
                    "output": output
                })

            elif call.function.name == 'addAssetToWatchlist':
                # Parse the arguments for addAssetToWatchlist
                asset_args = json.loads(call.function.arguments)
                watchlist_id = asset_args.get('watchlist_id')
                symbol = asset_args.get('symbol')
                output = am.add_asset_to_watchlist(watchlist_id, symbol)
                if not isinstance(output, str):
                    output = json.dumps(output)
                tool_outputs.append({
                    "tool_call_id": call.id,
                    "output": output
                })

            elif call.function.name == 'deleteWatchlistById':
                # Parse the arguments for deleteWatchlistById
                watchlist_id = json.loads(call.function.arguments).get('watchlist_id')
                output = am.delete_watchlist_by_id(watchlist_id)
                if not isinstance(output, str):
                    output = json.dumps(output)
                tool_outputs.append({
                    "tool_call_id": call.id,
                    "output": output
                })

            elif call.function.name == 'getWatchlistByName':
                # Parse the arguments for getWatchlistByName
                watchlist_name = json.loads(call.function.arguments).get('name')
                output = am.get_watchlist_by_name(watchlist_name)
                if not isinstance(output, str):
                    output = json.dumps(output)
                tool_outputs.append({
                    "tool_call_id": call.id,
                    "output": output
                })

            elif call.function.name == 'updateWatchlistByName':
                # Parse the arguments for updateWatchlistByName
                update_args = json.loads(call.function.arguments)
                current_name = update_args.get('current_name')
                new_name = update_args.get('new_name')
                symbols = update_args.get('symbols', [])
                output = am.update_watchlist_by_name(current_name, new_name, symbols)
                if not isinstance(output, str):
                    output = json.dumps(output)
                tool_outputs.append({
                    "tool_call_id": call.id,
                    "output": output
                })

            elif call.function.name == 'addAssetToWatchlistByName':
                # Parse the arguments for addAssetToWatchlistByName
                asset_args = json.loads(call.function.arguments)
                watchlist_name = asset_args.get('watchlist_name')
                symbol = asset_args.get('symbol')
                output = am.add_asset_to_watchlist_by_name(watchlist_name, symbol)
                if not isinstance(output, str):
                    output = json.dumps(output)
                tool_outputs.append({
                    "tool_call_id": call.id,
                    "output": output
                })

            elif call.function.name == 'deleteWatchlistByName':
                # Parse the arguments for deleteWatchlistByName
                watchlist_name = json.loads(call.function.arguments).get('name')
                output = am.delete_watchlist_by_name(watchlist_name)
                if not isinstance(output, str):
                    output = json.dumps(output)
                tool_outputs.append({
                    "tool_call_id": call.id,
                    "output": output
                })

            elif call.function.name == 'deleteSymbolFromWatchlist':
                # Parse the arguments for deleteSymbolFromWatchlist
                watchlist_id = json.loads(call.function.arguments).get('watchlist_id')
                symbol = json.loads(call.function.arguments).get('symbol')
                output = am.delete_symbol_from_watchlist(watchlist_id, symbol)
                if not isinstance(output, str):
                    output = json.dumps(output)
                tool_outputs.append({
                    "tool_call_id": call.id,
                    "output": output
                })

            elif call.function.name == 'getAccountConfigurations':
                # Call the get_account_configurations function
                output = am.get_account_configurations()
                if not isinstance(output, str):
                    output = json.dumps(output)
                tool_outputs.append({
                    "tool_call_id": call.id,
                    "output": output
                })

            elif call.function.name == 'updateAccountConfigurations':
                # Parse the arguments for updateAccountConfigurations
                config_args = json.loads(call.function.arguments)
                output = am.update_account_configurations(config_args)
                if not isinstance(output, str):
                    output = json.dumps(output)
                tool_outputs.append({
                    "tool_call_id": call.id,
                    "output": output
                })

            elif call.function.name == 'getAccountActivitiesOfMultipleTypes':
                # Parse the arguments for getAccountActivitiesOfMultipleTypes
                activity_types = json.loads(call.function.arguments).get(
                    'activity_types') if call.function.arguments else None
                output = am.get_account_activities_of_multiple_types(activity_types)
                if not isinstance(output, str):
                    output = json.dumps(output)
                tool_outputs.append({
                    "tool_call_id": call.id,
                    "output": output
                })

            elif call.function.name == 'getAccountActivitiesOfOneType':
                # Parse the arguments for getAccountActivitiesOfOneType
                activity_type = json.loads(call.function.arguments)['activity_type']
                other_params = {key: value for key, value in json.loads(call.function.arguments).items() if
                                key != 'activity_type'}
                output = am.get_account_activities_of_one_type(activity_type, **other_params)
                if not isinstance(output, str):
                    output = json.dumps(output)
                tool_outputs.append({
                    "tool_call_id": call.id,
                    "output": output
                })

            elif call.function.name == 'getMarketClockInfo':
                output = am.get_market_clock_info()
                if not isinstance(output, str):
                    output = json.dumps(output)
                tool_outputs.append({
                    "tool_call_id": call.id,
                    "output": output
                })

            elif call.function.name == 'getAssets':
                # Parse the arguments for getAssets
                asset_args = json.loads(call.function.arguments) if call.function.arguments else {}
                output = am.get_assets(**asset_args)
                if not isinstance(output, str):
                    output = json.dumps(output)
                tool_outputs.append({
                    "tool_call_id": call.id,
                    "output": output
                })

            elif call.function.name == 'getAssetByIdOrSymbol':
                # Assuming getAssetByIdOrSymbol needs a 'symbol_or_asset_id' argument
                symbol_or_asset_id = json.loads(call.function.arguments).get('symbol_or_asset_id')
                output = am.get_asset_by_id_or_symbol(symbol_or_asset_id)
                if not isinstance(output, str):
                    output = json.dumps(output)
                tool_outputs.append({
                    "tool_call_id": call.id,
                    "output": output
                })

            elif call.function.name == 'getAnnouncementById':
                # Assuming getAnnouncementById needs an 'announcement_id' argument
                announcement_id = json.loads(call.function.arguments).get('announcement_id')
                output = am.get_announcement_by_id(announcement_id)
                if not isinstance(output, str):
                    output = json.dumps(output)
                tool_outputs.append({
                    "tool_call_id": call.id,
                    "output": output
                })

            elif call.function.name == 'getOpenPosition':
                # Parse the arguments for getOpenPosition
                symbol_or_asset_id = json.loads(call.function.arguments).get('symbol_or_asset_id')
                output = am.get_open_position(symbol_or_asset_id)
                if not isinstance(output, str):
                    output = json.dumps(output)
                tool_outputs.append({
                    "tool_call_id": call.id,
                    "output": output
                })

            elif call.function.name == 'getCorporateActions':
                # Parse the arguments for getCorporateActions
                corporate_actions_args = json.loads(call.function.arguments)
                symbols = corporate_actions_args.get('symbols')
                types = corporate_actions_args.get('types', None)
                start = corporate_actions_args.get('start', None)
                end = corporate_actions_args.get('end', None)
                limit = corporate_actions_args.get('limit', 1000)
                page_token = corporate_actions_args.get('page_token', None)
                sort = corporate_actions_args.get('sort', 'asc')

                output = am.get_corporate_actions(symbols, types, start, end, limit, page_token, sort)
                if not isinstance(output, str):
                    output = json.dumps(output)
                tool_outputs.append({
                    "tool_call_id": call.id,
                    "output": output
                })

            elif call.function.name == 'getNewsArticles':
                # Parse the arguments for getNewsArticles
                news_args = json.loads(call.function.arguments) if call.function.arguments else {}
                output = am.get_news_articles(**news_args)
                if not isinstance(output, str):
                    output = json.dumps(output)
                tool_outputs.append({
                    "tool_call_id": call.id,
                    "output": output
                })

            elif call.function.name == 'getMostActiveStocks':
                # Parse the arguments for getMostActiveStocks
                most_active_args = json.loads(call.function.arguments) if call.function.arguments else {}
                by = most_active_args.get('by', 'volume')
                top = most_active_args.get('top', 10)
                output = am.get_most_active_stocks(by, top)
                if not isinstance(output, str):
                    output = json.dumps(output)
                tool_outputs.append({
                    "tool_call_id": call.id,
                    "output": output
                })

            elif call.function.name == 'getTopMarketMovers':
                # Parse the arguments for getTopMarketMovers
                market_movers_args = json.loads(call.function.arguments) if call.function.arguments else {}
                market_type = market_movers_args.get('market_type')
                top = market_movers_args.get('top', 10)
                output = am.get_top_market_movers(market_type, top)
                if not isinstance(output, str):
                    output = json.dumps(output)
                tool_outputs.append({
                    "tool_call_id": call.id,
                    "output": output
                })

            elif call.function.name == 'getHistoricalBars':
                # Parse arguments for getting historical bars
                historical_bars_args = json.loads(call.function.arguments)
                symbols = historical_bars_args.get('symbols')
                timeframe = historical_bars_args.get('timeframe')
                start = historical_bars_args.get('start')
                end = historical_bars_args.get('end')
                limit = historical_bars_args.get('limit')
                adjustment = historical_bars_args.get('adjustment')
                raw = historical_bars_args.get('raw')
                feed = historical_bars_args.get('feed')
                currency = historical_bars_args.get('currency')

                # Call the get_historical_bars function with the parsed arguments
                historical_bars_data = am.get_historical_bars(symbols, timeframe, start, end, limit, adjustment,
                                                              raw,
                                                              feed,
                                                              currency)
                if not isinstance(historical_bars_data, str):
                    historical_bars_data = json.dumps(historical_bars_data)
                tool_outputs.append({
                    "tool_call_id": call.id,
                    "output": historical_bars_data
                })

            elif call.function.name == 'getLatestBars':
                # Assuming getLatestBars needs 'symbols', 'feed', and 'currency' arguments
                args = json.loads(call.function.arguments)
                symbols = args.get('symbols', "")
                feed = args.get('feed', None)
                currency = args.get('currency', "USD")
                output = am.get_latest_bars(symbols, feed, currency)
                if not isinstance(output, str):
                    output = json.dumps(output)
                tool_outputs.append({
                    "tool_call_id": call.id,
                    "output": output
                })

            elif call.function.name == 'getConditionCodes':
                # Assuming getConditionCodes needs 'ticktype' and 'tape' arguments
                ticktype = json.loads(call.function.arguments).get('ticktype')
                tape = json.loads(call.function.arguments).get('tape')
                output = am.get_condition_codes(ticktype, tape)
                if not isinstance(output, str):
                    output = json.dumps(output)
                tool_outputs.append({
                    "tool_call_id": call.id,
                    "output": output
                })

            elif call.function.name == 'getHistoricalQuotes':
                # Assuming getHistoricalQuotes needs specific arguments
                quotes_args = json.loads(call.function.arguments)
                symbols = quotes_args.get('symbols')
                start = quotes_args.get('start')
                end = quotes_args.get('end')
                limit = quotes_args.get('limit')
                asof = quotes_args.get('asof')
                feed = quotes_args.get('feed')
                page_token = quotes_args.get('page_token')
                sort = quotes_args.get('sort')

                output = am.get_historical_quotes(symbols, start, end, limit, asof, feed, page_token, sort)

                if not isinstance(output, str):
                    output = json.dumps(output)

                tool_outputs.append({
                    "tool_call_id": call.id,
                    "output": output
                })

            elif call.function.name == 'getHistoricalTrades':
                # Assuming getHistoricalTrades needs specific arguments
                trade_args = json.loads(call.function.arguments)
                symbols = trade_args.get('symbols')
                start = trade_args.get('start')
                end = trade_args.get('end')
                limit = trade_args.get('limit')
                asof = trade_args.get('asof')
                feed = trade_args.get('feed')
                output = am.get_historical_trades(symbols, start, end, limit, asof, feed)
                if not isinstance(output, str):
                    output = json.dumps(output)
                tool_outputs.append({
                    "tool_call_id": call.id,
                    "output": output
                })

            elif call.function.name == 'getLatestTrades':
                # Assuming getLatestTrades needs 'symbols', 'feed', and 'iex' arguments
                trade_args = json.loads(call.function.arguments)
                symbols = trade_args.get('symbols')
                feed = trade_args.get('feed', 'iex')
                output = am.get_latest_trades(symbols, feed)
                if not isinstance(output, str):
                    output = json.dumps(output)
                tool_outputs.append({
                    "tool_call_id": call.id,
                    "output": output
                })

            elif call.function.name == "searchVideos":
                trade_args = json.loads(call.function.arguments)
                query = trade_args.get("query")
                max_results = trade_args.get("max_results")
                output = am.search_videos(query, max_results)
                if not isinstance(output, str):
                    output = json.dumps(output)
                tool_outputs.append({
                    "tool_call_id": call.id,
                    "output": output
                })

            elif call.function.name == 'talkTo':
                # Parse the arguments for talkTo
                talk_args = json.loads(call.function.arguments)
                target_assistant_id = talk_args.get('target_assistant_id')
                message = talk_args.get('message')
                output = am.talk_to(target_assistant_id, message)
                if not isinstance(output, str):
                    output = json.dumps(output)
                tool_outputs.append({
                    "tool_call_id": call.id,
                    "output": output
                })

            elif call.function.name == 'assistantList':
                output = am.assistant_list()
                if not isinstance(output, str):
                    output = json.dumps(output)
                tool_outputs.append({
                    "tool_call_id": call.id,
                    "output": output
                })

            elif call.function.name == 'scrapeEconomicData':
                output = am.scrape_economic_data()
                if not isinstance(output, str):
                    output = json.dumps(output)
                tool_outputs.append({
                    "tool_call_id": call.id,
                    "output": output
                })

            elif call.function.name == 'bingSearch':
                search_query = json.loads(call.function.arguments).get('query')
                output = am.bing_search(search_query)
                if not isinstance(output, str):
                    output = json.dumps(output)
                tool_outputs.append({
                    "tool_call_id": call.id,
                    "output": output
                })

            elif call.function.name == 'getStockInfo':
                # Parse the arguments for getStockInfo
                ticker_symbol = json.loads(call.function.arguments).get('ticker_symbol')
                output = am.get_stock_info(ticker_symbol)
                if not isinstance(output, str):
                    output = json.dumps(output)
                tool_outputs.append({
                    "tool_call_id": call.id,
                    "output": output
                })

            if tool_outputs:
                client.beta.threads.runs.submit_tool_outputs(
                    thread_id=thread_id,
                    run_id=run_id,
                    tool_outputs=tool_outputs
                )
