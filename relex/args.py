from tap import Tap

from relex.constants import VALID_DATABASES


class RelexParser(Tap):
    bw_project_name: str
    database: str
    input_data_filename: str
    overwrite_lca_databases: bool = False

    def configure(self) -> None:
        self.add_argument(
            "-p",
            "--bw-project-name",
            help="name of the brightway project that will be used",
            dest="bw_project_name",
            required=True,
        )

        self.add_argument(
            "-d",
            "--database",
            help="name of the exiobase database to use for imports. "
            "This arg should be a valid choice among options listed above",
            dest="database",
            choices=VALID_DATABASES,
        )

        self.add_argument(
            "-i",
            "--input-data",
            help="name of the file containing input data (activities and methods)",
            dest="input_data_filename",
            required=True,
        )

        self.add_argument(
            "-o",
            "--overwrite-databases",
            help="if true, existing background databases in the brightway project will "
            "be overwritten and rebuild",
            dest="overwrite_lca_databases",
            action="store_true",
            default=False,
            required=False,
        )
