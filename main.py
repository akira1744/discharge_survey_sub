import streamlit as st
import pandas as pd
import numpy as np
import japanize_matplotlib
import matplotlib.pyplot as plt
from matplotlib import rcParams
from cycler import cycler
from streamlit.proto.RootContainer_pb2 import DESCRIPTOR

st.set_page_config(layout="wide")

tableau_cycle = cycler(color=['#4E79A7', '#F28E2B', '#E15759', '#76B7B2', '#59A14E', '#EDC949', '#B07AA2', '#FF9DA7', '#9C755F', '#BAB0AC']) # 色設定

@st.cache(allow_output_mutation=True)
def load_mst_hp():
    mst_hp = pd.read_csv('data/mst_hp.csv', encoding='cp932',
                         index_col=0, dtype={'hpnum': int, 'prefcd': object, 'pref': object, 'med2cd': object, 'med2': object, 'citycd': object, 'city': object, 'hp': object})
    return mst_hp


@st.cache(allow_output_mutation=True)
def load_mst_hp2():
    mst_hp2 = pd.read_csv('data/mst_hp.csv', encoding='cp932',
                          index_col=0, dtype={'hpnum': int, 'prefcd': object, 'pref': object, 'med2cd': object, 'med2': object, 'citycd': object, 'city': object, 'hp': object})
    return mst_hp2


@st.cache(allow_output_mutation=True)
def load_mst_dpc():
    mst_dpc = pd.read_csv('data/mst_dpc.csv', encoding='cp932', dtype=object)
    return mst_dpc


@st.cache(allow_output_mutation=True)
def load_mdc2df():
    mdc2df = pd.read_csv('data/mdc2.csv', encoding='cp932', dtype={'hpnum': int, 'mdc2': object, 'value': int},index_col=0)
    return mdc2df


@st.cache(allow_output_mutation=True)
def load_mdc6df():
    mdc6df = pd.read_csv('data/mdc6.csv', encoding='cp932',
                         index_col=0, dtype={'hpnum': int, 'mdc6': object, 'ope': object, 'value': int})
    return mdc6df

mst_hp = load_mst_hp()
mst_hp2 = load_mst_hp2()
mst_dpc = load_mst_dpc()
mdc2df = load_mdc2df()
mdc6df = load_mdc6df()

st.markdown('## 患者数分析 (2019年度退院患者調査)')

col1, col2, col3 = st.columns([2, 2, 6])

# col1 集計方法選択　####################################################################
graph_set = col1.selectbox('集計方法', ('病院別集計', '疾患別集計'))

# col1　地域検索#########################################################################
col1.markdown('## 地域検索')
# 都道府県
prefsname = list(mst_hp['pref'].unique())
#　@@@
# select_prefs = col1.multiselect('都道府県', prefsname)
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
select_loc_hp = set(mst_hp.index)

# col1 医療機関指定　#############################################################
col1.markdown('## 注目医療機関')
hpnames = list(mst_hp2['hp'].unique())

# @@@
# select_hp_number = col1.multiselect('医療機関名', hpnames)
select_hp_name = col1.multiselect('医療機関名', hpnames)

select_hp_number = []
if select_hp_name != []:
    mst_hp3 = mst_hp2.loc[mst_hp2['hp'].isin(select_hp_name)]
    select_hp_number_df = mst_hp3['hp']
    for i in select_hp_name:
        select_hp_number.append(mst_hp3.loc[mst_hp3['hp']==i].index.values[0])

# # mentenanse
# col1.write('select_hp_name')
# col1.write(select_hp_name)
# col1.write(select_hp_number_df)
# col1.write('select_hp_number')
# col1.write(select_hp_number)


select_hp = select_loc_hp.union(select_hp_number)# 地域検索のhpnumと注目医療機関のhpnumを結合

#########################################################################
# グラフ表示用の文字列を作成
str_prefs = ' '.join(select_prefs)
str_med2s = ' '.join(select_med2s)
str_citys = ' '.join(select_citys)
str_hpnames = '\n'.join(select_hp_name)
str_loc = '{}\n{}\n{}'.format(str_prefs, str_med2s, str_citys)

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
select_mdc2 = list(mst_dpc['mdc'].unique())
select_mdc6 = list(mst_dpc['mdc6'].unique())
select_ope = list(mst_dpc['ope'].unique())

# 検索条件表示用の文字列を作成
str_mdc = ''.join(select_mdc)
str_mdc6 = ' '.join(select_mdc6name)
str_opename = ' '.join(select_opename)
str_dpc = '{}\n{}\n{}'.format(str_mdc, str_mdc6, str_opename)
str_header = '{}\n{}'.format(str_dpc, str_loc)

# 条件抽出前の準備　#############################################################################################
to_mdc2_bol = ((len(select_mdc6name) == 0) & (len(select_opename) == 0 ))# DataSourceを切り分けるための条件
highlight_hp_indexs = [] # ifの後の集計時に使用するために先に宣言

# 病院別集計 ####################################################################################################
if graph_set == '病院別集計':
    graph_title = '病院別退院患者数'

    # mdc2別の集計
    if to_mdc2_bol:

        mdc2df = mdc2df.loc[((mdc2df.index.isin(select_hp)) & (mdc2df['mdc2'].isin(select_mdc2)))]
        mdc2df = mdc2df[['value']]

        graph_mdc2 = mdc2df.groupby('hpnum', as_index=True).sum()
        graph_mdc2 = graph_mdc2.sort_index(ascending=False).sort_values('value', ascending=False)

        graph_hp = set(graph_mdc2.loc[graph_mdc2['value'] != 0].head(display_number).index)  # 0件を削除　表示件数に絞り込み告示番号
        graph_hp = graph_hp.union(select_hp_number)  # 医療期間指定の病院を追加

        graph_mdc2 = graph_mdc2.loc[graph_mdc2.index.isin(graph_hp)]  # 集計テーブルを告示番号で絞り込む
        graph_hpnum = list(graph_mdc2.index)  # 医療機関指定した病院のインデックス番号をリストで取得

        # 注目医療機関をハイライトする為のリストを作成
        for i in select_hp_number:
            if i in graph_hpnum:
                highlight_hp_indexs.append(graph_hpnum.index(i))

        graph_mdc2 = graph_mdc2.sort_index(ascending=True).sort_values('value', ascending=True)
        graph_mdc2 = graph_mdc2.merge(mst_hp2[['hp']], on='hpnum', how='left')

        x = graph_mdc2['hp']
        y = graph_mdc2['value']

        # # maintenance
        # col1.write('graph_hp')
        # col1.write(graph_hp)
        # col1.write('select_hp_number')
        # col1.write(select_hp_number)
        # col1.write('graph_hpnum')
        # col1.write(graph_hpnum)
        # col1.write('highlight_hp_indexs')
        # col1.write(highlight_hp_indexs)
        # col1.write('len(graph_mdc2)')
        # col1.write(len(graph_mdc2))
        # col1.write('x')
        # col1.write(x)
        # col1.write('y')
        # col1.write(y)

    # mdc6別の集計
    else:
        mdc6df = mdc6df.loc[((mdc6df.index.isin(select_hp)) & (mdc6df['mdc6'].isin(select_mdc6)) & (mdc6df['ope'].isin(select_ope)))]
        mdc6df = mdc6df[['value']]
        graph_mdc6 = mdc6df.groupby('hpnum', as_index=True).sum()

        graph_mdc6 = graph_mdc6.sort_index(ascending=False).sort_values('value', ascending=False)
        graph_hp = set(graph_mdc6.loc[graph_mdc6['value'] != 0].head(display_number).index)  # 0件を削除　表示件数に絞り込み告示番号

        graph_hp = graph_hp.union(select_hp_number)  # 医療期間指定の病院を追加
        graph_mdc6 = graph_mdc6.loc[graph_mdc6.index.isin(graph_hp)]  # 集計テーブルを告示番号で絞り込む
        graph_hpnum = list(graph_mdc6.index)  # 医療機関指定した病院のインデックス番号をリストで取得

        # 注目医療機関をハイライトする為のリストを作成
        for i in select_hp_number:
            if i in graph_hpnum:
                highlight_hp_indexs.append(graph_hpnum.index(i))

        graph_mdc6 = graph_mdc6.sort_index(ascending=True).sort_values('value', ascending=True)
        graph_mdc6 = graph_mdc6.merge(mst_hp2[['hp']], on='hpnum', how='left')

        x = graph_mdc6['hp']
        y = graph_mdc6['value']

        # maintenance
        # col1.write('graph_hp')
        # col1.write(graph_hp)
        # col1.write('graph_hpnum')
        # col1.write(graph_hpnum)
        # col1.write('highlight_hp_indexs')
        # col1.write(highlight_hp_indexs)
        # col1.write('len(graph_mdc6)')
        # col1.write(len(graph_mdc6))
        # col1.write('x')
        # col1.write(x)
        # col1.write('y')
        # col1.write(y)
    
# 疾患別集計#################################################################################################################
if graph_set == '疾患別集計':
    graph_title = 'MDC6別退院患者数'
    if select_hp_number != []:
        # mdc6df = mdc6df.loc[mdc6df.index.isin(select_hp_number)]
        mdc6df = mdc6df.loc[((mdc6df.index.isin(select_hp_number)) & (mdc6df['mdc6'].isin(select_mdc6)) & (mdc6df['ope'].isin(select_ope)))]
        graph_title = graph_title + '\n' + str_hpnames

    colname = 'mdc6'
    graph_mdc6 = mdc6df.groupby([colname]).sum().sort_values(['value'], ascending=[False])
    graph_set = set(graph_mdc6.loc[graph_mdc6['value'] != 0].head(display_number).index)  # 0件を削除　表示件数に絞り込み告示番号

    graph_mdc6 = graph_mdc6.loc[graph_mdc6.index.isin(graph_set)]  # 集計テーブルを告示番号で絞り込む
    graph_mdc6 = graph_mdc6.merge(mst_dpc[['mdc6', 'mdc6name']], on='mdc6', how='left')
    graph_mdc6 = graph_mdc6.sort_values('value', ascending=True)

    x = graph_mdc6['mdc6name']
    y = graph_mdc6['value']

    # maintenance
    # col1.write('graph_mdc6')
    # col1.write(graph_mdc6)
    # col1.write('graph_set')
    # col1.write(graph_set)
    # col1.write('len(graph_mdc6)')
    # col1.write(len(graph_mdc6))
    # col1.write('x')
    # col1.write(x)
    # col1.write('y')
    # col1.write(y)

# グラフ #######################################################################
fig = plt.figure(figsize=(10, 7.5), facecolor='1.0')
ax = plt.axes()
ax.tick_params(labelsize=8)
rcParams['font.sans-serif'] = ['Hiragino Maru Gothic Pro', 'Yu Gothic', 'Meirio','Takao', 'IPAexGothic', 'IPAPGothic', 'VL PGothic', 'Noto Sans CJK JP']
bar_list = ax.barh(x, y, color='0.7', label=graph_title)
# ヘッダー、フッター
ax.legend(loc='lower right', bbox_to_anchor=(0, 1), frameon=False,
          handlelength=0,	fontsize=11)  # 凡例をタイトルとして使用
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

# フッター　###################################################################################
link1 = 'https://www.mhlw.go.jp/stf/shingi2/0000196043_00004.html'
link2 = 'https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/0000198757.html'
link3 = 'https://www.e-stat.go.jp/stat-search/files?page=1&query=%E7%97%85%E9%99%A2%E6%95%B0%E3%80%80%E7%97%85%E5%BA%8A%E6%95%B0%E3%80%80%E4%BA%8C%E6%AC%A1%E5%8C%BB%E7%99%82%E5%9C%8F&sort=open_date%20desc&layout=dataset&stat_infid=000031982297&metadata=1&data=1'

my_expander = st.expander('DataSource')
with my_expander:
    st.markdown(
        '[1.令和元年度DPC導入の影響評価に係る調査「退院患者調査」の結果報告について]({})'.format(link1))
    st.markdown(
        '[2.診断群分類（DPC）電子点数表について]({})（診断群分類（DPC）電子点数表（令和元年5月22日更新） '.format(link2))
    st.markdown('[3.医療施設調査 / 令和元年医療施設（動態）調査 二次医療圏・市区町村編]({})'.format(link3))

my_expander = st.expander('Q & A')
with my_expander:
    st.markdown('Q1. 2020年度のデータは見れないか？')
    st.markdown('A1. 例年通りであれば2022年3月にデータが公開されます。公開され次第同様のホームページを作成します')
    st.markdown(' ')
    st.markdown('Q2. 院内の実績値と異なる')
    st.markdown('''
    A2. 厚労省の退院患者調査では、実績が10件未満のデータが公開されていない為、実績値よりも低い数字が表示されます。\n
    　　MDC6を選択している時は、疾患別手術別集計（参考資料２（８））の集計値が表示されます。\n
    　　MDC6を選択していない時は、MDC別医療機関別件数（参考資料２（２））の集計値が表示されます。
    '''
                )
# @@@
st.markdown('***')
st.markdown("Thanks for going through this mini-analysis with me! I'd love feedback on this, so if you want to reach out you can find me on [twitter] (https://twitter.com/inakichii).")
