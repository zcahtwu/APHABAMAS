import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats


MOTION_TYPES = {
    'slow_drift': 'Slow drift',
    'spikes': 'Spikes',
    'stepwise': 'Step-wise'
}
SEVERITIES = ['low', 'medium', 'high']
METHODS = {
    'Type 1': 'type1',
    'Type 2': 'type2',
    'Image-based': 'image_based'
}
METHOD_PAIRS = [
    ('Type 1', 'Type 2'),
    ('Type 1', 'Image-based'),
    ('Type 2', 'Image-based')
]
METRICS = ['SSIM', 'RMSD']
ALPHA = 0.05

script_dir = Path(__file__).resolve().parent
output_folder = script_dir / 'results' / 'phantom'


def load_phantom_metrics():
    records = []
    for motion_type in MOTION_TYPES:
        metrics_path = script_dir / motion_type / 'results' / 'metrics.json'
        if not metrics_path.exists():
            print(f'Skipping {motion_type}: {metrics_path} does not exist.')
            continue
        with metrics_path.open('r') as file:
            records.extend(json.load(file))

    if not records:
        raise FileNotFoundError('No motion-type metrics files were found.')

    dataframe = pd.DataFrame(records)
    return dataframe[dataframe['scan'] == 'phantom'].copy()


def metric_column(metric, method):
    return f'{metric}_{METHODS[method]}_with_GT'


def make_plotting_table(dataframe):
    """Convert the phantom metrics to the tidy table consumed by Figure 8."""
    rows = []
    for record in dataframe.to_dict('records'):
        for metric in METRICS:
            for method in METHODS:
                rows.append({
                    'motion_type': record['motion_type'],
                    'severity': record['severity'],
                    'repeat': record['repeat'],
                    'metric': metric,
                    'algorithm': method,
                    'value': record[metric_column(metric, method)]
                })
    return pd.DataFrame(rows)


def holm_correction(p_values):
    p_values = np.asarray(p_values)
    order = np.argsort(p_values)
    adjusted = np.maximum.accumulate(
        (len(p_values) - np.arange(len(p_values))) * p_values[order]
    )
    corrected = np.empty(len(p_values))
    corrected[order] = np.minimum(adjusted, 1)
    return corrected


def paired_test(differences, shapiro_p):
    if np.all(differences == 0):
        return 'No difference', 1.0
    if shapiro_p >= ALPHA:
        return 'Paired t-test', stats.ttest_1samp(differences, 0).pvalue
    return 'Wilcoxon signed-rank', stats.wilcoxon(differences).pvalue


def test_algorithm_differences(dataframe):
    results = []
    normality_folder = output_folder / 'normality_plots'
    normality_folder.mkdir(parents=True, exist_ok=True)

    for motion_type in MOTION_TYPES:
        for severity in SEVERITIES:
            case_data = dataframe[
                (dataframe['motion_type'] == motion_type)
                & (dataframe['severity'] == severity)
            ].sort_values('repeat')

            if case_data.empty:
                print(f'Skipping statistics for {motion_type}, {severity}: no results.')
                continue

            fig, axes = plt.subplots(2, 3, figsize=(13, 8))

            for metric_index, metric in enumerate(METRICS):
                case_results = []
                for pair_index, (method_1, method_2) in enumerate(METHOD_PAIRS):
                    columns = [
                        metric_column(metric, method_1),
                        metric_column(metric, method_2)
                    ]
                    paired_values = case_data[columns].dropna()
                    differences = (
                        paired_values[columns[0]] - paired_values[columns[1]]
                    ).to_numpy()

                    if len(differences) < 3:
                        print(
                            f'Skipping {motion_type}, {severity}, {metric}, '
                            f'{method_1} vs {method_2}: fewer than 3 pairs.'
                        )
                        axes[metric_index, pair_index].set_axis_off()
                        continue

                    shapiro_W, shapiro_p = stats.shapiro(differences)
                    test_name, raw_p = paired_test(differences, shapiro_p)
                    case_results.append({
                        'motion_type': motion_type,
                        'severity': severity,
                        'metric': metric,
                        'comparison': f'{method_1} vs {method_2}',
                        'n': len(differences),
                        'mean_difference': np.mean(differences),
                        'median_difference': np.median(differences),
                        'Shapiro_W': shapiro_W,
                        'Shapiro_p': shapiro_p,
                        'normal_differences': shapiro_p >= ALPHA,
                        'test': test_name,
                        'p_raw': raw_p
                    })

                    stats.probplot(differences, dist='norm', plot=axes[metric_index, pair_index])
                    axes[metric_index, pair_index].set_title(
                        f'{metric}: {method_1} − {method_2}\nShapiro p={shapiro_p:.3g}'
                    )

                if not case_results:
                    continue

                corrected = holm_correction([result['p_raw'] for result in case_results])
                for result, corrected_p in zip(case_results, corrected):
                    result['p_Holm'] = corrected_p
                    result['significant'] = corrected_p < ALPHA
                results.extend(case_results)

            fig.suptitle(f'{MOTION_TYPES[motion_type]} — {severity.capitalize()}')
            fig.tight_layout(rect=[0, 0, 1, 0.94])
            fig.savefig(
                normality_folder / f'{motion_type}_{severity}_paired_differences.svg',
                dpi=300
            )
            plt.close(fig)

    results_dataframe = pd.DataFrame(results)
    results_dataframe.to_csv(output_folder / 'paired_algorithm_tests.csv', index=False)
    return results_dataframe


if __name__ == '__main__':
    output_folder.mkdir(parents=True, exist_ok=True)
    phantom_metrics = load_phantom_metrics()
    plotting_table = make_plotting_table(phantom_metrics)
    plotting_table.to_csv(output_folder / 'phantom_GT_metrics.csv', index=False)
    statistical_results = test_algorithm_differences(phantom_metrics)
    print(statistical_results.to_string(index=False))
