import streamlit as st
import pandas as pd
import numpy as np
import japanize_matplotlib
import matplotlib.pyplot as plt
from matplotlib import rcParams
from cycler import cycler

# ページ設定
st.set_page_config(layout="wide")
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

st.markdown('# 患者数分析(2019年度退院患者調査)')
col1, col2, col3 = st.columns([2, 2, 6])

# col1 集計方法選択　####################################################################
graph_set = col1.selectbox('集計方法', ('集計方法を選択してください', '病院別集計', '疾患別集計'))

# col1　地域検索#########################################################################
col1.markdown('## 地域検索')
# 都道府県
prefsname = list(mst_hp['pref'].unique())
select_prefs = col1.multiselect('都道府県', prefsname,default=['東京都','埼玉県'])
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
col1.markdown('## 注目医療機関')
hpnames = list(mst_hp2['hp'].unique())
select_hpname = col1.multiselect('医療機関名', hpnames,default=['社会医療法人財団石心会　埼玉石心会病院'])

select_hp_number = []
if select_hpname != []:
    mst_hp2 = mst_hp2.loc[mst_hp2['hp'].isin(select_hpname)]
    select_hp_number = list(mst_hp2['告示番号'])

# グラフ表示用の文字列を作成
str_prefs = ' '.join(select_prefs)
str_med2s = ' '.join(select_med2s)
str_citys = ' '.join(select_citys)
str_hpnames = '\n'.join(select_hpname)
str_loc = '{}\n{}\n{}'.format(str_prefs, str_med2s, str_citys)

col1.markdown('# ') #位置調整

# col2 DPC検索　###############################################################
display_number = col2.number_input('表示件数', 10, 50, 25, step=5)

col2.markdown('## DPC検索')
# MDC
mdc = list(mst_dpc['mdcname'].unique())
select_mdc = col2.multiselect('MDC (病名大分類)', mdc)
if select_mdc != []:
    mst_dpc = mst_dpc[mst_dpc['mdcname'].isin(select_mdc)]
# MDC6
mdc6 = list(mst_dpc['mdc6name'].unique())
select_mdc6name = col2.multiselect('MDC6 (病名小分類)', mdc6)
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

# 条件抽出#######################################################################################################
select_hp = select_hp.union(select_hp_number)
df = df[((df['告示番号'].isin(select_hp)) & (
    df['mdc6'].isin(select_mdc6)) & (df['ope'].isin(select_ope)))]

# 病院別の集計 ####################################################################################################
if graph_set == '病院別集計':
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

# MDC6別の集計　##################################################################################################
if graph_set == '疾患別集計':
    graph_title = 'MDC6別退院患者数'
    if select_hp_number != []:
        df = df[df['告示番号'].isin(select_hp_number)]
        graph_title = graph_title + '\n' + str_hpnames 
        
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
if graph_set != '集計方法を選択してください':

    fig = plt.figure(figsize=(10, 7.5), facecolor='1.0')
    ax = plt.axes()
    ax.tick_params(labelsize=9)
    rcParams['font.sans-serif'] = ['Hiragino Maru Gothic Pro', 'Yu Gothic', 'Meirio',
                                   'Takao', 'IPAexGothic', 'IPAPGothic', 'VL PGothic', 'Noto Sans CJK JP']
    bar_list = ax.barh(x, y, color='0.7',label=graph_title)
    # ヘッダー、フッター
    ax.legend(loc='lower right', bbox_to_anchor=(0,1),frameon=False,handlelength=0,	fontsize=11) # 凡例をタイトルとして使用
    fig.text(0.985, 0.995, str_header, ha='right',va='center', fontsize=8)  # 検索条件の表示
    fig.text(0.985, 0, '2019年度退院患者調査', ha='right',va='center', fontsize=8)  # フッター表示
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

# フッター　###################################################################################
link1 = 'https://www.mhlw.go.jp/stf/shingi2/0000196043_00004.html'
link2 = 'https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/0000198757.html'
link3 = 'https://www.e-stat.go.jp/stat-search/files?page=1&query=%E7%97%85%E9%99%A2%E6%95%B0%E3%80%80%E7%97%85%E5%BA%8A%E6%95%B0%E3%80%80%E4%BA%8C%E6%AC%A1%E5%8C%BB%E7%99%82%E5%9C%8F&sort=open_date%20desc&layout=dataset&stat_infid=000031982297&metadata=1&data=1'

my_expander = st.expander('DataSource')
with my_expander:
    st.markdown('[1.令和元年度DPC導入の影響評価に係る調査「退院患者調査」の結果報告について]({})（※疾患別手術別の実績が10件未満の場合、データが非公開の為0件で集計） '.format(link1))
    st.markdown('[2.診断群分類（DPC）電子点数表について]({})（診断群分類（DPC）電子点数表（令和元年5月22日更新） '.format(link2))
    st.markdown('[3.医療施設調査 / 令和元年医療施設（動態）調査 二次医療圏・市区町村編]({})'.format(link3))

my_expander = st.expander('Q & A')
with my_expander:
    st.markdown('Q1. 2020年度のデータは見れないか？')
    st.markdown('A1. 例年通りであれば2022年3月にデータが公開されます。公開され次第同様のホームページを作成します')
    st.markdown(' ')
    st.markdown('Q2. 院内の実績値と異なる')
    st.markdown('''
    A2. 厚労省の退院患者調査では、疾患別手術別の実績が10件未満のデータは非公開となっている為0件で集計しています。\n
    　　患者数が多い疾患や手術の数字は実績値に近いと思います。\n
    　　全病院で同様集計がされていますので、他院との相対比較としてご使用ください。
    '''
    )

# st.markdown('***')
st.markdown("Thanks for visiting my website! I'd love feedback on this, so if you want to reach out you can find me on [twitter] (https://twitter.com/inakichii).")