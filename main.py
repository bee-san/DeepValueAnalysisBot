import discord
import os
import requests
import main2
from lxml import html
import json
from collections import OrderedDict

client = discord.Client()


@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("$hello"):
        await message.channel.send("Hello!")

    if message.content.startswith("$sentiment"):
        try:
            ticker = message.content.split(" ")[1]
            main2.create_sent_image([ticker])
            await message.channel.send(file=discord.File("analysis.png"))
        except:
            await message.channel.send("Error. Probably not a ticker.")
    if message.content.startswith("$dcf"):
        ticker = message.content.split(" ")[1]
        await message.channel.send(dcf(ticker))


def dcf(ticker):
    data = parse(ticker)
    dcf_analysis = ""
    graham_analysis = ""
    try:
        graham_analysis = "Graham Analysis\n" + graham(data)
    except:
        return "Error: EPS < 1.0."
    try:
        dcf_analysis = dcf_calculate(data)
    except:
        return "Error: EPS < 1.0."
    return (
        "WARNING: This is not investment advice. No single algorithm can state the true fair value. Do not trust this without doing your own search. \n\n"
        + graham_analysis
        + "\n\nMy Algorithm"
        + dcf_analysis
    )


def parse(ticker):
    url = "https://stockanalysis.com/stocks/{}/financials/cash-flow-statement".format(
        ticker
    )
    response = requests.get(url, verify=False)
    parser = html.fromstring(response.content)
    fcfs = parser.xpath(
        '//table[contains(@id,"fintable")]//tr[td/span/text()[contains(., "Free Cash Flow")]]'
    )[0].xpath(".//td/text()")

    last_fcf = float(fcfs[0].replace(",", ""))

    url = "https://in.finance.yahoo.com/quote/{}/analysis?p={}".format(ticker, ticker)
    response = requests.get(url, verify=False)
    parser = html.fromstring(response.content)
    ge = parser.xpath("//table//tbody//tr")

    for row in ge:
        label = row.xpath("td/span/text()")[0]
        if "Next 5 years" in label:
            ge = float(row.xpath("td/text()")[0].replace("%", ""))
            break

    url = "https://stockanalysis.com/stocks/{}/".format(ticker)
    response = requests.get(url, verify=False)
    parser = html.fromstring(response.content)
    shares = parser.xpath(
        '//div[@class="info"]//table//tbody//tr[td/text()[contains(., "Shares Out")]]'
    )

    shares = shares[0].xpath("td/text()")[1]
    factor = 1000 if "B" in shares else 1
    shares = float(shares.replace("B", "").replace("M", "")) * factor

    url = "https://stockanalysis.com/stocks/{}/financials/".format(ticker)
    response = requests.get(url, verify=False)
    parser = html.fromstring(response.content)
    eps = parser.xpath(
        '//table[contains(@id,"fintable")]//tr[td/span/text()[contains(., "EPS (Diluted)")]]'
    )[0].xpath(".//td/text()")
    eps = float(eps[0].replace(",", ""))
    market_price = float(
        parser.xpath('//div[@id="sp"]/span[@id="cpr"]/text()')[0]
        .replace("$", "")
        .replace(",", "")
    )
    """
    print("Market price: {}".format(market_price))
    print("EPS: {}".format(eps))
    print("Growth estimate: {}".format(ge))
    print("Term: 5 years")
    print("Discount Rate: 10%")
    print("Perpetual Rate: 3%\n")
    """
    return {
        "fcf": last_fcf,
        "ge": ge,
        "yr": 5,
        "dr": 10,
        "pr": 3,
        "shares": shares,
        "eps": eps,
        "mp": market_price,
    }


def dcf_calculate(data):
    output = ""
    forecast = [data["fcf"]]

    for i in range(1, data["yr"]):
        forecast.append(round(forecast[-1] + (data["ge"] / 100) * forecast[-1], 2))

    forecast.append(
        round(
            forecast[-1]
            * (1 + (data["pr"] / 100))
            / (data["dr"] / 100 - data["pr"] / 100),
            2,
        )
    )  # terminal value
    discount_factors = [
        1 / (1 + (data["dr"] / 100)) ** (i + 1) for i in range(len(forecast) - 1)
    ]

    pvs = [round(f * d, 2) for f, d in zip(forecast[:-1], discount_factors)]
    pvs.append(
        round(discount_factors[-1] * forecast[-1], 2)
    )  # discounted terminal value

    output += f"""\nForecasted cash flows: {", ".join(map(str, forecast))}"""
    output += f"""\nPV of cash flows: {", ".join(map(str, pvs))}"""

    dcf = sum(pvs)
    output += f"\nFair value: {dcf / data['shares']}\n"
    return output


def graham(data):
    if data["eps"] > 0:
        expected_value = data["eps"] * (8.5 + 2 * (data["ge"]))
        ge_priced_in = (data["mp"] / data["eps"] - 8.5) / 2
        y = f"""Expected value based on growth rate: {expected_value} \n Growth rate priced in for next 7-10 years: {ge_priced_in}"""
        return y
    else:
        return "Not applicable since EPS is negative."


f = open(".env", "r")
TOKEN = f.read()
print(TOKEN)
client.run(TOKEN)
