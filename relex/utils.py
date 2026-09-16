import logging
import os
from typing import TypedDict, Dict, List, cast

import pandas as pd
import bw2data as bd
import bw2io as bi
from dotenv import load_dotenv

from relex.paths import DATA
from relex.constants import VALID_DATABASES


class InputData(TypedDict):
    activities: List[Dict[str, str]]
    impact_cat: List[Dict[str, str]]


def load_input_data(filename: str) -> InputData:
    file = pd.ExcelFile(DATA / f"{filename}.xlsx")
    return {
        "activities": cast(
            List[Dict[str, str]],
            pd.read_excel(file, sheet_name="activities").to_dict(
                orient="records"
            ),
        ),
        "impact_cat": cast(
            List[Dict[str, str]],
            pd.read_excel(file, sheet_name="methods").to_dict(
                orient="records"
            ),
        ),
    }


def build_ecoinvent_in_bw(
    bw_project: str,
    bg_database: str,
    overwrite_lca_databases: bool,
) -> None:
    assert_input_databases_is_valid(bg_database)
    bd.projects.set_current(bw_project)
    logging.info("Processing background database %s", bg_database)
    load_dotenv()
    user_name = os.environ.get("ECOINVENT_USERNAME")
    pwd = os.environ.get("ECOINVENT_PWD")
    if bg_database in bd.databases:
        if not overwrite_lca_databases:
            logging.info(
                "Database %s is already in brightway project databases, skipping build step",
                bg_database,
            )
            return
        logging.warning(
            "%s is already in project databases. 'overwrite_databases' is active, "
            "deleting it from project databases and rebuilding. WARNING, it can take"
            "a lot of time !!!",
            bg_database,
        )
        del bd.databases[bg_database]
    logging.info("Building %s database in brightway", bg_database)
    _, version, system_model = bg_database.split("-")
    bi.import_ecoinvent_release(
        version=version,
        system_model=system_model,
        username=user_name,
        password=pwd,
    )


def assert_input_databases_is_valid(database: str):
    assert (
        database in VALID_DATABASES
    ), f"Database {database} is not supported, make sure input databases are supported"
    logging.info(
        "Provided database %s is valid. Starting to build in brightway", database
    )
