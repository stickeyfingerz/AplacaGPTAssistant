import numpy as np
import pandas as pd
import requests
from pytube import YouTube
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound
from googleapiclient.discovery import build
from bs4 import BeautifulSoup
import yfinance as yf
import tools_calls
import asyncio
import json
import websockets
import logging
import time
from openai import OpenAI
from typing import Literal, Optional, Union
from pathlib import Path

api_key = 'AIzaSyAsizaZnVCjbVyRcduwTYTzzExKr6tN4pc'
yt_api_key = 'AIzaSyAsizaZnVCjbVyRcduwTYTzzExKr6tN4pc'
APCA_API_KEY = 'PKHFSF4BFYO5BHNSRBW8'
APCA_API_SECRET_KEY = 'raR9rgofHw1ukymm2xOCXfnqSfqpbJpucn3nRLJI'
opAPI_KEY = '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'
news_api_key = '532704daf41b484188ba09ffac0512b1'
bing_api_key = '415f5e2524974809a6492dbced240b69'
client = OpenAI(api_key=opAPI_KEY)


def get_account():
    """
    Retrieves account information from the Alpaca API.
    """
    url = "https://paper-api.alpaca.markets/v2/account"
    headers = {
        "accept": "application/json",
        "APCA-API-KEY-ID": APCA_API_KEY,
        "APCA-API-SECRET-KEY": APCA_API_SECRET_KEY
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        return {"error": "Failed to retrieve account data"}


def describe_get_account_function():
    """
    Returns the description of the get_account function.
    """
    return {
        "name": "getAccount",
        "description": "Retrieve account information from Alpaca API",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }


def create_order(order_details):
    """
    Creates an order with the Alpaca API.
    """
    url = "https://paper-api.alpaca.markets/v2/orders"
    headers = {
        "accept": "application/json",
        "APCA-API-KEY-ID": APCA_API_KEY,
        "APCA-API-SECRET-KEY": APCA_API_SECRET_KEY
    }
    response = requests.post(url, headers=headers, json=order_details)
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        return {"error": "Failed to create order"}


def describe_create_order_function():
    """
    Returns the description of the create_order function.
    """
    return {
        "name": "createOrder",
        "description": "Create an order with the Alpaca API",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {"type": "string"},
                "qty": {"type": "number"},
                "side": {"type": "string"},
                "type": {"type": "string"},
                "time_in_force": {"type": "string"}
                # Add other required parameters as needed
            },
            "required": ["symbol", "qty", "side", "type", "time_in_force"]
        }
    }


def get_all_order(status):
    url = f"https://paper-api.alpaca.markets/v2/orders?status={status}"

    headers = {
        "accept": "application/json",
        "APCA-API-KEY-ID": APCA_API_KEY,
        "APCA-API-SECRET-KEY": APCA_API_SECRET_KEY
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # This will raise an exception for HTTP errors
        data = response.json()
        if isinstance(data, list):
            return data  # Return the list directly if it is indeed a list
        else:
            # Handle other cases (like if data is a dictionary)
            return data.get('most_actives', [])
    except requests.RequestException as e:
        print(f"Error fetching active stocks: {e}")
        return []


def describe_get_all_orders_function():
    """
    Returns the description of the get_all_orders function.
    """
    return {
        "name": "getAllOrders",
        "description": "Retrieve all orders from Alpaca API",
        "parameters": {
            "type": "object",
            "properties": {
                "status": {"type": "string"},
                "limit": {"type": "integer"},
                "after": {"type": "string"},
                "until": {"type": "string"},
                "direction": {"type": "string"},
                "nested": {"type": "boolean"},
                "symbols": {"type": "string"},
                "side": {"type": "string"}
                # Add other parameters as needed
            },
            "required": []
        }
    }


def cancel_all_orders():
    """
    Attempts to cancel all open orders with the Alpaca API.
    """
    url = "https://paper-api.alpaca.markets/v2/orders"
    headers = {
        "accept": "application/json",
        "APCA-API-KEY-ID": APCA_API_KEY,
        "APCA-API-SECRET-KEY": APCA_API_SECRET_KEY
    }
    response = requests.delete(url, headers=headers)
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        return {"error": "Failed to cancel orders", "status_code": response.status_code}


def describe_cancel_all_orders_function():
    """
    Returns the description of the cancel_all_orders function.
    """
    return {
        "name": "cancelAllOrders",
        "description": "Cancel all open orders with the Alpaca API",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }


def get_order_by_id(order_id, nested=False):
    """
    Retrieves a single order by its ID from the Alpaca API.
    """
    url = f"https://paper-api.alpaca.markets/v2/orders/{order_id}"
    headers = {
        "accept": "application/json",
        "APCA-API-KEY-ID": APCA_API_KEY,
        "APCA-API-SECRET-KEY": APCA_API_SECRET_KEY
    }
    params = {'nested': nested}
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        return {"error": "Failed to retrieve the order", "status_code": response.status_code}


def describe_get_order_by_id_function():
    """
    Returns the description of the get_order_by_id function.
    """
    return {
        "name": "getOrderById",
        "description": "Retrieve a specific order by its ID from Alpaca API",
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string", "description": "The ID of the order"},
                "nested": {"type": "boolean", "description": "Whether to include nested orders"}
            },
            "required": ["order_id"]
        }
    }


def replace_order_by_id(order_id, order_details):
    """
    Replaces an order with updated parameters using the Alpaca API.
    """
    url = f"https://paper-api.alpaca.markets/v2/orders/{order_id}"
    headers = {
        "accept": "application/json",
        "APCA-API-KEY-ID": APCA_API_KEY,
        "APCA-API-SECRET-KEY": APCA_API_SECRET_KEY
    }
    response = requests.patch(url, headers=headers, json=order_details)
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        return {"error": "Failed to replace the order", "status_code": response.status_code}


def describe_replace_order_by_id_function():
    """
    Returns the description of the replace_order_by_id function.
    """
    return {
        "name": "replaceOrderById",
        "description": "Replace an order with updated parameters using the Alpaca API",
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string", "description": "The ID of the order to replace"},
                "qty": {"type": "number", "description": "Number of shares to trade"},
                "time_in_force": {"type": "string", "description": "Time-In-Force designation"},
                # Add other parameters as needed
            },
            "required": ["order_id"]
        }
    }


def delete_order_by_id(order_id):
    """
    Attempts to cancel an open order with the Alpaca API using the order ID.
    """
    url = f"https://paper-api.alpaca.markets/v2/orders/{order_id}"
    headers = {
        "accept": "application/json",
        "APCA-API-KEY-ID": APCA_API_KEY,
        "APCA-API-SECRET-KEY": APCA_API_SECRET_KEY
    }
    response = requests.delete(url, headers=headers)
    if response.status_code == 204:
        return {"success": "Order successfully deleted"}
    elif response.status_code == 422:
        return {"error": "Order not cancelable", "status_code": 422}
    else:
        return {"error": "Failed to delete the order", "status_code": response.status_code}


def describe_delete_order_by_id_function():
    """
    Returns the description of the delete_order_by_id function.
    """
    return {
        "name": "deleteOrderById",
        "description": "Cancel an open order using its ID with the Alpaca API",
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string", "description": "The ID of the order to delete"}
            },
            "required": ["order_id"]
        }
    }


def get_all_positions():
    """
    Retrieves a list of all open positions from the Alpaca API.
    """
    url = "https://paper-api.alpaca.markets/v2/positions"
    headers = {
        "accept": "application/json",
        "APCA-API-KEY-ID": APCA_API_KEY,
        "APCA-API-SECRET-KEY": APCA_API_SECRET_KEY
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        return {"error": "Failed to retrieve open positions", "status_code": response.status_code}


def describe_get_all_positions_function():
    """
    Returns the description of the get_all_positions function.
    """
    return {
        "name": "getAllPositions",
        "description": "Retrieve all open positions from Alpaca API",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }


def close_all_positions(cancel_orders=False):
    """
    Closes all the account's open positions using the Alpaca API.
    """
    url = "https://paper-api.alpaca.markets/v2/positions"
    headers = {
        "accept": "application/json",
        "APCA-API-KEY-ID": APCA_API_KEY,
        "APCA-API-SECRET-KEY": APCA_API_SECRET_KEY
    }
    params = {'cancel_orders': cancel_orders}
    response = requests.delete(url, headers=headers, params=params)
    if response.status_code in [200, 204]:
        return {"success": "All positions successfully closed"}
    elif response.status_code == 422:
        return {"error": "Request rejected", "status_code": 422}
    else:
        return {"error": "Failed to close positions", "status_code": response.status_code}


def describe_close_all_positions_function():
    """
    Returns the description of the close_all_positions function.
    """
    return {
        "name": "closeAllPositions",
        "description": "Close all open positions using the Alpaca API",
        "parameters": {
            "type": "object",
            "properties": {
                "cancel_orders": {"type": "boolean",
                                  "description": "Whether to cancel all open orders before liquidating positions"}
            },
            "required": []
        }
    }


def get_open_position(symbol_or_asset_id):
    """
    Retrieves the account's open position for the given symbol or assetId from the Alpaca API.
    """
    url = f"https://paper-api.alpaca.markets/v2/positions/{symbol_or_asset_id}"
    headers = {
        "accept": "application/json",
        "APCA-API-KEY-ID": APCA_API_KEY,
        "APCA-API-SECRET-KEY": APCA_API_SECRET_KEY
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        return {"error": "Failed to retrieve open position", "status_code": response.status_code}


def describe_get_open_position_function():
    """
    Returns the description of the get_open_position function.
    """
    return {
        "name": "getOpenPosition",
        "description": "Retrieve an open position for a specific symbol or assetId from Alpaca API",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol_or_asset_id": {"type": "string", "description": "The symbol or asset ID of the open position"}
            },
            "required": ["symbol_or_asset_id"]
        }
    }


def close_position(symbol_or_asset_id, qty=None, percentage=None):
    """
    Closes the account's open position for the given symbol or assetId using the Alpaca API.
    """
    url = f"https://paper-api.alpaca.markets/v2/positions/{symbol_or_asset_id}"
    headers = {
        "accept": "application/json",
        "APCA-API-KEY-ID": APCA_API_KEY,
        "APCA-API-SECRET-KEY": APCA_API_SECRET_KEY
    }
    params = {}
    if qty is not None:
        params['qty'] = qty
    if percentage is not None:
        params['percentage'] = percentage

    response = requests.delete(url, headers=headers, params=params)
    if response.status_code in [200, 204]:
        return {"success": "Position successfully closed"}
    else:
        return {"error": "Failed to close position", "status_code": response.status_code}


def describe_close_position_function():
    """
    Returns the description of the close_position function.
    """
    return {
        "name": "closePosition",
        "description": "Close an open position for a specific symbol or assetId using the Alpaca API",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol_or_asset_id": {"type": "string",
                                       "description": "The symbol or asset ID of the position to close"},
                "qty": {"type": "number", "description": "Number of shares to liquidate"},
                "percentage": {"type": "number", "description": "Percentage of position to liquidate"}
            },
            "required": ["symbol_or_asset_id"]
        }
    }


def get_account_portfolio_history(period=None, timeframe=None, date_end=None, extended_hours=None,
                                  intraday_reporting=None, pnl_reset=None):
    """
    Retrieves timeseries data about equity and profit/loss of the account.
    """
    url = "https://paper-api.alpaca.markets/v2/account/portfolio/history"
    headers = {
        "accept": "application/json",
        "APCA-API-KEY-ID": APCA_API_KEY,
        "APCA-API-SECRET-KEY": APCA_API_SECRET_KEY
    }
    params = {'period': period}
    if timeframe:
        params['timeframe'] = timeframe
    if date_end:
        params['date_end'] = date_end
    if extended_hours:
        params['extended_hours'] = extended_hours
    if intraday_reporting:
        params['intraday_reporting'] = intraday_reporting
    if pnl_reset:
        params['pnl_reset'] = pnl_reset

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        return {"error": "Failed to retrieve account portfolio history", "status_code": response.status_code}


def describe_get_account_portfolio_history_function():
    """
    Returns the description of the get_account_portfolio_history function.
    """
    return {
        "name": "getAccountPortfolioHistory",
        "description": "Retrieve timeseries data about equity and P/L of the account from Alpaca API",
        "parameters": {
            "type": "object",
            "properties": {
                "period": {"type": "string", "description": "Duration of the data"},
                "timeframe": {"type": "string", "description": "Resolution of time window"},
                "date_end": {"type": "string", "description": "End date for the data"},
                "extended_hours": {"type": "string", "description": "Include extended hours in the result"},
                "intraday_reporting": {"type": "string", "description": "Reporting type for intraday"},
                "pnl_reset": {"type": "string", "description": "Profit And Loss calculation mode"}
            },
            "required": []
        }
    }


def get_all_watchlists():
    """
    Retrieves a list of all watchlists from the Alpaca API.
    """
    url = "https://paper-api.alpaca.markets/v2/watchlists"
    headers = {
        "accept": "application/json",
        "APCA-API-KEY-ID": APCA_API_KEY,
        "APCA-API-SECRET-KEY": APCA_API_SECRET_KEY
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        return {"error": "Failed to retrieve watchlists", "status_code": response.status_code}


def describe_get_all_watchlists_function():
    """
    Returns the description of the get_all_watchlists function.
    """
    return {
        "name": "getAllWatchlists",
        "description": "Retrieve all watchlists from Alpaca API",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }


def create_watchlist(name, symbols=None):
    """
    Creates a new watchlist with a given name and an initial set of assets using the Alpaca API.
    """
    url = "https://paper-api.alpaca.markets/v2/watchlists"
    headers = {
        "accept": "application/json",
        "APCA-API-KEY-ID": APCA_API_KEY,
        "APCA-API-SECRET-KEY": APCA_API_SECRET_KEY
    }
    data = {"name": name}
    if symbols is not None:
        data["symbols"] = symbols

    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        return {"error": "Failed to create watchlist", "status_code": response.status_code}


def describe_create_watchlist_function():
    """
    Returns the description of the create_watchlist function.
    """
    return {
        "name": "createWatchlist",
        "description": "Create a new watchlist with an initial set of assets using the Alpaca API",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Name of the watchlist"},
                "symbols": {"type": "array", "items": {"type": "string"}, "description": "Array of asset symbols"}
            },
            "required": ["name"]
        }
    }


def get_watchlist_by_id(watchlist_id):
    """
    Retrieves a specific watchlist by its ID using the Alpaca API.
    """
    url = f"https://paper-api.alpaca.markets/v2/watchlists/{watchlist_id}"
    headers = {
        "accept": "application/json",
        "APCA-API-KEY-ID": APCA_API_KEY,
        "APCA-API-SECRET-KEY": APCA_API_SECRET_KEY
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        return {"error": "Failed to retrieve watchlist", "status_code": response.status_code}


def describe_get_watchlist_by_id_function():
    """
    Returns the description of the get_watchlist_by_id function.
    """
    return {
        "name": "getWatchlistById",
        "description": "Retrieve a specific watchlist by its ID from Alpaca API",
        "parameters": {
            "type": "object",
            "properties": {
                "watchlist_id": {"type": "string", "description": "The ID of the watchlist"}
            },
            "required": ["watchlist_id"]
        }
    }


def update_watchlist_by_id(watchlist_id, name, symbols=None):
    """
    Updates the name and/or content of a watchlist identified by the ID using the Alpaca API.
    """
    url = f"https://paper-api.alpaca.markets/v2/watchlists/{watchlist_id}"
    headers = {
        "accept": "application/json",
        "APCA-API-KEY-ID": APCA_API_KEY,
        "APCA-API-SECRET-KEY": APCA_API_SECRET_KEY
    }
    data = {"name": name}
    if symbols is not None:
        data["symbols"] = symbols

    response = requests.put(url, headers=headers, json=data)
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        return {"error": "Failed to update watchlist", "status_code": response.status_code}


def describe_update_watchlist_by_id_function():
    """
    Returns the description of the update_watchlist_by_id function.
    """
    return {
        "name": "updateWatchlistById",
        "description": "Update the name and/or content of a watchlist by its ID using the Alpaca API",
        "parameters": {
            "type": "object",
            "properties": {
                "watchlist_id": {"type": "string", "description": "The ID of the watchlist to update"},
                "name": {"type": "string", "description": "New name of the watchlist"},
                "symbols": {"type": "array", "items": {"type": "string"}, "description": "Array of asset symbols"}
            },
            "required": ["watchlist_id", "name"]
        }
    }


def add_asset_to_watchlist(watchlist_id, symbol):
    """
    Appends an asset symbol to the end of a watchlist identified by the ID using the Alpaca API.
    """
    url = f"https://paper-api.alpaca.markets/v2/watchlists/{watchlist_id}"
    headers = {
        "accept": "application/json",
        "APCA-API-KEY-ID": APCA_API_KEY,
        "APCA-API-SECRET-KEY": APCA_API_SECRET_KEY
    }
    data = {"symbol": symbol}

    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        return {"error": "Failed to add asset to watchlist", "status_code": response.status_code}


def describe_add_asset_to_watchlist_function():
    """
    Returns the description of the add_asset_to_watchlist function.
    """
    return {
        "name": "addAssetToWatchlist",
        "description": "Append an asset symbol to a watchlist using the Alpaca API",
        "parameters": {
            "type": "object",
            "properties": {
                "watchlist_id": {"type": "string", "description": "The ID of the watchlist"},
                "symbol": {"type": "string", "description": "The symbol name to add to the watchlist"}
            },
            "required": ["watchlist_id", "symbol"]
        }
    }


def delete_watchlist_by_id(watchlist_id):
    """
    Deletes a watchlist identified by its ID using the Alpaca API.
    """
    url = f"https://paper-api.alpaca.markets/v2/watchlists/{watchlist_id}"
    headers = {
        "accept": "application/json",
        "APCA-API-KEY-ID": APCA_API_KEY,
        "APCA-API-SECRET-KEY": APCA_API_SECRET_KEY
    }

    response = requests.delete(url, headers=headers)
    if response.status_code in [200, 204]:
        return {"success": "Watchlist successfully deleted"}
    else:
        return {"error": "Failed to delete watchlist", "status_code": response.status_code}


def describe_delete_watchlist_by_id_function():
    """
    Returns the description of the delete_watchlist_by_id function.
    """
    return {
        "name": "deleteWatchlistById",
        "description": "Delete a watchlist by its ID using the Alpaca API",
        "parameters": {
            "type": "object",
            "properties": {
                "watchlist_id": {"type": "string", "description": "The ID of the watchlist to delete"}
            },
            "required": ["watchlist_id"]
        }
    }


def get_watchlist_by_name(watchlist_name):
    """
    Retrieves a specific watchlist by its name using the Alpaca API.
    """
    url = f"https://paper-api.alpaca.markets/v2/watchlists:by_name"
    params = {"name": watchlist_name}
    headers = {
        "accept": "application/json",
        "APCA-API-KEY-ID": APCA_API_KEY,
        "APCA-API-SECRET-KEY": APCA_API_SECRET_KEY
    }

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        return {"error": "Failed to retrieve watchlist by name", "status_code": response.status_code}


def describe_get_watchlist_by_name_function():
    """
    Returns the description of the get_watchlist_by_name function.
    """
    return {
        "name": "getWatchlistByName",
        "description": "Retrieve a specific watchlist by its name from Alpaca API",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "The name of the watchlist to retrieve"}
            },
            "required": ["name"]
        }
    }


def update_watchlist_by_name(current_name, new_name, symbols=None):
    """
    Updates the name and/or content of a watchlist identified by its name using the Alpaca API.
    """
    url = "https://paper-api.alpaca.markets/v2/watchlists:by_name"
    params = {"name": current_name}
    headers = {
        "accept": "application/json",
        "APCA-API-KEY-ID": APCA_API_KEY,
        "APCA-API-SECRET-KEY": APCA_API_SECRET_KEY
    }
    data = {"name": new_name}
    if symbols is not None:
        data["symbols"] = symbols

    response = requests.put(url, headers=headers, params=params, json=data)
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        return {"error": "Failed to update watchlist by name", "status_code": response.status_code}


def describe_update_watchlist_by_name_function():
    """
    Returns the description of the update_watchlist_by_name function.
    """
    return {
        "name": "updateWatchlistByName",
        "description": "Update the name and/or content of a watchlist by its name using the Alpaca API",
        "parameters": {
            "type": "object",
            "properties": {
                "current_name": {"type": "string", "description": "The current name of the watchlist"},
                "new_name": {"type": "string", "description": "The new name for the watchlist"},
                "symbols": {"type": "array", "items": {"type": "string"}, "description": "Array of asset symbols"}
            },
            "required": ["current_name", "new_name"]
        }
    }


def add_asset_to_watchlist_by_name(watchlist_name, symbol):
    """
    Appends an asset symbol to the end of a watchlist identified by its name using the Alpaca API.
    """
    url = "https://paper-api.alpaca.markets/v2/watchlists:by_name"
    params = {"name": watchlist_name}
    headers = {
        "accept": "application/json",
        "APCA-API-KEY-ID": APCA_API_KEY,
        "APCA-API-SECRET-KEY": APCA_API_SECRET_KEY
    }
    data = {"symbol": symbol}

    response = requests.post(url, headers=headers, params=params, json=data)
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        return {"error": "Failed to add asset to watchlist by name", "status_code": response.status_code}


def describe_add_asset_to_watchlist_by_name_function():
    """
    Returns the description of the add_asset_to_watchlist_by_name function.
    """
    return {
        "name": "addAssetToWatchlistByName",
        "description": "Append an asset symbol to a watchlist by its name using the Alpaca API",
        "parameters": {
            "type": "object",
            "properties": {
                "watchlist_name": {"type": "string", "description": "The name of the watchlist"},
                "symbol": {"type": "string", "description": "The symbol name to add to the watchlist"}
            },
            "required": ["watchlist_name", "symbol"]
        }
    }


def delete_watchlist_by_name(watchlist_name):
    """
    Deletes a watchlist identified by its name using the Alpaca API.
    """
    url = "https://paper-api.alpaca.markets/v2/watchlists:by_name"
    params = {"name": watchlist_name}
    headers = {
        "accept": "application/json",
        "APCA-API-KEY-ID": APCA_API_KEY,
        "APCA-API-SECRET-KEY": APCA_API_SECRET_KEY
    }

    response = requests.delete(url, headers=headers, params=params)
    if response.status_code in [200, 204]:
        return {"success": "Watchlist successfully deleted"}
    else:
        return {"error": "Failed to delete watchlist by name", "status_code": response.status_code}


def describe_delete_watchlist_by_name_function():
    """
    Returns the description of the delete_watchlist_by_name function.
    """
    return {
        "name": "deleteWatchlistByName",
        "description": "Delete a watchlist by its name using the Alpaca API",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "The name of the watchlist to delete"}
            },
            "required": ["name"]
        }
    }


def delete_symbol_from_watchlist(watchlist_id, symbol):
    """
    Deletes a specific symbol from a watchlist identified by its ID using the Alpaca API.
    """
    url = f"https://paper-api.alpaca.markets/v2/watchlists/{watchlist_id}/{symbol}"
    headers = {
        "accept": "application/json",
        "APCA-API-KEY-ID": APCA_API_KEY,
        "APCA-API-SECRET-KEY": APCA_API_SECRET_KEY
    }

    response = requests.delete(url, headers=headers)
    if response.status_code in [200, 204]:
        return {"success": "Symbol successfully deleted from watchlist"}
    else:
        return {"error": "Failed to delete symbol from watchlist", "status_code": response.status_code}


def describe_delete_symbol_from_watchlist_function():
    """
    Returns the description of the delete_symbol_from_watchlist function.
    """
    return {
        "name": "deleteSymbolFromWatchlist",
        "description": "Delete a specific symbol from a watchlist using the Alpaca API",
        "parameters": {
            "type": "object",
            "properties": {
                "watchlist_id": {"type": "string", "description": "The ID of the watchlist"},
                "symbol": {"type": "string", "description": "The symbol name to remove from the watchlist"}
            },
            "required": ["watchlist_id", "symbol"]
        }
    }


def get_account_configurations():
    """
    Retrieves current account configuration values using the Alpaca API.
    """
    url = "https://paper-api.alpaca.markets/v2/account/configurations"
    headers = {
        "accept": "application/json",
        "APCA-API-KEY-ID": APCA_API_KEY,
        "APCA-API-SECRET-KEY": APCA_API_SECRET_KEY
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        return {"error": "Failed to retrieve account configurations", "status_code": response.status_code}


def describe_get_account_configurations_function():
    """
    Returns the description of the get_account_configurations function.
    """
    return {
        "name": "getAccountConfigurations",
        "description": "Retrieve current account configuration values using the Alpaca API",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }


def update_account_configurations(configurations):
    """
    Updates and retrieves the current account configuration values using the Alpaca API.
    """
    url = "https://paper-api.alpaca.markets/v2/account/configurations"
    headers = {
        "accept": "application/json",
        "APCA-API-KEY-ID": APCA_API_KEY,
        "APCA-API-SECRET-KEY": APCA_API_SECRET_KEY
    }

    response = requests.patch(url, headers=headers, json=configurations)
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        return {"error": "Failed to update account configurations", "status_code": response.status_code}


def describe_update_account_configurations_function():
    """
    Returns the description of the update_account_configurations function.
    """
    return {
        "name": "updateAccountConfigurations",
        "description": "Update and retrieve current account configuration values using the Alpaca API",
        "parameters": {
            "type": "object",
            "properties": {
                # Define properties based on the BODY PARAMS provided
                "dtbp_check": {"type": "string"},
                "trade_confirm_email": {"type": "string"},
                "suspend_trade": {"type": "boolean"},
                "no_shorting": {"type": "boolean"},
                "fractional_trading": {"type": "boolean"},
                "max_margin_multiplier": {"type": "string"},
                "pdt_check": {"type": "string"},
                "ptp_no_exception_entry": {"type": "boolean"}
            },
            "required": []  # Specify required fields if any
        }
    }


def get_account_activities_of_multiple_types(activity_types=None):
    """
    Retrieves account activity entries for multiple types of activities using the Alpaca API.
    """
    url = "https://paper-api.alpaca.markets/v2/account/activities"
    headers = {
        "accept": "application/json",
        "APCA-API-KEY-ID": APCA_API_KEY,
        "APCA-API-SECRET-KEY": APCA_API_SECRET_KEY
    }
    params = {}
    if activity_types:
        params['activity_types'] = activity_types

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        return {"error": "Failed to retrieve account activities", "status_code": response.status_code}


def describe_get_account_activities_of_multiple_types_function():
    """
    Returns the description of the get_account_activities_of_multiple_types function.
    """
    return {
        "name": "getAccountActivitiesOfMultipleTypes",
        "description": "Retrieve account activity entries for multiple types of activities using the Alpaca API",
        "parameters": {
            "type": "object",
            "properties": {
                "activity_types": {"type": "string", "description": "Comma-separated list of activity types"}
            },
            "required": []  # No required parameters
        }
    }


def get_account_activities_of_one_type(activity_type, date=None, until=None, after=None, direction=None, page_size=None,
                                       page_token=None, category=None):
    """
    Retrieves account activity entries for a specific type of activity using the Alpaca API.
    """
    url = f"https://paper-api.alpaca.markets/v2/account/activities/{activity_type}"
    headers = {
        "accept": "application/json",
        "APCA-API-KEY-ID": APCA_API_KEY,
        "APCA-API-SECRET-KEY": APCA_API_SECRET_KEY
    }
    params = {}
    if date:
        params['date'] = date
    if until:
        params['until'] = until
    if after:
        params['after'] = after
    if direction:
        params['direction'] = direction
    if page_size:
        params['page_size'] = page_size
    if page_token:
        params['page_token'] = page_token
    if category:
        params['category'] = category

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        return {"error": "Failed to retrieve account activities of one type", "status_code": response.status_code}


def describe_get_account_activities_of_one_type_function():
    """
    Returns the description of the get_account_activities_of_one_type function.
    """
    return {
        "name": "getAccountActivitiesOfOneType",
        "description": "Retrieve account activity entries for a specific type of activity using the Alpaca API",
        "parameters": {
            "type": "object",
            "properties": {
                "activity_type": {"type": "string", "description": "The activity type"},
                "date": {"type": "string", "format": "date-time",
                         "description": "The date for which you want to see activities."},
                "until": {"type": "string", "format": "date-time",
                          "description": "Only activities submitted before this date will be returned."},
                "after": {"type": "string", "format": "date-time",
                          "description": "Only activities submitted after this date will be returned."},
                "direction": {"type": "string",
                              "description": "The chronological order of response based on the submission time. Can be 'asc' or 'desc'."},
                "page_size": {"type": "integer",
                              "description": "The maximum number of entries to return in the response."},
                "page_token": {"type": "string",
                               "description": "The ID of the end of your current page of results."},
                "category": {"type": "string",
                             "description": "Specify 'trade_activity' or 'non_trade_activity' to filter the type of results returned."}
            },
            "required": ["activity_type"]
        }
    }


def get_market_clock_info():
    """
    Retrieves the market clock information using the Alpaca API.
    """
    url = "https://paper-api.alpaca.markets/v2/clock"
    headers = {
        "accept": "application/json",
        "APCA-API-KEY-ID": APCA_API_KEY,
        "APCA-API-SECRET-KEY": APCA_API_SECRET_KEY
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        return {"error": "Failed to retrieve market clock information", "status_code": response.status_code}


def describe_get_market_clock_info_function():
    """
    Returns the description of the get_market_clock_info function.
    """
    return {
        "name": "getMarketClockInfo",
        "description": "Retrieve the market clock information using the Alpaca API",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []  # No required parameters
        }
    }


def get_assets(status=None, asset_class=None, exchange=None, attributes=None):
    """
    Retrieves a list of assets from the Alpaca API.
    """
    url = "https://paper-api.alpaca.markets/v2/assets"
    headers = {
        "accept": "application/json",
        "APCA-API-KEY-ID": APCA_API_KEY,
        "APCA-API-SECRET-KEY": APCA_API_SECRET_KEY
    }
    params = {}
    if status:
        params['status'] = status
    if asset_class:
        params['asset_class'] = asset_class
    if exchange:
        params['exchange'] = exchange
    if attributes:
        params['attributes'] = attributes

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        return {"error": "Failed to retrieve assets", "status_code": response.status_code}


def describe_get_assets_function():
    """
    Returns the description of the get_assets function.
    """
    return {
        "name": "getAssets",
        "description": "Retrieve a list of assets from the Alpaca API",
        "parameters": {
            "type": "object",
            "properties": {
                "status": {"type": "string", "description": "Asset status (e.g., 'active')"},
                "asset_class": {"type": "string", "description": "Asset class (defaults to 'us_equity')"},
                "exchange": {"type": "string", "description": "Exchange code (e.g., 'NYSE')"},
                "attributes": {"type": "array", "items": {"type": "string"},
                               "description": "Comma separated values of asset attributes"}
            },
            "required": []  # No required parameters
        }
    }


def get_asset_by_id_or_symbol(symbol_or_asset_id):
    """
    Retrieves asset information by its ID or symbol using the Alpaca API.
    """
    url = f"https://paper-api.alpaca.markets/v2/assets/{symbol_or_asset_id}"
    headers = {
        "accept": "application/json",
        "APCA-API-KEY-ID": APCA_API_KEY,
        "APCA-API-SECRET-KEY": APCA_API_SECRET_KEY
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        return {"error": "Failed to retrieve asset information", "status_code": response.status_code}


def describe_get_asset_by_id_or_symbol_function():
    """
    Returns the description of the get_asset_by_id_or_symbol function.
    """
    return {
        "name": "getAssetByIdOrSymbol",
        "description": "Retrieve asset information by ID or symbol using the Alpaca API",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol_or_asset_id": {"type": "string", "description": "The symbol or asset ID of the asset"}
            },
            "required": ["symbol_or_asset_id"]
        }
    }


def get_announcement_by_id(announcement_id):
    """
    Retrieves a specific corporate announcement by its ID using the Alpaca API.
    """
    url = f"https://paper-api.alpaca.markets/v2/corporate_actions/announcements/{announcement_id}"
    headers = {
        "accept": "application/json",
        "APCA-API-KEY-ID": APCA_API_KEY,
        "APCA-API-SECRET-KEY": APCA_API_SECRET_KEY
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        return {"error": "Failed to retrieve the announcement", "status_code": response.status_code}


def describe_get_announcement_by_id_function():
    """
    Returns the description of the get_announcement_by_id function.
    """
    return {
        "name": "getAnnouncementById",
        "description": "Retrieve a specific corporate announcement by its ID using the Alpaca API",
        "parameters": {
            "type": "object",
            "properties": {
                "announcement_id": {"type": "string", "description": "The ID of the corporate announcement"}
            },
            "required": ["announcement_id"]
        }
    }


def retrieve_announcements(ca_types, since, until, symbol=None, cusip=None, date_type=None):
    """
    Retrieves corporate action announcements with specified search criteria using the Alpaca API.
    """
    url = "https://paper-api.alpaca.markets/v2/corporate_actions/announcements"
    headers = {
        "accept": "application/json",
        "APCA-API-KEY-ID": APCA_API_KEY,
        "APCA-API-SECRET-KEY": APCA_API_SECRET_KEY
    }
    params = {
        "ca_types": ca_types,
        "since": since,
        "until": until,
        "symbol": symbol,
        "cusip": cusip,
        "date_type": date_type
    }
    # Remove None values from params
    params = {k: v for k, v in params.items() if v is not None}

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        return {"error": "Failed to retrieve announcements", "status_code": response.status_code}


def describe_retrieve_announcements_function():
    """
    Returns the description of the retrieve_announcements function.
    """
    return {
        "name": "retrieveAnnouncements",
        "description": "Retrieve corporate action announcements with specified search criteria using the Alpaca API",
        "parameters": {
            "type": "object",
            "properties": {
                "ca_types": {"type": "string", "description": "Types of corporate actions"},
                "since": {"type": "string", "format": "date", "description": "Start date of the range"},
                "until": {"type": "string", "format": "date", "description": "End date of the range"},
                "symbol": {"type": "string", "description": "Company symbol"},
                "cusip": {"type": "string", "description": "Company CUSIP"},
                "date_type": {"type": "string", "description": "Type of date to filter on"}
            },
            "required": ["ca_types", "since", "until"]
        }
    }


def get_corporate_actions(symbols, types=None, start=None, end=None, limit=1000, page_token=None, sort='asc'):
    """
    Retrieves corporate action data for given symbols over a specified time period.
    """
    url = "https://data.alpaca.markets/v1beta1/corporate-actions"
    headers = {
        "accept": "application/json",
        "APCA-API-KEY-ID": APCA_API_KEY,
        "APCA-API-SECRET-KEY": APCA_API_SECRET_KEY
    }
    params = {
        "symbols": symbols,
        "types": types,
        "start": start,
        "end": end,
        "limit": limit,
        "page_token": page_token,
        "sort": sort
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        return {"error": "Failed to retrieve corporate actions", "status_code": response.status_code}


def describe_get_corporate_actions_function():
    """
    Returns the description of the get_corporate_actions function.
    """
    return {
        "name": "getCorporateActions",
        "description": "Retrieve corporate actions data for given symbols using the Alpaca API",
        "parameters": {
            "type": "object",
            "properties": {
                "symbols": {"type": "string", "description": "Comma separated list of symbols"},
                "types": {"type": "string", "description": "Comma separated list of types"},
                "start": {"type": "string", "format": "date"},
                "end": {"type": "string", "format": "date"},
                "limit": {"type": "integer"},
                "page_token": {"type": "string"},
                "sort": {"type": "string"}
            },
            "required": ["symbols"]
        }
    }


def get_news_articles(start=None, end=None, sort='desc', symbols=None, limit=10, include_content=False,
                      exclude_contentless=False, page_token=None):
    """
    Retrieves news articles from the Alpaca API.
    """
    url = "https://data.alpaca.markets/v1beta1/news"
    headers = {
        "accept": "application/json",
        "APCA-API-KEY-ID": APCA_API_KEY,
        "APCA-API-SECRET-KEY": APCA_API_SECRET_KEY
    }
    params = {
        "start": start,
        "end": end,
        "sort": sort,
        "symbols": symbols,
        "limit": limit,
        "include_content": include_content,
        "exclude_contentless": exclude_contentless,
        "page_token": page_token
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        return {"error": "Failed to retrieve news articles", "status_code": response.status_code}


def describe_get_news_articles_function():
    """
    Returns the description of the get_news_articles function.
    """
    return {
        "name": "getNewsArticles",
        "description": "Retrieve latest news articles from Alpaca API",
        "parameters": {
            "type": "object",
            "properties": {
                "start": {"type": "string", "format": "date-time"},
                "end": {"type": "string", "format": "date-time"},
                "sort": {"type": "string"},
                "symbols": {"type": "string"},
                "limit": {"type": "integer"},
                "include_content": {"type": "boolean"},
                "exclude_contentless": {"type": "boolean"},
                "page_token": {"type": "string"}
            },
            "required": []
        }
    }


def get_most_active_stocks(by='volume', top=10):
    """
    Fetches the most active stocks by volume or trade count.
    """
    url = "https://data.alpaca.markets/v1beta1/screener/stocks/most-actives"
    headers = {
        "accept": "application/json",
        "APCA-API-KEY-ID": APCA_API_KEY,
        "APCA-API-SECRET-KEY": APCA_API_SECRET_KEY
    }
    params = {
        "by": by,
        "top": top
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        return {"error": "Failed to retrieve most active stocks", "status_code": response.status_code}


def describe_get_most_active_stocks_function():
    """
    Returns the description of the get_most_active_stocks function.
    """
    return {
        "name": "getMostActiveStocks",
        "description": "Fetch most active stocks by volume or trade count using the Alpaca API",
        "parameters": {
            "type": "object",
            "properties": {
                "by": {"type": "string", "description": "The metric for ranking (volume or trade count)"},
                "top": {"type": "integer", "description": "Number of top most active stocks to fetch"}
            },
            "required": []
        }
    }


def get_top_market_movers(market_type, top=10):
    """
    Fetches the top market movers from the Alpaca API for the specified market type (stocks or crypto).

    Args:
    - market_type (str): The market type to screen (stocks or crypto).
    - top (int, optional): Number of top market movers to fetch for gainers and losers. Defaults to 10.

    Returns:
    - dict: A JSON object containing the top market movers.
    """
    url = f"https://data.alpaca.markets/v1beta1/screener/{market_type}/movers"
    params = {'top': top}
    headers = {
        "accept": "application/json",
        "APCA-API-KEY-ID": APCA_API_KEY,
        "APCA-API-SECRET-KEY": APCA_API_SECRET_KEY

    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        return {"error": f"Failed to fetch top market movers. Status code: {response.status_code}"}


def describe_get_top_market_movers_function():
    """
    Returns the description of the get_top_market_movers function for integration with an API tool.

    Returns:
    - dict: A description of the get_top_market_movers function.
    """
    return {
        "name": "getTopMarketMovers",
        "description": "Fetch the top market movers from the Alpaca API for a specific market (stocks or crypto).",
        "parameters": {
            "type": "object",
            "properties": {
                "market_type": {"type": "string", "description": "Market type to screen (stocks or crypto)"},
                "top": {"type": "integer", "description": "Number of top market movers to fetch"}
            },
            "required": ["market_type"]
        }
    }


def get_historical_auctions(symbols=None, start=None, end=None, limit=None, asof=None, feed="iex", currency="USD"):
    """
    Fetches historical auction prices for the specified stock symbols between the specified dates.

    Args:
    - symbols (str): Comma-separated list of symbols.
    - start (str, optional): The inclusive start of the interval in RFC-3339 or YYYY-MM-DD format.
    - end (str, optional): The inclusive end of the interval in RFC-3339 or YYYY-MM-DD format.
    - limit (int, optional): Number of maximum data points to return in a response. Defaults to 1000.
    - asof (str, optional): The asof date in YYYY-MM-DD format.
    - feed (str, optional): The source feed of the data (sip, iex, otc).
    - currency (str, optional): The currency of all prices in ISO 4217 format. Defaults to USD.

    Returns:
    - dict: A JSON object containing historical auction data.
    """
    url = "https://data.alpaca.markets/v2/stocks/auctions"
    params = {
        'symbols': symbols,
        'start': start,
        'end': end,
        'limit': limit,
        'asof': asof,
        'feed': feed,
        'currency': currency
    }
    headers = {
        "accept": "application/json",
        "APCA-API-KEY-ID": APCA_API_KEY,
        "APCA-API-SECRET-KEY": APCA_API_SECRET_KEY

    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        return {"error": f"Failed to fetch historical auctions. Status code: {response.status_code}"}


def describe_get_historical_auctions_function():
    """
    Returns the description of the get_historical_auctions function for integration with an API tool.

    Returns:
    - dict: A description of the get_historical_auctions function.
    """
    return {
        "name": "getHistoricalAuctions",
        "description": "Fetch historical auction prices for the specified stock symbols between specified dates.",
        "parameters": {
            "type": "object",
            "properties": {
                "symbols": {"type": "string", "description": "Comma-separated list of symbols"},
                "start": {"type": "string", "description": "Start date in RFC-3339 or YYYY-MM-DD format"},
                "end": {"type": "string", "description": "End date in RFC-3339 or YYYY-MM-DD format"},
                "limit": {"type": "integer", "description": "Maximum data points to return"},
                "asof": {"type": "string", "description": "Asof date in YYYY-MM-DD format"},
                "feed": {"type": "string", "description": "Source feed of the data ( iex)"},
                "currency": {"type": "string", "description": "Currency in ISO 4217 format"},
            },
            "required": ["symbols"]
        }
    }


def get_historical_bars(symbols=None, timeframe=None, start=None, end=None, limit=1000, adjustment=None, raw=None,
                        feed="iex",
                        currency="USD"):
    """
    Retrieves historical stock bars data from the Alpaca API.
    """
    url = "https://data.alpaca.markets/v2/stocks/bars"
    headers = {
        "accept": "application/json",
        "APCA-API-KEY-ID": APCA_API_KEY,
        "APCA-API-SECRET-KEY": APCA_API_SECRET_KEY
    }
    params = {
        "symbols": symbols,
        "timeframe": timeframe,
        "start": start,
        "end": end,
        "limit": limit,
        "adjustment": adjustment,
        "raw": raw,
        "feed": feed,
        "currency": currency
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        info = json.loads(response.text)
        df = pd.DataFrame(info)

        if 'bars' in df.columns:
            bars_data = [item for sublist in df['bars'] for item in sublist]
            data = pd.DataFrame(bars_data)

            # Rename columns correctly and return the DataFrame
            data = data.rename(columns={'t': 'Time', 'o': 'Open', 'h': 'High', 'l': 'Low', 'c': 'Close', 'v': 'Volume',
                                        'n': 'Trade count', 'vw': 'Vwap'})
            # Ensure 'Time' is the index and is in datetime format
            data['Time'] = pd.to_datetime(data['Time'])
            data.set_index('Time', inplace=True)

            return data
    else:
        return pd.DataFrame()


def describe_get_historical_bars_function():
    """
    Returns the description of the get_historical_bars function.
    """
    return {
        "name": "getHistoricalBars",
        "description": "Retrieve historical stock bars data from Alpaca API",
        "parameters": {
            "type": "object",
            "properties": {
                "symbols": {
                    "type": "string",
                    "description": "Comma separated list of symbols"
                },
                "timeframe": {
                    "type": "string",
                    "description": "The timeframe of the bar aggregation"
                },
                "start": {
                    "type": "string",
                    "description": "The inclusive start of the interval"
                },
                "end": {
                    "type": "string",
                    "description": "The inclusive end of the interval"
                },
                "limit": {
                    "type": "int",
                    "description": "Number of maximum data points to return in a response"
                },
                "adjustment": {
                    "type": "string",
                    "description": "Specifies the corporate action adjustment for the stocks"
                },
                "raw": {
                    "type": "string",
                    "description": "The asof date of the queried stock symbol(s) in YYYY-MM-DD format"
                },
                "feed": {
                    "type": "string",
                    "description": "The source feed of the data (iex)"
                },
                "currency": {
                    "type": "string",
                    "description": "The currency of all prices in ISO 4217 format"
                }
            },
            "required": ["symbols", "timeframe"]
        }
    }


def get_latest_bars(symbols, feed='iex', currency="USD"):
    """
    Retrieves the latest minute-aggregated historical bar data for the provided ticker symbols.
    """
    url = "https://data.alpaca.markets/v2/stocks/bars/latest"
    headers = {
        "accept": "application/json",
        "APCA-API-KEY-ID": APCA_API_KEY,
        "APCA-API-SECRET-KEY": APCA_API_SECRET_KEY
    }
    params = {
        "symbols": symbols,
        "feed": feed,
        "currency": currency
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        return {"error": "Failed to retrieve latest bars data"}


def describe_get_latest_bars_function():
    """
    Returns the description of the get_latest_bars function.
    """
    return {
        "name": "getLatestBars",
        "description": "Retrieve the latest minute-aggregated historical bar data for ticker symbols",
        "parameters": {
            "type": "object",
            "properties": {
                "symbols": {
                    "type": "string",
                    "description": "Comma separated list of symbols",
                },
                "feed": {
                    "type": "string",
                    "description": "Source feed of the data (optional)"
                },
                "currency": {
                    "type": "string",
                    "description": "Currency of all prices in ISO 4217 format (default is USD)"
                }
            },
            "required": ["symbols"]
        }
    }


def get_condition_codes(ticktype, tape):
    """
    Retrieves condition codes and names from the Alpaca API.
    """
    url = f"https://data.alpaca.markets/v2/stocks/meta/conditions/{ticktype}"
    params = {"tape": tape}
    headers = {
        "accept": "application/json",
        "APCA-API-KEY-ID": APCA_API_KEY,
        "APCA-API-SECRET-KEY": APCA_API_SECRET_KEY
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        return {"error": "Failed to retrieve condition codes"}


def describe_get_condition_codes_function():
    """
    Returns the description of the get_condition_codes function.
    """
    return {
        "name": "getConditionCodes",
        "description": "Retrieve condition codes and names from Alpaca API",
        "parameters": {
            "type": "object",
            "properties": {
                "ticktype": {"type": "string"},
                "tape": {"type": "string"}
            },
            "required": ["ticktype", "tape"]
        }
    }


def get_historical_quotes(symbols, start=None, end=None, limit=1000, asof=None, feed="iex", page_token=None,
                          sort="asc"):
    """
    Retrieves historical stock quotes data for a list of stock symbols between specified dates.

    Args:
        symbols (str): Comma-separated list of symbols.
        start (str, optional): Inclusive start of the interval in RFC-3339 or YYYY-MM-DD format.
        end (str, optional): Inclusive end of the interval in RFC-3339 or YYYY-MM-DD format.
        limit (int, optional): Number of maximum data points to return in a response.
        asof (str, optional): The asof date of the queried stock symbol(s) in YYYY-MM-DD format.
        feed (str, optional): The source feed of the data. Options: 'sip' (all US exchanges), 'iex' (Investors Exchange), 'otc' (over the counter exchanges).
        page_token (str, optional): Pagination token to continue from.
        sort (str, optional): Sort data in ascending ('asc') or descending ('desc') order.

    Returns:
        dict: Historical stock quotes data.
    """
    url = "https://data.alpaca.markets/v2/stocks/quotes"
    headers = {
        "accept": "application/json",
        "APCA-API-KEY-ID": APCA_API_KEY,
        "APCA-API-SECRET-KEY": APCA_API_SECRET_KEY
    }
    params = {
        "symbols": symbols,
        "start": start,
        "end": end,
        "limit": limit,
        "asof": asof,
        "feed": feed,
        "page_token": page_token,
        "sort": sort
    }

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        return {"error": "Failed to retrieve historical quotes data"}


def describe_get_historical_quotes_function():
    """
    Returns the description of the get_historical_quotes function.
    """
    return {
        "name": "getHistoricalQuotes",
        "description": "Retrieve historical stock quotes data from Alpaca API",
        "parameters": {
            "type": "object",
            "properties": {
                "symbols": {"type": "string"},
                "start": {"type": "string",
                          "description": "Inclusive start of the interval in RFC-3339 or YYYY-MM-DD format."},
                "end": {"type": "string",
                        "description": "Inclusive end of the interval in RFC-3339 or YYYY-MM-DD format."},
                "limit": {"type": "integer", "description": "Number of maximum data points to return in a response."},
                "asof": {"type": "string",
                         "description": "The asof date of the queried stock symbol(s) in YYYY-MM-DD format."},
                "feed": {"type": "string", "description": "The source feed of the data."},
                "page_token": {"type": "string", "description": "Pagination token to continue from."},
                "sort": {"type": "string",
                         "description": "Sort data in ascending ('asc') or descending ('desc') order."}
            },
            "required": ["symbols"]
        }
    }


def get_snapshots(symbols, feed='iex'):
    """
    Retrieves snapshots of multiple tickers from the Alpaca API.

    Args:
        symbols (str): Comma separated list of symbols.
        feed (str): The source feed of the data. 'sip' contains all US exchanges, 'iex' contains only the Investors Exchange, 'otc' contains over the counter exchanges. Default is 'iex'.
        .

    Returns:
        dict: Snapshot data for the given symbols.
    """
    url = "https://data.alpaca.markets/v2/stocks/snapshots"
    params = {
        "symbols": symbols,
        "feed": feed,

    }
    headers = {
        "accept": "application/json"
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        return json.loads(response.text)
    else:
        return {"error": f"Failed to retrieve snapshots data for symbols: {symbols}"}


def describe_get_snapshots_function():
    return {
        "name": "getSnapshots",
        "description": "Retrieve snapshots of multiple tickers from Alpaca API",
        "parameters": {
            "type": "object",
            "properties": {
                "symbols": {"type": "string", "description": "Comma separated list of symbols"},
                "feed": {"type": "string", "description": "Source feed of the data (Default: 'iex')"},

            },
            "required": ["symbols"]
        }
    }


def get_historical_trades(symbols, start=None, end=None, limit=1000, asof=None, feed='iex', ):
    """
    Retrieves historical trade data for multiple stock symbols from the Alpaca API.

    Args:
        symbols (str): Comma separated list of symbols.
        start (str): The inclusive start of the interval in RFC-3339 or YYYY-MM-DD format. Default is None.
        end (str): The inclusive end of the interval in RFC-3339 or YYYY-MM-DD format. Default is None.
        limit (int): Number of maximum data points to return in a response. Default is 1000.
        asof (str): The asof date in YYYY-MM-DD format. Default is None.
        feed (str): The source feed of the data. 'sip' contains all US exchanges, 'iex' contains only the Investors Exchange, 'otc' contains over the counter exchanges. Default is 'iex'..

    Returns:
        dict: Historical trade data for the given symbols.
    """
    url = "https://data.alpaca.markets/v2/stocks/trades"
    params = {
        "symbols": symbols,
        "start": start,
        "end": end,
        "limit": limit,
        "asof": asof,
        "feed": feed,

    }
    headers = {
        "accept": "application/json"
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        return json.loads(response.text)
    else:
        return {"error": f"Failed to retrieve historical trade data for symbols: {symbols}"}


def describe_get_historical_trades_function():
    """
    Returns the description of the get_historical_trades function.
    """
    return {
        "name": "getHistoricalTrades",
        "description": "Retrieve historical trade data for multiple stock symbols from Alpaca API",
        "parameters": {
            "type": "object",
            "properties": {
                "symbols": {"type": "string", "description": "Comma separated list of symbols"},
                "start": {"type": "string", "description": "Inclusive start of the interval (RFC-3339 or YYYY-MM-DD)"},
                "end": {"type": "string", "description": "Inclusive end of the interval (RFC-3339 or YYYY-MM-DD)"},
                "limit": {"type": "integer", "description": "Maximum data points to return (Default: 1000)"},
                "asof": {"type": "string", "description": "Asof date in YYYY-MM-DD format"},
                "feed": {"type": "string", "description": "Source feed of the data (Default: 'iex')"},

            },
            "required": ["symbols"]
        }
    }


def get_latest_trades(symbols, feed='iex'):
    """
    Retrieves the latest historical trade data for multiple ticker symbols from the Alpaca API.

    Args:
        symbols (str): Comma separated list of symbols.
        feed (str): The source feed of the data. Defaults to 'sip'.


    Returns:
        dict: The latest trade data for the specified symbols.
    """
    url = f"https://data.alpaca.markets/v2/stocks/trades/latest?symbols={symbols}&feed={feed}"
    headers = {
        "accept": "application/json",
        "APCA-API-KEY-ID": APCA_API_KEY,
        "APCA-API-SECRET-KEY": APCA_API_SECRET_KEY
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        return {"error": "Failed to retrieve latest trade data"}


def describe_get_latest_trades_function():
    """
    Returns the description of the get_latest_trades function.
    """
    return {
        "name": "getLatestTrades",
        "description": "Retrieve the latest historical trade data for multiple ticker symbols from Alpaca API",
        "parameters": {
            "type": "object",
            "properties": {
                "symbols": {"type": "string", "description": "Comma separated list of symbols"},
                "feed": {"type": "string", "description": "The source feed of the data (default: 'iex')"},

            },
            "required": ["symbols"]
        }
    }


def search_videos(query, max_results):
    videos = videos_se(query, max_results)
    downloader = YouTubeTranscriptDownloader(videos)
    text = downloader.download_transcripts()
    return text


def videos_se(query, max_results=5):
    youtube = build('youtube', 'v3', developerKey=yt_api_key)
    request = youtube.search().list(
        q=query,
        part='snippet',
        type='video',
        maxResults=max_results
    )
    response = request.execute()

    return [f"https://www.youtube.com/watch?v={item['id']['videoId']}" for item in response.get('items', [])]


def extract_video_id(url):
    # Extract the video ID from a URL
    try:
        return YouTube(url).video_id
    except Exception as e:
        print(f"Error extracting video ID for {url}: {e}")
        return None


class YouTubeTranscriptDownloader:
    def __init__(self, yt_urls):
        # Accepting multiple URLs
        self.urls = yt_urls

    def download_transcripts(self):
        # Download transcripts for multiple videos
        all_transcripts = {}
        for url in self.urls:
            video_id = extract_video_id(url)
            if video_id:
                try:
                    transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
                    transcript = transcript_list.find_transcript(['en'])
                    transcript_text = transcript.fetch()
                    all_transcripts[url] = [line['text'] for line in transcript_text]
                except NoTranscriptFound:
                    print(f"No English transcript found for {url}")
                except Exception as e:
                    print(f"Error downloading transcript for {url}: {e}")
        return all_transcripts


def describe_search_videos_function():
    """
    Returns the description of the search_videos function.
    """
    return {
        "name": "searchVideos",
        "description": "Search for videos on YouTube using the YouTube Data API v3",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query to find videos."
                },
                "max_results": {
                    "type": "integer",
                    "description": "The maximum number of search results to return.",
                    "default": 3  # Default value for max_results
                }
            }
        }
    }


def process_user_message(prompt, assistant_id):
    thread = client.beta.threads.create()
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=prompt
    )

    # Create a run with additional instructions
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id,
        instructions="Please answer the queries using the knowledge provided in the files. Mark additional information clearly with a different color."
    )

    # Poll for the run to complete and retrieve the assistant's messages
    while run.status not in ["completed", "failed"]:
        if run.status == "requires_action":
            run_status = client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )
            tools_calls.handle_required_action(thread.id, run.id, run_status.required_action)
        if run.status == "completed":
            display_assistant_messages(run, thread)
        time.sleep(1)
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )
    return run, thread


def display_assistant_messages(run, thread):
    messages = client.beta.threads.messages.list(
        thread_id=thread.id
    )

    assistant_messages_for_run = [
        message for message in messages
        if message.run_id == run.id and message.role == "assistant"
    ]

    for message in assistant_messages_for_run:
        full_response = message.content[0].text.value
        return full_response


# talk_to function
def talk_to(target_assistant_id, message):
    run, thread = process_user_message(prompt=message, assistant_id=target_assistant_id)
    full_response = display_assistant_messages(run, thread)
    print(full_response)
    return full_response or "No response received."


def describe_talk_to_function():
    """
    Returns the description of the talk_to function.
    """
    return {
        "name": "talkTo",
        "description": "Communicate with a specified assistant and get its response",
        "parameters": {
            "type": "object",
            "properties": {
                "target_assistant_id": {
                    "type": "string",
                    "description": "The unique identifier of the target assistant."
                },
                "message": {
                    "type": "string",
                    "description": "The message to be sent to the target assistant."
                }
            },
            "required": ["target_assistant_id", "message"]
        }
    }


def assistant_list():
    my_assistants = client.beta.assistants.list(
        order="desc",
        limit=20,
    )

    # Simplified list containing only name and ID of each assistant
    simplified_assistants = []
    for assistanttk in my_assistants.data:
        assistant_info = {
            "id": assistanttk.id,
            "name": assistanttk.name if assistanttk.name else "No Name"
        }
        simplified_assistants.append(assistant_info)

    # Convert the list to JSON string
    return json.dumps(simplified_assistants)


def describe_assistant_list_function():
    """
    Returns the description of the assistant_list function.
    """
    return {
        "name": "assistantList",
        "description": "Retrieves a list of assistants with their IDs and names",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        },
        "returns": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string", "description": "Unique identifier of the assistant"},
                    "name": {"type": "string", "description": "Name of the assistant"}
                }
            },
            "description": "A list of objects, each representing an assistant with its ID and name"
        }
    }


def scrape_economic_data():
    data = []  # List to hold row data
    url = 'https://www.economy.com/united-states/indicators'

    try:
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table', {'class': 'table geo'})  # Replace with the actual class or ID
        rows = table.find_all('tr')

        for row in rows:
            row_data = {}
            cells = row.find_all(['th', 'td'])

            # Adjust the indices and keys based on your table structure
            if len(cells) > 1:
                row_data['Indicator'] = cells[0].text.strip()
                row_data['Last'] = cells[1].text.strip()
                row_data['Previous'] = cells[2].text.strip()
                row_data['Units'] = cells[3].text.strip()
                row_data['Frequency'] = cells[4].text.strip()
                data.append(row_data)

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

    return json.dumps(data)


def describe_scrape_economic_data_function():
    """
    Returns the description of the scrape_economic_data function.
    """
    return {
        "name": "scrapeEconomicData",
        "description": "Scrapes economic data from a specified website and returns it in a structured format",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        },
        "returns": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "Indicator": {"type": "string", "description": "The economic indicator"},
                    "Last": {"type": "string", "description": "The most recent data for the indicator"},
                    "Previous": {"type": "string", "description": "The previous data for the indicator"},
                    "Units": {"type": "string", "description": "The units of measurement for the indicator"},
                    "Frequency": {"type": "string", "description": "The frequency of data updates for the indicator"}
                }
            },
            "description": "A list of objects, each representing a row of economic data with various attributes"
        }
    }


def bing_search(query):
    headers = {"Ocp-Apim-Subscription-Key": bing_api_key}
    params = {"q": query, "textDecorations": True, "textFormat": "HTML"}
    try:
        response = requests.get("https://api.bing.microsoft.com/v7.0/search", headers=headers, params=params)
        response.raise_for_status()
        search_result = response.json()
        return [result for result in search_result.get("webPages", {}).get("value", [])]
    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return []


def describe_bing_search_function():
    """
    Returns the description of the bing_search function.
    """
    return {
        "name": "bingSearch",
        "description": "Performs a web search using the Bing Search API. It sends a request to the Bing API with the specified query, processes the response, and returns a list of search results.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query string to be sent to the Bing Search API."
                }
            },
            "required": ["query"]

        }
    }


def get_stock_info(ticker_symbol):
    """
    Retrieves comprehensive information for a given stock using the yfinance library.
    """
    stock = yf.Ticker(ticker_symbol)

    # Fetching various stock information
    info = stock.info  # General stock info, which is a dictionary

    # Convert pandas Series to a dictionary with string keys for JSON serialization
    dividends = {str(key): value for key, value in stock.dividends.items()}
    splits = {str(key): value for key, value in stock.splits.items()}

    # Combining all data into a single dictionary
    stock_data = {
        "info": info,
        "dividends": dividends,
        "splits": splits
    }

    return stock_data


def describe_get_stock_info_function():
    """
    Returns the description of the get_stock_info function.
    """
    return {
        "name": "getStockInfo",
        "description": "Retrieve comprehensive information for a specified stock using the yfinance library. This includes general stock information, historical market data, dividends, and stock splits.",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker_symbol": {
                    "type": "string",
                    "description": "The ticker symbol of the stock to retrieve information for."
                }
            },
            "required": ["ticker_symbol"]
        }
    }


async def alpaca_websocket():
    async with websockets.connect('wss://stream.data.alpaca.markets/v2/iex') as websocket:
        # Wait for successful connection
        connection_response = await websocket.recv()
        print("Connection response:", connection_response)

        # Authenticate
        auth_data = {
            "action": "auth",
            "key": APCA_API_KEY,
            "secret": APCA_API_SECRET_KEY
        }
        await websocket.send(json.dumps(auth_data))

        # Wait for authentication success
        auth_response = await websocket.recv()
        auth_response = json.loads(auth_response)
        if auth_response[0]['T'] == 'success' and auth_response[0]['msg'] == 'authenticated':
            print("Authentication successful")
            # Subscribe to data
            subscribe_data = {
                "action": "subscribe",
                "trades": ["AAPL"],
                "quotes": ["AAPL"],
                "updatedBars": ["AAPL"],
                "bars": ["AAPL"]
            }
            await websocket.send(json.dumps(subscribe_data))

            # Receive data
            while True:
                message = await websocket.recv()
                print(message)
        else:
            print("Authentication failed:", auth_response)


def live_data():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(alpaca_websocket())


def create_assistant():
    return client.beta.assistants.create(
        model="gpt-4",
        instructions=" i will see all the tools i have and  i will use the best tool for any questions",
        tools=[]
    )


def create_thread():
    try:
        thread = client.beta.threads.create()

        return thread
    except Exception as e:
        return str(e)


def add_message_to_thread(thread_id, role, content):
    try:
        message = client.beta.threads.messages.create(
            thread_id=thread_id,
            role=role,
            content=content
        )

        return message.id
    except Exception as e:
        return str(e)


def run_assistant(thread_id, assistant_id, instructions=""):
    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id,
        instructions=instructions
    )

    max_retries = 10  # Example retry limit
    retries = 0

    while run.status == "queued" or run.status == "running":
        run = client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run.id
        )

        if retries > max_retries:
            break
        retries += 1

    return run


def check_run_status(thread_id, run_id):
    run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
    return run.status


def wait_for_run_completion(thread_id, run_id, timeout=480):
    start_time = time.time()
    while time.time() - start_time < timeout:
        status = check_run_status(thread_id, run_id)
        if status == 'completed':
            return True
        elif status in ['failed', 'cancelled']:
            return False
        time.sleep(5)  # Wait for 5 seconds before checking again
    return False


def display_assistant_responses(thread_id):
    try:
        # Retrieve the list of messages in the thread
        messages = client.beta.threads.messages.list(
            thread_id=thread_id
        )

        # Iterate over messages to find the assistant's response
        for message in messages:
            # Check if the message is a response to the user's request
            if message.role == 'assistant' and message.run_id is not None:
                # Extract and print the assistant's response
                response_content = message.content[0].text.value
                print("Assistant's Response:\n", response_content)
                return response_content  # Return the response for further use if needed

        print("No response from the assistant found.")
        return None

    except Exception as e:
        print("Error in display_assistant_responses:", str(e))
        return None


def inspect_run_steps(thread_id, run_id):
    try:
        # Retrieve the steps of the run
        run_steps = client.beta.threads.runs.steps.list(
            thread_id=thread_id,
            run_id=run_id
        )

        # Check if the list retrieval was successful
        if run_steps.object == "list":
            for step in run_steps.data:
                # Process and print each step's details
                if step.type == "tool_calls":
                    print(f"Step ID: {step.id}, Status: {step.status}")
                    for tool_call in step.step_details.tool_calls:
                        if tool_call.type == "code":
                            print("Code Input:", tool_call.code.input)
                            print("Code Output:", tool_call.code.outputs)
                            return tool_call.code.input
        else:
            print("Failed to retrieve run steps.")
            return None
    except Exception as e:
        print("Error in inspect_run_steps:", str(e))
        return None


def coder(strategy):
    thread = create_thread()
    assistant = 'asst_607i8z45fVfEYduP0f5cHYYd'

    add_message_to_thread(thread_id=thread.id,
                          role='user',
                          content=strategy)
    active_run = run_assistant(thread_id=thread.id, assistant_id=assistant)

    if wait_for_run_completion(thread_id=thread.id, run_id=active_run.id):
        code = inspect_run_steps(thread.id, active_run.id)
        responses = display_assistant_responses(thread_id=thread.id)

        return responses, code


class Indicator:
    def __init__(self, tick, timeframe, start_dates, end_dates):
        self.ticker = tick
        self.start_date = start_dates
        self.end_date = end_dates
        self.timeframe = timeframe
        self.api_key = APCA_API_KEY
        self.api_secret = APCA_API_SECRET_KEY
        self.data_source = "iex"
        self.data = self.get_data_from_alpaca()

    def get_data_from_alpaca(self):
        base_url = 'https://data.alpaca.markets/v2'
        endpoint = f'/stocks/{self.ticker}/bars'
        url = base_url + endpoint
        headers = {
            'APCA-API-KEY-ID': self.api_key,
            'APCA-API-SECRET-KEY': self.api_secret
        }
        params = {
            'timeframe': self.timeframe,
            'start': self.start_date,  # Ensure correct format
            'end': self.end_date,
            'feed': "iex",  # 'iex' or 'sip'
            'limit': 10000
        }
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            datas = response.json()['bars']
            df = pd.DataFrame(datas)

            # Rename columns to match your existing code if necessary
            df.rename(columns={'c': 'Close', 'o': 'Open', 'h': 'High', 'l': 'Low', 'v': 'Volume'}, inplace=True)

            # Correct timestamp conversion
            df['t'] = pd.to_datetime(df['t'])
            df.set_index('t', inplace=True)

            return df
        else:
            raise Exception(f"Failed to fetch data: {response.status_code}")

    def calculate_rsi(self, window=14):
        delta = self.data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()

        rs = gain / loss
        self.data['RSI'] = 100 - (100 / (1 + rs))
        return self.data['RSI']

    def calculate_sma(self, window=None):
        if window is None:
            window = 20 if self.timeframe == '1D' else 14  # Default window size based on timeframe
        self.data['SMA'] = self.data['Close'].rolling(window=window).mean()
        return self.data['SMA']

    def calculate_macd(self, short_window=12, long_window=26, signal_window=9):
        self.data['EMA_12'] = self.data['Close'].ewm(span=short_window, adjust=False).mean()
        self.data['EMA_26'] = self.data['Close'].ewm(span=long_window, adjust=False).mean()
        self.data['MACD'] = self.data['EMA_12'] - self.data['EMA_26']
        self.data['MACD_Signal'] = self.data['MACD'].ewm(span=signal_window, adjust=False).mean()
        return self.data['MACD'], self.data['MACD_Signal'], self.data['EMA_12'], self.data['EMA_26']

    def calculate_stochastic_oscillator(self, window=14):
        low_min = self.data['Low'].rolling(window=window).min()
        high_max = self.data['High'].rolling(window=window).max()

        self.data['Stochastic'] = 100 * ((self.data['Close'] - low_min) / (high_max - low_min))
        return self.data['Stochastic']

    def calculate_atr(self, window=14):
        high_low = self.data['High'] - self.data['Low']
        high_close = np.abs(self.data['High'] - self.data['Close'].shift())
        low_close = np.abs(self.data['Low'] - self.data['Close'].shift())

        # Create a DataFrame from the three ranges
        ranges = pd.concat([high_low, high_close, low_close], axis=1)

        # Calculate the true range
        true_range = ranges.max(axis=1)

        # Ensure true_range is a Pandas Series before applying the rolling method
        if not isinstance(true_range, pd.Series):
            true_range = pd.Series(true_range)

        # Calculate the Average True Range (ATR)
        self.data['ATR'] = true_range.rolling(window=window).mean()
        return self.data['ATR']

    def calculate_pvi(self):
        pvi = pd.Series(index=self.data.index, data=1000.0)

        for i in range(1, len(self.data)):
            if self.data['Volume'].iloc[i] > self.data['Volume'].iloc[i - 1]:
                pvi.iloc[i] = pvi.iloc[i - 1] + (
                        (self.data['Close'].iloc[i] - self.data['Close'].iloc[i - 1]) / self.data['Close'].iloc[
                    i - 1]) * pvi.iloc[i - 1]
            else:
                pvi.iloc[i] = pvi.iloc[i - 1]

        self.data['PVI'] = pvi
        return self.data['PVI']

    def calculate_nvi(self):
        nvi = pd.Series(index=self.data.index, data=1000.0)

        for i in range(1, len(self.data)):
            if self.data['Volume'].iloc[i] < self.data['Volume'].iloc[i - 1]:
                nvi.iloc[i] = nvi.iloc[i - 1] + (
                        (self.data['Close'].iloc[i] - self.data['Close'].iloc[i - 1]) / self.data['Close'].iloc[
                    i - 1]) * nvi.iloc[i - 1]
            else:
                nvi.iloc[i] = nvi.iloc[i - 1]

        self.data['NVI'] = nvi
        return self.data['NVI']

    def calculate_vpt(self):
        percentage_change = self.data['Close'].pct_change()
        self.data['VPT'] = (percentage_change * self.data['Volume']).cumsum()
        return self.data['VPT']

    def calculate_chaikin_money_flow(self, period=20):
        money_flow_multiplier = ((self.data['Close'] - self.data['Low']) - (self.data['High'] - self.data['Close'])) / (
                self.data['High'] - self.data['Low'])
        money_flow_volume = money_flow_multiplier * self.data['Volume']
        self.data['CMF'] = money_flow_volume.rolling(window=period).sum() / self.data['Volume'].rolling(
            window=period).sum()
        return self.data['CMF']

    def calculate_accumulation_distribution(self):
        mfm = ((self.data['Close'] - self.data['Low']) - (self.data['High'] - self.data['Close'])) / (
                self.data['High'] - self.data['Low'])
        mfv = mfm * self.data['Volume']
        self.data['ADL'] = mfv.cumsum()
        return self.data['ADL']

    def calculate_vwap(self):
        cum_vol = self.data['Volume'].cumsum()
        cum_vol_price = (self.data['Volume'] * self.data['Close']).cumsum()
        self.data['VWAP'] = cum_vol_price / cum_vol
        return self.data['VWAP']

    def calculate_obv(self):
        self.data['OBV'] = (np.sign(self.data['Close'].diff()) * self.data['Volume']).fillna(0).cumsum()

        # Define a function to categorize the trend
        def categorize_trend(row):
            if row['Price Change'] > 0 and row['Volume Change'] > 0:
                return 'Bullish'
            elif row['Price Change'] > 0 and row['Volume Change'] <= 0:
                return 'Caution- weak hands buying'
            elif row['Price Change'] <= 0 and row['Volume Change'] > 0:
                return 'Bearish'
            elif row['Price Change'] <= 0 and row['Volume Change'] <= 0:
                return 'Caution- weak hands selling'
            else:
                return 'Indeterminate'

        # Apply the categorization function
        self.data['Trend'] = self.data.apply(categorize_trend, axis=1)
        return self.data['Trend'], self.data['OBV']

    def calculate_volume_rsi(self, window=14):
        volume_change = self.data['Volume'].diff()
        self.data['Volume Gain'] = volume_change.where(volume_change > 0, 0).rolling(window=window).mean()
        self.data['Volume Loss'] = -volume_change.where(volume_change < 0, 0).rolling(window=window).mean()

        rs = self.data['Volume Gain'] / self.data['Volume Loss']
        self.data['Volume RSI'] = 100 - (100 / (1 + rs))
        return self.data['Volume Gain'], self.data['Volume Loss']

    def calculate_mfi(self, window=14):
        typical_price = (self.data['High'] + self.data['Low'] + self.data['Close']) / 3
        raw_money_flow = typical_price * self.data['Volume']

        positive_flow = raw_money_flow.where(typical_price > typical_price.shift(), 0)
        negative_flow = raw_money_flow.where(typical_price < typical_price.shift(), 0)

        positive_flow_sum = positive_flow.rolling(window=window).sum()
        negative_flow_sum = negative_flow.rolling(window=window).sum()

        mfi_ratio = positive_flow_sum / negative_flow_sum
        self.data['MFI'] = 100 - (100 / (1 + mfi_ratio))
        return self.data['MFI']

    def calculate_ease_of_movement(self, window=14):
        high_low_diff = self.data['High'] - self.data['Low']
        move = (high_low_diff / 2) - ((self.data['Close'] - self.data['Close'].shift()) / 2)
        box_ratio = (self.data['Volume'] / 1000000) / (self.data['High'] - self.data['Low'])

        self.data['EOM'] = move / box_ratio
        self.data['EOM_SMA'] = self.data['EOM'].rolling(window=window).mean()
        return self.data['EOM'], self.data['EOM_SMA']

    def analyze_price_volume_trend(self):
        # Calculate Price and Volume Changes
        self.data['Price Change'] = self.data['Close'].diff()
        self.data['Volume Change'] = self.data['Volume'].diff()
        return self.data['Price Change']

    def add_statistics(self):
        # Calculate basic statistics for 'Close' prices
        self.data['Count'] = self.data['Close'].count()
        self.data['Mean'] = self.data['Close'].mean()
        self.data['Std Dev'] = self.data['Close'].std()
        self.data['Variance'] = self.data['Close'].var()
        self.data['Min'] = self.data['Close'].min()
        self.data['25th Percentile'] = self.data['Close'].quantile(0.25)
        self.data['Median'] = self.data['Close'].median()
        self.data['75th Percentile'] = self.data['Close'].quantile(0.75)
        self.data['Max'] = self.data['Close'].max()
        return self.data['Count'], self.data['Mean'], self.data['Std Dev'], self.data['Variance'], self.data['Min'], \
               self.data['25th Percentile'], self.data['Median'], self.data['75th Percentile'], self.data['Max']

    def get_data(self):
        self.get_data_from_alpaca()
        self.calculate_rsi()
        self.calculate_sma()
        self.calculate_macd()
        self.calculate_accumulation_distribution()
        self.calculate_atr()
        self.calculate_chaikin_money_flow()
        self.calculate_ease_of_movement()
        self.calculate_mfi()
        self.calculate_stochastic_oscillator()
        self.calculate_pvi()
        self.calculate_nvi()
        self.calculate_vpt()
        self.calculate_vwap()
        self.calculate_volume_rsi()
        self.add_statistics()
        self.analyze_price_volume_trend()
        self.calculate_obv()
        return self.data[
            ['RSI', 'SMA', 'MACD', 'ADL', 'ATR', 'CMF', 'EOM', 'EOM_SMA', 'MFI', 'Stochastic', 'PVI', 'NVI', 'VPT',
             'VWAP', 'Volume Gain', 'Volume Loss', 'Count', 'Mean', 'Std Dev', 'Variance', 'Min', '25th Percentile',
             'Median', '75th Percentile', 'Max']]


def generate_text(prompt, model="gpt-3.5-turbo", messages=None):
    if messages is None:
        messages = []
    try:

        response = client.chat.completions.create(
            model=model,
            messages=messages + [{"role": "user", "content": prompt}]
        )

        return response['choices'][0]['message']['content']
    except Exception as e:
        return str(e)


def attach_file_to_message(thread_id, message_content, file_path):
    try:
        # Upload a file with an "assistants" purpose
        file = client.files.create(
            file=open(file_path, "rb"),
            purpose='assistants'
        )

        # Create a message with the file attached in the specified thread
        message = client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=message_content,
            file_ids=[file.id]
        )

        return message.id
    except Exception as e:
        return str(e)


def save_audio_to_file(response, output_file="output.mp3"):
    try:
        speech_file_path = Path(output_file)
        response.stream_to_file(speech_file_path)
        return str(speech_file_path)
    except Exception as e:
        return str(e)


def generate_audio(model="tts-1", voice: Literal["alloy", "echo", "fable", "onyx", "nova", "shimmer"] = "alloy",
                   input_text=""):
    try:
        response = client.audio.speech.create(
            model=model,
            voice=voice,
            input=input_text
        )
        return response
    except Exception as e:
        return str(e)


def transcribe_audio(model="whisper-1", input_file_path="input.mp3",
                     response_format: Literal["json", "text", "srt", "verbose_json", "vtt"] = "json"):
    try:
        with open(input_file_path, "rb") as audio_file:
            response = client.audio.transcriptions.create(
                model=model,
                file=audio_file,
                response_format=response_format
            )
        return response
    except Exception as e:
        return str(e)


def translate_and_transcribe_audio(model="whisper-1", input_file_path="input.mp3", response_format="json"):
    try:
        with open(input_file_path, "rb") as audio_file:
            response = client.audio.translations.create(
                model=model,
                file=audio_file,
                response_format=response_format
            )
        return response
    except Exception as e:
        return str(e)


class AssistantWithFunctions:
    def __init__(self, ):
        self.client = client

    def create_assistant(self, name, instructions, model, functions):
        try:
            assistant = self.client.beta.assistants.create(
                name=name,
                instructions=instructions,
                model=model,
                tools=[{"type": "function", "function": function} for function in functions]
            )
            return assistant
        except Exception as e:
            logging.error(f"Error creating assistant: {e}")
            return None  # Or raise the exception again

    def create_run(self, thread_id, assistant_id, model=None, instructions=None, tools=None, metadata=None):
        try:
            response = self.client.beta.threads.runs.create(
                thread_id=thread_id,
                assistant_id=assistant_id,
                model=model,
                instructions=instructions,
                tools=tools,
                metadata=metadata
            )
            return response
        except Exception as e:
            return str(e)

    def get_functions_called(self, thread_id, run_id):
        try:
            run = self.client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run_id
            )

            if run["status"] == "requires_action":
                required_action = run["required_action"]
                if required_action["type"] == "submit_tool_outputs":
                    tool_calls = required_action["submit_tool_outputs"]["tool_calls"]
                    function_calls = []

                    for tool_call in tool_calls:
                        if tool_call["type"] == "function":
                            function_calls.append(tool_call["function"])

                    return function_calls

            return None
        except Exception as e:
            return str(e)

    def submit_function_outputs(self, thread_id, run_id, tool_call_id, output):
        try:
            response = self.client.beta.threads.runs.submit_tool_outputs(
                thread_id=thread_id,
                run_id=run_id,
                tool_outputs=[
                    {
                        "tool_call_id": tool_call_id,
                        "output": output,
                    }
                ]
            )
            return response
        except Exception as e:
            return str(e)


class CodeInterpreterAssistant:
    def __init__(self):
        self.client = client
        self.assistant_id = None

    def enable_code_interpreter(self, name, instructions, model):
        try:
            # Create an Assistant with Code Interpreter enabled
            assistant = self.client.beta.assistants.create(
                name=name,
                instructions=instructions,
                model=model,
                tools=[{"type": "code_interpreter"}]
            )
            self.assistant_id = assistant.id
            return self.assistant_id
        except Exception as e:
            return str(e)

    def attach_file_to_assistant(self, file_path):
        try:
            # Upload a file with an "assistants" purpose
            file = self.client.files.create(
                file=open(file_path, "rb"),
                purpose='assistants'
            )

            # Attach the file to the Assistant
            assistant = self.client.beta.assistants.update(
                assistant_id=self.assistant_id,
                file_ids=[file.id]
            )

            return assistant.id
        except Exception as e:
            return str(e)


class KnowledgeRetrievalAssistant:
    def __init__(self):
        self.client = client
        self.assistant_id = None

    def enable_retrieval(self, name, instructions, model):
        try:
            # Create an Assistant with Retrieval enabled
            assistant = self.client.beta.assistants.create(
                name=name,
                instructions=instructions,
                model=model,
                tools=[{"type": "retrieval"}]
            )
            self.assistant_id = assistant.id
            return self.assistant_id
        except Exception as e:
            return str(e)

    def attach_file_to_assistant(self, file_path):
        try:
            # Upload a file with an "assistants" purpose
            file = self.client.files.create(
                file=open(file_path, "rb"),
                purpose='assistants'
            )

            # Attach the file to the Assistant
            assistant = self.client.beta.assistants.update(
                assistant_id=self.assistant_id,
                file_ids=[file.id]
            )

            return assistant.id
        except Exception as e:
            return str(e)

    def attach_file_to_message(self, thread_id, message_content, file_path):
        try:
            # Upload a file with an "assistants" purpose
            file = self.client.files.create(
                file=open(file_path, "rb"),
                purpose='assistants'
            )

            # Create a message with the file attached in the specified thread
            message = self.client.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=message_content,
                file_ids=[file.id]
            )

            return message.id
        except Exception as e:
            return str(e)


class ImagesAPI:
    def __init__(self):
        self.client = client

    def generate_image(self, model: str, prompt: str, size: Literal["1024x1024", "1792x1024", "1024x1792"],
                       quality: Literal["standard", "hd"], n: int = 1):
        try:
            response = self.client.images.generate(
                model=model,
                prompt=prompt,
                size=size,
                quality=quality,
                n=n,
            )
            return response.data
        except Exception as e:
            return str(e)

    def edit_image(self, model: str, image_path: str, mask_path: str, prompt: str, size: Literal["1024x1024"],
                   n: int = 1):
        try:
            response = self.client.images.edit(
                model=model,
                image=open(image_path, "rb"),
                mask=open(mask_path, "rb"),
                prompt=prompt,
                size=size,
                n=n,
            )
            return response.data
        except Exception as e:
            return str(e)

    def create_image_variation(self, image_path: str, size: Literal["1024x1024"] = "1024x1024", n: int = 1):
        try:
            response = self.client.images.create_variation(
                image=open(image_path, "rb"),
                n=n,
                size=size,
            )
            return response.data
        except Exception as e:
            return str(e)


class VisionAPI:
    def __init__(self):
        self.client = client

    def ask_question_about_image(self, image_url, question, detail="auto", max_tokens=300):
        try:
            response = self.client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": question},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": image_url,
                                    "detail": detail
                                },
                            },
                        ],
                    }
                ],
                max_tokens=max_tokens,
            )
            return response.choices[0]
        except Exception as e:
            return str(e)

    def ask_question_about_images(self, image_urls, question, detail="auto", max_tokens=300):
        try:
            image_messages = [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": image_url,
                        "detail": detail
                    },
                }
                for image_url in image_urls
            ]

            response = self.client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": question},
                        ],
                    },
                    *image_messages
                ],
                max_tokens=max_tokens,
            )
            return response.choices[0]
        except Exception as e:
            return str(e)

    @staticmethod
    def encode_image(image_path):
        import base64
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def ask_question_about_encoded_image(self, base64_image, question, detail="auto", max_tokens=300):
        try:
            response = self.client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": question},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}",
                                    "detail": detail
                                },
                            },
                        ],
                    }
                ],
                max_tokens=max_tokens,
            )
            return response.choices[0]
        except Exception as e:
            return str(e)


class AssistantManager:
    def __init__(self):
        self.client = OpenAI()

    def retrieve_assistant(self, assistant_id: str):
        try:
            return self.client.beta.assistants.retrieve(assistant_id)
        except Exception as e:
            return str(e)

    def modify_assistant(self, assistant_id: str, model: str = "gpt-4", name: str = None, description: str = None,
                         instructions: str = None, tools: list = None, file_ids: list = None):
        if tools is None:
            tools = []
        if file_ids is None:
            file_ids = []

        try:
            return self.client.beta.assistants.update(
                assistant_id,
                model=model,
                name=name,
                description=description,
                instructions=instructions,
                tools=tools,
                file_ids=file_ids,
            )
        except Exception as e:
            return str(e)

    def delete_assistant(self, assistant_id: str):
        try:
            return self.client.beta.assistants.delete(assistant_id)
        except Exception as e:
            return str(e)

    def list_assistants(self, limit: int = 20, order: Literal["asc", "desc"] = "desc", after: str = None,
                        before: str = None):
        try:
            return self.client.beta.assistants.list(
                limit=limit,
                order=order,
                after=after,
                before=before,
            )
        except Exception as e:
            return str(e)


class AssistantFile:
    def __init__(self):
        self.client = client

    def create_file(self, assistant_id, file_id):
        try:
            response = self.client.beta.assistants.files.create(
                assistant_id=assistant_id,
                file_id=file_id
            )
            return response
        except Exception as e:
            return str(e)

    def retrieve_file(self, assistant_id, file_id):
        try:
            response = self.client.beta.assistants.files.retrieve(
                assistant_id=assistant_id,
                file_id=file_id
            )
            return response
        except Exception as e:
            return str(e)

    def delete_file(self, assistant_id, file_id):
        try:
            response = self.client.beta.assistants.files.delete(
                assistant_id=assistant_id,
                file_id=file_id
            )
            return response
        except Exception as e:
            return str(e)

    def list_files(self, assistant_id, limit=20, order: Literal["asc", "desc"] = "desc", after=None, before=None):
        try:
            response = self.client.beta.assistants.files.list(
                assistant_id=assistant_id,
                limit=limit,
                order=order,
                after=after,
                before=before
            )
            return response
        except Exception as e:
            return str(e)


class ThreadsBeta:
    def __init__(self):
        self.client = client

    def create_thread(self, messages=None, metadata=None):
        try:
            response = self.client.beta.threads.create(messages=messages, metadata=metadata)
            return response
        except Exception as e:
            return str(e)

    def retrieve_thread(self, thread_id):
        try:
            response = self.client.beta.threads.retrieve(thread_id)
            return response
        except Exception as e:
            return str(e)

    def modify_thread(self, thread_id, metadata=None):
        try:
            response = self.client.beta.threads.update(thread_id, metadata=metadata)
            return response
        except Exception as e:
            return str(e)

    def delete_thread(self, thread_id):
        try:
            response = self.client.beta.threads.delete(thread_id)
            return response
        except Exception as e:
            return str(e)


class MessagesBeta:
    def __init__(self):
        self.client = client

    def create_message(self, thread_id, role, content, file_ids=None, metadata=None):
        try:
            response = self.client.beta.threads.messages.create(
                thread_id=thread_id,
                role=role,
                content=content,
                file_ids=file_ids,
                metadata=metadata
            )
            return response
        except Exception as e:
            return str(e)

    def retrieve_message(self, thread_id, message_id):
        try:
            response = self.client.beta.threads.messages.retrieve(
                thread_id=thread_id,
                message_id=message_id
            )
            return response
        except Exception as e:
            return str(e)

    def modify_message(self, thread_id, message_id, metadata=None):
        try:
            response = self.client.beta.threads.messages.update(
                thread_id=thread_id,
                message_id=message_id,
                metadata=metadata
            )
            return response
        except Exception as e:
            return str(e)

    def list_messages(self, thread_id, limit=20, order=None, after=None, before=None):
        try:
            # Ensure that order is one of the expected values or None
            if order not in ("asc", "desc", None):
                raise ValueError("Invalid value for 'order'. Use 'asc', 'desc', or None.")

            response = self.client.beta.threads.messages.list(
                thread_id=thread_id,
                limit=limit,
                order=order,
                after=after,
                before=before
            )
            return response
        except Exception as e:
            return str(e)

    def retrieve_message_file(self, thread_id, message_id, file_id):
        try:
            response = self.client.beta.threads.messages.files.retrieve(
                thread_id=thread_id,
                message_id=message_id,
                file_id=file_id
            )
            return response
        except Exception as e:
            return str(e)

    def list_message_files(self, thread_id, message_id, limit=20, order=None, after=None, before=None):
        try:
            # Ensure that order is one of the expected values or None
            if order not in ("asc", "desc", None):
                raise ValueError("Invalid value for 'order'. Use 'asc', 'desc', or None.")

            response = self.client.beta.threads.messages.files.list(
                thread_id=thread_id,
                message_id=message_id,
                limit=limit,
                order=order,
                after=after,
                before=before
            )
            return response
        except Exception as e:
            return str(e)


class OpenAIRuns:
    def __init__(self):
        self.client = client

    # Create a new run
    def create_run(self, thread_id, assistant_id, model=None, instructions=None, tools=None, metadata=None):
        try:
            response = self.client.beta.threads.runs.create(
                thread_id=thread_id,
                assistant_id=assistant_id,
                model=model,
                instructions=instructions,
                tools=tools,
                metadata=metadata
            )
            return response
        except Exception as e:
            return str(e)

    # Retrieve a run by its ID
    def get_run(self, thread_id, run_id):
        try:
            response = self.client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run_id
            )
            return response
        except Exception as e:
            return str(e)

    # Modify a run by updating its metadata
    def update_run(self, thread_id, run_id, metadata):
        try:
            response = self.client.beta.threads.runs.update(
                thread_id=thread_id,
                run_id=run_id,
                metadata=metadata
            )
            return response
        except Exception as e:
            return str(e)

    # List all runs in a thread
    def list_runs(self, thread_id, limit=20, order: Literal["asc", "desc"] = "desc", after: Optional[str] = None,
                  before: Optional[str] = None):
        try:
            response = self.client.beta.threads.runs.list(
                thread_id=thread_id,
                limit=limit,
                order=order,
                after=after,
                before=before
            )
            return response
        except Exception as e:
            return str(e)

    # Submit tool outputs for a run
    def submit_tool_outputs(self, thread_id, run_id, tool_outputs):
        try:
            response = self.client.beta.threads.runs.submit_tool_outputs(
                thread_id=thread_id,
                run_id=run_id,
                tool_outputs=tool_outputs
            )
            return response
        except Exception as e:
            return str(e)

    # Cancel a run
    def cancel_run(self, thread_id, run_id):
        try:
            response = self.client.beta.threads.runs.cancel(
                thread_id=thread_id,
                run_id=run_id
            )
            return response
        except Exception as e:
            return str(e)

    # Create a thread and run it in one request
    def create_and_run(self, assistant_id, thread_data, model=None, instructions=None, tools=None, metadata=None):
        try:
            response = self.client.beta.threads.create_and_run(
                assistant_id=assistant_id,
                thread={
                    "messages": thread_data
                },
                model=model,
                instructions=instructions,
                tools=tools,
                metadata=metadata
            )
            return response
        except Exception as e:
            return str(e)

    # Retrieve a run step by its ID
    def get_run_step(self, thread_id, run_id, step_id):
        try:
            response = self.client.beta.threads.runs.steps.retrieve(
                thread_id=thread_id,
                run_id=run_id,
                step_id=step_id
            )
            return response
        except Exception as e:
            return str(e)

    # List all run steps in a run
    def list_run_steps(self, thread_id, run_id, limit=20, order: Literal["asc", "desc"] = "desc",
                       after: Optional[str] = None, before: Optional[str] = None):
        try:
            response = self.client.beta.threads.runs.steps.list(
                thread_id=thread_id,
                run_id=run_id,
                limit=limit,
                order=order,
                after=after,
                before=before
            )
            return response
        except Exception as e:
            return str(e)


class Embeddings:
    def __init__(self):
        self.client = client

    def create_embedding(
            self,
            model: str,
            input_text: Union[str, list],
            encoding_format: Literal["float", "base64", None] = None
    ):
        try:
            response = self.client.embeddings.create(
                model=model,
                input=input_text,
                encoding_format=encoding_format
            )
            return response
        except Exception as e:
            return str(e)


class FineTuning:
    def __init__(self):
        self.client = client

    def create_job(
            self,
            model: str,
            training_file: str,
            hyperparameters: dict = None,
            suffix: str = None,
            validation_file: str = None
    ):
        try:
            response = self.client.fine_tuning.jobs.create(
                model=model,
                training_file=training_file,
                hyperparameters=hyperparameters,
                suffix=suffix,
                validation_file=validation_file
            )
            return response
        except Exception as e:
            return str(e)

    def list_jobs(
            self,
            after: str = None,
            limit: int = 20
    ):
        try:
            response = self.client.fine_tuning.jobs.list(
                after=after,
                limit=limit
            )
            return response
        except Exception as e:
            return str(e)

    def retrieve_job(self, job_id: str):
        try:
            response = self.client.fine_tuning.jobs.retrieve(job_id)
            return response
        except Exception as e:
            return str(e)

    def cancel_job(self, job_id: str):
        try:
            response = self.client.fine_tuning.jobs.cancel(job_id)
            return response
        except Exception as e:
            return str(e)

    def list_events(
            self,
            fine_tuning_job_id: str,
            after: str = None,
            limit: int = 20
    ):
        try:
            response = self.client.fine_tuning.jobs.list_events(
                fine_tuning_job_id=fine_tuning_job_id,
                after=after,
                limit=limit
            )
            return response
        except Exception as e:
            return str(e)
