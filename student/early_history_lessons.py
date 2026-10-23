"""Early Chinese history story lessons used by the PandaSpeak History Journey."""


def vocab(word, pinyin, meaning):
    return {"word": word, "pinyin": pinyin, "meaning": meaning}


def lesson(slug, era, icon, title, chinese_title, intro, passage, vocabulary,
           today, speak_prompts, question, choices, answer):
    return {
        "slug": slug,
        "level": "level2",
        "era": era,
        "icon": icon,
        "title": title,
        "chinese_title": chinese_title,
        "intro": intro,
        "passage": passage,
        "vocabulary": vocabulary,
        "today": today,
        "speak_prompts": speak_prompts,
        "quiz": {"question": question, "choices": choices, "answer": answer},
    }


EARLY_HISTORY_LESSONS = {
    "yu-controls-floods": lesson(
        "yu-controls-floods", "Xia Tradition", "🌊",
        "Yu the Great Controls the Floods", "大禹治水",
        "Begin the History Journey with the traditional story of Yu the Great and the great floods.",
        "很久以前，中國發生了嚴重的洪水。傳說大禹為了治理洪水，走遍很多地方，疏通河道，讓洪水流向大海。他多年在外工作，甚至三次經過自己的家門都沒有進去。最後，大禹成功控制洪水，受到人民的尊敬。傳說後來大禹成為領袖，而他的兒子啟建立了夏朝的世襲統治。",
        [vocab("大禹", "Dà Yǔ", "Yu the Great"), vocab("洪水", "hóngshuǐ", "flood"), vocab("治水", "zhìshuǐ", "flood control"), vocab("河道", "hédào", "river channel"), vocab("夏朝", "Xiàcháo", "Xia dynasty")],
        "大禹治水是中國最著名的早期傳說之一。今天人們仍會用「三過家門而不入」形容為了重要工作而忘我的精神。",
        ["大禹為什麼受到人民尊敬？", "你覺得治理洪水最需要什麼能力？"],
        "傳說大禹用什麼方法治理洪水？", ["疏通河道", "建造長城", "發明文字", "開闢絲綢之路"], "疏通河道"
    ),
    "gun-fails-flood-control": lesson(
        "gun-fails-flood-control", "Xia Tradition", "🌧️",
        "Gun Fails to Control the Floods", "鯀治水失敗",
        "Discover the legend of Gun's unsuccessful attempt to stop the floods before Yu the Great.",
        "傳說古代洪水不斷，人民的生活非常困難。鯀接受治水的任務，希望用堤防阻擋洪水。他努力多年，但洪水仍然沒有停止。後來，他的兒子大禹繼續治水，改用疏通河道的方法。這個傳說提醒我們，遇到問題時，有時需要改變方法。",
        [vocab("鯀", "Gǔn", "Gun"), vocab("堤防", "dīfáng", "levee"), vocab("阻擋", "zǔdǎng", "to block"), vocab("失敗", "shībài", "to fail"), vocab("方法", "fāngfǎ", "method")],
        "鯀治水的故事屬於古代傳說，常與大禹治水一起講述。",
        ["鯀為什麼沒有成功？","遇到困難時，你會改變方法嗎？"],
        "傳說鯀主要用什麼方法治水？", ["建造堤防阻擋洪水","疏通河道","開鑿運河","種植樹木"], "建造堤防阻擋洪水"
    ),
    "taikang-loses-kingdom": lesson(
        "taikang-loses-kingdom", "Xia Tradition", "🏹",
        "Taikang Loses His Kingdom", "太康失國",
        "Learn the traditional account of how Taikang lost control of Xia.",
        "傳統記載中，太康繼承夏朝王位後，喜歡打獵，沒有好好管理國家。他長時間離開都城，人民漸漸不滿。這時，有窮氏的后羿掌握了機會，阻止太康回到都城。太康因此失去權力。這個故事常用來提醒統治者要重視自己的責任。",
        [vocab("太康", "Tài Kāng", "Taikang"), vocab("打獵", "dǎliè", "to hunt"), vocab("都城", "dūchéng", "capital"), vocab("權力", "quánlì", "power"), vocab("責任", "zérèn", "responsibility")],
        "太康失國是後世文獻保存的夏朝傳統敘事，細節難以獨立證實。",
        ["太康為什麼失去權力？","一位領導者應該負起哪些責任？"],
        "傳統故事中，太康經常離開都城做什麼？", ["打獵","讀書","治水","經商"], "打獵"
    ),
    "houyi-takes-xia": lesson(
        "houyi-takes-xia", "Xia Tradition", "🏹",
        "Hou Yi Takes Control of Xia", "后羿代夏",
        "Explore the traditional story of Hou Yi taking power during the Xia dynasty.",
        "傳統記載中，太康失去政權後，有窮氏的后羿控制了夏朝的政治。他善於射箭，也有很大的軍事力量。后羿雖然掌握權力，卻沒有建立穩定的統治。後來，他身邊的寒浞逐漸取得信任，最後奪走了他的權力。這個故事描述了夏朝早期的權力鬥爭。",
        [vocab("后羿", "Hòu Yì", "Hou Yi"), vocab("射箭", "shèjiàn", "archery"), vocab("政權", "zhèngquán", "political power"), vocab("軍事", "jūnshì", "military affairs"), vocab("鬥爭", "dòuzhēng", "struggle")],
        "這裡的后羿是夏朝傳統記載中的有窮氏首領，不應直接與射日神話混為一談。",
        ["后羿如何取得權力？","有權力就一定能管理好國家嗎？"],
        "傳統記載中，后羿以什麼本領聞名？", ["射箭","造船","寫詩","製陶"], "射箭"
    ),
    "han-zhuo-seizes-power": lesson(
        "han-zhuo-seizes-power", "Xia Tradition", "⚔️",
        "Han Zhuo Seizes Power", "寒浞奪權",
        "Follow the traditional account of Han Zhuo's rise and seizure of power.",
        "傳統記載中，寒浞原本受到后羿信任，後來卻想自己掌握政權。他趁后羿失去警覺時發動政變，奪取權力。寒浞和他的兒子繼續攻擊夏朝王室的勢力。多年以後，少康得到支持，重新建立夏朝的統治。這段故事也成為少康中興的背景。",
        [vocab("寒浞", "Hán Zhuó", "Han Zhuo"), vocab("奪權", "duóquán", "to seize power"), vocab("信任", "xìnrèn", "trust"), vocab("政變", "zhèngbiàn", "coup"), vocab("王室", "wángshì", "royal family")],
        "寒浞奪權與少康中興相連，主要見於後世對夏朝的傳統敘述。",
        ["寒浞如何取得權力？","為什麼信任對領導者很重要？"],
        "故事中，寒浞從誰手中奪取權力？", ["后羿","大禹","商湯","周公"], "后羿"
    ),
    "jie-and-mo-xi": lesson(
        "jie-and-mo-xi", "Xia Tradition", "👑",
        "King Jie and Mo Xi", "夏桀與妹喜",
        "Read the traditional tale of the last Xia ruler and Mo Xi.",
        "傳統故事中，夏桀是夏朝最後一位君主，妹喜是與他有關的著名人物。後世記載常說夏桀生活奢侈，不重視人民的困難，也把他的失德與妹喜聯繫在一起。可是，這些細節多來自後世傳說，不能全部當作確定的史實。最後，商湯起兵反抗夏桀，夏朝走向滅亡。",
        [vocab("夏桀", "Xià Jié", "King Jie of Xia"), vocab("妹喜", "Mò Xǐ", "Mo Xi"), vocab("奢侈", "shēchǐ", "extravagant"), vocab("失德", "shīdé", "to lose virtue"), vocab("滅亡", "mièwáng", "to fall")],
        "古代史書常把王朝滅亡歸咎於君主與女性人物；閱讀妹喜的故事時，應分辨歷史證據與後世的道德敘事。",
        ["後世如何描述夏桀？","為什麼閱讀古代故事需要分辨史實和傳說？"],
        "傳統記載中，夏桀是哪個朝代的最後一位君主？", ["夏朝","商朝","周朝","秦朝"], "夏朝"
    ),
    "shao-kang-revival": lesson(
        "shao-kang-revival", "Xia Tradition", "🌱",
        "The Revival under Shao Kang", "少康中興",
        "Learn the traditional story of how Shao Kang restored Xia rule after a period of decline.",
        "傳統記載中，夏朝曾經失去政權，王室力量衰弱。少康在困難的環境中長大，逐漸得到支持者的幫助。他重新集結力量，最後恢復夏朝的統治。後人把這段故事稱為「少康中興」。「中興」指一個王朝在衰弱之後重新恢復力量。",
        [vocab("少康", "Shào Kāng", "Shao Kang"), vocab("中興", "zhōngxīng", "revival"), vocab("恢復", "huīfù", "to restore"), vocab("統治", "tǒngzhì", "rule"), vocab("支持", "zhīchí", "support")],
        "「中興」後來常用來描述國家、王朝或組織在困難之後重新振作。學習這個詞，也能幫助理解後世的歷史敘事。",
        ["你怎麼理解「中興」？", "一個國家在困難之後要恢復力量，需要哪些條件？"],
        "「中興」最接近哪一個意思？", ["衰弱後重新恢復", "第一次建立國家", "出海旅行", "發明文字"], "衰弱後重新恢復"
    ),
    "shang-tang-overthrows-xia": lesson(
        "shang-tang-overthrows-xia", "Xia–Shang Transition", "🔥",
        "Tang Overthrows the Xia", "商湯滅夏",
        "Follow the traditional account of the fall of Xia and the rise of the Shang dynasty.",
        "傳統記載中，夏朝末年的君主夏桀失去許多人的支持。商部落的領袖湯逐漸強大，聯合其他力量反抗夏桀。最後，湯打敗夏桀，建立商朝。這個故事常被後世用來討論君主的責任，以及一個王朝為什麼會失去人民的支持。",
        [vocab("商湯", "Shāng Tāng", "Tang of Shang"), vocab("夏桀", "Xià Jié", "Jie of Xia"), vocab("反抗", "fǎnkàng", "to resist"), vocab("建立", "jiànlì", "to establish"), vocab("王朝", "wángcháo", "dynasty")],
        "商湯滅夏的故事形成了中國傳統歷史中「失德的統治者失去天下」的重要敘事模式，後來也常被用來解釋王朝更替。",
        ["為什麼一個統治者可能失去人民支持？", "你認為領導者最重要的責任是什麼？"],
        "傳統故事中，誰建立了商朝？", ["商湯", "大禹", "周武王", "秦始皇"], "商湯"
    ),
    "king-wu-overthrows-shang": lesson(
        "king-wu-overthrows-shang", "Shang–Zhou Transition", "⚔️",
        "King Wu Overthrows the Shang", "武王伐紂",
        "See how the traditional story of King Wu and the Battle of Muye explains the transition from Shang to Zhou.",
        "商朝末年，周的力量逐漸增強。周武王聯合其他部族討伐商紂王，雙方在牧野交戰。商朝戰敗，周武王建立周朝。後來的歷史敘事把這次王朝更替和統治者是否有德連在一起，也發展出「天命」的政治觀念。",
        [vocab("周武王", "Zhōu Wǔwáng", "King Wu of Zhou"), vocab("商紂王", "Shāng Zhòuwáng", "King Zhou of Shang"), vocab("牧野", "Mùyě", "Muye"), vocab("討伐", "tǎofá", "to campaign against"), vocab("天命", "tiānmìng", "Mandate of Heaven")],
        "「天命」成為理解周代政治思想的重要概念：統治不只與權力有關，也被描述為與統治者的行為和責任有關。",
        ["古人為什麼用「天命」解釋王朝更替？", "你認為權力和責任應該有什麼關係？"],
        "武王伐紂之後建立了哪一個朝代？", ["周朝", "漢朝", "唐朝", "宋朝"], "周朝"
    ),
    "duke-of-zhou": lesson(
        "duke-of-zhou", "Western Zhou", "🎵",
        "The Duke of Zhou and the Zhou Order", "周公制禮作樂",
        "Explore the traditional role of the Duke of Zhou in shaping Zhou institutions, ritual and political culture.",
        "周朝建立後，周公成為重要的政治人物。傳統記載把許多禮制、音樂和政治制度的建立與周公聯繫在一起，稱為「制禮作樂」。禮不只是儀式，也用來規範不同身分的人應該如何相處。這些觀念對後來的中國政治與文化產生了長期影響。",
        [vocab("周公", "Zhōu Gōng", "Duke of Zhou"), vocab("禮", "lǐ", "ritual / propriety"), vocab("樂", "yuè", "music"), vocab("制度", "zhìdù", "institution / system"), vocab("規範", "guīfàn", "to regulate")],
        "今天華語中的「禮貌」「禮儀」仍使用「禮」這個字。雖然現代社會和周代不同，如何用規則維持社會秩序仍是重要問題。",
        ["「禮」除了儀式之外，還有什麼作用？", "現代社會有哪些規則幫助人們相處？"],
        "傳統上「制禮作樂」最常和誰聯繫在一起？", ["周公", "鄭和", "漢武帝", "岳飛"], "周公"
    ),
    "beacon-fires": lesson(
        "beacon-fires", "Western Zhou", "🔥",
        "The Beacon Fires and the Feudal Lords", "烽火戲諸侯",
        "Hear the famous cautionary tale associated with King You of Zhou, Bao Si and the end of Western Zhou.",
        "傳說西周末年的周幽王為了讓褒姒發笑，多次點燃原本用來警告敵人來襲的烽火。諸侯看到烽火後趕來救援，卻發現沒有敵人。後來真正的危機發生時，救援沒有及時到來。這個故事後來成為失去信任會帶來嚴重後果的著名典故。",
        [vocab("烽火", "fēnghuǒ", "beacon fire"), vocab("周幽王", "Zhōu Yōuwáng", "King You of Zhou"), vocab("褒姒", "Bāo Sì", "Bao Si"), vocab("諸侯", "zhūhóu", "feudal lords"), vocab("信任", "xìnrèn", "trust")],
        "「烽火戲諸侯」今天仍常被當作失去信用的故事。它也很像「狼來了」：警報如果被反覆濫用，人們可能不再相信真正的警告。",
        ["為什麼信任一旦失去就很難恢復？", "你知道其他和「信用」有關的故事嗎？"],
        "烽火原本的主要用途是什麼？", ["警告敵人來襲", "舉行宴會", "照亮宮殿", "慶祝新年"], "警告敵人來襲"
    ),
}


# Placement relative to the existing Oracle Bones lesson.
EARLY_BEFORE_ORACLE = [
    EARLY_HISTORY_LESSONS["gun-fails-flood-control"],
    EARLY_HISTORY_LESSONS["yu-controls-floods"],
    EARLY_HISTORY_LESSONS["taikang-loses-kingdom"],
    EARLY_HISTORY_LESSONS["houyi-takes-xia"],
    EARLY_HISTORY_LESSONS["han-zhuo-seizes-power"],
    EARLY_HISTORY_LESSONS["shao-kang-revival"],
    EARLY_HISTORY_LESSONS["jie-and-mo-xi"],
    EARLY_HISTORY_LESSONS["shang-tang-overthrows-xia"],
]

EARLY_AFTER_ORACLE = [
    EARLY_HISTORY_LESSONS["king-wu-overthrows-shang"],
    EARLY_HISTORY_LESSONS["duke-of-zhou"],
    EARLY_HISTORY_LESSONS["beacon-fires"],
]
