def vocab(word, pinyin, meaning):
    return {'word': word, 'pinyin': pinyin, 'meaning': meaning}


PASSAGES = {
    'yellow-robe': '公元960年，趙匡胤率軍出征途中，在陳橋驛發生兵變。將士把黃袍披在他身上，擁立他為皇帝。趙匡胤建立宋朝，是為宋太祖。「黃袍加身」後來也用來形容被眾人推上領導地位。',
    'wine-cup-military-power': '宋太祖建立宋朝後，希望避免武將勢力過大。他宴請重要將領，以飲酒談話的方式勸他們交出兵權。「杯酒釋兵權」成為宋初加強中央統治的著名故事。',
    'candle-shadow-axe-sound': '宋太祖去世後，由弟弟趙光義即位，是為宋太宗。後世記載中出現「燭影斧聲」的說法，使宋太祖之死與皇位繼承成為著名歷史疑案，但其中許多細節無法確定。',
    'yang-family-generals': '北宋初年，楊業等將領參與對遼作戰。楊業後來戰敗被俘，絕食而死。後世戲曲和小說把楊家將的故事大幅發展，使楊家將成為忠勇報國的著名傳說。',
    'chanyuan-treaty': '宋真宗時，遼軍南下。宰相寇準主張皇帝親征，宋真宗前往澶州。公元1005年，宋遼達成澶淵之盟，此後雙方維持了較長時間的和平。',
    'bao-zheng-cases': '包拯是北宋著名官員，以清廉正直聞名。後世民間故事、戲曲和小說把他塑造成公正斷案的「包青天」。許多包公斷案故事帶有傳說成分，但他的清官形象流傳至今。',
    'fan-zhongyan': '范仲淹是北宋政治家與文學家。他在《岳陽樓記》中寫下「先天下之憂而憂，後天下之樂而樂」，表達關心國家與百姓的理想，成為流傳千年的名句。',
    'wang-anshi-reforms': '宋神宗時，王安石推行一系列改革，希望改善財政、軍事與社會問題，史稱「王安石變法」。改革引起激烈爭論，也成為北宋政治史的重要事件。',
    'sima-guang-vat': '相傳司馬光小時候和孩子們玩耍時，一名孩子掉進大水缸。其他人慌忙求救，司馬光卻拿石頭砸破水缸，讓水流出，救了孩子。「司馬光砸缸」成為著名的機智故事。',
    'su-dongpo-pork': '蘇軾號東坡居士，是北宋著名文學家。後世流傳他與杭州治水、烹調豬肉有關的故事，「東坡肉」也因此與他的名字緊密相連。這些故事兼具歷史與民間傳說色彩。',
    'crow-terrace-poetry-case': '宋神宗時，蘇軾因詩文被指責影射朝政而遭逮捕審問，史稱「烏臺詩案」。事件反映北宋新舊黨爭與政治環境，也深刻影響蘇軾後來的人生。',
    'jingkang-incident': '公元1127年，金軍攻破北宋都城汴京，宋徽宗、宋欽宗等皇族被俘北去，史稱「靖康之變」。北宋因此滅亡，之後趙構在南方建立南宋。',
    'yue-fei-loyalty': '南宋名將岳飛率軍抗金，多次取得戰果。他忠於國家、治軍嚴明，後世以「精忠報國」概括他的忠義形象，成為中國歷史上最著名的將領之一。',
    'yue-mother-tattoo': '「岳母刺字」是流傳極廣的民間故事。相傳岳飛的母親在他背上刺下「精忠報國」，勉勵他忠心報國。這個故事的史實來源存在爭議，但在後世文化中影響很大。',
    'twelve-gold-plaques': '岳飛北伐期間取得進展，但朝廷命令他班師。後世故事常以「十二道金牌」形容朝廷接連催促岳飛撤軍。這一說法成為岳飛悲劇結局的重要象徵。',
    'groundless-charge': '岳飛被召回後遭到逮捕，最終被殺。後世常以「莫須有」概括加在岳飛身上的罪名，秦檜也因此成為這段故事中的重要人物。「莫須有」後來常指缺乏根據的指控。',
    'xin-qiji-resistance': '辛棄疾不只是著名詞人，年輕時也曾參加抗金活動。他曾率少數人突入敵營，擒回叛徒張安國。這段經歷展現了他早年的勇氣，也影響他一生的作品與理想。',
    'wen-tianxiang': '南宋末年，文天祥堅持抵抗元軍，被俘後拒絕投降。他在《過零丁洋》中留下「人生自古誰無死，留取丹心照汗青」的名句，成為忠義精神的代表。',
    'battle-yamen': '公元1279年，宋元軍隊在崖山附近進行最後決戰。宋軍戰敗，陸秀夫背著幼帝趙昺投海殉國。崖山海戰標誌南宋滅亡，也象徵宋朝歷史的終結。',
}


def lesson(slug, level, icon, title, chinese_title, intro):
    return {
        'slug': slug, 'level': level, 'era': 'Song Dynasty', 'icon': icon,
        'title': title, 'chinese_title': chinese_title, 'intro': intro,
        'passage': PASSAGES[slug],
        'vocabulary': [vocab('宋朝', 'Sòng cháo', 'Song Dynasty'), vocab('歷史', 'lì shǐ', 'history'), vocab('故事', 'gù shì', 'story')],
        'today': 'This is one of the widely recognized stories or events associated with the Song Dynasty.',
        'speak_prompts': ['請用中文簡單說明這個故事。', '你認為這個故事為什麼重要？'],
        'quiz': {'question': '這個故事主要發生在哪一個朝代？', 'choices': ['唐朝', '宋朝', '元朝', '明朝'], 'answer': '宋朝'},
    }


SONG_HISTORY_LESSONS = {
    'yellow-robe': lesson('yellow-robe', 'level3', '👑', 'The Yellow Robe', '黃袍加身', '趙匡胤建立宋朝的著名故事。'),
    'wine-cup-military-power': lesson('wine-cup-military-power', 'level2', '🍷', 'Relieving Military Power over a Cup of Wine', '杯酒釋兵權', '宋太祖以宴飲方式讓大將交出兵權。'),
    'candle-shadow-axe-sound': lesson('candle-shadow-axe-sound', 'level3', '🕯️', 'Candle Shadows and the Sound of an Axe', '燭影斧聲', '宋初皇位繼承的著名歷史疑案。'),
    'yang-family-generals': lesson('yang-family-generals', 'level2', '⚔️', 'The Generals of the Yang Family', '楊家將', '由歷史人物發展而成的忠勇傳說。'),
    'chanyuan-treaty': lesson('chanyuan-treaty', 'level3', '🤝', 'Kou Zhun and the Chanyuan Treaty', '寇準抗遼・澶淵之盟', '北宋與遼關係的重要轉折。'),
    'bao-zheng-cases': lesson('bao-zheng-cases', 'level2', '⚖️', 'Bao Zheng Solves Cases', '包拯斷案（包青天）', '清官包拯與後世包青天傳說。'),
    'fan-zhongyan': lesson('fan-zhongyan', 'level2', '📜', 'Fan Zhongyan and His Famous Ideal', '范仲淹「先天下之憂而憂」', '《岳陽樓記》中流傳千年的名句。'),
    'wang-anshi-reforms': lesson('wang-anshi-reforms', 'level3', '🏛️', 'Wang Anshi’s Reforms', '王安石變法', '北宋最著名的政治改革之一。'),
    'sima-guang-vat': lesson('sima-guang-vat', 'level2', '🏺', 'Sima Guang Breaks the Water Vat', '司馬光砸缸', '司馬光小時候機智救人的著名故事。'),
    'su-dongpo-pork': lesson('su-dongpo-pork', 'level2', '🥩', 'Su Dongpo and Dongpo Pork', '蘇東坡與東坡肉', '蘇軾與杭州及東坡肉相關的著名故事。'),
    'crow-terrace-poetry-case': lesson('crow-terrace-poetry-case', 'level3', '✍️', 'The Crow Terrace Poetry Case', '蘇軾「烏臺詩案」', '蘇軾人生中的重要政治事件。'),
    'jingkang-incident': lesson('jingkang-incident', 'level3', '🔥', 'The Jingkang Incident', '靖康之變', '金軍攻破汴京，北宋滅亡。'),
    'yue-fei-loyalty': lesson('yue-fei-loyalty', 'level2', '🛡️', 'Yue Fei: Serve the Country with Utmost Loyalty', '岳飛精忠報國', '南宋抗金名將岳飛的忠義故事。'),
    'yue-mother-tattoo': lesson('yue-mother-tattoo', 'level2', '🪡', 'Yue Fei’s Mother Tattoos His Back', '岳母刺字', '流傳極廣的精忠報國民間故事。'),
    'twelve-gold-plaques': lesson('twelve-gold-plaques', 'level3', '📨', 'The Twelve Gold Plaques', '岳飛十二道金牌', '岳飛北伐被召回的著名故事。'),
    'groundless-charge': lesson('groundless-charge', 'level3', '⛓️', 'A Groundless Charge', '莫須有・岳飛之死', '岳飛之死與「莫須有」的著名故事。'),
    'xin-qiji-resistance': lesson('xin-qiji-resistance', 'level3', '🐎', 'Xin Qiji Resists the Jin', '辛棄疾抗金', '著名詞人辛棄疾年輕時的抗金經歷。'),
    'wen-tianxiang': lesson('wen-tianxiang', 'level2', '❤️', 'Wen Tianxiang: Who Since Ancient Times Has Not Died?', '文天祥「人生自古誰無死」', '南宋末年最著名的忠義故事之一。'),
    'battle-yamen': lesson('battle-yamen', 'level3', '🌊', 'The Battle of Yamen', '崖山海戰', '公元1279年南宋最後的決戰。'),
}

SONG_CARDS = list(SONG_HISTORY_LESSONS.values())
