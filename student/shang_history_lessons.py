"""Additional Shang dynasty lessons; historical traditions are distinguished from evidence."""
from .early_history_lessons import lesson, vocab

SHANG_HISTORY_LESSONS = {
    "yi-yin-assists-tang": lesson(
        "yi-yin-assists-tang", "Early Shang", "📜",
        "Yi Yin Helps King Tang", "伊尹輔佐商湯",
        "Meet the adviser traditionally credited with helping Tang establish the Shang dynasty.",
        "傳統記載中，伊尹是一位有智慧的大臣。他幫助商湯治理國家，也支持商湯對抗夏桀。商湯建立商朝後，伊尹繼續輔佐王室。後世常把伊尹看成善於治國的賢臣。不過，這些故事主要來自後世文獻，部分細節難以證實。",
        [vocab("伊尹","Yī Yǐn","Yi Yin"),vocab("輔佐","fǔzuǒ","to assist a ruler"),vocab("大臣","dàchén","minister"),vocab("治國","zhìguó","to govern a country"),vocab("賢臣","xiánchén","wise minister")],
        "伊尹在傳統歷史中象徵有能力的輔佐者；閱讀早期商朝故事時，也要留意史料形成的年代。",
        ["伊尹如何幫助商湯？","好的領導者為什麼需要顧問？"],
        "伊尹主要輔佐哪位君主？",["商湯","周武王","秦始皇","漢武帝"],"商湯"
    ),
    "pan-geng-moves-capital": lesson(
        "pan-geng-moves-capital", "Shang", "🏯",
        "Pan Geng Moves the Capital to Yin", "盤庚遷殷",
        "Learn why a Shang king is remembered for moving the royal center to Yin.",
        "商朝的都城曾經改變。傳統記載說，盤庚決定把都城遷到殷，雖然有些人不願意搬遷，他仍努力說服大家。殷後來成為商朝重要的政治中心。考古學家在今天的河南安陽發現殷墟，出土許多甲骨文和青銅器，幫助我們了解晚商的生活。",
        [vocab("盤庚","Pán Gēng","Pan Geng"),vocab("遷都","qiāndū","to move the capital"),vocab("都城","dūchéng","capital city"),vocab("殷墟","Yīnxū","Yin ruins"),vocab("考古","kǎogǔ","archaeology")],
        "安陽殷墟是研究晚商歷史的重要考古遺址；盤庚遷都的具體過程仍需結合文獻與考古資料理解。",
        ["盤庚為什麼要遷都？","搬遷都城會帶來哪些困難？"],
        "殷墟位於今天哪個省？",["河南","廣東","四川","福建"],"河南"
    ),
    "wu-ding-fu-yue": lesson(
        "wu-ding-fu-yue", "Shang", "👑",
        "King Wu Ding and Fu Yue", "武丁與傅說",
        "Discover the traditional tale of a king seeking a capable adviser.",
        "商王武丁希望找到能幫助他治理國家的人。傳說他夢見一位賢人，後來找到傅說，請他擔任重要職務。傅說幫助武丁處理政事，成為著名的賢臣。武丁確實是甲骨文中有記錄的商王，但夢中尋賢的情節主要屬於後世流傳的故事。",
        [vocab("武丁","Wǔ Dīng","King Wu Ding"),vocab("傅說","Fù Yuè","Fu Yue"),vocab("賢人","xiánrén","capable and virtuous person"),vocab("夢見","mèngjiàn","to dream of"),vocab("政事","zhèngshì","government affairs")],
        "武丁時期留下大量甲骨文；傅說的傳說則提醒我們區分考古證據與文學敘事。",
        ["武丁希望找到什麼樣的人？","你認為能力和品德哪一個更重要？"],
        "傳說武丁在什麼情況下見到賢人？",["夢中","戰場上","市場裡","海上"],"夢中"
    ),
    "shang-bronze-civilization": lesson(
        "shang-bronze-civilization", "Shang", "🏺",
        "Bronze Civilization of the Shang", "商朝的青銅文明",
        "Explore the sophisticated bronze vessels and rituals of Shang society.",
        "商朝工匠能製作精美的青銅器。許多青銅器用於祭祀，也代表貴族的身分和權力。工匠把銅、錫等金屬混合，再用模具鑄造器物。今天博物館保存了許多商代青銅器，讓我們看到當時高超的技術和獨特的藝術。",
        [vocab("青銅器","qīngtóngqì","bronze object"),vocab("工匠","gōngjiàng","craftsperson"),vocab("祭祀","jìsì","ritual offering"),vocab("鑄造","zhùzào","to cast metal"),vocab("模具","mújù","mold")],
        "商代青銅器是研究古代技術、禮儀和社會階層的重要實物證據。",
        ["青銅器有哪些用途？","為什麼考古文物能幫助我們了解歷史？"],
        "商代許多青銅器主要用於什麼活動？",["祭祀","印刷書籍","製造紙張","航海"],"祭祀"
    ),
    "bi-gan-tragic-death": lesson(
        "bi-gan-tragic-death", "Late Shang Tradition", "💔",
        "The Tragic Death of Bi Gan", "比干剖心",
        "Read the famous traditional account of a minister who dared to criticize the king.",
        "傳統故事中，比干是商朝末年的忠臣。他看到紂王的行為，勇敢地提出勸告。傳說紂王非常生氣，最後命人剖開比干的心。這段情節十分悲慘，主要來自後世文獻，不能完全當作已證實的歷史。後人常用比干的故事讚美敢說真話的勇氣。",
        [vocab("比干","Bǐ Gān","Bi Gan"),vocab("忠臣","zhōngchén","loyal minister"),vocab("勸告","quàngào","to advise"),vocab("勇氣","yǒngqì","courage"),vocab("傳說","chuánshuō","legend")],
        "比干剖心是著名的忠臣傳說；其戲劇性的細節缺乏同時代證據。",
        ["比干為什麼勸告紂王？","說真話需要勇氣嗎？"],
        "比干在傳統故事中以什麼聞名？",["忠誠進諫","發明紙張","開闢絲路","修築長城"],"忠誠進諫"
    ),
    "king-zhou-and-daji": lesson(
        "king-zhou-and-daji", "Late Shang Tradition", "👑",
        "King Zhou and Daji", "紂王與妲己",
        "Separate historical questions from the famous legends surrounding Shang's last ruler.",
        "傳統故事把商朝末年的紂王描述成殘暴的君主，妲己則是與他有關的著名人物。後世小說又加入許多神怪情節，使故事更加精彩。但是，不能把小說內容當作真正的歷史，也不能簡單地把商朝滅亡歸咎於妲己。商朝最後被周的軍隊打敗，進入新的時代。",
        [vocab("紂王","Zhòuwáng","King Zhou of Shang"),vocab("妲己","Dájǐ","Daji"),vocab("殘暴","cánbào","cruel"),vocab("小說","xiǎoshuō","novel"),vocab("滅亡","mièwáng","to fall")],
        "妲己的形象受到後世文學影響很大。研究王朝滅亡時，應考慮政治、軍事與社會因素，而非只責怪單一人物。",
        ["歷史和小說有什麼不同？","為什麼不能只用一個人解釋王朝滅亡？"],
        "關於妲己的許多神怪情節主要來自哪裡？",["後世小說","甲骨文","現代新聞","漢代紙幣"],"後世小說"
    ),
}
SHANG_CARDS = list(SHANG_HISTORY_LESSONS.values())
