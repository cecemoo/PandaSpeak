"""Northern and Southern Dynasties story lessons for the PandaSpeak History Journey."""

def vocab(word, pinyin, meaning):
    return {"word": word, "pinyin": pinyin, "meaning": meaning}

PASSAGES = {
    "tan-daoji-sand": "南朝宋名將檀道濟北伐時，軍中糧食快吃完了。敵軍探子聽說宋軍缺糧，準備追擊。檀道濟故意讓士兵夜裡一邊量沙，一邊大聲報出糧食數目，再把少量白米蓋在沙上。敵軍遠遠看見，以為宋軍糧食充足，不敢進攻。這就是「唱籌量沙」的故事。",
    "destroy-great-wall": "檀道濟戰功很高，也很有威望，因此受到朝廷猜忌。宋文帝病重時，有人擔心檀道濟日後難以控制，便下令將他處死。檀道濟被捕時憤怒地說，朝廷這是在毀掉自己的萬里長城。後來北魏南侵，宋文帝想起檀道濟，十分後悔。",
    "yuanjia-northern-expedition": "宋文帝劉義隆在位時，南朝宋國力一度強盛。他多次派兵北伐，希望收復黃河以南的土地。公元四五〇年的北伐準備不足，宋軍深入北方後被北魏反擊，損失慘重。「元嘉草草」後來用來提醒人們，不可在準備不足時輕率出兵。",
    "taiwu-buddhism": "北魏太武帝拓跋燾統一北方後，因政治與宗教原因開始打擊佛教。公元四四六年，他下令拆毀寺院、焚燒佛經，僧人被迫還俗。這是中國歷史上著名的「三武一宗滅佛」事件之一，也反映了南北朝時期宗教與政治之間複雜的關係。",
    "mulan-army": "傳說北方有一位女子名叫花木蘭。父親年老，家中又沒有成年的哥哥，木蘭便女扮男裝，代父從軍。她在軍中征戰多年，立下戰功，回家後才換回女裝，戰友們十分驚訝。《木蘭辭》使這個故事流傳千年，也成為南北朝最著名的傳說之一。",
    "xiaowen-luoyang": "北魏孝文帝希望加強中央統治，也想更深入地吸收中原文化。公元四九四年，他把首都從平城遷到洛陽。為了讓反對遷都的大臣接受，他先以南征為名帶軍隊到洛陽，再宣布遷都。洛陽後來成為北魏重要的政治與文化中心。",
    "xiaowen-reforms": "遷都洛陽後，北魏孝文帝推動一系列改革。他鼓勵鮮卑人改用漢姓、穿中原服飾、學習漢語，皇族拓跋氏也改姓元。這些改革促進了不同民族之間的文化交流與融合，但也引起部分鮮卑貴族的不滿。",
    "jianglang-talent": "南朝文人江淹年輕時文章寫得非常好，受到許多人讚賞。傳說他晚年夢見一位文人向他要回一支五色筆，從此文思大不如前。人們便用「江郎才盡」形容一個人原本很有才華，後來才思逐漸衰退。",
    "draw-dragon-eyes": "南朝梁畫家張僧繇很會畫畫。傳說他在寺廟牆上畫了四條龍，卻故意不畫眼睛。別人一直請他補上，他只好替其中兩條龍點上眼睛。沒想到雷電大作，兩條龍破壁飛走。後來「畫龍點睛」用來比喻在關鍵處加上一筆，使內容更加生動有力。",
    "emperor-wu-monk": "梁武帝蕭衍非常信奉佛教，修建寺院、支持佛學，甚至幾次離開皇宮到同泰寺「捨身」出家。大臣們只好用大量金錢把皇帝贖回朝廷。這些故事顯示佛教在南朝梁的巨大影響，也反映梁武帝晚年治國上的矛盾。",
    "houjing-rebellion": "公元五四八年，降將侯景在南朝梁發動叛亂，很快攻向首都建康。梁朝宗室彼此猜忌，沒有有效合作救援。侯景攻破台城後控制朝廷，江南遭到嚴重破壞。這場「侯景之亂」使原本繁盛的梁朝迅速衰弱。",
    "emperor-wu-taicheng": "侯景之亂時，梁武帝被困在建康台城。城中糧食逐漸用盡，年老的皇帝也失去自由。公元五四九年，梁武帝在台城去世。這位在位近半個世紀的皇帝，晚年因政治失控而遭遇悲劇性的結局。",
    "jade-trees-flowers": "南朝陳後主陳叔寶喜愛音樂、詩歌和宴樂。隋軍準備南下時，陳朝政治已十分腐敗。後世常以《玉樹後庭花》象徵陳後主沉迷享樂、不理政事，也把它視為亡國之音。公元五八九年，隋軍攻入建康，陳朝滅亡。",
    "broken-mirror-reunion": "陳朝即將滅亡時，徐德言擔心戰亂會使自己和妻子樂昌公主失散。他把一面銅鏡打成兩半，夫妻各拿一半，約定日後在長安尋找對方。陳亡後兩人果然失散，最後靠兩半銅鏡重新相認。「破鏡重圓」後來用來形容夫妻失散後重新團聚。",
}

def lesson(slug, level, icon, title, chinese_title, intro):
    return {
        "slug": slug, "level": level, "era": "Northern & Southern Dynasties", "icon": icon,
        "title": title, "chinese_title": chinese_title, "intro": intro,
        "passage": PASSAGES.get(slug, "本課將介紹南北朝時期的著名故事。"),
        "vocabulary": [vocab("南北朝", "Nánběicháo", "Northern and Southern Dynasties"), vocab("歷史", "lìshǐ", "history"), vocab("故事", "gùshì", "story")],
        "today": "這個故事是了解南北朝政治、文化與社會的重要材料。",
        "speak_prompts": ["這個故事中有哪些重要人物？", "你從這個故事學到什麼？"],
        "quiz": {"question": "這個故事主要和哪一個時代有關？", "choices": ["南北朝", "漢朝", "唐朝", "明朝"], "answer": "南北朝"},
    }

NORTHERN_SOUTHERN_HISTORY_LESSONS = {
    "tan-daoji-sand": lesson("tan-daoji-sand", "level3", "🏺", "Measuring Sand as Grain", "唱籌量沙", "Learn how Tan Daoji used deception to make an enemy believe his army still had plenty of grain."),
    "destroy-great-wall": lesson("destroy-great-wall", "level2", "🧱", "Destroying One's Own Great Wall", "自毀長城", "Learn the story of the famous general Tan Daoji and the warning associated with losing a nation's strongest defender."),
    "yuanjia-northern-expedition": lesson("yuanjia-northern-expedition", "level3", "⚔️", "The Yuanjia Northern Expeditions", "元嘉北伐・元嘉草草", "Explore the ambitious but costly Northern Expeditions of Liu Song and the later expression 元嘉草草."),
    "taiwu-buddhism": lesson("taiwu-buddhism", "level3", "📜", "Emperor Taiwu's Suppression of Buddhism", "北魏太武帝滅佛", "Explore the political and religious tensions behind Northern Wei Emperor Taiwu's suppression of Buddhism."),
    "mulan-army": lesson("mulan-army", "level2", "🐎", "Mulan Joins the Army for Her Father", "木蘭代父從軍", "Read the legendary story preserved in the Ballad of Mulan, one of the best-known tales associated with the Northern Dynasties."),
    "xiaowen-luoyang": lesson("xiaowen-luoyang", "level2", "🏯", "Emperor Xiaowen Moves the Capital to Luoyang", "孝文帝遷都洛陽", "Learn why Northern Wei Emperor Xiaowen moved his capital from Pingcheng to Luoyang."),
    "xiaowen-reforms": lesson("xiaowen-reforms", "level3", "👘", "Emperor Xiaowen's Reforms", "孝文帝漢化改革", "Explore Emperor Xiaowen's reforms and the cultural integration of the Northern Wei."),
    "jianglang-talent": lesson("jianglang-talent", "level2", "✍️", "Jiang Lang's Talent Is Exhausted", "江郎才盡", "Learn the legend behind the common expression for someone whose former creative talent seems to have faded."),
    "draw-dragon-eyes": lesson("draw-dragon-eyes", "level2", "🐉", "Painting the Dragon and Dotting the Eyes", "畫龍點睛", "Discover the famous legend about painter Zhang Sengyou and an expression still widely used today."),
    "emperor-wu-monk": lesson("emperor-wu-monk", "level3", "🏛️", "Emperor Wu Enters the Monastery", "梁武帝捨身同泰寺", "Learn about Emperor Wu of Liang's extraordinary devotion to Buddhism and repeated stays at Tongtai Temple."),
    "houjing-rebellion": lesson("houjing-rebellion", "level3", "🔥", "The Hou Jing Rebellion", "侯景之亂", "Explore the rebellion that devastated Jiankang and greatly weakened the Liang dynasty."),
    "emperor-wu-taicheng": lesson("emperor-wu-taicheng", "level3", "🏰", "Emperor Wu Trapped in Taicheng", "梁武帝困死台城", "Follow the tragic end of Emperor Wu of Liang after Hou Jing captured the imperial city."),
    "jade-trees-flowers": lesson("jade-trees-flowers", "level3", "🎵", "Flowers in the Jade Trees", "玉樹後庭花・陳後主亡國", "Learn how the last ruler of Chen became associated with a famous song and the image of a ruler absorbed in pleasure as his dynasty fell."),
    "broken-mirror-reunion": lesson("broken-mirror-reunion", "level2", "🪞", "A Broken Mirror Reunited", "破鏡重圓", "Learn the famous story of Xu Deyan and Princess Lechang at the fall of Chen and the origin of a common idiom."),
}

NORTHERN_SOUTHERN_CARDS = list(NORTHERN_SOUTHERN_HISTORY_LESSONS.values())
