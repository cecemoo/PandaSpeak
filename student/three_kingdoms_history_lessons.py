"""Three Kingdoms stories for the PandaSpeak History Journey.

The collection follows the familiar cultural narrative chronologically. Several
famous episodes come from Romance of the Three Kingdoms rather than the strict
historical record; lesson text can distinguish history from literary tradition.
"""


PASSAGES = {
    "cao-cao-heroes": "有一天，曹操請劉備一起喝酒，談論誰才是真正的英雄。劉備小心回答，不敢說出自己真正的想法。突然雷聲大作，劉備手一抖，筷子掉在地上。曹操見劉備如此膽小，放心地點點頭，從此不再懷疑他。",
    "guan-yu-five-passes": "劉備、關羽在戰亂中失散了。身在曹營的他，心裡一直想念劉備。得知劉備的消息後，馬上出發尋找。一路上經過五個關口，斬殺六名敵將。最後終於和劉備團聚，兄弟情深令人感動。",
    "peach-garden-oath": "東漢末年，天下大亂。劉備、關羽和張飛在桃園相遇，一見如故。三人殺牛設酒，結拜為兄弟，發誓同生共死。這就是歷史上有名的「桃園三結義」。",
    "three-heroes-lu-bu": "董卓手下的大將呂布，勇猛無比，無人能敵。劉備、關羽和張飛三兄弟一起上前迎戰。三人圍攻呂布，打得難分難解。呂布最後抵擋不住，敗下陣來。",
    "three-visits": "劉備聽說南陽住著一位大賢人，名叫諸葛亮。他親自前往拜訪，卻兩次都沒見到人。第三次，諸葛亮終於被他的誠意打動，答應出山相助。劉備如魚得水，實力大增。",
    "changban-zhao-yun": "曹操大軍追來，劉備帶著百姓一起逃難。在長坂坡混亂中，劉備的兒子阿斗不見了。趙雲單槍匹馬，衝進曹軍陣中尋找阿斗。他抱著阿斗殺出重圍，回到劉備身邊。",
    "guan-yu-jingzhou": "關羽鎮守荊州，連打勝仗，變得驕傲自大。他看不起東吳的呂蒙，帶大軍去攻打曹魏。呂蒙假裝生病，暗中準備偷襲。吳軍白衣渡江，一舉拿下荊州。關羽前後受敵，最後被吳軍抓住殺害。",
    "huarong-pass": "赤壁大敗後，曹操帶著殘兵逃往華容道。諸葛亮早就算到，派關羽在那裡等候。關羽想起當年曹操對他的厚待，心中不忍。他放開一條路，讓曹操過去。關羽回去向諸葛亮請罪，諸葛亮也原諒了他。",
    "red-cliffs": "曹操率領大軍南下，號稱有八十萬人。孫權和劉備結盟，只有五萬兵力，在赤壁迎戰。周瑜和諸葛亮決定用火攻。黃蓋駕著裝滿柴草的火船，衝向曹操的戰船。曹軍大火，死傷無數，曹操只好逃走。",
    "straw-boats-arrows": "赤壁之戰前，周瑜要諸葛亮十天造出十萬支箭。諸葛亮說三天就夠了。第三天清晨，江上起了大霧。諸葛亮帶著二十艘草船，靠近曹軍水寨。曹軍看不見敵人，只能放箭，箭都射在草人上。諸葛亮滿載而歸，讓周瑜心服口服。",
    "baidicheng-trust": "劉備伐吳失敗，病重於白帝城。臨終前，他把兒子劉禪託付給諸葛亮。他說：「君才十倍曹丕，必能安國，終定大事。」諸葛亮含淚受命，誓死效忠。",
    "empty-fort": "諸葛亮北伐，街亭失守，司馬懿率大軍逼近西城。城中無兵，諸葛亮卻大開城門，獨自在城樓上彈琴。司馬懿疑有埋伏，退兵而去。空城計，千古傳為美談。",
    "guan-yu-maicheng": "建安二十四年，關羽攻打襄樊，威震華夏。不料孫權背盟，偷襲荊州，關羽腹背受敵。關羽敗走麥城，被吳軍擒獲，不屈而死。一代名將，就此落幕。",
    "seven-captures-meng-huo": "劉備死後，南中孟獲叛亂。諸葛亮率軍南征，七次擒獲孟獲，又七次放了他。孟獲感動，說：「公，天威也，南人不復反矣。」從此南方安定，蜀漢無後顧之憂。",
    "yiling-battle": "關羽死後，劉備為報仇，親自率大軍伐吳。陸遜堅守不出，蜀軍銳氣漸失。陸遜趁夜火燒連營，劉備大敗，退守白帝城。夷陵一戰，蜀漢元氣大傷。",
    "jin-reunifies": "晉朝建立後，皇帝司馬炎決心統一中國。公元二八〇年，晉軍分六路大舉進攻吳國。吳國皇帝孫皓昏庸無能，將士們紛紛投降。晉軍攻入建業，孫皓出城投降，吳國滅亡。從此，中國重新統一，三國時代正式結束。",
    "shu-falls": "諸葛亮死後，蜀漢國力漸漸衰弱。公元二六三年，魏國大將鄧艾、鍾會分兵進攻蜀漢。鄧艾偷渡陰平，直逼成都。後主劉禪自知無力抵抗，開城投降。蜀漢滅亡，享國四十三年。",
    "sima-clan-rise": "司馬懿是魏國的重臣，足智多謀，深得人心。公元二四九年，他發動高平陵之變，奪取了魏國的大權。司馬懿死後，他的兒子司馬師、司馬昭先後掌權，魏國皇帝成了傀儡。公元二六六年，司馬炎逼迫魏帝讓位，建立晉朝。曹魏滅亡，三國的局勢徹底改變。",
    "tears-ma-su": "公元二二八年，諸葛亮第一次北伐。馬謖自告奮勇，鎮守街亭。諸葛亮再三叮囑，要他依山紮營。馬謖卻不聽命令，在山上紮營，被魏軍切斷水源，大敗而逃。諸葛亮含淚下令，將馬謖斬首，以正軍法。",
    "wuzhang-plains": "公元二三四年，諸葛亮第五次北伐，駐軍五丈原。他日夜操勞，積勞成疾，病情越來越重。臨終前，他把後事安排妥當，囑咐將士們繼續北伐。八月，諸葛亮病逝於軍中，年僅五十四歲。那天晚上，一顆大星從天上墜落，蜀軍全軍悲痛。",
}


def lesson(slug, level, era, icon, title, chinese_title, year):
    intro = f"Explore {chinese_title}, a famous story from the Three Kingdoms tradition."
    return {
        "slug": slug, "level": level, "era": era, "icon": icon,
        "title": title, "chinese_title": chinese_title, "intro": intro,
        "passage": PASSAGES.get(slug, f"這一課介紹「{chinese_title}」。"),
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
