import pandas as pd

from relex.paths import OUTPUT_DATA
from relex.utils import ReducedInventoriesData


def save_reduced_inventory_data(reduced_inventory_data: ReducedInventoriesData, output_file: str):
    if not OUTPUT_DATA.exists():
        OUTPUT_DATA.mkdir()

    with pd.ExcelWriter(OUTPUT_DATA / f"{output_file}.xlsx") as writer:
        reduced_inventory_data["top_emissions_per_activity"].pivot(
            index="elementary_flow",
            columns="technosphere_flow",
            values="inventory_amount",
        ).to_excel(writer, sheet_name="reduced_inventories")
        reduced_inventory_data["flows_cfs"].pivot(
            index="elementary_flow", columns="method", values="cf"
        ).to_excel(writer, sheet_name="cfs")
