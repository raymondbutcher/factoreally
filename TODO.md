* Move the NumberAnalyzer logic into NumberHint.create_from_values
* Simplify outlier code in number_hint.py - are all of the outlier dataclasses needed? Does it actually use anything besides data_without_extreme_outliers, outliers.bounds.iqr_lower, outliers.bounds.iqr_upper?
* Improve NumberStringHint to use the NumericAnalyzer for better random numbers.
* Create a `--cli` argument which is a path to a file. This file should contain a JSON object with any of the keys `--in`, `--out`, `--model`. When these keys exist, they will be used as default values for the respective CLI arguments. Passing in CLI arguments takes priority over the values in this file
* Add CLI argument and `--cli` file key `--disable` which is a comma separated list of patterns to disable. These patterns should be skipped when analyzing fields, to improve performance.
* Keep track of which patterns were never seen, and at the end suggest using `--disable` to disable them as it may improve performance.
* Add options key "autodisable" which is a boolean that automatically adds unused patterns to the disable list. Alter the message at the end of the run to say it was added to the list, instead of suggesting to disable it.
