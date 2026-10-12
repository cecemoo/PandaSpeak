def vocab(word, pinyin, meaning):
    return {'word': word, 'pinyin': pinyin, 'meaning': meaning}


PASSAGES = {
    'qing-entry': '1644年，李自成攻入北京後，明朝將領吳三桂與清軍合作。多爾袞率清軍入關，擊敗李自成軍並進入北京。順治帝隨後遷都北京，清朝開始建立對中原的統治。',
    'zheng-chenggong-taiwan': '鄭成功原本是抗清的南明將領。1661年他率軍渡海攻打臺灣的荷蘭東印度公司據點，1662年荷方投降。鄭氏政權在臺灣建立統治，直到1683年清朝取得臺灣。',
    'revolt-three-feudatories': '1673年，吳三桂等藩王反抗清廷撤藩，戰事波及中國南方多地。康熙帝堅持平亂，清軍於1681年結束叛亂，中央對地方的控制因而加強。',
    'qing-taiwan-1683': '1683年，清朝將領施琅率水師在澎湖擊敗鄭氏軍隊，鄭克塽隨後降清。1684年清廷設臺灣府，隸屬福建省，臺灣進入清朝統治時期。',
    'kangxi-southern-tour': '康熙帝多次南巡江南，視察黃河與運河治理，也接觸地方官員及士人。南巡反映清朝皇帝重視交通、財政與地方統治，也留下許多民間傳說。',
    'treaty-nerchinsk': '1689年，清朝與俄國在尼布楚談判並簽訂條約，處理東北邊界與貿易問題。這是清朝對外外交史的重要事件之一，也顯示當時清俄雙方以談判處理邊界爭端。',
    'yongzheng-reforms': '雍正帝在位期間推行攤丁入畝、養廉銀等改革，試圖改善賦稅分配及官員俸給。他也設立軍機處的前身機制，使皇權與中央行政更加集中。',
    'qianlong-dream-red-chamber': '清代作家曹雪芹創作《紅樓夢》，透過賈府人物的命運描寫家庭、情感與社會變遷。這部小說以細膩的人物刻畫與語言聞名，被視為中國古典小說的代表作之一。',
    'heshen-downfall': '和珅深受乾隆帝信任，長期掌握重要權力。1799年乾隆帝去世後，嘉慶帝迅速查辦和珅，將其革職並賜死。民間以「和珅跌倒，嘉慶吃飽」形容其龐大財產被查抄。',
    'opium-war': '1840年至1842年，清朝與英國爆發第一次鴉片戰爭。清軍戰敗後簽訂《南京條約》，割讓香港島並開放通商口岸。這場戰爭是近代中國歷史的重要轉折。',
    'taiping-rebellion': '1851年洪秀全等人在廣西發動起事，建立太平天國。1853年太平軍攻占南京並定都於此。戰爭持續多年，造成嚴重的人口與經濟損失，1864年清軍攻陷南京後太平天國主要政權覆滅。',
    'self-strengthening': '十九世紀後半，曾國藩、李鴻章、左宗棠等官員推動洋務運動，興辦軍工、船政、學堂與企業。他們希望以新技術強化國防，但改革仍受到政治與制度上的限制。',
    'sino-japanese-war': '1894年清朝與日本因朝鮮問題爆發戰爭，清軍與北洋艦隊相繼失利。1895年雙方簽訂《馬關條約》，清朝割讓臺灣及澎湖給日本。此事深刻影響東亞與臺灣近代歷史。',
    'hundred-days-reform': '1898年，光緒帝在康有為、梁啟超等人影響下推行新政，涉及教育、行政與經濟。改革約百日後遭到保守勢力反擊，慈禧太后重新掌權，許多措施被撤銷。',
    'boxer-rebellion': '義和團在華北興起，帶有反外國勢力與反基督教的色彩。1900年局勢升級，八國聯軍攻入北京。清廷於1901年簽訂《辛丑條約》，承擔巨額賠款與其他義務。',
    'late-qing-new-policies': '1901年後清政府推動新政，改革軍隊、教育及行政制度。1905年科舉制度正式廢除，結束延續千餘年的選官考試傳統。改革帶來新式教育與政治討論，但未能阻止王朝危機。',
    'wuchang-uprising': '1911年10月10日，武昌起義爆發，隨後多省宣布脫離清廷。1912年2月12日，宣統帝溥儀退位，清朝統治正式結束。依照朝代故事分類，清朝滅亡屬於清朝故事。',
}


def lesson(slug, level, icon, title, chinese_title, intro):
    return {
        'slug': slug, 'level': level, 'era': 'Qing Dynasty', 'icon': icon,
        'title': title, 'chinese_title': chinese_title, 'intro': intro,
        'passage': PASSAGES[slug],
        'vocabulary': [vocab('清朝', 'Qīng cháo', 'Qing Dynasty'), vocab('歷史', 'lì shǐ', 'history'), vocab('故事', 'gù shì', 'story')],
        'today': 'A significant event, figure, or cultural story from the Qing Dynasty.',
        'speak_prompts': ['請用中文簡單說明這個故事。', '你認為這個故事為什麼重要？'],
        'quiz': {'question': '這個故事主要與哪一個歷史時期有關？', 'choices': ['元朝', '明朝', '清朝', '民國'], 'answer': '清朝'},
    }


QING_HISTORY_LESSONS = {
    'qing-entry': lesson('qing-entry', 'level2', '🏯', 'The Qing Takes Beijing', '清軍入關', '1644年清軍入關，清朝開始統治北京。'),
    'zheng-chenggong-taiwan': lesson('zheng-chenggong-taiwan', 'level2', '⛵', 'Zheng Chenggong Recovers Taiwan', '鄭成功收復臺灣', '鄭成功於1662年驅逐荷蘭東印度公司勢力。'),
    'revolt-three-feudatories': lesson('revolt-three-feudatories', 'level3', '⚔️', 'Revolt of the Three Feudatories', '三藩之亂', '康熙年間歷時八年的大規模叛亂。'),
    'qing-taiwan-1683': lesson('qing-taiwan-1683', 'level3', '🌊', 'Qing Rule Begins in Taiwan', '清朝統一臺灣', '施琅率清軍於1683年擊敗鄭氏政權。'),
    'kangxi-southern-tour': lesson('kangxi-southern-tour', 'level2', '🚣', 'Kangxi\'s Southern Tours', '康熙南巡', '康熙帝南巡了解河工、民情與地方治理。'),
    'treaty-nerchinsk': lesson('treaty-nerchinsk', 'level3', '📜', 'Treaty of Nerchinsk', '尼布楚條約', '1689年清朝與俄國簽訂邊界條約。'),
    'yongzheng-reforms': lesson('yongzheng-reforms', 'level3', '📊', 'Yongzheng\'s Reforms', '雍正改革', '雍正帝整頓財政與行政制度。'),
    'qianlong-dream-red-chamber': lesson('qianlong-dream-red-chamber', 'level2', '📖', 'Dream of the Red Chamber', '曹雪芹與《紅樓夢》', '清代小說《紅樓夢》成為中國文學經典。'),
    'heshen-downfall': lesson('heshen-downfall', 'level2', '💰', 'The Fall of Heshen', '和珅跌倒，嘉慶吃飽', '和珅被查辦，民間流傳著名俗語。'),
    'opium-war': lesson('opium-war', 'level2', '🚢', 'The First Opium War', '鴉片戰爭', '1840年爆發的戰爭改變清朝對外關係。'),
    'taiping-rebellion': lesson('taiping-rebellion', 'level3', '🔥', 'The Taiping Rebellion', '太平天國', '十九世紀中葉規模巨大的內戰。'),
    'self-strengthening': lesson('self-strengthening', 'level3', '🏭', 'The Self-Strengthening Movement', '洋務運動', '清朝官員嘗試引進近代工業與軍事技術。'),
    'sino-japanese-war': lesson('sino-japanese-war', 'level2', '⚓', 'First Sino-Japanese War', '甲午戰爭', '1894至1895年清朝戰敗，臺灣被割讓。'),
    'hundred-days-reform': lesson('hundred-days-reform', 'level3', '📚', 'Hundred Days\' Reform', '戊戌變法', '1898年光緒帝推動短暫的制度改革。'),
    'boxer-rebellion': lesson('boxer-rebellion', 'level3', '🥊', 'Boxer Uprising', '義和團事件', '1900年前後的排外運動與八國聯軍戰事。'),
    'late-qing-new-policies': lesson('late-qing-new-policies', 'level3', '🏫', 'Late Qing New Policies', '清末新政', '清廷推動學制、軍制與行政改革。'),
    'wuchang-uprising': lesson('wuchang-uprising', 'level2', '🚩', 'Wuchang Uprising and the Fall of Qing', '武昌起義與清朝滅亡', '1911年起義促成革命，1912年清帝退位。'),
}

QING_CARDS = list(QING_HISTORY_LESSONS.values())
