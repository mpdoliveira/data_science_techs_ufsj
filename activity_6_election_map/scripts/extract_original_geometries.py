from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "dash"))
from core import carregar_base


def extrair():
    html_path = ROOT / "sjdr_election_map.html"
    destino = ROOT / "dash" / "data"
    conteudo = html_path.read_text(encoding="utf-8")
    encontrados = []
    for match in re.finditer(r"\bgeo_json_\w+_add\s*\(\{", conteudo):
        trecho = conteudo[match.end() - 1:]
        colecao, _ = json.JSONDecoder().raw_decode(trecho)
        if colecao.get("type") == "FeatureCollection":
            encontrados.append(colecao)
    if len(encontrados) < 3:
        raise ValueError("HTML não contém as duas camadas de Voronoi e o limite municipal esperados.")

    _, locais, _ = carregar_base(ROOT / "resultados_presidente_sjdr_coordenadas_manuais.csv")
    relatorio = {}
    for turno, camada in zip((1, 2), encontrados[:2]):
        dados_turno = locais.loc[locais.NR_TURNO == turno]
        ids = []
        for feature in camada["features"]:
            p = feature["properties"]
            votos = p["VOTOS"]
            total = p["TOTAL"]
            codigo = int(p["CANDIDATO"])
            encontrados_local = dados_turno.loc[
                (dados_turno.VALIDOS == total) & (dados_turno[codigo] == votos)
            ]
            if len(encontrados_local) != 1:
                raise ValueError(
                    f"Sem correspondência única no turno {turno}: {p['LOCAL']} "
                    f"({codigo}, {votos}, {total}). Correspondências: {len(encontrados_local)}"
                )
            registro = encontrados_local.iloc[0]
            ident = str(registro.LOCAL_ID)
            if ident in ids:
                raise ValueError(f"Local duplicado no mapa: {ident}")
            ids.append(ident)
            p["LOCAL_ID"] = ident
            p["TURNO"] = turno
            p["COR_ORIGINAL"] = p["COR"]
            p["OPACIDADE_ORIGINAL"] = p["OPACIDADE"]
        caminho = destino / f"voronoi_turno_{turno}.geojson"
        caminho.write_text(json.dumps(camada, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        relatorio[str(turno)] = {
            "locais_com_resultados": len(dados_turno),
            "poligonos_do_mapa_original": len(ids),
            "locais_sem_poligono": sorted(set(dados_turno.LOCAL_ID) - set(ids)),
        }
    (destino / "limite_municipal.geojson").write_text(
        json.dumps(encontrados[2], ensure_ascii=False, separators=(",", ":")), encoding="utf-8"
    )
    (destino / "cobertura_mapa.json").write_text(
        json.dumps(relatorio, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(relatorio, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    extrair()
