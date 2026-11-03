import pandas as pd
from pandas.api import types


def is_number(series: pd.Series) -> bool:
    """Vrai pour une colonne numérique (entiers ou décimaux), booléens exclus."""
    return types.is_numeric_dtype(series) and not types.is_bool_dtype(series)


TYPE_CHECKS = {
    "int": types.is_integer_dtype,
    "float": is_number,
    "str": types.is_string_dtype,
}


def validate(df: pd.DataFrame, schema: dict) -> list[str]:
    """Retourne la liste des erreurs de validation (vide si conforme)."""
    errors = []
    for name, rules in schema["columns"].items():
        if name not in df.columns:
            errors.append(f"Colonne absente : {name}")
            continue
        if rules["dtype"] not in TYPE_CHECKS:
            errors.append(f"{name} : type '{rules['dtype']}' inconnu dans le schéma")
            continue
        values = df[name].dropna()
        n_missing = len(df) - len(values)
        if n_missing:
            errors.append(f"{name} : {n_missing} valeur(s) manquante(s)")
        elif not TYPE_CHECKS[rules["dtype"]](values):
            errors.append(f"{name} : type {df[name].dtype}, attendu {rules['dtype']}")
            continue
        if "allowed" in rules:
            unknown = sorted(set(values) - set(rules["allowed"]))
            if unknown:
                errors.append(f"{name} : valeurs non autorisées {unknown}")
        if not types.is_numeric_dtype(values):
            continue
        if "min" in rules:
            n = (values < rules["min"]).sum()
            if n:
                errors.append(f"{name} : {n} valeur(s) < {rules['min']}")
        if "max" in rules:
            n = (values > rules["max"]).sum()
            if n:
                errors.append(f"{name} : {n} valeur(s) > {rules['max']}")
    extra = set(df.columns) - set(schema["columns"])
    if extra:
        errors.append(f"Colonnes non déclarées dans le schéma : {sorted(extra)}")
    return errors