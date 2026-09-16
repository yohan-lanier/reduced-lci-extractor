from relex.args import RelexParser
from relex.utils import build_ecoinvent_in_bw, load_input_data

if __name__ == "__main__":
    args = RelexParser()
    bw_project = args.bw_project_name
    database = args.database
    build_ecoinvent_in_bw(
        bw_project, database, overwrite_lca_databases=args.overwrite_lca_databases
    )
    input_data = load_input_data(args.input_data_filename)
