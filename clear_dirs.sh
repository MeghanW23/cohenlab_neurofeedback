#!/bin/bash
echo "This script clears directories that store data not needed past script runtime"

directories_to_check=(
$(python -c "from settings import TMP_OUTDIR_PATH; print TMP_OUTDIR_PATH"),
$(python -c "from settings import TMP_OUTDIR_PATH; print TMP_OUTDIR_PATH"),

)