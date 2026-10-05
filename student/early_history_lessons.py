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
    EARLY_HISTORY_LESSONS["yu-controls-floods"],
    EARLY_HISTORY_LESSONS["shao-kang-revival"],
    EARLY_HISTORY_LESSONS["shang-tang-overthrows-xia"],
]

EARLY_AFTER_ORACLE = [
    EARLY_HISTORY_LESSONS["king-wu-overthrows-shang"],
    EARLY_HISTORY_LESSONS["duke-of-zhou"],
    EARLY_HISTORY_LESSONS["beacon-fires"],
]
