# SPC
A statistical process control (SPC) tool for automating the steps in SPC analysis.

## Description

Feed in a pandas dataframe, along with the name of the target column and the date column and the SPC chart type.

- Allowable chart types:
  - XmR-chart
  - Individual-chart
  - p-chart
  - c-chart
  - u-chart
  - XbarR-chart
  - XbarS-chart
 
You also have the option to include additional input on what data to calculate the control lines on.

- change_dates: You can include a list of dates. At each date, the control lines will be re-calculated. This argument is useful if you know the process changes and a certain date, and you want control lines to reflect this change.
- baseline_date: This argument is useful if you want the control lines to be calculated only on the data up to baseline_date. This may be useful if you would like to test whether a change in the system is having an impact on the observed process.

- The tool will then test up to 8 rules for special cause variation.

- SPC charts will then be output (using Plotly) for interactive visualization.

- The tool can also return the data needed to build SPC charts from scratch.

## Examples

You can find usage examples in the examples directory of this repository. The examples demonstrate how to use the SPC tool with different datasets and chart types.

## Version History

* 0.1
    * Initial Release (24-06-2023)
