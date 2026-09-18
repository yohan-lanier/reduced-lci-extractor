# Reduced LCI Extractor

`relex` extracts a small, teaching-friendly life-cycle inventory from selected
ecoinvent activities and Brightway impact assessment methods. For each requested
activity and method, it keeps the elementary flows that contribute at least a
chosen share of the result, then retrieves the characterization factors for
those flows.

This is useful for exercises and demonstrations where students need to inspect
the important emissions without handling a complete ecoinvent database. The
package requires a valid ecoinvent licence and does not distribute ecoinvent
data.

## Requirements

- Python 3.12 or newer
- A valid ecoinvent licence and account
- Internet access the first time an ecoinvent database is imported
- A Brightway-compatible ecoinvent release supported by this package:
	`ecoinvent-3.10.1-cutoff`, `ecoinvent-3.11-cutoff`, or
	`ecoinvent-3.12-cutoff`

The ecoinvent username and password are read from the `ECOINVENT_USERNAME` and
`ECOINVENT_PWD` environment variables. A `.env` file in the working directory
can be used, for example:

```text
ECOINVENT_USERNAME=your-ecoinvent-username
ECOINVENT_PWD=your-ecoinvent-password
```

Keep that file private and do not commit it.

## Installation

Clone the repository, create and activate a virtual environment, then install
the package and its dependencies:

```bash
git clone <repository-url>
cd reduced-lci-extractor
python -m venv .venv
```

On Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

On macOS or Linux:

```bash
source .venv/bin/activate
```

Install the project in editable mode:

```pwsh
python -m pip install --upgrade pip
python -m pip install -e .
```

## Input data

The command-line interface reads an Excel workbook from `data/input/`. Pass the
filename without its `.xlsx` extension. A tempate is provided in the input data
folder. The workbook must contain these sheets:

### `activities`

One row per ecoinvent activity. The columns are passed to Brightway's
`bd.get_node` lookup, together with the selected database. A typical activity
selection uses:

| name | reference product | location |
| --- | --- | --- |
| market for electricity, low voltage | electricity, low voltage | FR |

Use values that exactly match the activity in the selected ecoinvent database.
Additional Brightway lookup fields may be used when appropriate.

### `methods`

One row per impact assessment method. The required columns are
`method_name` and `impact_cat_name`. Matching is case-insensitive:

| method_name | impact_cat_name |
| --- | --- |
| ReCiPe 2016 v1.03, midpoint | climate change |

The values must identify methods already installed in the Brightway project.
The exact names available in a project can be inspected with
`list(bw2data.methods)`.

## Command-line usage

Run the module from the repository root:

```bash
python -m relex \
	--bw-project-name teaching-project \
	--database ecoinvent-3.12-cutoff \
	--input-data-filename exercise-01 \
	--cutoff 0.01 \
	--save-filename exercise-01-reduced
```

The first ecoinvent import can take a while and requires credentials.
If the selected database is already present in the Brightway project, the
import step is skipped unless `--overwrite-databases` is supplied.

The input file in this example is `data/input/exercise-01.xlsx`; the result is
written to `data/output/exercise-01-reduced.xlsx`. `--cutoff` is a proportion
between 0 and 1. The default, `0.01`, keeps the top emissions contributing to
the requested cutoff according to Brightway's contribution analysis.

Available options:

| Option | Required | Default | Description |
| --- | --- | --- | --- |
| `-p`, `--bw-project-name` | yes | - | Brightway project to use |
| `-d`, `--database` | yes | - | Supported ecoinvent cutoff database |
| `-i`, `--input-data-filename` | yes | - | Workbook name in `data/input/`, without `.xlsx` |
| `-c`, `--cutoff` | no | `0.01` | Contribution cutoff between 0 and 1 |
| `-s`, `--save-filename` | no | `output-file` | Output workbook name, without `.xlsx` |
| `-o`, `--overwrite-databases` | no | off | Re-import an existing ecoinvent database |

The output workbook contains:

- `reduced_inventories`: elementary flows by selected technosphere activity,
	with inventory amounts
- `cfs`: characterization factors for the retained elementary flows and
	selected methods

## Python API and tutorial

For users who do not want to use the command line, see
[`tutorial.ipynb`](tutorial.ipynb). It demonstrates database setup, activity
and method selection, reduction, result inspection, and saving the output.

The main programmatic workflow is:

```python
from relex.compute_reduced_inventories import get_reduced_inventories
from relex.save import save_reduced_inventory_data
from relex.utils import build_ecoinvent_in_bw

build_ecoinvent_in_bw(
		"teaching-project",
		"ecoinvent-3.12-cutoff",
		overwrite_lca_databases=False,
)

result = get_reduced_inventories(
		"teaching-project",
		activities=[
				{
						"name": "market for electricity, low voltage",
						"reference product": "electricity, low voltage",
						"location": "FR",
				}
		],
		impact_categories=[
				{
						"method_name": "ReCiPe 2016 v1.03, midpoint",
						"impact_cat_name": "climate change",
				}
		],
		database="ecoinvent-3.12-cutoff",
		cutoff=0.01,
)

save_reduced_inventory_data(result, output_file="exercise-01-reduced")
```

The API returns a dictionary with two pandas DataFrames:
`top_emissions_per_activity` and `flows_cfs`.
