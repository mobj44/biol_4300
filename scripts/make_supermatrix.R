install.packages('evobiR')
library(evobiR)

# Define input and output folders
input_dir <- "data/trimmed_alignments"
output_dir <- "data/supermatrix"

# Create output directory if it doesn't exist
if (!dir.exists(output_dir)) {
    dir.create(output_dir, recursive = TRUE)
}
# Set working directory to input folder (SuperMatrix looks here for fasta files)
setwd(input_dir)

# Run SuperMatrix and save results to output_dir
SuperMatrix(
    missing = "-",
    prefix = file.path("..", "supermatrix", "super_matrix")
)
