import pandas as pd
from pandas.api import types

TYPE_CHECKS = {
    "int": types.is_integer_dtype,
    "float": types.is_float_dtype,
    "str": types.is_string_dtype,
}


def validate(df: pd.DataFrame, schema: dict) -> list[str]:
    """Retourne la liste des erreurs de validation (vide si conforme)."""
    errors = []
    for name, rules in schema["columns"].items():
        if name not in df.columns:
            errors.append(f"Colonne absente : {name}")
            continue
        n_missing = df[name].isna().sum()
        if n_missing:
            errors.append(f"{name} : {n_missing} valeur(s) manquante(s)")
            continue
        if rules["dtype"] not in TYPE_CHECKS:
            errors.append(f"{name} : type '{rules['dtype']}' inconnu dans le schéma")
            continue
        if not TYPE_CHECKS[rules["dtype"]](df[name]):
            errors.append(f"{name} : type {df[name].dtype}, attendu {rules['dtype']}")
            continue
        if "min" in rules:
            n = (df[name] < rules["min"]).sum()
            if n:
                errors.append(f"{name} : {n} valeur(s) < {rules['min']}")
        if "max" in rules:
            n = (df[name] > rules["max"]).sum()
            if n:
                errors.append(f"{name} : {n} valeur(s) > {rules['max']}")
    extra = set(df.columns) - set(schema["columns"])
    if extra:
        errors.append(f"Colonnes non déclarées dans le schéma : {sorted(extra)}")
    return errors