import logging
from typing import Dict, List

import bw2calc as bc
import bw2data as bd
import pandas as pd
from bw2analyzer import ContributionAnalysis
from tqdm import tqdm

from relex.utils import ReducedInventoriesData


def get_reduced_inventories(
    bw_project: str,
    activities: List[Dict[str, str]],
    impact_categories: List[Dict[str, str]],
    database: str,
    cutoff: float = 0.01,
) -> ReducedInventoriesData:
    bd.projects.set_current(bw_project)

    if not 0 < cutoff <= 1:
        raise ValueError("Cutoff should be between > 0 and <= 1.")

    bw_methods = get_impact_categories_keys(impact_categories)
    bw_activities = get_activities_keys(activities, database=database)
    if not bw_methods or not bw_activities:
        logging.error("No methods or no activities found.")
        raise NotImplementedError

    logging.info("[...] Performing LCA computations to get top emissions")
    top_emissions_for_all_data = compute_top_emissions_for_all_data(
        bw_activities, bw_methods, cutoff=cutoff
    )
    unique_elem_flows = top_emissions_for_all_data.loc[:, "flow_id"].unique()
    logging.info(
        "%s unique elementary flows obtained from lca computation",
        len(unique_elem_flows),
    )
    logging.info("[...] Retreiving CFs for top emissions and provided impact categories")
    return {
        "top_emissions_per_activity": top_emissions_for_all_data[
            ["elementary_flow", "technosphere_flow", "inventory_amount"]
        ],
        "flows_cfs": get_cfs_for_elem_flow_list(list(unique_elem_flows), bw_methods)[
            ["elementary_flow", "cf", "method"]
        ],
    }


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
    bw_activities = []
    for activity in activities:
        try:
            bw_act = bd.get_node(**activity, database=database)
        except bd.errors.UnknownObject as e:
            logging.error("Could not find activity %s, check syntax", activity)
            raise ValueError() from e
        bw_activities.append(bw_act)
    return bw_activities


def compute_top_emissions_for_all_data(
    bw_activities: List,
    bw_methods: List,
    cutoff: float = 0.01,
) -> pd.DataFrame:
    first_method = bw_methods[0]
    first_activity = bw_activities[0]

    lca = bc.LCA(demand={first_activity.id: 1}, method=first_method)

    current_method = first_method

    results = pd.DataFrame()
    for i, bw_activity in enumerate(tqdm(bw_activities, desc="[...] Going through activities")):
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
            top_elem_flows.loc[:, "activity_id"] = bw_activity.id
            results = pd.concat([results, top_elem_flows])
    results = results.groupby(by=["flow_id", "activity_id"]).first().reset_index()
    results["elementary_flow"] = results["flow_id"].apply(create_label_from_flow_id)
    results["technosphere_flow"] = results["activity_id"].apply(create_label_from_flow_id)
    return results


def create_label_from_flow_id(flow_id: int) -> str:
    node = bd.get_node(id=flow_id).as_dict()
    node_type = node["type"]
    if node_type in ["emission", "natural resource"]:
        return create_label_for_elem_flow(node)
    if node_type == "processwithreferenceproduct":
        return create_label_for_tech_flow(node)

    logging.error("Node type %s not supported for label creation", node_type)
    raise NotImplementedError


def create_label_for_elem_flow(node: Dict) -> str:
    return f"{node["name"]}, {node["categories"]} [{node["unit"]}]"


def create_label_for_tech_flow(node: Dict) -> str:
    return f"{node["name"]}, {node["reference product"]} | {node["location"]} [{node["unit"]}]"


def get_cfs_for_elem_flow_list(flows: List[int], bw_methods: List) -> pd.DataFrame:
    cfs = pd.DataFrame()
    for method_key in tqdm(bw_methods, desc="[...] Going through methods"):
        method_cfs = pd.DataFrame(list(bd.Method(method_key)), columns=["id", "cf"])
        method_cfs["id"] = method_cfs["id"].apply(lambda x: x.id)

        flows_cf = (
            pd.DataFrame(flows, columns=["id"]).merge(method_cfs, how="left", on="id").fillna(0)
        )
        flows_cf.loc[:, "method"] = f"{method_key[1]} - {method_key[2]}"
        cfs = pd.concat([cfs, flows_cf])

    cfs["elementary_flow"] = cfs["id"].apply(create_label_from_flow_id)

    return cfs
