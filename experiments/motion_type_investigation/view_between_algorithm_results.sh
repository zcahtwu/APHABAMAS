#!/usr/bin/env bash

set -euo pipefail

if [[ $# -ne 3 ]]; then
    echo "Usage: $0 <slow_drift|spikes|stepwise> <very_low|low|medium|high> <repeat>"
    echo "Example: $0 slow_drift very_low 1"
    exit 1
fi

motion_type=$1
severity=$2
repeat_input=$3

if [[ ! $motion_type =~ ^(slow_drift|spikes|stepwise)$ ]]; then
    echo "Invalid motion type: $motion_type"
    exit 1
fi

if [[ ! $severity =~ ^(very_low|low|medium|high)$ ]]; then
    echo "Invalid motion level: $severity"
    exit 1
fi

if [[ ! $repeat_input =~ ^[0-9]+$ ]] || (( 10#$repeat_input < 1 )); then
    echo "Repeat must be a positive integer."
    exit 1
fi

printf -v repeat_number '%02d' "$((10#$repeat_input))"
script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
case_folder="$script_dir/$motion_type/results/$severity/repeat_$repeat_number/phantom"

type1="$case_folder/type1_original.nii.gz"
type2="$case_folder/type2.nii.gz"
image_based="$case_folder/image_based.nii.gz"

for image in "$type1" "$type2" "$image_based"; do
    if [[ ! -f $image ]]; then
        echo "Missing image: $image"
        exit 1
    fi
done

for command_name in fslmaths fsleyes; do
    if ! command -v "$command_name" >/dev/null 2>&1; then
        echo "$command_name is not available in the current environment."
        exit 1
    fi
done

difference_folder=$(mktemp -d)
trap 'rm -r -- "$difference_folder"' EXIT

type1_to_type2="$difference_folder/type1_minus_type2.nii.gz"
type1_to_image_based="$difference_folder/type1_minus_image_based.nii.gz"
type2_to_image_based="$difference_folder/type2_minus_image_based.nii.gz"

fslmaths "$type1" -sub "$type2" "$type1_to_type2"
fslmaths "$type1" -sub "$image_based" "$type1_to_image_based"
fslmaths "$type2" -sub "$image_based" "$type2_to_image_based"

fsleyes \
    "$type1" -dr 0 2 \
    "$type2" -dr 0 2 \
    "$image_based" -dr 0 2 \
    "$type1_to_type2" -dr -0.2 0.2 \
    "$type1_to_image_based" -dr -0.2 0.2 \
    "$type2_to_image_based" -dr -0.2 0.2
