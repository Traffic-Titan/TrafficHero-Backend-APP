'''
尚未製作API
'''
english = ['KeelungCity', 'TaipeiCity', 'NewTaipeiCity', 'TaoyuanCity', 'HsinchuCity', 'HsinchuCounty', 'MiaoliCounty', 'TaichungCity', 'ChanghuaCounty', 'NantouCounty', 'YunlinCounty', 'ChiayiCity', 'ChiayiCounty', 'TainanCity', 'KaohsiungCity', 'PingtungCounty', 'TaitungCounty', 'HualienCounty', 'YilanCounty', 'PenghuCounty', 'KinmenCounty']
chinese = ['基隆市', '臺北市', '新北市', '桃園市', '新竹市', '新竹縣', '苗栗縣', '臺中市', '彰化縣', '南投縣', '雲林縣', '嘉義市', '嘉義縣', '臺南市', '高雄市', '屏東縣', '臺東縣', '花蓮縣', '宜蘭縣', '澎湖縣', '金門縣']

def englishToChinese(name: str):
    if name in english:
        return chinese[english.index(name)]
    else:
        return None
    
def chineseToEnglish(name: str):
    if name in chinese:
        return english[chinese.index(name)]
    else:
        return None