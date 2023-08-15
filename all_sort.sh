#!/bin/bash

# Matching files function
process_directory() {
    cd "$1"

    # make the directories if they don't exist
    mkdir -p DOI
    mkdir -p PMC
    mkdir -p Table

    mv *_table_*.html Table
    # Loop over each file in the current directory
    for file in *.html; do
        # Split the filename into the ID field and the suffix field
        id=$(echo "$file" | cut -d'_' -f1)
        suffix=$(echo "$file" | cut -d'_' -f2)

        # Determine the other suffix
        if [[ $suffix == "DOI.html" ]]; then
            other_suffix="PMC.html"
            dir="DOI"
            other_dir="PMC"
        else
            other_suffix="DOI.html"
            dir="PMC"
            other_dir="DOI"
        fi

        # -e checks existence of file
        if [[ -e ${id}_${other_suffix} ]]; then
            # If countepart exists, move the file to the corresponding subdirectory
            mv "$file" "$dir/"
            mv "${id}_${other_suffix}" "$other_dir/"
            # And add the ID to the matching_ids.txt file
            echo "$id" >> matching_ids.txt
        fi
    done


    # back to the parent directory
    cd ..
}

# iterates through each directory and runs function
for dir in */; do
    process_directory "$dir"
done

