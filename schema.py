import datetime
import requests
import graphene
import pandas as pd


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


class PowerSummary(graphene.ObjectType):
    sources = graphene.List(PowerSource)
    totalPowerOutput = graphene.Float()


# === GraphQL Query Class ===
class Query(graphene.ObjectType):
    sources = graphene.Field(
        PowerSummary, name=graphene.String(required=False), zone=graphene.String(required=False))
    historicalSources = graphene.List(HistoricalSource)

    def resolve_sources(self, info, name=None, zone=None):
        if not zone:
            zone = "US-MIDA-PJM"

        url = f"https://api.electricitymap.org/v3/power-breakdown/latest?zone={zone}"
        headers = {"auth-token": "nztSjedCFYMxcA05Odpl"}

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Error fetching data for zone {zone}: {e}")
            return []

        data = response.json().get("powerConsumptionBreakdown", {})

        # Create DataFrame and sort
        df = pd.DataFrame(list(data.items()), columns=["name", "power"])

        if name:
            df = df[df["name"].str.lower().str.contains(name.lower())]

        df = df.sort_values(by="power", ascending=False)

        # Build sorted source list
        results = [PowerSource(name=row["name"], power=row["power"]) for _, row in df.iterrows()]
        total_output = df["power"].sum()

        return PowerSummary(sources=results, totalPowerOutput=total_output)

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
