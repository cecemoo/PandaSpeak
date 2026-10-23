"""Selected Zhou dynasty history lessons for the PandaSpeak journey."""
from .early_history_lessons import lesson, vocab

ZHOU_HISTORY_LESSONS = {
    "jiang-taigong-fishing": lesson(
        "jiang-taigong-fishing", "Western Zhou Tradition", "🎣",
        "Jiang Taigong Goes Fishing", "姜太公釣魚",
        "Explore the legend of Jiang Ziya waiting for a ruler who valued his wisdom.",
        "傳說姜太公年紀很大時，仍在河邊釣魚。他不用普通的魚鉤，因為他真正等待的不是魚，而是懂得重用人才的君主。後來周文王遇見他，欣賞他的智慧，請他協助治理國家。這個故事常被稱為「姜太公釣魚，願者上鉤」。",
        [vocab("姜太公", "Jiāng Tàigōng", "Jiang Taigong"), vocab("釣魚", "diàoyú", "to fish"), vocab("智慧", "zhìhuì", "wisdom"), vocab("人才", "réncái", "talent"), vocab("君主", "jūnzhǔ", "ruler")],
        "這是後世流傳的著名傳說，釣魚的細節不能視為已證實的史實。",
        ["這個故事的主要人物是誰？","這個故事帶給你什麼啟發？"],
        "姜太公等待的是什麼？", ["賞識人才的君主","魚","商紂王","一艘船"], "賞識人才的君主"
    ),
    "duke-huan-qi-hegemon": lesson(
        "duke-huan-qi-hegemon", "Spring and Autumn", "👑",
        "Duke Huan of Qi Becomes Hegemon", "齊桓公稱霸",
        "Discover how Duke Huan and Guan Zhong strengthened the state of Qi.",
        "春秋時期，齊桓公任用管仲治理國家。管仲推動改革，讓齊國的經濟和軍事力量逐漸增強。齊桓公召集諸侯會盟，成為春秋時期著名的霸主之一。這個故事說明君主如何透過人才和制度擴大影響力。",
        [vocab("齊桓公", "Qí Huángōng", "Duke Huan of Qi"), vocab("管仲", "Guǎn Zhòng", "Guan Zhong"), vocab("改革", "gǎigé", "reform"), vocab("諸侯", "zhūhóu", "feudal lords"), vocab("霸主", "bàzhǔ", "hegemon")],
        "春秋時期的霸主不是周天子，而是能號召其他諸侯的強大國君。",
        ["這個故事的主要人物是誰？","這個故事帶給你什麼啟發？"],
        "誰幫助齊桓公改革齊國？", ["管仲","孔子","孟子","荊軻"], "管仲"
    ),
    "retreat-three-she": lesson(
        "retreat-three-she", "Spring and Autumn", "🏹",
        "Retreating Ninety Li", "退避三舍",
        "Learn the story behind an idiom about keeping a promise and yielding ground.",
        "傳統記載中，晉文公曾受楚國幫助，答應日後兩國交戰時先退避三舍。後來晉楚兩軍相遇，晉軍真的後退三舍，約九十里。這不只是守信，也是一種軍事策略。後人用「退避三舍」表示主動讓步，避免正面衝突。",
        [vocab("退避三舍", "tuìbì sāns hè", "to yield ground"), vocab("晉文公", "Jìn Wéngōng", "Duke Wen of Jin"), vocab("承諾", "chéngnuò", "promise"), vocab("軍隊", "jūnduì", "army"), vocab("策略", "cèlüè", "strategy")],
        "「三舍」是古代行軍距離的說法；故事常與城濮之戰聯繫在一起。",
        ["這個故事的主要人物是誰？","這個故事帶給你什麼啟發？"],
        "退避三舍今天常表示什麼？", ["主動讓步","立即進攻","尋找寶物","遷移都城"], "主動讓步"
    ),
    "one-cry-amazes": lesson(
        "one-cry-amazes", "Spring and Autumn", "🐦",
        "Amazing the World with One Cry", "一鳴驚人",
        "Read the famous tale of a ruler who surprised everyone after a quiet period.",
        "傳統故事中，楚莊王即位後，長時間沒有展現治國的能力。有人用一隻多年不飛也不叫的鳥來提醒他。楚莊王回答，這隻鳥一旦飛起來就會直上天空，一旦鳴叫就會令人驚訝。後來他整頓政事，讓楚國更加強大。這就是「一鳴驚人」的故事。",
        [vocab("一鳴驚人", "yì míng jīng rén", "to astonish with sudden success"), vocab("楚莊王", "Chǔ Zhuāngwáng", "King Zhuang of Chu"), vocab("整頓", "zhěngdùn", "to reorganize"), vocab("表現", "biǎoxiàn", "performance"), vocab("驚訝", "jīngyà", "surprised")],
        "這個成語今天形容平時不突出的人突然做出令人驚訝的成績。",
        ["這個故事的主要人物是誰？","這個故事帶給你什麼啟發？"],
        "一鳴驚人形容什麼？", ["突然表現出色","一直沉默","失去權力","長途旅行"], "突然表現出色"
    ),
    "goujian-endures-hardship": lesson(
        "goujian-endures-hardship", "Spring and Autumn", "🌿",
        "Goujian Endures Hardship for Revenge", "臥薪嘗膽",
        "Follow the traditional account of King Goujian rebuilding Yue after defeat.",
        "越王勾踐曾被吳王夫差打敗。他回國後努力整頓國家，提醒自己不要忘記失敗的痛苦。後世流傳他睡在柴草上、品嘗苦膽的故事，因此有了「臥薪嘗膽」這個成語。多年後，越國力量增強，終於打敗吳國。",
        [vocab("勾踐", "Gōu Jiàn", "Goujian"), vocab("夫差", "Fū Chāi", "Fuchai"), vocab("臥薪嘗膽", "wò xīn cháng dǎn", "to endure hardship for a goal"), vocab("失敗", "shībài", "defeat"), vocab("報仇", "bàochóu", "revenge")],
        "臥薪嘗膽的具體細節在不同時代的文獻中逐漸形成，應區分傳說與歷史。",
        ["這個故事的主要人物是誰？","這個故事帶給你什麼啟發？"],
        "臥薪嘗膽通常比喻什麼？", ["忍受困難努力達成目標","喜歡吃苦味食物","放棄理想","離開家鄉"], "忍受困難努力達成目標"
    ),
    "confucius-travels-states": lesson(
        "confucius-travels-states", "Spring and Autumn", "📚",
        "Confucius Travels Among the States", "孔子周遊列國",
        "Follow Confucius as he travels to share ideas about government and society.",
        "孔子生活在春秋末年，重視仁、禮和教育。他曾帶著弟子到不同的諸侯國，希望君主接受他的政治理想。雖然他的建議沒有全部實現，他仍持續教學。後來弟子與再傳弟子保存他的言行，形成《論語》的重要內容。",
        [vocab("孔子", "Kǒngzǐ", "Confucius"), vocab("弟子", "dìzǐ", "disciple"), vocab("諸侯國", "zhūhóuguó", "feudal state"), vocab("教育", "jiàoyù", "education"), vocab("論語", "Lúnyǔ", "Analects")],
        "孔子的思想對後世東亞教育與倫理產生深遠影響；《論語》是研究其思想的重要文獻。",
        ["這個故事的主要人物是誰？","這個故事帶給你什麼啟發？"],
        "孔子周遊列國主要希望做什麼？", ["推廣政治理念","尋找金礦","建立海軍","發明火藥"], "推廣政治理念"
    ),
    "laozi-leaves-pass": lesson(
        "laozi-leaves-pass", "Eastern Zhou Tradition", "🐂",
        "Laozi Leaves Through the Pass", "老子出關",
        "Explore the legend of Laozi and the origins associated with the Dao De Jing.",
        "傳說老子看見天下混亂，決定離開周朝的政治中心。他騎著青牛向西走，到了關口，守關的人請他留下智慧。老子於是寫下關於「道」與「德」的文字，後人把這個故事與《道德經》聯繫在一起。老子的生平與著作形成過程，仍有許多歷史爭論。",
        [vocab("老子", "Lǎozǐ", "Laozi"), vocab("出關", "chūguān", "to leave through a pass"), vocab("道德經", "Dàodéjīng", "Dao De Jing"), vocab("傳說", "chuánshuō", "legend"), vocab("智慧", "zhìhuì", "wisdom")],
        "騎青牛出關主要是後世傳說；《道德經》的成書歷史比單一人物寫作的故事更複雜。",
        ["這個故事的主要人物是誰？","這個故事帶給你什麼啟發？"],
        "傳說老子在關口留下哪部著作？", ["道德經","論語","史記","孫子兵法"], "道德經"
    ),
    "shang-yang-reforms": lesson(
        "shang-yang-reforms", "Warring States", "⚖️",
        "Shang Yang's Reforms", "商鞅變法",
        "Discover how reforms helped transform Qin during the Warring States period.",
        "戰國時期，商鞅在秦國推動改革。他重視農業和軍功，改變部分舊制度，讓國家能更有效地管理土地、人口和軍隊。改革使秦國逐漸強大，但也引起反對。商鞅後來遭到處死，許多改革措施卻繼續影響秦國。",
        [vocab("商鞅", "Shāng Yāng", "Shang Yang"), vocab("變法", "biànfǎ", "legal and institutional reform"), vocab("秦國", "Qín Guó", "state of Qin"), vocab("軍功", "jūngōng", "military merit"), vocab("制度", "zhìdù", "system")],
        "商鞅變法是理解秦國崛起的重要事件，也引發法律、權力和社會公平的討論。",
        ["這個故事的主要人物是誰？","這個故事帶給你什麼啟發？"],
        "商鞅在哪個國家推動改革？", ["秦國","齊國","吳國","越國"], "秦國"
    ),
    "sun-bin-pang-juan": lesson(
        "sun-bin-pang-juan", "Warring States", "♟️",
        "Sun Bin and Pang Juan", "孫臏與龐涓",
        "Explore the rivalry and military strategies associated with two famous figures.",
        "戰國時期，孫臏是齊國著名的軍事謀士。傳統故事說，他曾受到龐涓陷害，後來幫助齊軍對抗魏國。桂陵之戰與馬陵之戰常和他的策略聯繫在一起。孫臏善於觀察敵軍的行動，利用形勢取得優勢。兩人的私人恩怨在後世故事中有許多戲劇化情節。",
        [vocab("孫臏", "Sūn Bìn", "Sun Bin"), vocab("龐涓", "Páng Juān", "Pang Juan"), vocab("軍事", "jūnshì", "military affairs"), vocab("策略", "cèlüè", "strategy"), vocab("魏國", "Wèi Guó", "state of Wei")],
        "孫臏的軍事思想與《孫臏兵法》相關；龐涓陷害孫臏的細節應謹慎看待。",
        ["這個故事的主要人物是誰？","這個故事帶給你什麼啟發？"],
        "孫臏主要幫助哪個國家作戰？", ["齊國","秦國","楚國","燕國"], "齊國"
    ),
    "return-jade-zhao": lesson(
        "return-jade-zhao", "Warring States", "💎",
        "Returning the Jade Intact to Zhao", "完璧歸趙",
        "Read how Lin Xiangru protected a precious jade in negotiations with Qin.",
        "戰國時期，秦王想得到趙國的和氏璧，表示願意交換城池。趙國派藺相如帶著寶玉前往秦國。藺相如發現秦王可能不守承諾，便設法保護寶玉，最後讓和氏璧安全回到趙國。後人用「完璧歸趙」形容把物品完整歸還原主。",
        [vocab("完璧歸趙", "wán bì guī Zhào", "return something intact"), vocab("藺相如", "Lìn Xiāngrú", "Lin Xiangru"), vocab("和氏璧", "Héshìbì", "He clan jade disc"), vocab("承諾", "chéngnuò", "promise"), vocab("談判", "tánpàn", "negotiation")],
        "這個故事見於《史記》，也常被用來討論外交談判與勇氣。",
        ["這個故事的主要人物是誰？","這個故事帶給你什麼啟發？"],
        "完璧歸趙中的「璧」是什麼？", ["玉器","銅鐘","竹簡","寶劍"], "玉器"
    ),
    "carry-thorns-apology": lesson(
        "carry-thorns-apology", "Warring States", "🤝",
        "Carrying Thorns to Apologize", "負荊請罪",
        "Discover how Lian Po apologized to Lin Xiangru and restored their cooperation.",
        "戰國時期，趙國的將軍廉頗不服藺相如地位比自己高。藺相如為了國家利益，盡量避免和他衝突。廉頗知道原因後感到慚愧，背著荊條到藺相如家中請罪。兩人後來和好，一起為趙國努力。這就是「負荊請罪」的故事。",
        [vocab("負荊請罪", "fù jīng qǐng zuì", "make a sincere apology"), vocab("廉頗", "Lián Pō", "Lian Po"), vocab("藺相如", "Lìn Xiāngrú", "Lin Xiangru"), vocab("道歉", "dàoqiàn", "to apologize"), vocab("和好", "héhǎo", "to reconcile")],
        "「負荊請罪」今天用來形容主動承認錯誤並誠懇道歉。",
        ["這個故事的主要人物是誰？","這個故事帶給你什麼啟發？"],
        "廉頗為什麼背著荊條？", ["向藺相如道歉","準備打獵","搬運木材","慶祝勝利"], "向藺相如道歉"
    ),
    "jing-ke-assassinates-qin": lesson(
        "jing-ke-assassinates-qin", "Warring States", "🗡️",
        "Jing Ke Attempts to Assassinate the King of Qin", "荊軻刺秦王",
        "Follow the dramatic failed assassination attempt during Qin's expansion.",
        "戰國末年，秦國不斷擴張，燕國感到威脅。燕太子丹派荊軻前往秦國，試圖刺殺秦王嬴政。荊軻帶著地圖等物品進入宮廷，卻沒有成功，最後被殺。秦國後來繼續統一六國的戰爭。這個故事常被用來討論勇氣、忠誠與政治選擇。",
        [vocab("荊軻", "Jīng Kē", "Jing Ke"), vocab("秦王", "Qín Wáng", "King of Qin"), vocab("燕國", "Yān Guó", "state of Yan"), vocab("刺殺", "cìshā", "to assassinate"), vocab("地圖", "dìtú", "map")],
        "荊軻刺秦王發生在秦統一之前；嬴政當時尚未稱秦始皇。",
        ["這個故事的主要人物是誰？","這個故事帶給你什麼啟發？"],
        "荊軻試圖刺殺誰？", ["秦王嬴政","周武王","漢高祖","齊桓公"], "秦王嬴政"
    ),
}
ZHOU_CARDS = list(ZHOU_HISTORY_LESSONS.values())
