import logging
from typing import Dict, List

from bw2analyzer import ContributionAnalysis
import bw2calc as bc
import bw2data as bd
import pandas as pd
from tqdm import tqdm


def compute_top_emissions_for_all_data(
    bw_project: str,
    activities: List[Dict[str, str]],
    impact_categories: List[Dict[str, str]],
    database: str,
    cutoff: float = 0.01,
)->pd.DataFrame:
    if not 0 < cutoff <= 1:
        raise ValueError("Cutoff should be between > 0 and <= 1.")
    bd.projects.set_current(bw_project)
    bw_methods = get_impact_categories_keys(impact_categories)
    bw_activities = get_activities_keys(activities, database=database)
    if not bw_methods or not bw_activities:
        logging.error("No methods or no activities found.")
        raise NotImplementedError
    first_method = bw_methods[0]
    first_activity = bw_activities[0]

    lca = bc.LCA(demand={first_activity.id: 1}, method=first_method)

    current_method = first_method

    results=pd.DataFrame()
    for i, bw_activity in enumerate(
        tqdm(bw_activities, desc="[...] Going through activities")
    ):
        if i == 0:
            lca.lci(factorize=True)
        else:
            lca.lci(demand={bw_activity.id: 1})
        for bw_method in tqdm(bw_methods, desc="[...] Going through methods"):
            if bw_method != current_method:
                lca.switch_method(bw_method)
                current_method = bw_method
            lca.lcia()
            top_elem_flows = pd.DataFrame(
                ContributionAnalysis().annotated_top_emissions(
                    lca, names=False, limit_type="percent", limit=cutoff
                ),
                columns=["lca_score", "inventory_amount", "flow_id"],
            ).drop(columns="lca_score")
            top_elem_flows.loc[:,"activity_id"]=bw_activity.id
            results = pd.concat([results, top_elem_flows])

    return results


def get_impact_categories_keys(impact_categories: List[Dict[str, str]]) -> List:
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


def get_activities_keys(activities: List[Dict[str, str]], database: str) -> List:
    bw_activities=[]
    for activity in activities:
        try:
            bw_act = bd.get_node(**activity, database=database)
        except bd.errors.UnknownObject as e:
            logging.error("Could not find activity %s, check syntax", activity)
            raise ValueError() from e
        bw_activities.append(bw_act)
    return bw_activities
