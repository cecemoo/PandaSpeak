def vocab(word, pinyin, meaning):
    return {'word': word, 'pinyin': pinyin, 'meaning': meaning}


PASSAGES = {
    'xuanwu-gate': '公元626年，李世民在長安玄武門發動政變，擊敗太子李建成與齊王李元吉。之後李世民成為太子並即位，是為唐太宗。玄武門之變是唐初最著名的政治事件之一。',
    'zhenguan-reign': '唐太宗在位期間重視納諫、選用人才並減輕百姓負擔，國家逐漸安定強盛。這段著名的治世被稱為「貞觀之治」，也為唐朝後來的繁榮奠定基礎。',
    'wei-zheng-remonstrates': '魏徵以敢於向唐太宗直言進諫而聞名。即使意見讓皇帝不高興，他仍指出問題。唐太宗後來把魏徵比作能照出自己得失的一面鏡子。',
    'xuanzang-journey': '唐代僧人玄奘為求取佛經，從長安出發前往印度。他歷經艱難，帶回大量佛教經典並主持翻譯。後世小說《西遊記》受到這段歷史的啟發，但小說中的神怪故事屬於文學創作。',
    'princess-wencheng-tibet': '唐太宗時期，文成公主入藏，與吐蕃贊普松贊干布成婚。這段歷史成為唐朝與吐蕃交流中最著名的故事之一。',
    'wu-zetian-emperor': '武則天從唐朝后妃逐漸掌握最高權力，公元690年稱帝，建立武周。她是中國歷史上唯一正式稱帝的女性，因此成為唐代最著名的人物之一。',
    'invite-into-urn': '武則天時期，酷吏來俊臣審問周興。來俊臣先問如何逼犯人招供，周興提出把人放進大甕加熱的方法。來俊臣隨即說要請周興自己進甕，「請君入甕」因此成為著名成語。',
    'di-renjie-cases': '狄仁傑是武則天時期著名大臣，以能力與判案故事聞名。後世文學又把他塑造成善於推理斷案的人物，使「狄公案」成為廣為流傳的傳奇。',
    'kaiyuan-prosperity': '唐玄宗統治前期，政治較為穩定，經濟與文化繁榮，國力達到高峰。這段時期被稱為「開元盛世」，是人們談到盛唐時最常提到的時代之一。',
    'li-bai-xuanzong': '李白是唐代最著名的詩人之一。相傳他受到唐玄宗召見，在長安供奉翰林。許多後世故事把李白豪放的性格、詩才與宮廷生活連在一起。',
    'xuanzong-yang-guifei': '唐玄宗與楊貴妃的故事是唐代最著名的愛情與宮廷故事之一。楊貴妃深受寵愛，後來白居易的《長恨歌》等作品使這段故事流傳千年。',
    'lychee-yang-guifei': '楊貴妃喜愛荔枝的故事廣為流傳。後世杜牧以「一騎紅塵妃子笑」描寫快馬運送荔枝進宮的情景，使這個故事成為楊貴妃最著名的傳說之一。',
    'an-lushan-rebellion': '公元755年，安祿山起兵反唐，安史之亂爆發。戰亂持續多年，造成巨大破壞，也使唐朝由盛轉衰，是唐代最重要的歷史轉折之一。',
    'mawei-slope': '安史之亂爆發後，唐玄宗逃離長安。軍隊行至馬嵬坡時發生兵變，楊國忠被殺，楊貴妃也被迫死去。馬嵬坡之變成為唐玄宗與楊貴妃故事最悲劇的一幕。',
    'du-fu-an-lushan': '杜甫親身經歷安史之亂，戰爭與百姓苦難深深影響他的詩歌。他以作品記錄亂世，因此後世稱他的詩為「詩史」，也稱他為「詩聖」。',
    'huang-chao-rebellion': '唐朝末年政治腐敗、社會矛盾加劇。黃巢領導的大規模起義席捲各地，並一度攻入長安。這場戰亂重創唐朝，使王朝更加衰弱。',
    'zhu-wen-ends-tang': '唐朝末年，朱溫逐漸掌握朝廷與軍事大權。公元907年，他迫使唐哀帝退位，建立後梁。延續近三百年的唐朝至此正式滅亡。',
}


def lesson(slug, level, icon, title, chinese_title, intro):
    return {
        'slug': slug,
        'level': level,
        'era': 'Tang Dynasty',
        'icon': icon,
        'title': title,
        'chinese_title': chinese_title,
        'intro': intro,
        'passage': PASSAGES[slug],
        'vocabulary': [
            vocab('唐朝', 'Táng cháo', 'Tang Dynasty'),
            vocab('歷史', 'lì shǐ', 'history'),
            vocab('故事', 'gù shì', 'story'),
        ],
        'today': 'This is one of the widely recognized stories or events associated with the Tang Dynasty.',
        'speak_prompts': ['請用中文簡單說明這個故事。', '你認為這個故事為什麼重要？'],
        'quiz': {
            'question': '這個故事主要發生在哪一個朝代？',
            'choices': ['隋朝', '唐朝', '宋朝', '元朝'],
            'answer': '唐朝',
        },
    }


TANG_HISTORY_LESSONS = {
    'xuanwu-gate': lesson('xuanwu-gate', 'level3', '⚔️', 'The Xuanwu Gate Incident', '玄武門之變', '唐初最著名的皇位鬥爭之一。'),
    'zhenguan-reign': lesson('zhenguan-reign', 'level3', '👑', 'The Reign of Zhenguan', '貞觀之治', '唐太宗時期著名的治世。'),
    'wei-zheng-remonstrates': lesson('wei-zheng-remonstrates', 'level2', '🪞', 'Wei Zheng Speaks Frankly', '魏徵直諫', '魏徵敢於向唐太宗直言進諫的著名故事。'),
    'xuanzang-journey': lesson('xuanzang-journey', 'level2', '🐫', 'Xuanzang Journeys West for the Scriptures', '玄奘西行取經', '歷史上的玄奘西行，後來啟發《西遊記》。'),
    'princess-wencheng-tibet': lesson('princess-wencheng-tibet', 'level2', '🏔️', 'Princess Wencheng Enters Tibet', '文成公主入藏', '唐朝與吐蕃交流中最著名的故事之一。'),
    'wu-zetian-emperor': lesson('wu-zetian-emperor', 'level2', '👸', 'Wu Zetian Becomes Emperor', '武則天稱帝', '中國歷史上唯一正式稱帝的女性。'),
    'invite-into-urn': lesson('invite-into-urn', 'level2', '🏺', 'Invite the Ruler into the Urn', '請君入甕', '著名成語「請君入甕」的來源故事。'),
    'di-renjie-cases': lesson('di-renjie-cases', 'level2', '⚖️', 'Di Renjie Solves Cases', '狄仁傑斷案', '歷史人物與後世狄公傳奇相結合的著名故事。'),
    'kaiyuan-prosperity': lesson('kaiyuan-prosperity', 'level3', '🏮', 'The Prosperity of Kaiyuan', '開元盛世', '唐玄宗前期的盛唐高峰。'),
    'li-bai-xuanzong': lesson('li-bai-xuanzong', 'level2', '✍️', 'Li Bai and Emperor Xuanzong', '李白與唐玄宗', '詩仙李白與唐代宮廷相關的著名故事。'),
    'xuanzong-yang-guifei': lesson('xuanzong-yang-guifei', 'level2', '🌸', 'Emperor Xuanzong and Yang Guifei', '楊貴妃與唐玄宗', '流傳千年的唐代宮廷愛情故事。'),
    'lychee-yang-guifei': lesson('lychee-yang-guifei', 'level2', '🍒', 'A Galloping Horse Brings Lychees', '一騎紅塵妃子笑', '以荔枝與楊貴妃聞名的故事。'),
    'an-lushan-rebellion': lesson('an-lushan-rebellion', 'level3', '🔥', 'The An Lushan Rebellion', '安史之亂', '使唐朝由盛轉衰的重大歷史轉折。'),
    'mawei-slope': lesson('mawei-slope', 'level3', '🐎', 'The Mawei Slope Incident', '馬嵬坡之變', '安史之亂中楊貴妃悲劇結局的著名事件。'),
    'du-fu-an-lushan': lesson('du-fu-an-lushan', 'level3', '📖', 'Du Fu and the An Lushan Rebellion', '杜甫與安史之亂', '杜甫以詩歌記錄戰亂與百姓生活。'),
    'huang-chao-rebellion': lesson('huang-chao-rebellion', 'level3', '🏴', 'The Huang Chao Rebellion', '黃巢起義', '重創晚唐的重要大規模起義。'),
    'zhu-wen-ends-tang': lesson('zhu-wen-ends-tang', 'level3', '🏯', 'Zhu Wen Ends the Tang Dynasty', '朱溫滅唐', '公元907年唐朝正式滅亡。'),
}

TANG_CARDS = list(TANG_HISTORY_LESSONS.values())
