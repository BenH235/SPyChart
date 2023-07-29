# SPyChart

An automated Statistical Process Control (SPC) tool designed to streamline SPC analytics.

## Description

This tool allows you to create Statistical Process Control (SPC) charts by feeding in a pandas dataframe with a datetime index and a column containing the process to analyse. There are multiple chart types available, such as XmR-chart, Individual-chart, p-chart, c-chart, u-chart, XbarR-chart, and XbarS-chart.

## Input Requirements

The minimum input requirements to create an SPC chart are:

- A pandas dataframe with a date index and a column containing process data to analyze.
- Selection of one of the available chart types.

Some chart types (p-chart, c-chart, XbarR-chart, and XbarS-chart) may require additional inputs. These inputs are described in detail in the example notebook.

## Additional Arguments

The tool supports the following additional arguments:

- `change_dates`: Requires a list of dates, representing process change dates. At each date, the control lines will be re-calculated. This argument is useful if you know there have been process changes and you want the control lines to reflect these changes.
- `baseline_date`: Requires a single date. This argument is useful if you want the control lines to be calculated only on data up to the baseline_date. This may be useful if you would like to test whether a change in the system is having an impact on the observed process.

## Rule-based Testing

Up to 5 rules are tested to identify any special cause variation.

## Outputs

The SPC charts will be generated using Plotly, providing an interactive visualisation. Additionally, the data used to create the chart will be available, allowing you to produce your own SPC charts.

## Examples

Usage examples of the tool can be found in the examples directory of the repository. These examples demonstrate how to use the SPC tool with various datasets and chart types.

## Version History

* 0.1
    * Initial Release (25-06-2023)





