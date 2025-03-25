import graphene


class PowerSource(graphene.ObjectType):
    name = graphene.String()
    power = graphene.Float()


class Query(graphene.ObjectType):
    sources = graphene.List(
        PowerSource,
        name=graphene.String(required=False)
    )

    def resolve_sources(self, info, name=None):
        # Fetch + parse
        import requests, pandas as pd
        url = "https://api.electricitymap.org/v3/power-breakdown/latest?zone=US-MIDA-PJM"
        headers = {"auth-token": "nztSjedCFYMxcA05Odpl"}
        response = requests.get(url, headers=headers)
        data = response.json()['powerConsumptionBreakdown']

        results = [PowerSource(name=k, power=v) for k, v in data.items()]

        # Filter by name if provided
        if name:
            results = [ps for ps in results if ps.name.lower() == name.lower()]

        return results


schema = graphene.Schema(query=Query)
