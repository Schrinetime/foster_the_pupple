import os
import glob
import pandas as pd

folder_loc = os.getcwd()
files = sorted(glob.glob(os.path.join(folder_loc, "logs", "*.csv")))

dfs = {}
for file in files:
    dfs[file] = pd.read_csv(file)

pre = dfs[list(dfs.keys())[-2]]
cur = dfs[list(dfs.keys())[-1]]

df_all = cur.merge(pre.drop_duplicates(),
                   how='outer', indicator=True)

diff = df_all[df_all['_merge'].ne('both')]

updates = diff[(diff['id'].duplicated(keep=False) &
                ~diff.duplicated(subset=[c for c in cur if c != 'age'], keep=False)
                )].sort_values('id')


def check_update_context(df):

    change_df = df[[c for c in df.columns if df[c].nunique() > 1]]
    name_breed = f"{df['name'].iloc[0]} ({df['breed'].iloc[0]})"
    for c in [c for c in change_df.columns if c != '_merge']:

        change_was = change_df.loc[change_df['_merge'].eq('right_only'), c].iloc[0]
        changed_to = change_df.loc[change_df['_merge'].eq('left_only'), c].iloc[0]

        if c == 'breed':
            context = f"seems to be a {changed_to}, rather than a {change_was}"

        elif c == 'loc':
            context = f"is now in {changed_to} instead of {change_was}"

        else:
            context = f"{changed_to} was {change_was}"

        print(f"{name_breed} {context.lower()}")


updates.groupby('id').apply(check_update_context)

in_out = diff[~diff['id'].duplicated(keep=False)].sort_values(['_merge', 'status', 'loc'])


def check_in_out_context(df):

    if df['_merge'] == 'left_only':

        if df['status'] == 'adoption':
            status_text = "is now available for adoption"

        elif df['status'] == 'lost&found':
            status_text = "is lost :("

        else:
            status_text = "is new around here"
    else:

        if df['status'] == 'adoption':
            status_text = "was adopted! (...or x_x)"

        elif df['status'] == 'lost&found':
            status_text = "was found! (...or x_x)"

        else:
            status_text = "is no longer around"

    print(f"{df['name']} ({df['breed']}) {status_text}")


in_out.apply(check_in_out_context, axis=1)
arf = cur[cur['loc'].ne('Foster Home')]
