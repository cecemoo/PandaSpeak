"""Jin dynasty story lessons for the PandaSpeak History Journey."""

def vocab(word, pinyin, meaning):
    return {"word": word, "pinyin": pinyin, "meaning": meaning}

PASSAGES = {
    "happy-not-miss-shu": "蜀漢滅亡後，後主劉禪被接到洛陽，住在晉朝安排的府裡。司馬昭設宴請他喝酒，故意讓人表演蜀地的歌舞，想試探他的心意。旁邊的人都傷心落淚，只有劉禪看得津津有味。有人問他想不想念蜀國，他回答：在這裡很快樂，不想念蜀國。後來「樂不思蜀」就成了有名的成語。",
    "shi-chong-wealth": "西晉初年，大官石崇非常富有，喜歡誇耀自己的財富。皇帝的舅舅王愷也很有錢，兩人就比誰更奢侈。王愷用糖水洗鍋，石崇就用蠟燭當柴燒。晉武帝出面幫王愷，拿出外國進貢的珊瑚樹撐場面，石崇卻拿出更多更大的珊瑚樹，一一打碎。「石崇鬥富」成了奢侈浪費的代名詞。",
    "sima-zhao-intent": "司馬懿死後，他的兒子司馬師和司馬昭先後掌權，魏國的皇帝只是傀儡。司馬昭一心想取代魏國，自己當皇帝，這份野心連路上的行人都看得出來。年輕的皇帝曹髦不甘心受人擺布，決定親自起兵反抗。可惜他力量太小，最後被司馬昭的手下殺害。",
    "three-kingdoms-unite-jin": "公元二八〇年，晉武帝司馬炎派大軍分六路進攻吳國。吳國的皇帝孫皓昏庸無能，將領們紛紛投降。晉軍攻進建業，孫皓出城投降，吳國滅亡。曹魏、蜀漢、東吳三家先後歸於晉朝，中國重新統一，三國時代正式結束。",
    "war-eight-princes": "晉武帝死後，他的兒子晉惠帝愚笨，不能管理國家。皇后賈南風專權，引起宗室諸王不滿。從公元二九一年開始，八位手握兵權的親王互相殘殺，爭奪權力。這場內亂打了十六年，西晉元氣大傷，終於走向滅亡。",
    "battle-fei-river": "公元三八三年，前秦苻堅率領大軍進攻東晉，號稱有百萬之眾。東晉只有八萬兵馬，由謝安指揮，在淝水迎戰。開戰那天，謝安還在下棋，聽到勝利的消息也不動聲色。東晉以少勝多，大敗前秦，這就是有名的淝水之戰。",
    "comeback-east-mountain": "謝安是東晉的名臣，年輕時隱居在東山，不願做官。後來國家遇到危難，大家都請他出來幫忙。謝安重新出山，帶領東晉軍隊在淝水打敗了前秦。從此「東山再起」就用來形容失勢後重新崛起。",
    "dance-rooster": "西晉末年，祖逖和劉琨一起做官，住在同一個房間。有一天半夜，雞叫了起來，祖逖把劉琨叫醒，說：「聽見雞叫了，我們起來練劍吧！」從此以後，他們每天半夜聽到雞叫就起來練武。後來兩人都成了有名的將領，人們用「聞雞起舞」來形容勤奮努力的人。",
    "strike-oar-midstream": "公元三一三年，祖逖帶兵渡過長江，準備收復北方失地。船到江心，他拿起船槳敲打著水面，發誓說：「如果不能收復中原，我就不再渡過這條江！」將士們聽了都很感動，決心奮勇作戰。後來人們用「中流擊楫」來形容立志報國的決心。",
    "whips-stop-river": "淝水之戰前，前秦皇帝苻堅帶著號稱百萬的大軍南下。他驕傲地說：「我的士兵每人把馬鞭扔進長江，就能截斷江水！」這句話就是成語「投鞭斷流」的由來。可是他太輕敵了，最後在淝水被東晉打得大敗。",
    "five-pecks-rice": "東晉詩人陶淵明曾任彭澤縣令，俸祿只有五斗米。一天，上級派督郵來視察，有人勸他穿官服迎接。陶淵明說：「我不能為五斗米折腰，向鄉里小人低頭。」他當天辭官歸隱，成為千古美談。",
    "grass-trees-soldiers": "公元三八三年，前秦大軍在淝水大敗。苻堅帶著殘兵逃跑，心驚膽戰。回頭望去，八公山上的草木，在他眼中都變成了追來的晉軍。他嚇得加快腳步，後人用「草木皆兵」形容極度驚慌的樣子。",
    "lanting-preface": "公元三五三年，大書法家王羲之在蘭亭舉行雅集。他邀請四十一位文人，曲水流觴，飲酒賦詩。王羲之把詩作編成詩集，並親自寫下序言。這篇《蘭亭集序》被譽為「天下第一行書」。",
    "wind-cranes": "淝水之戰後，前秦軍隊潰不成軍，四處逃散。逃跑的士兵聽見風聲和鶴的叫聲，都以為是晉軍追來了。他們丟盔棄甲，拚命奔逃。後人用「風聲鶴唳」形容驚恐不安的樣子。",
}


def lesson(slug, level, icon, title, chinese_title, intro):
    return {
        "slug": slug, "level": level, "era": "Jin Dynasty", "icon": icon,
        "title": title, "chinese_title": chinese_title, "intro": intro,
        "passage": PASSAGES.get(slug, "本課將介紹這個晉朝著名故事。"),
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
