from relex.args import RelexParser
from relex.logger import configure_logger
from relex.compute_reduced_inventories import get_reduced_inventories
from relex.utils import build_ecoinvent_in_bw, load_input_data

if __name__ == "__main__":
    configure_logger()
    args = RelexParser().parse_args()
    bw_project = args.bw_project_name
    database = args.database
    build_ecoinvent_in_bw(
        bw_project, database, overwrite_lca_databases=args.overwrite_lca_databases
    )
    input_data = load_input_data(args.input_data_filename)
    reduced_inventory_data = get_reduced_inventories(
        bw_project,
        input_data["activities"],
        input_data["impact_cat"],
        database=database,
    )
