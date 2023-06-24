# SPC
A statistical process control (SPC) tool for automating the steps in SPC analysis.

## Description

The minimum required to create an SPC chart with this tool is a pandas dataframe, containing a date column and the process to analyse, and a chosen chart from one of the following chart types:

  - XmR-chart
  - Individual-chart
  - p-chart
  - c-chart
  - u-chart
  - XbarR-chart
  - XbarS-chart

Additional arguments include:

- change_dates: Requires a list of dates, representing process change dates. At each date, the control lines will be re-calculated. This argument is useful if you know there have been process changes and you want the control lines to reflect these changes.
- baseline_date: Requires a single date. This argument is useful if you want the control lines to be calculated only on the data up to the baseline_date. This may be useful if you would like to test whether a change in the system is having an impact on the observed process.

The tool will then test up to 8 rules for special cause variation. The chart will then be produced (using Plotly) for interactive visulisation and will include the control lines, the input data, and any points which exhibit special cause variation. The data will also be available, should you wish to produce your own SPC chart.

## Examples

You can find usage examples in the examples directory of this repository. The examples demonstrate how to use the SPC tool with different datasets and chart types.

## Version History

* 0.1
    * Initial Release (24-06-2023)
