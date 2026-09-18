from tap import Tap

from relex.constants import VALID_DATABASES


class RelexParser(Tap):
    bw_project_name: str
    database: str
    input_data_filename: str
    cutoff: float = 0.01
    save_filename: str = "output-file"
    overwrite_lca_databases: bool = False

    def configure(self) -> None:
        self.add_argument(
            "-p",
            "--bw-project-name",
            help="name of the brightway project that will be used",
            dest="bw_project_name",
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
            "--input-data-filename",
            help="name of the file containing input data (activities and methods)",
            dest="input_data_filename",
        )

        self.add_argument(
            "-c",
            "--cutoff",
            help="cutoff value to apply when getting top emissions of an "
            "activity for a given impact category",
            dest="cutoff",
            required=False,
            default=0.01,
        )

        self.add_argument(
            "-s",
            "--save-filename",
            help="name of the output file containing reduced inventory data.",
            dest="save_filename",
            default="output-file",
            required=False,
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
