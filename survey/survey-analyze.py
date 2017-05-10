#!/usr/bin/env python3

import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np
import pandas as pd
import datetime
import os
import re
import collections

def setup():
    pd.set_option('display.width', 120)

def reorder_columns(df):
    """
    Reorder the columns in a DataFrame from largest to smallest using the last row's numeric data.
    Useful for modifying the legend order to match that of the last plotted values.
    """

    last_row = df.iloc[[-1]]
    latest_date = last_row.index[0] # index value
    df = df.sort_values(by=latest_date, ascending=False, axis=1)
    return df

def normalize_language(lang):
    """Process freeform language string into a known format"""

    pattern = re.compile(r"\s+")
    language = pattern.sub("", lang if isinstance(lang, str) else "").lower()
    if len(language) > 0:
        language = language[0].upper() + language[1:]
        language_temp = language
        mappings = {"C#" : "CSharp",
                    "Golang" : "Go",
                    "Android" : "Java",
                    "Scala" : "Java",
                    "Javascript-node.js" : "Javascript",
                    "Node.js" : "Javascript",
                    "Objectivec" : "Objective-c"}
        language = mappings[language] if language in mappings else language
#        if language_temp != language:
#            print("Changed from {} to {}".format(language_temp, language))
    return language

def save_data(df, filename):
    df.to_csv(filename)
    print("Data saved: {}".format(filename))

def save_plot(p, start, end, name):
#    filename = name + start + "To" + end + ".png"
    filename = name + ".png"
    p.get_figure().savefig(filename)
    print("Plot saved: {}".format(filename))

def analyze_file(filename, quiet, one_per_ipaddress, yearly):
    if not os.path.isfile(filename):
        raise RuntimeError("Not a file: {}".format(filename))

    if not quiet:
        print("Reading {}".format(filename))

    # Filter out some lines, there are some of these: Expected 32 fields in line 452, saw 33
    data = pd.read_csv(filename, error_bad_lines=False, warn_bad_lines=not quiet, encoding="latin1")

    # Drop obvious duplicates as they have the same data including submission time down to 1 second
    keep_obvious_duplicates = False
    if not keep_obvious_duplicates:
        size_before = len(data)
        data = data.drop_duplicates()
        duplicates_count = size_before - len(data)
        if duplicates_count > 0 and not quiet:
            print("Removed {} ({}%) obvious duplicates from {} ".format(duplicates_count, round(duplicates_count/size_before*100.0, 1), os.path.basename(filename)))

    # Filter out entries from the same IP address.
    # Off by default... note that 2008-03 all entries for the from 1st to 18th are from one IP address !?!
    if one_per_ipaddress:
        size_before = len(data)
        data = data.drop_duplicates(subset="IPAddress")
        duplicates_count = size_before - len(data)
#        if duplicates_count > 0 and not quiet:
        if duplicates_count > 0:
            print("Removed {} ({}%) IP address duplicates from {} ".format(duplicates_count, round(duplicates_count/size_before*100.0, 1), os.path.basename(filename)))

    ops_headings = [
        "BSD",
        "HPUX",
        "Linux",
        "MacOSX",
        "Solaris",
        "Windows",
        "OtherOS"]

    misc_headings = [
        "LogDate",
        "IPAddress",
        "SpareLang1",
        "SpareLang2",
        "SpareLang3",
        "OtherLang",
        "NamedLanguage",
        "SpareOS1",
        "SpareOS2",
        "SpareOS3",
        "OtherOS",
        "NamedOS"]

    lang_headings = [lang for lang in data.columns.values if lang not in ops_headings + misc_headings]

    # Some data is corrupt as it contains unexpected values - just filter out these rows
    acceptable_values = ["1", 1, 1.0]
    for column_name in lang_headings + ops_headings:
        size_before = len(data)
        data = data[data[column_name].isin(acceptable_values) | data[column_name].isnull()]
        invalid_count = size_before - len(data)
        if invalid_count > 0 and not quiet:
            print("Removed {} invalid rows due to corrupted data in the '{}' column".format(invalid_count, column_name))
        data[column_name] = data[column_name].apply(pd.to_numeric) # Corrupted data usually means the dtype was not float64

    filebasename = os.path.splitext(os.path.basename(filename))[0]
    data["LogDate"] = pd.to_datetime(data["LogDate"])
    data["Date"] = [datetime.datetime(t.year, 1 if yearly else t.month, 1) for t in data["LogDate"]]

    operating_systems = data.filter(["Date"] + ops_headings)
    ops = operating_systems.groupby(["Date"])
    ops = ops.aggregate(np.sum).reset_index()
    ops = ops.rename(columns = {"OtherOS" : "Other"})

    languages = data.filter(["Date"] + lang_headings)
    langs = languages.groupby(["Date"])
    langs = langs.aggregate(np.sum).reset_index()

    # Create a Counter dictionary of the named languages and the count of each
    named_languages = collections.Counter([normalize_language(lang) for lang in data["NamedLanguage"]])
    del named_languages[""]

    # These are misunderstandings by users thinking C/C++ are target languages
    del named_languages["C/c++"]
    del named_languages["C"]
    del named_languages["C++"]

    # Add in new columns for the languages specified in the NamedLanguage column
    minimum_count = -1
    for lang, count in named_languages.items():
        if count >= minimum_count: # filter out noise when minimum_count is set to be > 0
            if lang not in langs:
                langs[lang] = 0.0
            langs[lang] = langs[lang] + float(count)

    return (ops, langs)

def analyze_directory(directory, quiet, show_graphs, show_tables, begin_year, end_year, one_per_ipaddress, yearly):

    drop_first_period = False

    # Start/end year validation
    if begin_year and begin_year < 2000:
        raise RuntimeError("Invalid start year {}".format(begin_year))
    if end_year and end_year < 2000:
        raise RuntimeError("Invalid end year {}".format(end_year))
    start_limit = None if not begin_year else datetime.datetime(begin_year, 1, 1)
    end_limit = None if not end_year else datetime.datetime(end_year, 12, 31)
    if start_limit and end_limit and start_limit >= end_limit:
        raise RuntimeError("start year {} must be less than end year {}".format(begin_year, end_year))

    files = sorted([os.path.join(directory, f) for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))])
    operating_systems = None
    languages = None
    for f in files[:]:
        (ops, langs) = analyze_file(f, quiet, one_per_ipaddress, yearly)
        operating_systems = pd.concat([operating_systems, ops])
        languages = pd.concat([languages, langs])

    # Sum up duplicate rows - this is actually only really necessary for the yearly option
    operating_systems = operating_systems.groupby(["Date"])
    operating_systems = operating_systems.aggregate(np.sum).reset_index()
    languages = languages.groupby(["Date"])
    languages = languages.aggregate(np.sum).reset_index()

    # Operating systems...
    ops = operating_systems.set_index("Date")
    ops.reindex()
    if drop_first_period and len(ops) > 1:
        ops = ops.drop(ops.index[0]) # Remove first month's data which doesn't start from 1st of the month

    if start_limit:
        ops = ops[ops.index >= start_limit]
        if ops.empty:
            raise RuntimeError("No data to show after limiting to start year {}".format(begin_year))
    if end_limit:
        ops = ops[ops.index <= end_limit]
        if ops.empty:
            raise RuntimeError("No data to show after limiting to end year {}".format(end_year))
    if ops.empty:
        raise RuntimeError("No data to show - something has gone horribly wrong!")

    total_ops = pd.DataFrame(ops.sum())
    total_ops = total_ops.rename(columns = {0 : "Count"})
    ops_sum = total_ops["Count"].sum()
    total_ops["Percent"] = total_ops["Count"].div(ops_sum).multiply(100.0).round(1)
    total_ops = total_ops.sort_values(by="Count", ascending=False)

    ops = reorder_columns(ops)

    columns = ops.columns
    ops_percent = ops[columns].div(ops[columns].sum(axis=1), axis=0).multiply(100.0)

    if show_tables:
        print("Operating Systems Count:\n{}".format(ops.to_string()))
        print("Operating Systems Percent:\n{}".format(ops_percent.to_string()))

    start_date = ops.index.min()
    start = start_date.strftime("%Y-%m")
    end_date = ops.index.max()
    end = end_date.strftime("%Y-%m")
    print("Operating system totals over entire period ({} to {}):\n{}".format(start, end, total_ops.to_string()))

    # Target languages...
    langs = languages.set_index("Date")
    langs.reindex()
    if drop_first_period and len(langs) > 1:
        langs = langs.drop(langs.index[0]) # Remove first month's data which doesn't start from 1st of the month

    if start_limit:
        langs = langs[langs.index >= start_limit]
    if end_limit:
        langs = langs[langs.index <= end_limit]

    # Get totals for each language and sort
    total_langs = pd.DataFrame(langs.sum()).sort_values(by=0, ascending=False)
    # Remove least popular languages, also removes a lot of junk entered in the free form NamedLanguage column
    total_langs = total_langs[total_langs[0] > 50.0]
    total_langs = total_langs.rename(columns = {0 : "Count"})
    langs_sum = total_langs["Count"].sum()
    total_langs["Percent"] = total_langs["Count"].div(langs_sum).multiply(100.0).round(2)
    keep_langs = [lang for lang in total_langs.index]
    langs = langs[keep_langs]
    langs = reorder_columns(langs)

    columns = langs.columns
    langs_percent = langs[columns].div(langs[columns].sum(axis=1), axis=0).multiply(100.0)

    if show_tables:
        print("Target languages Count:\n{}".format(langs.to_string()))
        print("Target languages Percent:\n{}".format(langs_percent.to_string()))

    if start_date != langs.index.min():
        raise RuntimeError("Unexpected error: start date for target language does not match start date for operating systems")
    if end_date != langs.index.max():
        raise RuntimeError("Unexpected error: end date for target language does not match end date for operating systems")

    print("Target languages totals over entire period ({} to {}):\n{}".format(start, end, total_langs.to_string()))

    save_data(ops, "SWIGSurveyOperatingSystemsCount.csv")
    save_data(ops_percent, "SWIGSurveyOperatingSystemsPercent.csv")
    save_data(langs, "SWIGSurveyTargetLanguagesCount.csv")
    save_data(langs_percent, "SWIGSurveyTargetLanguagesPercent.csv")

    # Graphing...
    figure_size = (14, 9)
    p = ops.plot(title="SWIG Survey - Operating System Usage", ylim=(0), figsize=figure_size)
    p.set_ylabel("Count")
    p.legend(loc="upper right")
    save_plot(p, start, end, "SWIGSurveyOperatingSystemsCount")
    p = ops_percent.plot(title="SWIG Survey - Operating System Usage", ylim=(0), figsize=figure_size)
    p.set_ylabel("Percent")
    p.legend(loc="upper right")
    save_plot(p, start, end, "SWIGSurveyOperatingSystemsPercent")

    group1_count = 10
    group2_count = 20
    p = langs[langs.columns[:group1_count]].plot(title="SWIG Survey - Target Language Usage (Top {})".format(group1_count), ylim=(0), figsize=figure_size)
    p.set_ylabel("Count")
    p.legend(loc="upper right")
    save_plot(p, start, end, "SWIGSurveyTargetLanguagesTopCount")
    p = langs_percent[langs_percent.columns[:group1_count]].plot(title="SWIG Survey - Target Language Usage (Top {})".format(group1_count), ylim=(0), figsize=figure_size)
    p.set_ylabel("Percent")
    p.legend(loc="upper right")
    save_plot(p, start, end, "SWIGSurveyTargetLanguagesTopPercent")

    if len(langs) > group1_count:
        p = langs[langs.columns[group1_count:group2_count]].plot(title="SWIG Survey - Target Language Usage (Next {})".format(group2_count-group1_count), ylim=(0), figsize=figure_size)
        p.set_ylabel("Count")
        p.legend(loc="upper right")
        save_plot(p, start, end, "SWIGSurveyTargetLanguagesNextCount")
        p = langs_percent[langs_percent.columns[group1_count:group2_count]].plot(title="SWIG Survey - Target Language Usage (Next {})".format(group2_count-group1_count), ylim=(0), figsize=figure_size)
        p.set_ylabel("Percent")
        p.legend(loc="upper right")
        save_plot(p, start, end, "SWIGSurveyTargetLanguagesNextPercent")

    if show_graphs:
        plt.show()

if __name__ == "__main__":
    import argparse
    default_directory = "swigsurvey"
    parser = argparse.ArgumentParser(description="Analyze the SWIG survey results. Generate graph and data csv files showing operating system and target language usage.")
    parser.add_argument("-b", "--begin-year", required=False, default=None, type=int, help="Limit analysis to begin at the given year (default is no limit)")
    parser.add_argument("-d", "--directory", required=False, default=default_directory, help="Directory to analyze, default is '{}'".format(default_directory))
    parser.add_argument("-e", "--end-year", required=False, default=None, type=int, help="Limit analysis to end at the given year (default is no limit)")
    parser.add_argument("-g", "--show-graphs", required=False, default=False, action="store_true", help="Show graphs at end of run (default is not to show)")
    parser.add_argument("-i", "--one-per-ipaddress", required=False, default=False, action="store_true", help="Only accept one entry for each IP address per month (default is to keep duplicates submitted by one IP address")
    parser.add_argument("-t", "--show-tables", required=False, default=False, action="store_true", help="Show results tables (default is not to show)")
    parser.add_argument("-v", "--verbose", required=False, default=False, action="store_true", help="Verbose mode")
    parser.add_argument("-y", "--yearly", required=False, default=False, action="store_true", help="Group data and analyse per year (default is to do this per month)")
    args = parser.parse_args()

    setup()
    analyze_directory(args.directory, not args.verbose, args.show_graphs, args.show_tables, args.begin_year, args.end_year, args.one_per_ipaddress, args.yearly)
