import logging
from typing import Dict, List

import bw2calc as bc
import bw2data as bd


def compute_top_emissions_for_all_data(
    bw_project: str,
    activities: List[Dict[str, str]],
    impact_categories: List[Dict[str, str]],
    database:str
):
    bd.projects.set_current(bw_project)
    methods = get_impact_categories_keys(impact_categories)
    for activity in activities:
        act_data = bd.get_node(**activity, database=database).as_dict()
        functional_units = {act_data["name"]: {act_data["id"]: 1}}
        config = {"impact_categories": methods}
        data_objs = bd.get_multilca_data_objs(functional_units, config)
        mlca = bc.MultiLCA(
            demands=functional_units, method_config=config, data_objs=data_objs
        )
        mlca.lci()
        mlca.lcia()


def get_impact_categories_keys(impact_categories: List[Dict[str, str]])->List:
    keys = []
    for impact_cat in impact_categories:
        keys.append(
            [
                m
                for m in bd.methods
                if impact_cat["method_name"] == m[1].lower()
                and impact_cat["impact_cat_name"] == m[2].lower()
            ][0]
        )

    if not keys:
        logging.error("Wowowowo no methods found")
        raise NotImplementedError
    return keys
