import datetime
import requests
import graphene


# === GraphQL Types ===
class PowerSource(graphene.ObjectType):
    name = graphene.String()
    power = graphene.Float()


class HistoricalSource(graphene.ObjectType):
    datetime = graphene.String()
    source = graphene.String()
    power = graphene.Float()


# === Helper Function: Fetch Latest Data ===
def fetch_latest_data():
    url = "https://api.electricitymap.org/v3/power-breakdown/latest?zone=US-MIDA-PJM"
    headers = {"auth-token": "nztSjedCFYMxcA05Odpl"}

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    return response.json().get("powerConsumptionBreakdown", {})


# === Helper Function: Fetch Historical Data ===
def fetch_historical_data():
    url = f"https://api.electricitymap.org/v3/power-breakdown/history?zone=US-MIDA-PJM"
    headers = {"auth-token": "nztSjedCFYMxcA05Odpl"}

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    return response.json().get("history", [])


# === GraphQL Query Class ===
class Query(graphene.ObjectType):
    sources = graphene.List(PowerSource, name=graphene.String(required=False))
    historical_sources = graphene.List(HistoricalSource)

    def resolve_sources(self, info, name=None):
        data = fetch_latest_data()

        results = [PowerSource(name=k, power=v) for k, v in data.items()]

        if name:
            results = [ps for ps in results if name.lower() in ps.name.lower()]

        return results

    def resolve_historicalSources(self, info):
        raw_data = fetch_historical_data()
        results = []

        for entry in raw_data:
            timestamp = entry.get("datetime")
            breakdown = entry.get("powerConsumptionBreakdown", {})
            for source, value in breakdown.items():
                results.append(
                    HistoricalSource(datetime=timestamp, source=source, power=value)
                )

        return results


# === GraphQL Schema ===
schema = graphene.Schema(query=Query)
