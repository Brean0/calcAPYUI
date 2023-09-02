# import readline
import streamlit as st
import pandas as pd
from subgrounds import Subgrounds

# streamlit config
st.set_page_config(
    page_title = "Beanstalk APY",
    page_icon = "🌱",
    layout="wide"
)

col1, col2 = st.columns([0.4,0.6], gap ="large")

sg = Subgrounds()
bean = sg.load_subgraph('https://graph.node.bean.money/subgraphs/name/beanstalk-dev')

def getSeeds(address):
    if(address == '0xbea0000029ad1c77d3d5d23ba2d8893db9d1efab'):
        return 3
    elif(address == '0xc9c32cd16bf7efb85ff14e0c8603cc90f6f2ee49'):
        return 3.25
    elif(address == '0xbea0e11282e2bb5893bece110cf199501e872bad'):
        return 4.5
    else: 
        return 0
    
def getGlobalStuff():
    BEANSTALK = '0xc1e088fc1323b20bcbee9bd1b9fc9546db5624c5'

    globalState = bean.Query.silo(id = BEANSTALK).assets(
        orderBy = 'depositedBDV', 
        orderDirection = 'desc', 
        first = 5
    )
    globalData = sg.query_df([
        globalState.token,
        globalState.depositedBDV
    ])
    totalBDV = 0
    totalSeeds = 0
    for i in range(5):
        depositedBDV = globalData.iloc[i]['silo_assets_depositedBDV']
        totalSeeds += depositedBDV * getSeeds(globalData.iloc[i]['silo_assets_token'])
        totalBDV += depositedBDV
    totalSeeds = totalSeeds/1e6
    totalBDV = totalBDV/1e6
    totalStalk = float(sg.query_df([bean.Query.silo(id = BEANSTALK).stalk])['silo_stalk']/1e10)
    return(totalSeeds, totalBDV, totalStalk)

def getUserStuff(address):

    userState = bean.Query.silo(id = address).assets(
        orderBy = 'depositedBDV', 
        orderDirection = 'desc',
        first = 10000
    )
    totalStalk = sg.query_df([bean.Query.silo(id = address)])['silo_stalk']
    userData = sg.query_df([
        userState.token,
        userState.depositedBDV
    ])
    # # TODO, get seeds in a more programic way
    totalBDV = 0
    totalSeeds = 0
    for i in range(5):
        depositedBDV = userData.iloc[i]['silo_assets_depositedBDV']
        totalSeeds += depositedBDV * getSeeds(userData.iloc[i]['silo_assets_token'])
        totalBDV += depositedBDV
    totalSeeds = totalSeeds/1e6
    totalBDV = totalBDV/1e6
    totalStalk = float(totalStalk/1e10)
    return(totalSeeds, totalBDV, totalStalk)

def iterateUser(totalStalk, totalSeeds, userStalk, userSeeds, beansEarnedPerSeason):
    beanSeeds = 3
    _userBeans = 0
    for i in range(8760):
        totalSeeds = totalSeeds + beanSeeds*beansEarnedPerSeason
        totalStalk = totalStalk + beansEarnedPerSeason + (1/10000) * totalSeeds
        _userBeans = _userBeans + (beansEarnedPerSeason*userStalk/totalStalk)
        userStalk = userStalk + (beansEarnedPerSeason*userStalk/totalStalk) + (userSeeds/10000) + (beanSeeds/10000 * _userBeans)
    return(round(totalSeeds,2), round(totalStalk,2), round(_userBeans,2), round(userStalk,2))

def getAPY(address, beansEarnedPerSeason, basis):
    (totalSeeds, totalBDV, totalStalk) = getGlobalStuff()

    # input 
    (userSeeds, userBDV, userStalk) = getUserStuff(address)
    #iterations
    userBeans = 0
    (totalSeeds, totalStalk, userBeans, userStalk) = iterateUser(totalStalk, totalSeeds , userStalk, userSeeds, beansEarnedPerSeason)
    with col2:
        st.write("Avg beans earned per season:", str(beansEarnedPerSeason))
        st.write("Total Stalk: {stalk:2,}".format(stalk = totalStalk))
        st.write("Total Seeds: {seeds:2,}".format(seeds = totalSeeds))
        st.write("User Stalk:  {stalk:2,}".format(stalk = userStalk))
        st.write("User Seeds:  {seeds:2,}".format(seeds = userSeeds))
        st.write("User BDV:  {BDV:2,}".format(BDV = userBDV))
        st.write("Beans earned in a year:  {beans:3,}".format(beans = userBeans))
        txt = "Overall apy: {:%}"
        if(basis != ''):
            st.write("Basis: {Basis:2,}".format(Basis = int(basis)))
            userBDV = int(basis)
        st.write(txt.format((userBeans + userBDV)/(userBDV) - 1))
        

if(__name__ == "__main__"):
    with col1:
        st.title("Beanstalk APY")
        st.subheader("Estimates a farmers overall APY with stalk growth and seeds.")
        address = st.text_input('input address: ')
        beansPerSeason = st.text_input(('input average bean minted per season over a year: '))
        basis = st.text_input('(optional) input cost basis: \n\n (for example, you bought 20,000 BDV worth of unripe deposits for 10,000.)')
        if(address != '' and beansPerSeason != ''):
            getAPY(address.lower(), int(beansPerSeason), basis)