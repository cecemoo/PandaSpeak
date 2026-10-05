"""Qin-era story lessons for the PandaSpeak History Journey."""


def vocab(word, pinyin, meaning):
    return {"word": word, "pinyin": pinyin, "meaning": meaning}


def lesson(slug, era, icon, title, chinese_title, intro, passage, vocabulary,
           today, speak_prompts, question, choices, answer):
    return {
        "slug": slug, "level": "level2", "era": era, "icon": icon,
        "title": title, "chinese_title": chinese_title, "intro": intro,
        "passage": passage, "vocabulary": vocabulary, "today": today,
        "speak_prompts": speak_prompts,
        "quiz": {"question": question, "choices": choices, "answer": answer},
    }


QIN_HISTORY_LESSONS = {
    "jing-ke-assassination": lesson(
        "jing-ke-assassination", "Late Warring States", "🗡️", "Jing Ke Attempts to Assassinate the King of Qin", "荊軻刺秦王",
        "Follow the famous story of Jing Ke's dangerous mission against the future Qin Shi Huang.",
        "戰國末年，秦國越來越強大。燕太子丹擔心秦國進攻燕國，因此派荊軻前往秦國刺殺秦王嬴政。荊軻帶著地圖和匕首進入秦王宮，但行刺最後失敗。秦王嬴政後來統一六國，成為秦始皇。",
        [vocab("荊軻", "Jīng Kē", "Jing Ke"), vocab("刺殺", "cìshā", "to assassinate"), vocab("秦王", "Qínwáng", "King of Qin"), vocab("匕首", "bǐshǒu", "dagger"), vocab("燕國", "Yānguó", "State of Yan")],
        "荊軻刺秦王成為中國歷史上非常著名的故事，也常出現在文學、戲劇和電影中。",
        ["荊軻為什麼去刺殺秦王？", "你認為這次行動為什麼失敗？"],
        "荊軻刺殺的是後來的哪一位皇帝？", ["秦始皇", "漢武帝", "唐太宗", "康熙帝"], "秦始皇"),
    "qin-standardization": lesson(
        "qin-standardization", "Qin Dynasty", "📏", "Standardizing the Empire", "書同文，車同軌",
        "See how the Qin government promoted common standards across its newly unified empire.",
        "秦統一六國後，秦始皇推動許多統一政策，包括文字、貨幣和度量衡。傳統上也用「書同文，車同軌」來描述統一後共同標準的形成。這些政策讓不同地區的行政、交通和經濟往來更加方便。",
        [vocab("書同文", "shū tóng wén", "standardized writing"), vocab("車同軌", "chē tóng guǐ", "standardized axle tracks"), vocab("度量衡", "dùliànghéng", "weights and measures"), vocab("貨幣", "huòbì", "currency"), vocab("標準", "biāozhǔn", "standard")],
        "今天我們使用共同的文字、尺寸和貨幣標準時，也可以思考標準化如何幫助社會交流。",
        ["統一標準有什麼好處？", "生活中還有哪些共同標準？"],
        "秦朝統一的項目包括哪一個？", ["度量衡", "網路密碼", "飛機航線", "電話號碼"], "度量衡"),
    "qin-great-wall": lesson(
        "qin-great-wall", "Qin Dynasty", "🧱", "Qin and the Great Wall", "秦朝與萬里長城",
        "Learn why the Qin connected and expanded northern defensive walls.",
        "秦朝建立後，北方邊境仍面臨軍事威脅。秦始皇命令將一些原有的城牆連接、修築和擴展，用來加強北方防禦。今天看到的長城大多不是秦代留下的原貌，但秦代修築長城成為中國歷史中的重要記憶。",
        [vocab("長城", "Chángchéng", "Great Wall"), vocab("邊境", "biānjìng", "frontier"), vocab("防禦", "fángyù", "defense"), vocab("修築", "xiūzhù", "to construct"), vocab("城牆", "chéngqiáng", "wall")],
        "今天保存較完整的長城多為明代修建或重建，因此學習長城歷史時要注意不同時代的差別。",
        ["秦朝為什麼修築北方城牆？", "為什麼長城會在不同朝代繼續修建？"],
        "秦朝修築北方城牆的主要目的之一是什麼？", ["加強防禦", "舉辦運動會", "種植水稻", "發展海運"], "加強防禦"),
    "meng-jiangnu": lesson(
        "meng-jiangnu", "Qin Legend", "💧", "Meng Jiangnü Weeps at the Great Wall", "孟姜女哭長城",
        "Discover one of China's best-known folk legends connected with the Great Wall.",
        "民間傳說中，孟姜女的丈夫被徵去修築長城。她長途跋涉去尋找丈夫，卻得知丈夫已經去世。傳說她悲痛大哭，甚至哭倒了一段長城。這不是可以當作史實證明的事件，而是一個流傳很久的民間故事，反映人們對徭役、家庭分離和苦難的想像。",
        [vocab("孟姜女", "Mèng Jiāngnǚ", "Meng Jiangnü"), vocab("民間傳說", "mínjiān chuánshuō", "folk legend"), vocab("徭役", "yáoyì", "forced labor service"), vocab("悲痛", "bēitòng", "grief"), vocab("長城", "Chángchéng", "Great Wall")],
        "歷史故事和民間傳說不完全相同。學習孟姜女的故事，也可以練習分辨傳說、文學和史實。",
        ["這個故事反映了哪些人的生活困難？", "民間傳說和歷史記錄有什麼不同？"],
        "孟姜女哭長城應該如何理解？", ["著名民間傳說", "現代新聞報導", "秦朝法律全文", "考古發掘紀錄"], "著名民間傳說"),
    "burning-books": lesson(
        "burning-books", "Qin Dynasty", "📚", "Burning Books and the Scholars", "焚書坑儒",
        "Examine a famous and debated account of Qin intellectual control.",
        "傳統史書記載，秦始皇統治時曾下令焚燒部分書籍，以限制某些政治批評；後來又有被稱為「坑儒」的事件。現代研究提醒我們，事件的細節、被處罰者的身分，以及後世如何描述這段歷史，都需要謹慎討論。因此「焚書坑儒」既是著名典故，也是學習如何閱讀歷史資料的好例子。",
        [vocab("焚書", "fénshū", "burning books"), vocab("坑儒", "kēngrú", "traditional term for the scholar incident"), vocab("史書", "shǐshū", "historical record"), vocab("批評", "pīpíng", "criticism"), vocab("爭議", "zhēngyì", "controversy")],
        "研究古代事件時，歷史學者會比較不同資料，而不是只依靠一個後世流傳的說法。",
        ["為什麼研究歷史要比較不同資料？", "政府控制思想可能產生什麼問題？"],
        "學習「焚書坑儒」時最適合採取什麼態度？", ["比較史料並注意爭議", "所有傳說都完全正確", "不用看歷史資料", "只看故事標題"], "比較史料並注意爭議"),
    "sha-qiu-coup": lesson(
        "sha-qiu-coup", "Late Qin", "📜", "The Coup at Shaqiu", "沙丘之變",
        "See how Qin Shi Huang's death created a dangerous struggle over succession.",
        "秦始皇在巡行途中去世後，秦朝很快陷入權力危機。傳統記載中，趙高、李斯等人隱瞞皇帝死訊，並改變皇位繼承安排，使胡亥成為秦二世。這次事件通常被稱為「沙丘之變」，也成為秦朝迅速衰亡的重要轉折之一。",
        [vocab("沙丘之變", "Shāqiū zhī Biàn", "Coup at Shaqiu"), vocab("趙高", "Zhào Gāo", "Zhao Gao"), vocab("李斯", "Lǐ Sī", "Li Si"), vocab("胡亥", "Hú Hài", "Huhai"), vocab("繼承", "jìchéng", "succession")],
        "領導權的交接如果缺少穩定制度，往往可能造成嚴重的政治危機。",
        ["為什麼皇位繼承會影響國家穩定？", "隱瞞重要資訊可能帶來什麼後果？"],
        "沙丘之變發生在誰去世之後？", ["秦始皇", "漢高祖", "周武王", "商湯"], "秦始皇"),
    "calling-deer-horse": lesson(
        "calling-deer-horse", "Late Qin", "🦌", "Calling a Deer a Horse", "指鹿為馬",
        "Learn the origin of the famous idiom associated with Zhao Gao and the late Qin court.",
        "傳統記載中，趙高在秦二世面前牽來一隻鹿，卻故意說那是一匹馬。他想觀察哪些官員會順著他的話，哪些人敢說真話。後來「指鹿為馬」成為著名成語，用來形容故意顛倒是非、把錯的說成對的。",
        [vocab("指鹿為馬", "zhǐ lù wéi mǎ", "call a deer a horse"), vocab("趙高", "Zhào Gāo", "Zhao Gao"), vocab("官員", "guānyuán", "official"), vocab("是非", "shìfēi", "right and wrong"), vocab("故意", "gùyì", "deliberately")],
        "「指鹿為馬」今天仍是常用成語，可以用來談權力、誠實和人們是否敢說真話。",
        ["趙高為什麼故意把鹿說成馬？", "在什麼情況下人們可能不敢說真話？"],
        "「指鹿為馬」現在通常形容什麼？", ["故意顛倒是非", "跑得非常快", "照顧動物", "旅行很遠"], "故意顛倒是非"),
    "dazexiang-uprising": lesson(
        "dazexiang-uprising", "Fall of Qin", "✊", "The Dazexiang Uprising", "大澤鄉起義",
        "Learn how Chen Sheng and Wu Guang helped ignite widespread rebellion against Qin rule.",
        "秦二世時期，陳勝、吳廣等人被徵發前往服役。傳統記載中，他們因大雨延誤行程，擔心受到秦法處罰，於是在大澤鄉起兵反抗。這場起義雖然最後失敗，卻鼓舞各地反秦力量，秦朝的統治也開始快速瓦解。",
        [vocab("大澤鄉起義", "Dàzéxiāng Qǐyì", "Dazexiang Uprising"), vocab("陳勝", "Chén Shèng", "Chen Sheng"), vocab("吳廣", "Wú Guǎng", "Wu Guang"), vocab("起義", "qǐyì", "uprising"), vocab("反抗", "fǎnkàng", "to resist")],
        "陳勝、吳廣起義常被視為秦末大規模反抗的重要開端。",
        ["為什麼秦末會出現許多反抗力量？", "嚴格的法律可能怎麼影響人民？"],
        "大澤鄉起義最常和哪兩個人聯繫在一起？", ["陳勝、吳廣", "劉備、關羽", "李白、杜甫", "商湯、伊尹"], "陳勝、吳廣"),
    "battle-of-julu": lesson(
        "battle-of-julu", "Fall of Qin", "⚔️", "Battle of Julu: Breaking the Cauldrons", "巨鹿之戰與破釜沉舟",
        "Follow Xiang Yu into the decisive fighting against Qin forces and learn a famous idiom.",
        "秦末反抗力量不斷增加。項羽率軍救援巨鹿時，傳統故事說他命令士兵破壞炊具、渡河後毀掉退路，表示一定要決戰到底。楚軍在巨鹿之戰中擊敗秦軍主力。「破釜沉舟」後來成為成語，形容下定決心、不留退路。",
        [vocab("巨鹿之戰", "Jùlù zhī Zhàn", "Battle of Julu"), vocab("項羽", "Xiàng Yǔ", "Xiang Yu"), vocab("破釜沉舟", "pò fǔ chén zhōu", "break the cauldrons and sink the boats"), vocab("秦軍", "Qínjūn", "Qin army"), vocab("決心", "juéxīn", "determination")],
        "「破釜沉舟」今天仍常用來形容為了達成目標而下定決心。",
        ["「破釜沉舟」為什麼能鼓舞士兵？", "你覺得做重大決定時應不應該完全不留退路？"],
        "「破釜沉舟」和哪一位人物最有關？", ["項羽", "孔子", "鄭和", "岳飛"], "項羽"),
    "fall-of-qin": lesson(
        "fall-of-qin", "Fall of Qin", "🏳️", "Liu Bang Enters Guanzhong and Qin Falls", "劉邦入關，秦朝滅亡",
        "Complete the Qin story with Liu Bang's entry into the Qin heartland and the dynasty's surrender.",
        "秦末各地起兵後，劉邦率軍進入關中。西元前二〇六年，秦王子嬰向劉邦投降，秦朝滅亡。秦朝從統一六國到滅亡只有很短的時間，但它建立的中央集權和許多統一制度，對後來中國歷史產生長期影響。秦亡之後，劉邦和項羽之間又展開新的爭奪。",
        [vocab("劉邦", "Liú Bāng", "Liu Bang"), vocab("關中", "Guānzhōng", "Guanzhong"), vocab("子嬰", "Zǐyīng", "Ziying"), vocab("投降", "tóuxiáng", "to surrender"), vocab("滅亡", "mièwáng", "to fall / perish")],
        "一個王朝雖然存在時間很短，也可能留下長期制度影響。秦朝就是重要例子。",
        ["秦朝為什麼會快速滅亡？", "秦朝有哪些制度影響了後世？"],
        "秦朝最後向誰的軍隊投降？", ["劉邦", "周武王", "曹操", "朱元璋"], "劉邦"),
}

QIN_BEFORE_UNIFICATION = [QIN_HISTORY_LESSONS["jing-ke-assassination"]]
QIN_AFTER_UNIFICATION = [
    QIN_HISTORY_LESSONS["qin-standardization"], QIN_HISTORY_LESSONS["qin-great-wall"],
    QIN_HISTORY_LESSONS["meng-jiangnu"], QIN_HISTORY_LESSONS["burning-books"],
    QIN_HISTORY_LESSONS["sha-qiu-coup"], QIN_HISTORY_LESSONS["calling-deer-horse"],
    QIN_HISTORY_LESSONS["dazexiang-uprising"], QIN_HISTORY_LESSONS["battle-of-julu"],
    QIN_HISTORY_LESSONS["fall-of-qin"],
]
