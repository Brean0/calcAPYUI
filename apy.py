from subgrounds import Subgrounds
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
    return(totalSeeds, totalStalk, _userBeans, userStalk)

def getAPY(address, beansEarnedPerSeason):
    (totalSeeds, totalBDV, totalStalk) = getGlobalStuff()

    # input 
    (userSeeds, userBDV, userStalk) = getUserStuff(address)
    #iterations
    userBeans = 0
    (totalSeeds, totalStalk, userBeans, userStalk) = iterateUser(totalStalk, totalSeeds , userStalk, userSeeds, beansEarnedPerSeason)

    print("beansEarnedPerSeason:", beansEarnedPerSeason)
    print("totalStalk:", totalStalk)
    print("totalSeeds:", totalSeeds)
    print("userStalk: ", userStalk)
    print("userSeeds:", userSeeds)
    print("userBDV:", userBDV)
    print("Bean earned in a year:", userBeans)
    txt = "apy: {:%}"
    print(txt.format((userBeans + userBDV)/(userBDV) - 1))

if(__name__ == "__main__"):
    address = input('input User address: ')
    beansPerSeason = int(input('input average bean minted over a year: '))
    getAPY(address.lower(), beansPerSeason)