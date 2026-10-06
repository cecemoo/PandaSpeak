def vocab(word, pinyin, meaning):
    return {'word': word, 'pinyin': pinyin, 'meaning': meaning}


PASSAGES = {
    'genghis-unifies-mongols': '十二世紀末到十三世紀初，鐵木真逐步擊敗草原上的競爭部族。公元1206年，他被推舉為成吉思汗，蒙古各部在他的領導下形成強大的政治與軍事力量，為後來蒙古帝國與元朝的建立奠定基礎。',
    'genghis-western-campaigns': '成吉思汗建立蒙古政權後，蒙古軍隊向中亞等地展開大規模西征。這些戰爭迅速擴大蒙古勢力，也深刻改變了歐亞大陸的政治、交通與文化交流。',
    'qiu-chuji-meets-genghis': '道士丘處機年事已高，仍應成吉思汗之召長途西行。兩人會面後，丘處機談到養生與治國，並勸成吉思汗減少殺戮。這段旅程後來由弟子記錄在《長春真人西遊記》中。',
    'kublai-founds-yuan': '忽必烈是成吉思汗的孫子。公元1271年，他正式採用「大元」作為國號，建立元朝，是為元世祖。此後元朝繼續進攻南宋，逐步完成對中國主要地區的統一。',
    'kublai-capital-dadu': '忽必烈把大都作為元朝的重要都城。大都位於今天北京一帶，經過大規模規劃與建設，成為元朝政治中心，也是一座繁榮的國際城市。',
    'battle-xiangyang': '南宋末年，襄陽和樊城是抵抗蒙古軍隊的重要防線。蒙古軍長期圍攻，公元1273年襄陽失守。襄陽之戰的結果使南宋長江防線受到重大打擊，加速了南宋的滅亡。',
    'battle-yamen-yuan': '公元1279年，宋元軍隊在崖山附近進行最後的大規模海戰。南宋戰敗，幼帝趙昺隨陸秀夫投海，南宋政權至此滅亡，元朝完成對南方主要地區的征服。',
    'wen-tianxiang-unyielding': '南宋大臣文天祥在抗元戰爭中被俘。元朝多次勸降，他仍拒絕投降，最後被處死。他堅持忠義的故事在中國歷史上廣為流傳。',
    'who-can-escape-death': '文天祥在《過零丁洋》中寫下「人生自古誰無死，留取丹心照汗青」，表達自己面對死亡仍堅持信念的決心。這兩句詩後來成為中國文化中非常著名的名句。',
    'marco-polo-china': '十三世紀，威尼斯人馬可波羅據傳來到中國，並在後來的遊記中描述忽必烈時期的城市、交通與生活。《馬可波羅遊記》使許多歐洲人對東方產生濃厚興趣。',
    'guo-shoujing-calendar': '元代科學家郭守敬精通天文、水利與曆法。他主持天文觀測並參與制定《授時曆》，提高了曆法計算的準確性，是元代科技史上的重要成就。',
    'huang-daopo-textiles': '黃道婆學習並改進棉紡織技術，回到松江一帶後傳授新的紡織工具與方法。她的故事與元代江南棉紡織業的發展密切相關。',
    'zhao-mengfu-art': '趙孟頫是元代著名書法家、畫家與文人。他主張從古代藝術傳統中尋找新的創作方向，在書法與繪畫史上都有重要影響。',
    'guan-hanqing-dou-e': '關漢卿是元代最著名的雜劇作家之一。他創作的《竇娥冤》描寫一名無辜女子遭受冤屈的故事，作品對社會不公的描寫使它成為元曲代表作。',
    'injustice-dou-e': '《竇娥冤》中，竇娥被誣陷殺人並遭判死刑。她在刑場上發下誓願，要用異常現象證明自己的冤屈。這個悲劇成為中國戲曲史上最著名的故事之一。',
    'snow-in-june': '在《竇娥冤》的故事中，竇娥臨刑前說，如果自己確實蒙冤，六月也會降雪。故事中她死後果然六月飛雪，因此「六月飛雪」後來常被用來形容極大的冤屈。',
    'yuan-drama-flourishes': '元代雜劇高度發展，關漢卿、王實甫、馬致遠等作家留下許多著名作品。元曲與唐詩、宋詞一樣，成為中國文學史上具有代表性的文學形式。',
    'red-turban-rebellion': '元朝末年，政治與社會矛盾加劇，各地爆發反抗。公元1351年前後，紅巾軍起義迅速擴大，嚴重削弱元朝統治，也為新的政治力量崛起創造條件。',
    'zhu-yuanzhang-rises': '朱元璋出身貧寒，元末加入反元力量，逐步建立自己的軍隊與政權。他擊敗多個競爭勢力，控制長江中下游，最終成為推翻元朝的重要人物。',
    'ming-founded-yuan-ends': '公元1368年，朱元璋在南京稱帝，建立明朝。同年明軍北伐並攻入大都，元順帝北撤。元朝在中原的統治結束，中國歷史進入明朝。',
}


def lesson(slug, level, icon, title, chinese_title, intro):
    return {
        'slug': slug, 'level': level, 'era': 'Yuan Dynasty', 'icon': icon,
        'title': title, 'chinese_title': chinese_title, 'intro': intro,
        'passage': PASSAGES[slug],
        'vocabulary': [vocab('元朝', 'Yuán cháo', 'Yuan Dynasty'), vocab('歷史', 'lì shǐ', 'history'), vocab('故事', 'gù shì', 'story')],
        'today': 'This is one of the widely recognized stories, people, or events associated with the Mongol and Yuan period.',
        'speak_prompts': ['請用中文簡單說明這個故事。', '你認為這個故事為什麼重要？'],
        'quiz': {'question': '這個故事主要與哪一個歷史時期有關？', 'choices': ['唐朝', '宋朝', '元朝', '明朝'], 'answer': '元朝'},
    }


YUAN_HISTORY_LESSONS = {
    'genghis-unifies-mongols': lesson('genghis-unifies-mongols', 'level2', '🐎', 'Genghis Khan Unifies the Mongols', '成吉思汗統一蒙古', '蒙古帝國與元朝前史的重要起點。'),
    'genghis-western-campaigns': lesson('genghis-western-campaigns', 'level3', '🏹', 'Genghis Khan’s Western Campaigns', '成吉思汗西征', '深刻改變歐亞大陸格局的蒙古西征。'),
    'qiu-chuji-meets-genghis': lesson('qiu-chuji-meets-genghis', 'level3', '⛰️', 'Qiu Chuji Journeys West to Meet Genghis Khan', '丘處機西行見成吉思汗', '丘處機長途西行與成吉思汗會面的著名故事。'),
    'kublai-founds-yuan': lesson('kublai-founds-yuan', 'level2', '👑', 'Kublai Khan Founds the Yuan Dynasty', '忽必烈建立元朝', '公元1271年忽必烈正式建立元朝。'),
    'kublai-capital-dadu': lesson('kublai-capital-dadu', 'level2', '🏙️', 'Kublai Khan Establishes the Capital at Dadu', '元世祖定都大都', '大都成為元朝政治與國際交流中心。'),
    'battle-xiangyang': lesson('battle-xiangyang', 'level3', '🏰', 'The Battle of Xiangyang', '襄陽之戰', '宋元戰爭中的重要長期攻防戰。'),
    'battle-yamen-yuan': lesson('battle-yamen-yuan', 'level3', '🌊', 'The Battle of Yamen and the Fall of Southern Song', '崖山海戰・南宋滅亡', '南宋最後的重大戰役與元朝統一。'),
    'wen-tianxiang-unyielding': lesson('wen-tianxiang-unyielding', 'level2', '🛡️', 'Wen Tianxiang Refuses to Surrender', '文天祥寧死不屈', '文天祥被俘後拒絕投降的著名故事。'),
    'who-can-escape-death': lesson('who-can-escape-death', 'level2', '📜', 'Who Since Ancient Times Has Escaped Death?', '人生自古誰無死', '文天祥《過零丁洋》中流傳千年的名句。'),
    'marco-polo-china': lesson('marco-polo-china', 'level2', '🌍', 'Marco Polo Comes to China', '馬可波羅來華', '歐洲最著名的元代中國旅行故事之一。'),
    'guo-shoujing-calendar': lesson('guo-shoujing-calendar', 'level3', '🌌', 'Guo Shoujing Creates the Shoushi Calendar', '郭守敬制定《授時曆》', '元代天文與曆法的重要科技成就。'),
    'huang-daopo-textiles': lesson('huang-daopo-textiles', 'level2', '🧵', 'Huang Daopo Improves Textile Technology', '黃道婆改進紡織技術', '推動江南棉紡織發展的著名人物故事。'),
    'zhao-mengfu-art': lesson('zhao-mengfu-art', 'level3', '🖌️', 'The Calligraphy and Painting of Zhao Mengfu', '趙孟頫書畫', '元代書畫藝術的重要代表。'),
    'guan-hanqing-dou-e': lesson('guan-hanqing-dou-e', 'level2', '🎭', 'Guan Hanqing and The Injustice to Dou E', '關漢卿與《竇娥冤》', '元曲代表作與著名劇作家的故事。'),
    'injustice-dou-e': lesson('injustice-dou-e', 'level2', '⚖️', 'The Injustice to Dou E', '竇娥冤', '中國戲曲中最著名的冤案故事之一。'),
    'snow-in-june': lesson('snow-in-june', 'level2', '❄️', 'Snow in June', '六月飛雪', '以異常六月降雪象徵巨大冤屈的故事。'),
    'yuan-drama-flourishes': lesson('yuan-drama-flourishes', 'level3', '🎼', 'The Flourishing of Yuan Drama', '元曲興盛', '唐詩、宋詞之後的重要文學高峰。'),
    'red-turban-rebellion': lesson('red-turban-rebellion', 'level3', '🚩', 'The Red Turban Rebellion', '紅巾軍起義', '動搖元朝統治的元末大規模起義。'),
    'zhu-yuanzhang-rises': lesson('zhu-yuanzhang-rises', 'level3', '⚔️', 'The Rise of Zhu Yuanzhang', '朱元璋崛起', '從貧寒出身走向建立新王朝的歷史轉折。'),
    'ming-founded-yuan-ends': lesson('ming-founded-yuan-ends', 'level2', '🏯', 'Zhu Yuanzhang Founds Ming and Yuan Rule Ends', '朱元璋建立明朝・元朝滅亡', '公元1368年明朝建立，元朝在中原的統治結束。'),
}

YUAN_CARDS = list(YUAN_HISTORY_LESSONS.values())
