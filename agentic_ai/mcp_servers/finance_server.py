from mcp.server import FastMCP

mcp = FastMCP(
    "User Server",
    host="127.0.0.1",
    port=8001
)

@mcp.tool()
def get_exchange_rate(
        from_currency: str,
        to_currency: str
) -> dict:
    rates = {
        "USD_INR": 88.0,
        "EUR_INR": 103.0,
        "GBP_INR": 119.0,
        "INR_USD": 0.0114,
        "INR_EUR": 0.0097,
        "INR_GBP": 0.0084
    }

    key = f"{from_currency.upper()}_{to_currency.upper()}"

    if key not in rates:
        return {
            "error": (
                f"Exchange rate not available for "
                f"{from_currency} to {to_currency}"
            )
        }

    return {
        "from": from_currency.upper(),
        "to": to_currency.upper(),
        "rate": rates[key]
    }


# mcp run AI_AGENTS\weather_server.py --transport streamable-http

if __name__ == "__main__":
    mcp.run("streamable-http")

# if __name__ == "__main__":
#     mcp.run("streamable-http", port=8001)

# if __name__ == "__main__":
#     mcp.run("streamable-http", port=8001)
