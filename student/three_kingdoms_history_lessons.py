"""Three Kingdoms stories for the PandaSpeak History Journey.

The collection follows the familiar cultural narrative chronologically. Several
famous episodes come from Romance of the Three Kingdoms rather than the strict
historical record; lesson text can distinguish history from literary tradition.
"""


def lesson(slug, level, era, icon, title, chinese_title, year):
    intro = f"Explore {chinese_title}, a famous story from the Three Kingdoms tradition."
    return {
        "slug": slug, "level": level, "era": era, "icon": icon,
        "title": title, "chinese_title": chinese_title, "intro": intro,
        "passage": f"這一課介紹「{chinese_title}」。故事內容與語言學習活動將在下一步加入。",
        "vocabulary": [],
        "today": "學習三國故事時，也要分辨歷史記載、後世傳說和《三國演義》的文學描寫。",
        "speak_prompts": [f"你聽過「{chinese_title}」嗎？", "你對這個故事中的人物有什麼印象？"],
        "quiz": {"question": f"這一課的主題是什麼？", "choices": [chinese_title, "甲骨文", "絲綢之路", "大禹治水"], "answer": chinese_title},
        "year": year,
    }


THREE_KINGDOMS_HISTORY_LESSONS = {
    "peach-garden-oath": lesson("peach-garden-oath", "level2", "Late Han", "🌸", "Oath of the Peach Garden", "桃園三結義", "184"),
    "three-heroes-lu-bu": lesson("three-heroes-lu-bu", "level3", "Late Han", "⚔️", "Three Heroes Battle Lü Bu", "三英戰呂布", "190"),
    "cao-cao-heroes": lesson("cao-cao-heroes", "level3", "Warlord Era", "🍶", "Cao Cao Discusses Heroes over Wine", "煮酒論英雄", "c. 199"),
    "guan-yu-five-passes": lesson("guan-yu-five-passes", "level3", "Warlord Era", "🗡️", "Guan Yu Passes Five Gates and Slays Six Generals", "過五關斬六將", "c. 200"),
    "three-visits": lesson("three-visits", "level2", "Late Han", "🏡", "Three Visits to the Thatched Cottage", "三顧茅廬", "207"),
    "changban-zhao-yun": lesson("changban-zhao-yun", "level2", "Late Han", "🐎", "Zhao Yun Rescues A Dou at Changban", "趙雲長坂坡救阿斗", "208"),
    "straw-boats-arrows": lesson("straw-boats-arrows", "level2", "Red Cliffs", "🏹", "Borrowing Arrows with Straw Boats", "草船借箭", "208"),
    "red-cliffs": lesson("red-cliffs", "level2", "Red Cliffs", "🔥", "Battle of Red Cliffs", "赤壁之戰", "208"),
    "huarong-pass": lesson("huarong-pass", "level3", "Red Cliffs", "🛤️", "Guan Yu Releases Cao Cao at Huarong Pass", "華容道義釋曹操", "208"),
    "guan-yu-jingzhou": lesson("guan-yu-jingzhou", "level3", "Shu–Wu Conflict", "🏯", "Guan Yu Loses Jingzhou", "關羽大意失荊州", "219"),
    "guan-yu-maicheng": lesson("guan-yu-maicheng", "level3", "Shu–Wu Conflict", "🌧️", "Guan Yu Defeated at Maicheng", "關羽敗走麥城", "219"),
    "yiling-battle": lesson("yiling-battle", "level3", "Three Kingdoms", "🔥", "Battle of Yiling", "夷陵之戰", "222"),
    "baidicheng-trust": lesson("baidicheng-trust", "level3", "Three Kingdoms", "📜", "Liu Bei Entrusts His Son at Baidicheng", "白帝城託孤", "223"),
    "seven-captures-meng-huo": lesson("seven-captures-meng-huo", "level2", "Three Kingdoms", "🌿", "Seven Captures of Meng Huo", "七擒孟獲", "225"),
    "empty-fort": lesson("empty-fort", "level2", "Northern Expeditions", "🎶", "Empty Fort Strategy", "空城計", "228"),
    "tears-ma-su": lesson("tears-ma-su", "level3", "Northern Expeditions", "⚖️", "Zhuge Liang Executes Ma Su with Tears", "揮淚斬馬謖", "228"),
    "wuzhang-plains": lesson("wuzhang-plains", "level3", "Northern Expeditions", "⭐", "Zhuge Liang Dies at Wuzhang Plains", "諸葛亮病逝五丈原", "234"),
    "sima-clan-rise": lesson("sima-clan-rise", "level3", "Late Three Kingdoms", "🏛️", "The Sima Clan Seizes Power", "司馬氏掌權", "249–266"),
    "shu-falls": lesson("shu-falls", "level3", "Late Three Kingdoms", "🏳️", "Fall of Shu Han", "蜀漢滅亡", "263"),
    "jin-reunifies": lesson("jin-reunifies", "level3", "End of Three Kingdoms", "🗺️", "Jin Conquers Wu and Reunifies China", "西晉滅吳", "280"),
}

THREE_KINGDOMS_CARDS = [THREE_KINGDOMS_HISTORY_LESSONS[slug] for slug in [
    "peach-garden-oath",
    "three-heroes-lu-bu",
    "cao-cao-heroes",
    "guan-yu-five-passes",
    "three-visits",
    "changban-zhao-yun",
    "straw-boats-arrows",
    "red-cliffs",
    "huarong-pass",
    "guan-yu-jingzhou",
    "guan-yu-maicheng",
    "yiling-battle",
    "baidicheng-trust",
    "seven-captures-meng-huo",
    "empty-fort",
    "tears-ma-su",
    "wuzhang-plains",
    "sima-clan-rise",
    "shu-falls",
    "jin-reunifies",
]]
