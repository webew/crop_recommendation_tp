import pandas as pd
import pytest

from crop_recommendation_tp.config import load_yaml
from crop_recommendation_tp.validation import validate

# Découverte : uv run pytest parcourt le projet et repère les fichiers nommés test_*.py, ici tests/test_validation.py.
# Collecte : dans ces fichiers, pytest retient les fonctions dont le nom commence par test_. Un autre nom (par exemple verifier_donnees) serait ignoré.
# Préparation : pour chaque test, pytest lit les noms des paramètres (df, schema). Il cherche une fixture portant le même nom, l’exécute et récupère son résultat. Les deux fixtures ci-dessus fournissent donc le tableau et le schéma.
# Exécution : pytest appelle test_donnees_conformes(df=..., schema=...). Le test réussit si l’assert est vrai, et échoue avec le détail de la différence sinon.

# Les fixtures df et schema sont réutilisables : les prochains tests du même fichier les recevront de la même façon, avec un tableau neuf à chaque fois (une modification dans un test n’affecte pas les autres).

@pytest.fixture
def schema():
    return load_yaml("config/schema.yaml")


@pytest.fixture
def df():
    """Tableau de deux lignes conformes au schéma."""
    return pd.DataFrame(
        {
            "N": [90, 20],
            "P": [42, 60],
            "K": [43, 20],
            "temperature": [20.9, 25.0],
            "humidity": [82.0, 60.5],
            "ph": [6.5, 7.0],
            "rainfall": [202.9, 100.0],
            "label": ["rice", "apple"],
        }
    )


def test_donnees_conformes(df, schema):
    assert validate(df, schema) == []
    
    
def test_colonne_absente(df, schema):
    erreurs = validate(df.drop(columns=["ph"]), schema)
    assert erreurs == ["Colonne absente : ph"]


def test_ph_hors_bornes(df, schema):
    df.loc[0, "ph"] = 75.0
    assert validate(df, schema) == ["ph : 1 valeur(s) > 14"]


def test_valeur_manquante_et_valeur_hors_bornes(df, schema):
    df.loc[0, "N"] = None
    df.loc[1, "N"] = -5
    erreurs = validate(df, schema)
    assert erreurs == ["N : 1 valeur(s) manquante(s)", "N : 1 valeur(s) < 0"]
    
    
def test_culture_inconnue(df, schema):
    df.loc[0, "label"] = "ricee"
    assert validate(df, schema) == ["label : valeurs non autorisées ['ricee']"]


def test_colonne_non_declaree(df, schema):
    df["extra"] = 1
    assert validate(df, schema) == ["Colonnes non déclarées dans le schéma : ['extra']"]


def test_type_inconnu_dans_le_schema(df, schema):
    schema["columns"]["N"]["dtype"] = "integer"
    assert validate(df, schema) == ["N : type 'integer' inconnu dans le schéma"]


def test_entiers_acceptes_pour_un_float(df, schema):
    df["temperature"] = [21, 25]
    assert validate(df, schema) == []


def test_booleens_refuses_pour_un_float(df, schema):
    df["ph"] = [True, False]
    assert validate(df, schema) == ["ph : type bool, attendu float"]
    