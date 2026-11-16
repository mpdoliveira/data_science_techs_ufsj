import pandas as pd
from geopy.geocoders import Nominatim, options
from geopy.extra.rate_limiter import RateLimiter
from geopy.location import Location

df = pd.read_csv("resultados_presidente_sjdr.csv")


options.default_timeout = 15
geolocator = Nominatim(
    user_agent="election_map/1.0 (marcos.pdo1412@gmail.com)"
)
geocode = RateLimiter(
    geolocator.geocode,
    min_delay_seconds=1.1,
    max_retries=2,
    error_wait_seconds=5,
    swallow_exceptions=True,
)

enderecos = df["DS_LOCAL_VOTACAO_ENDERECO"].fillna("").str.strip()

cache = {
    endereco: geocode(f"{endereco}, São João del-Rei, Minas Gerais, Brasil")
    for endereco in enderecos.unique()
    if endereco
}

coordenadas = enderecos.map(cache)


def get_latitude(loc: object) -> float | None:
    if isinstance(loc, Location):
        return loc.latitude
    return None


def get_longitude(loc: object) -> float | None:
    if isinstance(loc, Location):
        return loc.longitude
    return None


df["LATITUDE"] = coordenadas.map(get_latitude)
df["LONGITUDE"] = coordenadas.map(get_longitude)

df.to_csv(
    "resultados_presidente_sjdr_geocodificado.csv",
    index=False,
    encoding="utf-8",
)
