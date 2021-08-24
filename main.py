import streamlit as st
import pandas as pd
import numpy as np
import japanize_matplotlib
import matplotlib.pyplot as plt
from matplotlib import rcParams
from cycler import cycler

# ページ設定
st.set_page_config(layout="wide")
col1, col2, col3 = st.columns([2, 2, 6])
# 色のマスタ設定
tableau_cycle = cycler(color=['#4E79A7', '#F28E2B', '#E15759', '#76B7B2',
                              '#59A14E', '#EDC949', '#B07AA2', '#FF9DA7', '#9C755F', '#BAB0AC'])

# load data


@st.cache(allow_output_mutation=True)
def load_mst_hp():
    df = pd.read_csv('data/mst_hp.csv', encoding='cp932', dtype=object)
    return df


@st.cache(allow_output_mutation=True)
def load_mst_hp2():
    df = pd.read_csv('data/mst_hp.csv', encoding='cp932', dtype=object)
    return df


mst_hp = load_mst_hp()
mst_hp2 = load_mst_hp2()


@st.cache(allow_output_mutation=True)
def load_mst_dpc():
    df = pd.read_csv('data/mst_dpc.csv', encoding='cp932', dtype=object)
    return df


mst_dpc = load_mst_dpc()


@st.cache(allow_output_mutation=True)
def load_data():
    df = pd.read_csv('data/data.csv', encoding='cp932',
                     dtype={'告示番号': str, 'mdc6': str, 'ope': str, 'value': int})
    df = df.merge(mst_hp2[['告示番号', 'hp']], on='告示番号', how='left')
    # df = df.merge(mst_dpc[['mdc6','mdc6name']], on ='mdc6',how='left')
    return df


df = load_data()

# col1　地域検索#########################################################################
col1.markdown('## 地域検索')
# 都道府県
prefsname = list(mst_hp['pref'].unique())
select_prefs = col1.multiselect('都道府県', prefsname)
if select_prefs != []:
    mst_hp = mst_hp.loc[mst_hp['pref'].isin(select_prefs)]
# 二次医療圏
med2s = list(mst_hp['med2'].unique())
select_med2s = col1.multiselect('二次医療圏', med2s)
if select_med2s != []:
    mst_hp = mst_hp.loc[mst_hp['med2'].isin(select_med2s)]
# 市町村
citys = list(mst_hp['city'].unique())
select_citys = col1.multiselect('市区町村', citys)
if select_citys != []:
    mst_hp = mst_hp.loc[mst_hp['city'].isin(select_citys)]
# 検索条件を変数に格納
select_hp = set(mst_hp['告示番号'])

# col1 医療機関指定　#############################################################
col1.markdown('## 医療機関指定')
hpnames = list(mst_hp2['hp'].unique())
select_hpname = col1.multiselect('医療機関名', hpnames)
# select_hpname = col1.multiselect('医療機関名',hpnames,default=['社会医療法人財団石心会　埼玉石心会病院'])
select_hp_number = []
if select_hpname != []:
    mst_hp2 = mst_hp2.loc[mst_hp2['hp'].isin(select_hpname)]
    select_hp_number = list(mst_hp2['告示番号'])

col1.markdown('## グラフ設定')
# グラフ形式選択のボックスを追加
graph_set = col1.selectbox('グラフ選択', ('表示するグラフを選択してください', '病院別', '疾患別'))
display_number = col1.number_input('表示件数', 10, 50, 25, step=5)

# グラフ表示用の文字列を作成
str_prefs = ' '.join(select_prefs)
str_med2s = ' '.join(select_med2s)
str_citys = ' '.join(select_citys)
str_hpnames = ' '.join(select_hpname)

str_loc = '{}\n{}\n{}'.format(str_prefs, str_med2s, str_citys)

# col2 DPC検索　###############################################################
col2.markdown('## DPC検索')
# MDC
mdc = list(mst_dpc['mdcname'].unique())
select_mdc = col2.multiselect('MDC', mdc)
if select_mdc != []:
    mst_dpc = mst_dpc[mst_dpc['mdcname'].isin(select_mdc)]
# MDC6
mdc6 = list(mst_dpc['mdc6name'].unique())
select_mdc6name = col2.multiselect('MDC6', mdc6)
if select_mdc6name != []:
    mst_dpc = mst_dpc[mst_dpc['mdc6name'].isin(select_mdc6name)]
# 手術
openames = list(mst_dpc['opename'].unique())
select_opename = col2.multiselect('手術', openames)
# 手術が選択された場合に該当手術リストを表示
if select_opename != []:
    mst_dpc = mst_dpc[mst_dpc['opename'].isin(select_opename)]
    ope = mst_dpc['手術名'].reset_index(drop=True)
    col2.table(ope)
# 検索条件を変数に格納
select_mdc6 = list(mst_dpc['mdc6'].unique())
select_ope = list(mst_dpc['ope'].unique())
# 検索条件表示用の文字列を作成
str_mdc = ''.join(select_mdc)
str_mdc6 = ' '.join(select_mdc6name)
str_opename = ' '.join(select_opename)
str_dpc = '{}\n{}\n{}'.format(str_mdc, str_mdc6, str_opename)
str_header = '{}\n{}'.format(str_dpc, str_loc)

# データ処理#####################################################################
# 条件抽出
select_hp = select_hp.union(select_hp_number)
df = df[((df['告示番号'].isin(select_hp)) & (
    df['mdc6'].isin(select_mdc6)) & (df['ope'].isin(select_ope)))]

# 病院別の集計 ####################################################################################################
if graph_set == '病院別':
    graph_title = '病院別退院患者数'
    graph_df = df.groupby(['告示番号', 'hp'], as_index=False).sum(
    ).sort_values(['value', '告示番号'], ascending=[False, False])
    graph_hp = set(graph_df.loc[graph_df['value'] != 0].head(
        display_number)['告示番号'])  # 0件を削除　表示件数に絞り込み告示番号
    graph_hp = graph_hp.union(select_hp_number)  # 医療期間指定の病院を追加
    graph_df = graph_df.loc[graph_df['告示番号'].isin(
        graph_hp)]  # 集計テーブルを告示番号で絞り込む
    graph_df.reset_index(drop=True)
    graph_hpnames = list(graph_df['hp'])  # 医療機関指定した病院のインデックス番号をリストで取得
    highlight_hp_indexs = []
    for i in select_hpname:
        if i in graph_hpnames:
            highlight_hp_indexs.append(graph_hpnames.index(i))

    graph_df = graph_df.sort_values(['value', '告示番号'], ascending=[True, True])

    x = graph_df['hp']
    y = graph_df['value']

################################################################################################################
# MDC6別の集計
if graph_set == '疾患別':
    graph_title = 'MDC6別退院患者数'
    if select_hp_number != []:
        df = df[df['告示番号'].isin(select_hp_number)]
        graph_title = 'MDC6別患者数' + '\n(' + str_hpnames + ')'

    colname = 'mdc6'
    graph_df = df.groupby([colname], as_index=False).sum(
    ).sort_values(['value'], ascending=[False])
    graph_set = set(graph_df.loc[graph_df['value'] != 0].head(
        display_number)[colname])  # 0件を削除　表示件数に絞り込み告示番号
    graph_df = graph_df.loc[graph_df[colname].isin(
        graph_set)]  # 集計テーブルを告示番号で絞り込む
    graph_df = graph_df.merge(
        mst_dpc[['mdc6', 'mdc6name']], on='mdc6', how='left')
    graph_df.reset_index(drop=True)

    graph_hpnames = list(graph_df[colname])  # 医療機関指定した病院のインデックス番号をリストで取得
    highlight_hp_indexs = []
    for i in select_hpname:
        if i in graph_hpnames:
            highlight_hp_indexs.append(graph_hpnames.index(i))

    graph_df = graph_df.sort_values(['value'], ascending=[True])

    x = graph_df['mdc6name']
    y = graph_df['value']

# グラフ #######################################################################
if graph_set != '表示するグラフを選択してください':

    fig = plt.figure(figsize=(10, 8), facecolor='1.0')
    ax = plt.axes()
    ax.tick_params(labelsize=10)
    bar_list = ax.barh(x, y, color='0.7')
    rcParams['font.sans-serif'] = ['Hiragino Maru Gothic Pro', 'Yu Gothic', 'Meirio',
                                   'Takao', 'IPAexGothic', 'IPAPGothic', 'VL PGothic', 'Noto Sans CJK JP']

    # ヘッダー、フッター
    fig.text(0.20, 0.995, graph_title, ha='left',
             va='center', fontsize=10)  # グラフタイトル
    fig.text(0.985, 0.995, str_header, ha='right',
             va='center', fontsize=8)  # 検索条件の表示
    fig.text(0.985, 0, '2019年度退院患者調査', ha='right',
             va='center', fontsize=8)  # フッター表示

    # 外枠
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.gca().spines['left'].set_visible(False)
    ax.tick_params(left=False, right=False, top=False)

    # グラフの色設定
    plt.rcParams['axes.prop_cycle'] = tableau_cycle
    # 医療機関指定に追加された順番で色を指定
    cycle = plt.rcParams['axes.prop_cycle'].by_key()['color']
    if highlight_hp_indexs != []:
        for i in highlight_hp_indexs:
            bar_list[-1-i].set_color(cycle[highlight_hp_indexs.index(i)])

    # 件数のラベルを追加
    for patch in ax.patches:
        w, h = patch.get_width(), patch.get_height()
        y = patch.get_y()
        ax.text(w * 1.01, h / 2 + y, f"{w:,}", va="center")
    plt.tight_layout()

    col3.pyplot(fig)
