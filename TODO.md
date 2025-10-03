* Add CLI argument and `--cli` file key `--disable` which is a comma separated list of patterns to disable. These patterns should be skipped when analyzing fields, to improve performance.
* Keep track of which patterns were never seen, and at the end suggest using `--disable` to disable them as it may improve performance.
* Add options key "autodisable" which is a boolean that automatically adds unused patterns to the disable list. Alter the message at the end of the run to say it was added to the list, instead of suggesting to disable it.
