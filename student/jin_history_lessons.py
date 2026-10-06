"""Jin dynasty story lessons for the PandaSpeak History Journey."""

def vocab(word, pinyin, meaning):
    return {"word": word, "pinyin": pinyin, "meaning": meaning}

def lesson(slug, level, icon, title, chinese_title, intro):
    return {
        "slug": slug, "level": level, "era": "Jin Dynasty", "icon": icon,
        "title": title, "chinese_title": chinese_title, "intro": intro,
        "passage": "本課將介紹這個晉朝著名故事的歷史背景、主要人物和後世影響。完整故事內容、影音和詞彙將陸續加入。",
        "vocabulary": [vocab("晉朝", "Jìncháo", "Jin Dynasty"), vocab("歷史", "lìshǐ", "history"), vocab("故事", "gùshì", "story")],
        "today": "這個故事至今仍是了解晉朝歷史與中國文化的重要材料。",
        "speak_prompts": ["這個故事中有哪些重要人物？", "你從這個故事學到什麼？"],
        "quiz": {"question": "這個故事主要和哪一個時代有關？", "choices": ["晉朝", "唐朝", "明朝", "清朝"], "answer": "晉朝"},
    }

JIN_HISTORY_LESSONS = {
    "sima-zhao-intent": lesson("sima-zhao-intent", "level2", "👑", "Sima Zhao's Intent Is Known to Everyone", "司馬昭之心，路人皆知", "Learn the famous expression describing Sima Zhao's obvious political ambition near the end of the Three Kingdoms period."),
    "happy-not-miss-shu": lesson("happy-not-miss-shu", "level2", "🎭", "So Happy He Did Not Miss Shu", "樂不思蜀", "Learn the famous story of Liu Shan after the fall of Shu and the expression still used today."),
    "three-kingdoms-unite-jin": lesson("three-kingdoms-unite-jin", "level3", "🏯", "The Three Kingdoms Unite under Jin", "三家歸晉", "Learn how the era of the Three Kingdoms ended and China was reunified under the Western Jin."),
    "shi-chong-wealth": lesson("shi-chong-wealth", "level3", "💎", "Shi Chong Competes in Wealth", "石崇鬥富", "Explore the extravagant life of Western Jin elites through the famous stories about Shi Chong competing in displays of wealth."),
    "war-eight-princes": lesson("war-eight-princes", "level3", "⚔️", "The War of the Eight Princes", "八王之亂", "Explore the destructive struggle among Jin princes and its effect on the Western Jin."),
    "dance-rooster": lesson("dance-rooster", "level2", "🐓", "Rise at the Crow of the Rooster", "聞雞起舞", "Learn the famous story of Zu Ti and Liu Kun training diligently after hearing the rooster crow."),
    "strike-oar-midstream": lesson("strike-oar-midstream", "level3", "🚣", "Striking the Oar Midstream", "中流擊楫", "Follow Zu Ti's determination to recover lost territory in the north."),
    "comeback-east-mountain": lesson("comeback-east-mountain", "level2", "⛰️", "Making a Comeback", "東山再起", "Discover the story of Xie An and the origin of a common expression for returning to prominence."),
    "whips-stop-river": lesson("whips-stop-river", "level3", "🌊", "Throwing Whips Could Stop the River", "投鞭斷流", "Learn how Fu Jian used this boast to describe the enormous Former Qin army before the Battle of Fei River."),
    "battle-fei-river": lesson("battle-fei-river", "level3", "🛡️", "The Battle of Fei River", "淝水之戰", "Learn how the Eastern Jin defeated a much larger Former Qin army in one of China's famous battles."),
    "grass-trees-soldiers": lesson("grass-trees-soldiers", "level2", "🌿", "Every Bush and Tree Looks Like an Enemy", "草木皆兵", "Learn the famous idiom connected with fear and the Battle of Fei River."),
    "wind-cranes": lesson("wind-cranes", "level2", "🕊️", "The Wind and Cranes Sound Like Pursuers", "風聲鶴唳", "Discover another famous expression associated with the defeated army after the Battle of Fei River."),
    "lanting-preface": lesson("lanting-preface", "level3", "🖌️", "Wang Xizhi and the Orchid Pavilion", "王羲之與蘭亭集序", "Meet Wang Xizhi and learn why the Orchid Pavilion Preface became a landmark of Chinese calligraphy."),
    "five-pecks-rice": lesson("five-pecks-rice", "level2", "🌾", "Not Bowing for Five Pecks of Rice", "不為五斗米折腰", "Learn the story associated with Tao Yuanming and refusing to sacrifice one's principles for a minor official salary."),
}

JIN_CARDS = list(JIN_HISTORY_LESSONS.values())
