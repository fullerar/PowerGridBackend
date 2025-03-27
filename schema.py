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


# === Helper Function: Fetch Historical Data ===
def fetch_historical_data(zone="US-MIDA-PJM"):
    url = f"https://api.electricitymap.org/v3/power-breakdown/history?zone={zone}"
    headers = {"auth-token": "nztSjedCFYMxcA05Odpl"}

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    return response.json().get("history", [])


# === GraphQL Query Class ===
class Query(graphene.ObjectType):
    sources = graphene.List(PowerSource, name=graphene.String(required=False), zone=graphene.String(required=False))
    historicalSources = graphene.List(HistoricalSource)

    def resolve_sources(self, info, name=None, zone=None):
        if not zone:
            zone = "US-MIDA-PJM"  # fallback

        url = f"https://api.electricitymap.org/v3/power-breakdown/latest?zone={zone}"
        headers = {"auth-token": "nztSjedCFYMxcA05Odpl"}
        response = requests.get(url, headers=headers)
        data = response.json().get('powerConsumptionBreakdown', {})

        results = [PowerSource(name=k, power=v) for k, v in data.items()]

        if name:
            results = [ps for ps in results if name.lower() in ps.name.lower()]

        return results

    def resolve_historicalSources(self, info, zone=None):
        if not zone:
            zone = "US-MIDA-PJM"

        raw_data = fetch_historical_data(zone)
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
