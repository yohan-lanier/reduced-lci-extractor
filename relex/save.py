import pandas as pd

from relex.paths import DATA
from relex.utils import ReducedInventoriesData


def save_reduced_inventory_data(reduced_inventory_data: ReducedInventoriesData, output_file: str):
    with pd.ExcelWriter(DATA / f"{output_file}.xlsx") as writer:
        reduced_inventory_data["flows_cfs"].pivot(
            index="id", columns="method", values="cf"
        ).to_excel(writer, sheet_name="cfs")
        reduced_inventory_data["top_emissions_per_activity"].pivot(
            index="flow_id", columns="activity_id", values="inventory_amount"
        ).to_excel(writer, sheet_name="reduced_inventories")
