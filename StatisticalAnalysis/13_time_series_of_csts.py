import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np

bl_lst = ['BB']

bl_dict = {
            # 'BB':['2005-2008','2006-2009','2007-2010','2008-2011','2009-2012','2010-2013',
            #      '2011-2014','2012-2015','2013-2016','2014-2017','2015-2018'],
           'BB':['2005-2011','2012-2018'],
           'SA':['2008-2014','2012-2018'],
           'BV':['2012-2018'],#'2005-2011','2008-2014',
           'LS':['2012-2018']}

for bl in bl_lst:

    pth = fr"Q:\FORLand\Clemens\data\tables\crop_sequence_types\BB\BB_CSTArea.xlsx"
    df_lst = []

    per_lst = bl_dict[bl]
    for per in per_lst:
        df = pd.read_excel(pth, sheet_name=per)
        df = df.drop(index=df.index[df['MainType'].isin(['SUM'])])  #'D', 'F', 'H',
        df = pd.melt(df, id_vars=['MainType'], value_vars=['1', '2', '3', '4', '5', '6', '7', '8', '9'])
        df['Period'] = per
        df_lst.append(df)

    df = pd.concat(df_lst, axis=0)
    df['CST'] = df['MainType'].astype(str) + df['variable'].astype(str)

    per_dict = {per:str(i+1) for i, per in enumerate(per_lst)}
    df['per_ind'] = df['Period'].map(per_dict)

    per_indeces = df['per_ind'].unique()
    df_sval = df.loc[df['per_ind'] == '1'].copy()
    sval_dict = {cst:df_sval['value'].to_list()[i] for i, cst in enumerate(df_sval['CST'])}
    # sval_dict.update((k, 0.0001) for k, v in sval_dict.items() if v == 0)

    df_lst = []
    csts = df['CST'].unique()
    for cst in csts:
        df_sub = df.loc[df['CST'] == cst].copy()
        df_sub['value'] = df_sub['value'] / sval_dict[cst]
        df_lst.append(df_sub)

    df_ind = pd.concat(df_lst, axis=0)
    df_ind = df_ind.drop(index=df_ind.index[df_ind['CST'].isin(['D9'])])
    df_ind.replace([np.inf, -np.inf], np.nan, inplace=True)
    df_ind = df_ind.dropna()

    mean_val = df_ind['value'].mean()
    std_val = df_ind['value'].std()
    print(mean_val, std_val)
    df_ind = df_ind.loc[(df_ind['value']< 1 - std_val) | (df_ind['value'] > 1 + std_val) | (df_ind['value'] == 1)]

    winner = df_ind.loc[df_ind['value'] > 1 + std_val]
    winner_csts = list(winner['CST'].unique())
    print('Increase: ', winner_csts)

    looser = df_ind.loc[df_ind['value'] < 1 - std_val]
    looser_csts = list(looser['CST'].unique())
    print('Decrease: ', looser_csts)

    ## plot structural types
    main_types = df['MainType'].unique()
    colors = ['#ffd37f', '#e69600', '#a87000', '#d1ff73', '#7aab00', '#4c7300', '#bee8ff', '#73b2ff', '#004da8']  ##list(mcolors.BASE_COLORS)
    df_sub = df.groupby(['MainType', 'Period'])['value'].sum().reset_index()
    fig, ax = plt.subplots(nrows=1, ncols=1)
    for i, mt in enumerate(main_types):
        df_plt = df_sub.loc[df_sub['MainType'] == mt]
        color = colors[i]
        ax.plot(df_plt['Period'], df_plt['value'], c=color)
    out_pth = r"Q:\FORLand\Clemens\figures\plots\changes between periods\time series normalized\ts_struct_types_2005-2018.png"
    plt.savefig(out_pth)

    #### functional types
    sub_types = df['variable'].unique()
    colors=['#ffd37f', '#e69600', '#a87000', '#d1ff73', '#7aab00', '#4c7300', '#bee8ff', '#73b2ff', '#004da8']
    ## plot structural types
    df_sub = df.groupby(['variable', 'Period'])['value'].sum().reset_index()
    fig, ax = plt.subplots(nrows=1, ncols=1)
    for i, st in enumerate(sub_types):
        df_plt = df_sub.loc[df_sub['variable'] == st]
        color = colors[i]
        ax.plot(df_plt['Period'], df_plt['value'], c=color)
    out_pth = r"Q:\FORLand\Clemens\figures\plots\changes between periods\time series normalized\ts_funct_types_2005-2018.png"
    plt.savefig(out_pth)

    #### csts normal
    csts = df['CST'].unique()
    colors = list(mcolors.CSS4_COLORS)
    ## plot structural types
    df_sub = df.groupby(['CST', 'Period'])['value'].sum().reset_index()
    fig, ax = plt.subplots(nrows=1, ncols=1)
    for i, cst in enumerate(csts):
        df_plt = df_sub.loc[df_sub['CST'] == cst]
        color = colors[i]
        ax.plot(df_plt['Period'], df_plt['value'], c=color)
    out_pth = r"Q:\FORLand\Clemens\figures\plots\changes between periods\time series normalized\ts_csts_2005-2018.png"
    plt.savefig(out_pth)

    #### csts normalized
    csts = df_ind['CST'].unique()
    colors = list(mcolors.CSS4_COLORS)
    ## plot structural types
    df_sub = df_ind.groupby(['CST', 'Period'])['value'].sum().reset_index()
    fig, ax = plt.subplots(nrows=1, ncols=1)
    for i, cst in enumerate(csts):
        df_plt = df_sub.loc[df_sub['CST'] == cst]
        color = colors[i]
        ax.plot(df_plt['Period'], df_plt['value'], c=color)
    out_pth = r"Q:\FORLand\Clemens\figures\plots\changes between periods\time series normalized\ts_csts-normalized_2005-2018.png"
    plt.savefig(out_pth)