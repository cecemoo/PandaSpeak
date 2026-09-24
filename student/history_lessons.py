"""Built-in Chinese History lessons for Level II and III students.

History lessons intentionally use Traditional Chinese and keep the language-learning
focus: discover the story, listen, speak, connect history to today, then complete a
short challenge.
"""


def vocab(word, pinyin, meaning):
    return {"word": word, "pinyin": pinyin, "meaning": meaning}


def lesson(slug, level, era, icon, title, chinese_title, intro, passage, vocabulary,
           today, speak_prompts, question, choices, answer):
    return {
        "slug": slug,
        "level": level,
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


HISTORY_LESSONS = {
    "oracle-bones": lesson(
        "oracle-bones", "level2", "Early China", "🐢",
        "Oracle Bones and Early Chinese Writing", "甲骨文與早期漢字",
        "Discover how some of the earliest known Chinese writing was preserved on bones and shells.",
        "三千多年前，商朝的人把文字刻在龜甲和動物骨頭上。這些文字叫做甲骨文。人們用甲骨文記錄問題、祭祀和生活中的事情。今天的很多漢字雖然已經改變，但是我們還可以看到它們和古代文字的關係。",
        [vocab("甲骨文", "jiǎgǔwén", "oracle-bone script"), vocab("文字", "wénzì", "writing / characters"), vocab("商朝", "Shāngcháo", "Shang dynasty"), vocab("記錄", "jìlù", "to record"), vocab("古代", "gǔdài", "ancient times")],
        "漢字經過幾千年的變化，今天仍然是華語世界最重要的書寫系統。看到「日、月、山、水」時，可以想一想它們早期象形文字的樣子。",
        ["你覺得漢字和英文的字母有什麼不同？", "如果你可以保存一件今天的事情給三千年後的人看，你會記錄什麼？"],
        "甲骨文最常和哪一個朝代有關？", ["商朝", "唐朝", "宋朝", "清朝"], "商朝"
    ),
    "qin-unification": lesson(
        "qin-unification", "level2", "Ancient Dynasties", "👑",
        "Qin Shi Huang and Unification", "秦始皇與統一",
        "Learn why the Qin unification became a major turning point in Chinese history.",
        "西元前二二一年，秦始皇統一了多個國家，建立秦朝。他推動統一文字、貨幣和度量衡，希望不同地區的人可以使用相同的制度。秦朝時間不長，但是很多制度對後來的中國歷史有很大的影響。",
        [vocab("秦始皇", "Qín Shǐhuáng", "Qin Shi Huang"), vocab("統一", "tǒngyī", "to unify"), vocab("皇帝", "huángdì", "emperor"), vocab("貨幣", "huòbì", "currency"), vocab("制度", "zhìdù", "system")],
        "今天到西安附近參觀兵馬俑，可以看到秦代留下的重要歷史遺產。中國文字長期共享書寫標準，也和早期統一政策有歷史關聯。",
        ["你認為統一文字有什麼好處？", "你想去看兵馬俑嗎？為什麼？"],
        "秦始皇推動統一的項目不包括哪一個？", ["文字", "貨幣", "度量衡", "網路"], "網路"
    ),
    "han-silk-road": lesson(
        "han-silk-road", "level2", "Imperial China", "🐫",
        "The Han Dynasty and the Silk Road", "漢朝與絲綢之路",
        "Follow the routes that connected China with Central Asia and places farther west.",
        "漢朝時期，中國和中亞的交流增加。商人沿著後來被稱為絲綢之路的路線旅行，帶著絲綢和其他商品，也把新的物品、思想和文化帶到不同地方。絲綢之路不是只有一條路，而是一個很大的交通和交流網絡。",
        [vocab("漢朝", "Hàncháo", "Han dynasty"), vocab("絲綢之路", "Sīchóu Zhī Lù", "Silk Road"), vocab("商人", "shāngrén", "merchant"), vocab("交流", "jiāoliú", "exchange"), vocab("文化", "wénhuà", "culture")],
        "今天的西安曾是古代重要都城，也是研究絲路歷史的重要城市。現代人談到跨文化交流時，仍常用絲綢之路作為歷史例子。",
        ["旅行可以帶來哪些文化交流？", "如果你是古代商人，你想帶什麼商品去遠方？"],
        "絲綢之路比較接近哪一種描述？", ["只有一條短路", "一個交通與交流網絡", "一座宮殿", "一種文字"], "一個交通與交流網絡"
    ),
    "tang-changan": lesson(
        "tang-changan", "level2", "Golden Ages", "🏮",
        "Tang Chang'an: A Cosmopolitan Capital", "唐朝的長安",
        "Meet the people, languages, foods and ideas that made Tang Chang'an an international city.",
        "唐朝的長安是當時世界上很大的城市之一。很多商人、學生、使者和宗教人士來到長安。城市裡可以看到不同地方的商品、音樂和飲食。唐詩也在這個時代非常發達，李白和杜甫成為後世熟悉的詩人。",
        [vocab("長安", "Cháng'ān", "Chang'an"), vocab("唐朝", "Tángcháo", "Tang dynasty"), vocab("使者", "shǐzhě", "envoy"), vocab("唐詩", "Tángshī", "Tang poetry"), vocab("詩人", "shīrén", "poet")],
        "今天的西安就是古代長安所在的地區。唐詩仍是華語教育與文化中的重要內容，也留下很多日常引用的名句和典故。",
        ["你覺得什麼條件會讓一個城市變得國際化？", "如果你可以去唐朝長安一天，你最想看什麼？"],
        "古代長安大致位於今天的哪一座城市？", ["西安", "上海", "香港", "臺北"], "西安"
    ),
    "song-innovation": lesson(
        "song-innovation", "level3", "Golden Ages", "🧭",
        "Song China: Cities, Printing and Innovation", "宋代的城市與發明",
        "Explore how commerce, printing and technology changed daily life during the Song period.",
        "宋代的城市經濟和商業非常活躍，城市居民可以在市場、茶館和娛樂場所消費。印刷技術的發展讓書籍更容易流通，知識也能傳播得更廣。指南針、火藥與印刷等技術在中國歷史上經過長期發展，並在不同時期影響世界。理解這些變化，不只是記住「發明」，而是觀察技術如何改變社會。",
        [vocab("宋代", "Sòngdài", "Song period"), vocab("商業", "shāngyè", "commerce"), vocab("印刷", "yìnshuā", "printing"), vocab("傳播", "chuánbō", "to spread"), vocab("技術", "jìshù", "technology")],
        "今天電子閱讀和網路再次改變知識傳播方式。比較印刷術與網路，可以討論科技如何降低資訊傳播的成本，也如何改變教育。",
        ["印刷技術為什麼可能改變教育？", "你認為哪一種現代科技對社會的影響最像早期印刷？為什麼？"],
        "這一課強調研究歷史發明時還應該注意什麼？", ["只背發明名稱", "技術如何改變社會", "只記皇帝名字", "忽略城市生活"], "技術如何改變社會"
    ),
    "zheng-he": lesson(
        "zheng-he", "level3", "China and the World", "⛵",
        "Zheng He's Voyages", "鄭和下西洋",
        "Consider what the Ming voyages tell us about diplomacy, trade and maritime connections.",
        "十五世紀初，明朝派鄭和率領大型船隊多次出航，前往東南亞、南亞、阿拉伯半島與東非一帶。船隊進行外交活動，也交換物品。鄭和下西洋反映了當時中國與印度洋世界之間的海上聯繫。研究這段歷史時，可以同時思考國家力量、貿易與外交的關係。",
        [vocab("鄭和", "Zhèng Hé", "Zheng He"), vocab("下西洋", "xià Xīyáng", "voyage to the Western Seas"), vocab("船隊", "chuánduì", "fleet"), vocab("外交", "wàijiāo", "diplomacy"), vocab("貿易", "màoyì", "trade")],
        "今天東南亞仍有許多華人社群，區域內海上貿易也非常重要。鄭和故事常被用來討論中國與東南亞及印度洋的歷史聯繫。",
        ["貿易和外交有什麼關係？", "大型遠洋航行需要一個國家具備哪些能力？"],
        "鄭和的船隊主要透過哪一種方式與其他地區連結？", ["海上航行", "鐵路", "飛機", "網路"], "海上航行"
    ),
    "ming-qing-beijing": lesson(
        "ming-qing-beijing", "level3", "Late Imperial China", "🏯",
        "Ming-Qing Beijing and the Forbidden City", "明清北京與紫禁城",
        "Use Beijing's imperial center to examine government, architecture and symbols of authority.",
        "明朝永樂年間，北京成為重要政治中心，紫禁城也在十五世紀初建成。明、清兩代的皇帝都曾在這裡處理國家政務。宮殿的空間安排、建築形式和儀式反映皇權與政治秩序。到了二十世紀，紫禁城從皇宮逐漸轉變為博物院，成為大眾可以參觀的文化遺產。",
        [vocab("紫禁城", "Zǐjìnchéng", "Forbidden City"), vocab("皇權", "huángquán", "imperial authority"), vocab("政務", "zhèngwù", "government affairs"), vocab("儀式", "yíshì", "ceremony"), vocab("文化遺產", "wénhuà yíchǎn", "cultural heritage")],
        "今天北京故宮博物院保存大量文物與建築。臺北的國立故宮博物院也收藏大量中國歷代文物，因此「故宮」在不同地方承載不同的近現代歷史。",
        ["建築可以怎麼表現政治權力？", "歷史建築變成博物館之後，它的功能有什麼改變？"],
        "紫禁城在近現代最大的功能轉變是什麼？", ["從皇宮成為博物院", "從港口成為機場", "從學校成為市場", "從寺廟成為工廠"], "從皇宮成為博物院"
    ),
    "modern-and-taiwan": lesson(
        "modern-and-taiwan", "level3", "Modern China & Taiwan", "🌏",
        "From Empire to the Modern Chinese-Speaking World", "從帝制到現代華語世界",
        "Build a careful timeline from the end of imperial rule to today's diverse Chinese-speaking communities.",
        "一九一一年革命之後，清朝在一九一二年結束，中國兩千多年的皇帝制度告一段落。二十世紀的中國與臺灣經歷戰爭、政治變化、經濟發展和人口移動，形成今天不同的社會。現代華語世界包含中國大陸、臺灣、香港、澳門、新加坡以及世界各地的華人社群，各地的歷史經驗、用語、文字習慣與文化都不完全相同。學習歷史可以幫助我們理解這些差異，而不是把所有華語社會看成完全一樣。",
        [vocab("帝制", "dìzhì", "imperial system"), vocab("革命", "gémìng", "revolution"), vocab("社會", "shèhuì", "society"), vocab("人口移動", "rénkǒu yídòng", "population movement"), vocab("華語世界", "Huáyǔ shìjiè", "Chinese-speaking world")],
        "今天不同華語地區可能使用繁體字或簡體字，也有不同口音、詞彙與文化習慣。PandaSpeak 使用繁體中文，學生也可以學會辨識華語世界的多樣性。",
        ["為什麼了解歷史有助於理解不同華語地區？", "你注意過臺灣、中國大陸、香港或新加坡使用的中文有哪些不同嗎？"],
        "這一課最重要的觀念是什麼？", ["所有華語社會完全一樣", "華語世界有共同點也有不同歷史經驗", "現代中文只有一種使用方式", "歷史和語言沒有關係"], "華語世界有共同點也有不同歷史經驗"
    ),
}


HISTORY_CARDS = [lesson for lesson in HISTORY_LESSONS.values()]
