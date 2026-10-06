def vocab(word, pinyin, meaning):
    return {'word': word, 'pinyin': pinyin, 'meaning': meaning}


PASSAGES = {
    'zhu-wen-founds-later-liang': '公元907年，朱溫迫使唐哀帝退位，建立後梁。唐朝滅亡後，中原進入五代十國時期。朱溫建立的後梁是五代中的第一個王朝。',
    'li-cunxu-destroys-later-liang': '公元923年，李存勗建立後唐，隨後攻滅後梁。他以善戰聞名，但建立政權後的統治並不穩定，後唐很快陷入新的政治衝突。',
    'actors-disaster': '後唐莊宗李存勗喜愛音樂與伶人。稱帝後，他重用身邊的伶人，使朝政受到影響。後來歐陽修在《伶官傳序》中以他的興亡說明「憂勞可以興國，逸豫可以亡身」的道理。',
    'shi-jingtang-khitan-aid': '石敬瑭為了推翻後唐，向契丹求援。契丹出兵幫助他建立後晉。這次借兵改變了北方政治局勢，也為後來燕雲十六州的問題埋下深遠影響。',
    'sixteen-prefectures': '石敬瑭得到契丹支持後，把燕雲十六州割讓給契丹。這片地區具有重要的軍事與地理價值，後來中原王朝長期希望收復，成為宋代北方局勢的重要背景。',
    'child-emperor-shi-jingtang': '石敬瑭依靠契丹建立後晉，並尊契丹皇帝為父，自稱「兒皇帝」。這個稱呼成為他在歷史上最著名、也最具爭議的故事之一。',
    'feng-dao-four-dynasties': '馮道在五代政權頻繁更替的時代，先後在多個王朝任高官。他自號「長樂老」。後世對他的評價很不相同：有人批評他缺乏忠節，也有人認為他在亂世中努力維持政務與文化。',
    'guo-wei-overthrows-later-han': '後漢末年，郭威與朝廷矛盾加深，最終起兵。公元951年，他建立後周，後漢滅亡。後周後來在郭威與柴榮的治理下逐漸強盛。',
    'guo-wei-yellow-banner': '相傳郭威軍隊擁立他時，將黃旗披在他的身上，表示推舉他做皇帝。這個故事常被拿來與後來趙匡胤「黃袍加身」的故事相比。',
    'chai-rong-gaoping': '公元954年，後周世宗柴榮即位不久，在高平之戰中迎戰北漢與契丹聯軍。後周取得勝利，柴榮也整頓軍隊，為後周後來的擴張與北宋統一奠定基礎。',
    'qian-liu-wuyue': '錢鏐建立吳越政權，以杭州一帶為中心。在五代十國的戰亂中，吳越重視地方安定、水利與經濟發展。「保境安民」成為後世概括吳越政策時常用的說法。',
    'wang-shenzhi-min': '王審知在福建建立並治理閩國。他重視地方安定、農業與海外貿易，被後世尊稱為「開閩王」。他的統治是十國歷史中重要的地方發展故事。',
    'li-yu-loses-southern-tang': '李煜是南唐最後一位君主，也是一位著名詞人。公元975年，北宋攻滅南唐，李煜成為亡國之君。他的政治失敗與文學成就形成鮮明對比。',
    'li-yu-yumeiren': '南唐滅亡後，李煜被帶到北宋都城。他寫下許多懷念故國的詞，其中《虞美人》尤其著名。「問君能有幾多愁」成為流傳千年的名句，也使李煜成為著名的亡國詞人。',
    'chenqiao-mutiny': '公元960年，後周將領趙匡胤率軍北上。軍隊到達陳橋驛後發生兵變，將士擁立趙匡胤為皇帝。趙匡胤回到開封建立宋朝，後周因此結束。',
    'five-dynasties-yellow-robe': '陳橋兵變時，相傳將士把象徵皇權的黃袍披在趙匡胤身上，擁立他為皇帝，這就是著名的「黃袍加身」。公元960年，趙匡胤建立宋朝，五代的中原政權至此結束。',
}


def lesson(slug, level, icon, title, chinese_title, intro):
    return {
        'slug': slug,
        'level': level,
        'era': 'Five Dynasties & Ten Kingdoms',
        'icon': icon,
        'title': title,
        'chinese_title': chinese_title,
        'intro': intro,
        'passage': PASSAGES[slug],
        'vocabulary': [
            vocab('五代十國', 'Wǔ Dài Shí Guó', 'Five Dynasties and Ten Kingdoms'),
            vocab('歷史', 'lì shǐ', 'history'),
            vocab('故事', 'gù shì', 'story'),
        ],
        'today': 'This is one of the widely recognized stories or events associated with the Five Dynasties and Ten Kingdoms period.',
        'speak_prompts': ['請用中文簡單說明這個故事。', '你認為這個故事為什麼重要？'],
        'quiz': {
            'question': '這個故事主要發生在哪一個歷史時期？',
            'choices': ['唐朝', '五代十國', '宋朝', '元朝'],
            'answer': '五代十國',
        },
    }


FIVE_DYNASTIES_HISTORY_LESSONS = {
    'zhu-wen-founds-later-liang': lesson('zhu-wen-founds-later-liang', 'level3', '🏯', 'Zhu Wen Founds Later Liang', '朱溫篡唐建後梁', '唐亡後五代時期的開始。'),
    'li-cunxu-destroys-later-liang': lesson('li-cunxu-destroys-later-liang', 'level3', '⚔️', 'Li Cunxu Destroys Later Liang', '李存勗滅後梁', '後唐取代後梁的重要戰爭。'),
    'actors-disaster': lesson('actors-disaster', 'level3', '🎭', 'The Disaster of the Court Actors', '伶官之禍', '李存勗興亡與《伶官傳序》的著名故事。'),
    'shi-jingtang-khitan-aid': lesson('shi-jingtang-khitan-aid', 'level3', '🐎', 'Shi Jingtang Seeks Khitan Aid', '石敬瑭借兵契丹', '後晉建立背後的重要政治交易。'),
    'sixteen-prefectures': lesson('sixteen-prefectures', 'level3', '🗺️', 'The Sixteen Prefectures', '割讓燕雲十六州', '影響後世北方局勢的重要事件。'),
    'child-emperor-shi-jingtang': lesson('child-emperor-shi-jingtang', 'level2', '👑', 'The Child Emperor Shi Jingtang', '兒皇帝石敬瑭', '石敬瑭與契丹關係中最著名的稱呼。'),
    'feng-dao-four-dynasties': lesson('feng-dao-four-dynasties', 'level3', '📜', 'Feng Dao Serves Many Dynasties', '馮道歷事四朝', '亂世名臣「長樂老」的爭議故事。'),
    'guo-wei-overthrows-later-han': lesson('guo-wei-overthrows-later-han', 'level3', '⚔️', 'Guo Wei Overthrows Later Han', '郭威起兵滅後漢', '後周建立的重要轉折。'),
    'guo-wei-yellow-banner': lesson('guo-wei-yellow-banner', 'level3', '🚩', 'Guo Wei and the Yellow Banner', '郭威黃旗加身', '常與後來黃袍加身相比的故事。'),
    'chai-rong-gaoping': lesson('chai-rong-gaoping', 'level3', '🛡️', 'Chai Rong and the Battle of Gaoping', '柴榮高平之戰', '後周走向強盛的重要戰役。'),
    'qian-liu-wuyue': lesson('qian-liu-wuyue', 'level2', '🌊', 'Qian Liu Protects Wuyue', '錢鏐保境安民', '吳越在亂世中重視地方安定與發展。'),
    'wang-shenzhi-min': lesson('wang-shenzhi-min', 'level3', '⛰️', 'Wang Shenzhi Governs Min', '王審知治閩', '「開閩王」治理福建的故事。'),
    'li-yu-loses-southern-tang': lesson('li-yu-loses-southern-tang', 'level2', '🍂', 'Li Yu Loses Southern Tang', '南唐後主李煜亡國', '著名詞人李煜成為亡國之君。'),
    'li-yu-yumeiren': lesson('li-yu-yumeiren', 'level2', '📝', 'Li Yu, Yu Meiren, and the Sorrow of a Lost Kingdom', '李煜《虞美人》與亡國之恨', '李煜以詞寫下對故國的深切懷念。'),
    'chenqiao-mutiny': lesson('chenqiao-mutiny', 'level2', '🏕️', 'The Chenqiao Mutiny', '陳橋兵變', '趙匡胤被擁立並建立宋朝的關鍵事件。'),
    'five-dynasties-yellow-robe': lesson('five-dynasties-yellow-robe', 'level2', '🟨', 'The Yellow Robe Is Draped on Zhao Kuangyin', '黃袍加身', '五代結束、宋朝建立最著名的故事之一。'),
}

FIVE_DYNASTIES_CARDS = list(FIVE_DYNASTIES_HISTORY_LESSONS.values())
