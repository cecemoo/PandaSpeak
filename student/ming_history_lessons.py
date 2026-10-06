def vocab(word, pinyin, meaning):
    return {'word': word, 'pinyin': pinyin, 'meaning': meaning}


PASSAGES = {
    'jingnan-campaign': '明太祖朱元璋去世後，皇太孫朱允炆即位，是為建文帝。建文帝推行削藩，引起燕王朱棣反抗。公元1399年，朱棣以「靖難」為名起兵，經過數年戰爭攻入南京。建文帝下落成謎，朱棣即位，是為明成祖永樂帝。',
    'yongle-moves-capital-beijing': '永樂帝朱棣即位後，加強北京的政治與軍事地位。公元1421年，明朝正式遷都北京。此後北京長期成為明清兩代的政治中心，對中國後來的城市與政治格局影響深遠。',
    'forbidden-city-built': '永樂年間，明朝大規模營建北京宮城。公元1420年前後，紫禁城基本建成，成為明清皇帝居住和處理政務的核心場所。它的宮殿布局與建築制度成為中國古代宮殿建築的重要代表。',
    'zheng-he': '公元1405年至1433年間，鄭和率領大型船隊七次遠航，前往東南亞、南亞、阿拉伯半島與東非一帶。船隊進行外交、貿易與交流活動。鄭和下西洋是明代最著名的海上活動之一，也反映當時中國與印度洋世界的廣泛聯繫。',
    'tumu-crisis': '公元1449年，明英宗在宦官王振影響下親征瓦剌。明軍在土木堡遭到重大失敗，英宗本人被俘，史稱「土木堡之變」。北京隨即面臨嚴重威脅，明朝政局也因此發生巨大震動。',
    'yu-qian-defends-beijing': '土木堡之變後，瓦剌軍逼近北京。大臣于謙主張堅守京城，反對南遷，並組織軍民防禦。北京保衛戰最終成功穩住局勢，于謙也因此成為明代著名的忠臣與民族英雄人物。',
    'duomen-coup': '明英宗被瓦剌釋放回國後，弟弟明代宗仍在位。公元1457年，石亨、徐有貞等人迎英宗復位，史稱「奪門之變」。英宗重新掌權後，于謙遭到處死，成為明代政治史上的著名事件。',
    'wang-yangming-longchang': '王陽明被貶到貴州龍場後，在艱苦環境中反思儒學與人生問題。後世常以「龍場悟道」概括他思想上的重要轉折。他提出「心即理」「知行合一」等思想，對明代及東亞思想史影響深遠。',
    'qi-jiguang-fights-wokou': '明朝中期，東南沿海長期受到倭寇侵擾。將領戚繼光訓練「戚家軍」，改進戰術，在浙江、福建等地多次作戰，逐步平定嚴重的倭患。戚繼光抗倭成為明代最著名的軍事故事之一。',
    'hai-rui-memorial': '海瑞以清廉和敢於直言著稱。嘉靖年間，他上疏批評皇帝長期不上朝、迷信方術並忽視政務，因此被捕入獄。海瑞冒死進諫的故事，使他成為中國歷史上著名的清官形象。',
    'zhang-juzheng-reforms': '萬曆初年，張居正主持朝政，推行整頓吏治、清查土地與改革賦役等措施。他的改革一度改善明朝財政與行政效率，但也引起強烈政治爭議。張居正改革是理解明代中後期政治的重要事件。',
    'li-shizhen-bencao': '明代醫藥學家李時珍花費多年整理藥物知識並實地考察，完成《本草綱目》。書中記錄大量藥物、性質與用途，是中國傳統醫藥史上的重要著作，也使李時珍成為家喻戶曉的歷史人物。',
    'xu-xiake-travels': '徐霞客一生遊歷中國許多地區，仔細記錄山川、地貌、河流與旅行見聞。他的文字後來整理為《徐霞客遊記》。這部作品兼具文學與地理觀察價值，是明代旅行與地理研究的代表。',
    'wei-zhongxian-power': '明朝末年，宦官魏忠賢權勢極盛，依靠宮廷勢力排斥反對者，與東林黨人的政治衝突尤其激烈。崇禎帝即位後清算魏忠賢勢力。這段歷史常被視為晚明政治腐敗與黨爭的象徵之一。',
    'yuan-chonghuan-ningyuan': '明末後金勢力崛起，遼東戰事日益激烈。將領袁崇煥守衛寧遠，曾以城防與火炮抵抗後金軍。後來他遭崇禎帝猜疑並被處死，其功過與冤屈成為明末歷史中長期受到討論的故事。',
    'li-zicheng-rebellion': '明朝末年天災、賦役與社會矛盾加劇，各地爆發大規模起義。李自成率領的農民軍迅速壯大，提出「闖王」旗號，最終向北京進軍，成為直接動搖明朝統治的重要力量。',
    'li-zicheng-enters-beijing': '公元1644年，李自成率軍攻入北京，明朝中央政權迅速崩潰。這一事件標誌著明朝在北京的統治走到終點，也使中國政局進入明清鼎革的劇烈轉折。',
    'chongzhen-meishan': '李自成軍攻入北京時，崇禎帝朱由檢離開紫禁城，最後在煤山自縊。崇禎之死通常被視為明朝中央政權滅亡的象徵。按照朝代故事的分類，這個明朝滅亡故事屬於明朝。',
}


def lesson(slug, level, icon, title, chinese_title, intro):
    return {
        'slug': slug, 'level': level, 'era': 'Ming Dynasty', 'icon': icon,
        'title': title, 'chinese_title': chinese_title, 'intro': intro,
        'passage': PASSAGES[slug],
        'vocabulary': [vocab('明朝', 'Míng cháo', 'Ming Dynasty'), vocab('歷史', 'lì shǐ', 'history'), vocab('故事', 'gù shì', 'story')],
        'today': 'This is one of the widely recognized stories, people, or events associated with the Ming Dynasty.',
        'speak_prompts': ['請用中文簡單說明這個故事。', '你認為這個故事為什麼重要？'],
        'quiz': {'question': '這個故事主要與哪一個歷史時期有關？', 'choices': ['宋朝', '元朝', '明朝', '清朝'], 'answer': '明朝'},
    }


MING_HISTORY_LESSONS = {
    'jingnan-campaign': lesson('jingnan-campaign', 'level3', '⚔️', 'The Jingnan Campaign', '靖難之役', '朱棣起兵奪取帝位，成為永樂帝。'),
    'yongle-moves-capital-beijing': lesson('yongle-moves-capital-beijing', 'level2', '🏯', 'The Yongle Emperor Moves the Capital to Beijing', '永樂遷都北京', '北京成為明朝的政治中心。'),
    'forbidden-city-built': lesson('forbidden-city-built', 'level2', '🏛️', 'The Forbidden City Is Built', '紫禁城建成', '明清皇宮與中國古代宮殿建築的代表。'),
    'zheng-he': lesson('zheng-he', 'level2', '⛵', 'Zheng He’s Voyages', '鄭和下西洋', '七次遠航與明代海上交流的著名故事。'),
    'tumu-crisis': lesson('tumu-crisis', 'level3', '🏹', 'The Tumu Crisis', '土木堡之變', '明英宗被俘，明朝遭遇重大軍事危機。'),
    'yu-qian-defends-beijing': lesson('yu-qian-defends-beijing', 'level2', '🛡️', 'Yu Qian Defends Beijing', '于謙保衛北京', '土木堡之變後力主守城的著名故事。'),
    'duomen-coup': lesson('duomen-coup', 'level3', '🚪', 'The Duomen Coup', '奪門之變', '明英宗復位與于謙遇害的政治轉折。'),
    'wang-yangming-longchang': lesson('wang-yangming-longchang', 'level3', '💡', 'Wang Yangming’s Enlightenment at Longchang', '王陽明龍場悟道', '王陽明思想形成的重要傳說與轉折。'),
    'qi-jiguang-fights-wokou': lesson('qi-jiguang-fights-wokou', 'level2', '⚔️', 'Qi Jiguang Fights the Wokou', '戚繼光抗倭', '戚家軍平定東南沿海倭患的著名故事。'),
    'hai-rui-memorial': lesson('hai-rui-memorial', 'level2', '📜', 'Hai Rui Risks His Life to Remonstrate', '海瑞冒死進諫', '清官海瑞直言批評嘉靖帝的故事。'),
    'zhang-juzheng-reforms': lesson('zhang-juzheng-reforms', 'level3', '📊', 'Zhang Juzheng’s Reforms', '張居正改革', '萬曆初年重要的政治與財政改革。'),
    'li-shizhen-bencao': lesson('li-shizhen-bencao', 'level2', '🌿', 'Li Shizhen Writes the Compendium of Materia Medica', '李時珍與《本草綱目》', '明代最著名的醫藥學成就之一。'),
    'xu-xiake-travels': lesson('xu-xiake-travels', 'level2', '🗺️', 'The Travels of Xu Xiake', '徐霞客遊記', '旅行、地理觀察與文學結合的著名作品。'),
    'wei-zhongxian-power': lesson('wei-zhongxian-power', 'level3', '🏚️', 'The Rise and Fall of Wei Zhongxian', '魏忠賢專權', '晚明宦官政治與黨爭的代表事件。'),
    'yuan-chonghuan-ningyuan': lesson('yuan-chonghuan-ningyuan', 'level3', '🏰', 'Yuan Chonghuan Defends Ningyuan', '袁崇煥守寧遠', '明末遼東戰爭中的著名將領與爭議故事。'),
    'li-zicheng-rebellion': lesson('li-zicheng-rebellion', 'level3', '🚩', 'Li Zicheng’s Rebellion', '李自成起義', '明末大規模農民起義與王朝危機。'),
    'li-zicheng-enters-beijing': lesson('li-zicheng-enters-beijing', 'level2', '🏙️', 'Li Zicheng Enters Beijing', '李自成攻入北京', '公元1644年明朝中央政權迅速崩潰。'),
    'chongzhen-meishan': lesson('chongzhen-meishan', 'level2', '🌳', 'The Chongzhen Emperor Dies at Meishan', '崇禎煤山自縊・明朝滅亡', '明朝中央政權滅亡的象徵性事件。'),
}

MING_CARDS = list(MING_HISTORY_LESSONS.values())
