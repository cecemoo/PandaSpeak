def vocab(word, pinyin, meaning):
    return {'word': word, 'pinyin': pinyin, 'meaning': meaning}


PASSAGES = {
    'yang-jian-founds-sui': '公元581年，楊堅建立隋朝，是為隋文帝。經歷數百年的分裂後，中國再次走向統一。隋朝雖然只有短短三十多年，卻為後來的唐朝奠定了重要基礎。',
    'sui-conquers-chen': '公元589年，隋軍南下滅陳，結束了南北朝長期分裂的局面。隋文帝完成統一，使南北重新置於同一個中央政權之下。',
    'kaihuang-reign': '隋文帝在位期間整頓政治、節省開支、發展經濟，國力逐漸增強。這段相對安定繁榮的時期，後世稱為「開皇之治」。',
    'empress-dugu': '獨孤伽羅是隋文帝楊堅的皇后，也是隋初重要的政治人物。她與楊堅感情深厚，並常參與政治意見，因此後世常把兩人的關係作為隋朝宮廷故事的一部分。',
    'yang-guang-crown-prince': '楊廣是隋文帝的次子。為了取得太子之位，他努力塑造節儉、孝順的形象，並與兄長楊勇競爭。後來楊勇被廢，楊廣成為太子，最終即位為隋煬帝。',
    'grand-canal': '隋煬帝時期大規模修建和連接運河，形成貫通南北的大運河體系。工程耗費大量人力，但也加強了南北交通與物資交流，對後世影響深遠。',
    'goguryeo-campaigns': '隋煬帝多次大規模征討高句麗，動員大量士兵和民夫。戰爭未能取得預期成果，反而加重百姓負擔，使國內矛盾更加嚴重。',
    'wagang-rebellion': '隋朝末年，各地民變四起，其中瓦崗軍最為著名。瓦崗軍聚集許多反隋力量，成為隋末群雄競爭中的重要勢力。',
    'li-mi-wagang': '李密加入瓦崗軍後成為重要領袖，一度聲勢強盛。他率軍與隋軍作戰，在隋末政治與軍事局勢中扮演重要角色，但後來瓦崗勢力逐漸衰落。',
    'jiangdu-mutiny': '公元618年，隋煬帝在江都時，禁軍將領發動兵變。隋煬帝被殺，象徵隋朝統治已走到最後階段。',
    'li-yuan-taiyuan': '公元617年，李淵在太原起兵，率軍向長安進發。次年建立唐朝，是為唐高祖。太原起兵因此成為隋唐政權交替的重要事件。',
    'fall-sui-rise-tang': '隋末戰亂不斷，各地勢力紛紛起兵。公元618年唐朝建立，隋朝逐步退出歷史舞台。短暫的隋朝結束後，中國進入更加繁盛的唐朝時代。',
}


def lesson(slug, level, icon, title, chinese_title, intro):
    return {
        'slug': slug,
        'level': level,
        'era': 'Sui Dynasty',
        'icon': icon,
        'title': title,
        'chinese_title': chinese_title,
        'intro': intro,
        'passage': PASSAGES[slug],
        'vocabulary': [
            vocab('隋朝', 'Suí cháo', 'Sui Dynasty'),
            vocab('歷史', 'lì shǐ', 'history'),
            vocab('故事', 'gù shì', 'story'),
        ],
        'today': 'This story is one of the widely recognized events or stories associated with the Sui Dynasty.',
        'speak_prompts': [
            '請用中文簡單說明這個故事。',
            '你認為這個故事為什麼重要？',
        ],
        'quiz': {
            'question': '這個故事主要發生在哪一個朝代？',
            'choices': ['晉朝', '南北朝', '隋朝', '唐朝'],
            'answer': '隋朝',
        },
    }


SUI_HISTORY_LESSONS = {
    'yang-jian-founds-sui': lesson('yang-jian-founds-sui', 'level3', '👑', 'Yang Jian Founds the Sui Dynasty', '楊堅建立隋朝', '楊堅建立隋朝，開啟重新統一中國的進程。'),
    'sui-conquers-chen': lesson('sui-conquers-chen', 'level3', '🗺️', 'Sui Conquers Chen and Reunifies China', '隋滅陳・統一天下', '隋滅陳後，結束南北長期分裂。'),
    'kaihuang-reign': lesson('kaihuang-reign', 'level3', '📜', 'The Reign of Kaihuang', '開皇之治', '隋文帝時期著名的治世。'),
    'empress-dugu': lesson('empress-dugu', 'level3', '👸', 'Empress Dugu and Emperor Wen', '獨孤皇后與隋文帝', '隋初著名的帝后與宮廷政治故事。'),
    'yang-guang-crown-prince': lesson('yang-guang-crown-prince', 'level3', '🏯', 'Yang Guang Competes for the Crown', '楊廣奪嫡', '楊廣取得太子之位的著名宮廷故事。'),
    'grand-canal': lesson('grand-canal', 'level2', '🌉', 'Emperor Yang and the Grand Canal', '隋煬帝開鑿大運河', '隋朝最著名、影響最深遠的工程之一。'),
    'goguryeo-campaigns': lesson('goguryeo-campaigns', 'level3', '⚔️', 'The Campaigns against Goguryeo', '隋煬帝三征高句麗', '大規模戰爭加重隋末社會負擔。'),
    'wagang-rebellion': lesson('wagang-rebellion', 'level2', '🏴', 'The Wagang Rebellion', '瓦崗寨起義', '隋末最著名的反隋力量之一。'),
    'li-mi-wagang': lesson('li-mi-wagang', 'level3', '🛡️', 'Li Mi and the Wagang Army', '李密與瓦崗軍', '李密成為瓦崗軍的重要領袖。'),
    'jiangdu-mutiny': lesson('jiangdu-mutiny', 'level3', '🔥', 'The Jiangdu Mutiny and Death of Emperor Yang', '隋煬帝之死・江都兵變', '江都兵變標誌隋朝統治走向終結。'),
    'li-yuan-taiyuan': lesson('li-yuan-taiyuan', 'level2', '🐎', 'Li Yuan Rises at Taiyuan', '李淵太原起兵', '李淵起兵後建立唐朝。'),
    'fall-sui-rise-tang': lesson('fall-sui-rise-tang', 'level3', '🏮', 'The Fall of Sui and Rise of Tang', '隋亡唐興', '隋朝滅亡與唐朝建立的政權交替。'),
}

SUI_CARDS = list(SUI_HISTORY_LESSONS.values())
