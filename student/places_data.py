"""Content for the Famous Spots & Food Map (student dashboard).

Ten famous hotspots across China, Hong Kong, Taiwan and Macau. Each spot has
real photos (Wikimedia Commons, credited in PHOTO_CREDITS), place and food
vocabulary with BoPoMoFo + Pinyin, and a two-question quiz with four answer
choices per question. Open to all learning levels.
"""


def _v(chars, bopomofo, pinyin, english):
    return {'chars': chars, 'bopomofo': bopomofo, 'pinyin': pinyin, 'english': english}


def _q(question, choices, answer):
    return {'question': question, 'choices': choices, 'answer': answer}


SPOTS = [
    {
        'slug': 'beijing',
        'city': _v('北京', 'ㄅㄟˇ ㄐㄧㄥ', 'Běijīng', 'Beijing'),
        'region': 'Northern China',
        'region_zh': '華北',
        'landmark': _v('長城', 'ㄔㄤˊ ㄔㄥˊ', 'Chángchéng', 'the Great Wall'),
        'intro': 'The Great Wall winds for thousands of miles across the mountains of '
                 'northern China. Near Beijing you can climb its steep stone steps — '
                 'and afterwards sit down to the city\u2019s most famous dish.',
        'photo': 'great-wall.jpg',
        'food_photo': 'peking-duck.jpg',
        'place_vocab': [
            _v('長城', 'ㄔㄤˊ ㄔㄥˊ', 'Chángchéng', 'the Great Wall'),
            _v('爬山', 'ㄆㄚˊ ㄕㄢ', 'páshān', 'to climb a mountain'),
            _v('風景', 'ㄈㄥ ㄐㄧㄥˇ', 'fēngjǐng', 'scenery'),
        ],
        'food': _v('北京烤鴨', 'ㄅㄟˇ ㄐㄧㄥ ㄎㄠˇ ㄧㄚ', 'Běijīng kǎoyā', 'Peking duck'),
        'food_note': 'Crispy roast duck, sliced thin and wrapped in little pancakes '
                     'with spring onion and sweet sauce.',
        'food_vocab': [
            _v('烤鴨', 'ㄎㄠˇ ㄧㄚ', 'kǎoyā', 'roast duck'),
            _v('好吃', 'ㄏㄠˇ ㄔ', 'hǎochī', 'delicious'),
        ],
        'quiz': [
            _q('What does 長城 mean?',
               ['The Great Wall', 'The Forbidden City', 'A long river', 'Night market'], 0),
            _q('Which food is Beijing most famous for?',
               ['小籠包 Soup dumplings', '北京烤鴨 Peking duck', '火鍋 Hot pot', '點心 Dim sum'], 1),
        ],
        'pin': (71, 20),
    },
    {
        'slug': 'xian',
        'city': _v('西安', 'ㄒㄧ ㄢ', 'Xī\u2019ān', 'Xi\u2019an'),
        'region': 'Northwest China',
        'region_zh': '西北',
        'landmark': _v('兵馬俑', 'ㄅㄧㄥ ㄇㄚˇ ㄩㄥˇ', 'Bīngmǎyǒng', 'the Terracotta Army'),
        'intro': 'Thousands of life-size clay soldiers stand guard in Xi\u2019an. They were '
                 'made more than 2,000 years ago for Qin Shi Huang, the first emperor of China.',
        'photo': 'terracotta-army.jpg',
        'food_photo': 'roujiamo.jpg',
        'place_vocab': [
            _v('兵馬俑', 'ㄅㄧㄥ ㄇㄚˇ ㄩㄥˇ', 'Bīngmǎyǒng', 'the Terracotta Army'),
            _v('皇帝', 'ㄏㄨㄤˊ ㄉㄧˋ', 'huángdì', 'emperor'),
            _v('歷史', 'ㄌㄧˋ ㄕˇ', 'lìshǐ', 'history'),
        ],
        'food': _v('肉夾饃', 'ㄖㄡˋ ㄐㄧㄚ ㄇㄛˊ', 'ròujiāmó', 'roujiamo (meat bun)'),
        'food_note': 'Chopped seasoned meat tucked into a baked flatbread — often '
                     'called a Chinese hamburger.',
        'food_vocab': [
            _v('肉', 'ㄖㄡˋ', 'ròu', 'meat'),
            _v('吃', 'ㄔ', 'chī', 'to eat'),
        ],
        'quiz': [
            _q('The Terracotta Army was made for whom?',
               ['A famous poet', 'China\u2019s first emperor', 'A tea farmer', 'A panda keeper'], 1),
            _q('What does 肉 mean?',
               ['Fish', 'Rice', 'Meat', 'Tea'], 2),
        ],
        'pin': (59, 35),
    },
    {
        'slug': 'chengdu',
        'city': _v('成都', 'ㄔㄥˊ ㄉㄨ', 'Chéngdū', 'Chengdu'),
        'region': 'Southwest China',
        'region_zh': '西南',
        'landmark': _v('貓熊基地', 'ㄇㄠ ㄒㄩㄥˊ ㄐㄧ ㄉㄧˋ', 'Māoxióng Jīdì', 'the Panda Base'),
        'intro': 'Chengdu is the home of the giant panda. At the Panda Base you can watch '
                 'them munch bamboo all morning — then warm up with the city\u2019s famous '
                 'spicy hot pot.',
        'photo': 'panda-base.jpg',
        'food_photo': 'hotpot.jpg',
        'place_vocab': [
            _v('貓熊', 'ㄇㄠ ㄒㄩㄥˊ', 'māoxióng', 'giant panda'),
            _v('竹子', 'ㄓㄨˊ ㄗ˙', 'zhúzi', 'bamboo'),
            _v('可愛', 'ㄎㄜˇ ㄞˋ', 'kě\u2019ài', 'cute'),
        ],
        'food': _v('火鍋', 'ㄏㄨㄛˇ ㄍㄨㄛ', 'huǒguō', 'hot pot'),
        'food_note': 'A bubbling pot of spicy broth in the middle of the table — '
                     'everyone cooks their own meat and vegetables in it.',
        'food_vocab': [
            _v('火鍋', 'ㄏㄨㄛˇ ㄍㄨㄛ', 'huǒguō', 'hot pot'),
            _v('辣', 'ㄌㄚˋ', 'là', 'spicy'),
        ],
        'quiz': [
            _q('What do giant pandas love to eat?',
               ['Dumplings', 'Noodles', 'Bamboo', 'Tea'], 2),
            _q('Chengdu hot pot is famous for being…',
               ['Sweet', 'Spicy', 'Sour', 'Cold'], 1),
        ],
        'pin': (46, 46),
    },
    {
        'slug': 'shanghai',
        'city': _v('上海', 'ㄕㄤˋ ㄏㄞˇ', 'Shànghǎi', 'Shanghai'),
        'region': 'Eastern China',
        'region_zh': '華東',
        'landmark': _v('外灘', 'ㄨㄞˋ ㄊㄢ', 'Wàitān', 'the Bund'),
        'intro': 'The Bund is Shanghai\u2019s famous riverfront walk. Historic buildings '
                 'line one side of the Huangpu River, and glittering skyscrapers '
                 'rise on the other.',
        'photo': 'the-bund.jpg',
        'food_photo': 'xiaolongbao.jpg',
        'place_vocab': [
            _v('外灘', 'ㄨㄞˋ ㄊㄢ', 'Wàitān', 'the Bund'),
            _v('河', 'ㄏㄜˊ', 'hé', 'river'),
            _v('夜景', 'ㄧㄝˋ ㄐㄧㄥˇ', 'yèjǐng', 'night view'),
        ],
        'food': _v('小籠包', 'ㄒㄧㄠˇ ㄌㄨㄥˊ ㄅㄠ', 'xiǎolóngbāo', 'soup dumplings'),
        'food_note': 'Small steamed dumplings with a spoonful of hot soup inside — '
                     'bite a little hole first, sip, then eat.',
        'food_vocab': [
            _v('小籠包', 'ㄒㄧㄠˇ ㄌㄨㄥˊ ㄅㄠ', 'xiǎolóngbāo', 'soup dumplings'),
            _v('蒸', 'ㄓㄥ', 'zhēng', 'to steam'),
        ],
        'quiz': [
            _q('What is 小籠包?',
               ['Roast duck', 'Soup dumplings', 'Hot pot', 'Egg tart'], 1),
            _q('The Bund stands beside which river?',
               ['The Li River', 'The Huangpu River', 'Victoria Harbour', 'West Lake'], 1),
        ],
        'pin': (81, 41),
    },
    {
        'slug': 'hangzhou',
        'city': _v('杭州', 'ㄏㄤˊ ㄓㄡ', 'Hángzhōu', 'Hangzhou'),
        'region': 'Eastern China',
        'region_zh': '華東',
        'landmark': _v('西湖', 'ㄒㄧ ㄏㄨˊ', 'Xīhú', 'West Lake'),
        'intro': 'West Lake is Hangzhou\u2019s peaceful heart — pagodas, lotus flowers and '
                 'long causeways around calm water. The green hills nearby grow '
                 'China\u2019s most famous tea.',
        'photo': 'west-lake.jpg',
        'food_photo': 'longjing-tea.jpg',
        'place_vocab': [
            _v('西湖', 'ㄒㄧ ㄏㄨˊ', 'Xīhú', 'West Lake'),
            _v('湖', 'ㄏㄨˊ', 'hú', 'lake'),
            _v('船', 'ㄔㄨㄢˊ', 'chuán', 'boat'),
        ],
        'food': _v('龍井茶', 'ㄌㄨㄥˊ ㄐㄧㄥˇ ㄔㄚˊ', 'Lóngjǐng chá', 'Dragon Well tea'),
        'food_note': 'A smooth, fragrant green tea picked from the hills around '
                     'West Lake — Hangzhou\u2019s gift to tea lovers.',
        'food_vocab': [
            _v('茶', 'ㄔㄚˊ', 'chá', 'tea'),
            _v('喝', 'ㄏㄜ', 'hē', 'to drink'),
        ],
        'quiz': [
            _q('西湖 means…',
               ['East Sea', 'West Lake', 'North River', 'Long Well'], 1),
            _q('Longjing is a kind of…',
               ['Soup', 'Duck', 'Dumpling', 'Green tea'], 3),
        ],
        'pin': (77, 47),
    },
    {
        'slug': 'guilin',
        'city': _v('桂林', 'ㄍㄨㄟˋ ㄌㄧㄣˊ', 'Guìlín', 'Guilin'),
        'region': 'Southern China',
        'region_zh': '華南',
        'landmark': _v('漓江', 'ㄌㄧˊ ㄐㄧㄤ', 'Líjiāng', 'the Li River'),
        'intro': 'Guilin\u2019s scenery is famous across China: green karst peaks rise '
                 'beside the Li River while bamboo rafts drift slowly past. People '
                 'say Guilin\u2019s mountains and water are the finest under heaven.',
        'photo': 'li-river.jpg',
        'food_photo': 'guilin-noodles.jpg',
        'place_vocab': [
            _v('漓江', 'ㄌㄧˊ ㄐㄧㄤ', 'Líjiāng', 'the Li River'),
            _v('山水', 'ㄕㄢ ㄕㄨㄟˇ', 'shānshuǐ', 'mountain-and-water scenery'),
            _v('江', 'ㄐㄧㄤ', 'jiāng', 'river'),
        ],
        'food': _v('桂林米粉', 'ㄍㄨㄟˋ ㄌㄧㄣˊ ㄇㄧˇ ㄈㄣˇ', 'Guìlín mǐfěn', 'Guilin rice noodles'),
        'food_note': 'Silky rice noodles in a rich broth with crispy pork, peanuts '
                     'and spring onions — breakfast for half the city.',
        'food_vocab': [
            _v('米粉', 'ㄇㄧˇ ㄈㄣˇ', 'mǐfěn', 'rice noodles'),
            _v('湯', 'ㄊㄤ', 'tāng', 'soup / broth'),
        ],
        'quiz': [
            _q('The famous river in Guilin is the…',
               ['Li River', 'Huangpu River', 'Victoria Harbour', 'West Lake'], 0),
            _q('米粉 are noodles made from…',
               ['Wheat', 'Potato', 'Rice', 'Corn'], 2),
        ],
        'pin': (63, 61),
    },
    {
        'slug': 'hong-kong',
        'city': _v('香港', 'ㄒㄧㄤ ㄍㄤˇ', 'Xiānggǎng', 'Hong Kong'),
        'region': 'Hong Kong',
        'region_zh': '香港',
        'landmark': _v('維多利亞港', 'ㄨㄟˊ ㄉㄨㄛ ㄌㄧˋ ㄧㄚˋ ㄍㄤˇ',
                       'Wéiduōlìyà Gǎng', 'Victoria Harbour'),
        'intro': 'Victoria Harbour separates Hong Kong Island from Kowloon. Ride the '
                 'Star Ferry across the water and watch a thousand skyscrapers '
                 'light up at night.',
        'photo': 'victoria-harbour.jpg',
        'food_photo': 'dim-sum.jpg',
        'place_vocab': [
            _v('維多利亞港', 'ㄨㄟˊ ㄉㄨㄛ ㄌㄧˋ ㄧㄚˋ ㄍㄤˇ', 'Wéiduōlìyà Gǎng', 'Victoria Harbour'),
            _v('渡輪', 'ㄉㄨˋ ㄌㄨㄣˊ', 'dùlún', 'ferry'),
            _v('高樓', 'ㄍㄠ ㄌㄡˊ', 'gāolóu', 'tall building'),
        ],
        'food': _v('點心', 'ㄉㄧㄢˇ ㄒㄧㄣ', 'diǎnxīn', 'dim sum'),
        'food_note': 'Bite-size dishes served in little bamboo steamers with tea — '
                     'shrimp dumplings, siu mai and soft rice rolls.',
        'food_vocab': [
            _v('點心', 'ㄉㄧㄢˇ ㄒㄧㄣ', 'diǎnxīn', 'dim sum'),
            _v('蝦餃', 'ㄒㄧㄚ ㄐㄧㄠˇ', 'xiājiǎo', 'shrimp dumplings'),
        ],
        'quiz': [
            _q('點心 (dim sum) is…',
               ['A big roast duck', 'Small dishes served with tea', 'A spicy soup', 'A sweet drink'], 1),
            _q('You can cross Victoria Harbour by…',
               ['Bamboo raft', 'Panda bus', 'Star Ferry', 'Night train'], 2),
        ],
        'pin': (69, 73),
    },
    {
        'slug': 'macau',
        'city': _v('澳門', 'ㄠˋ ㄇㄣˊ', 'Àomén', 'Macau'),
        'region': 'Macau',
        'region_zh': '澳門',
        'landmark': _v('大三巴牌坊', 'ㄉㄚˋ ㄙㄢ ㄅㄚ ㄆㄞˊ ㄈㄤ', 'Dàsānbā Páifāng',
                       'the Ruins of St. Paul\u2019s'),
        'intro': 'The Ruins of St. Paul\u2019s are Macau\u2019s most famous landmark — the '
                 'stone front of a church built 400 years ago. The lanes below mix '
                 'Chinese and Portuguese flavors.',
        'photo': 'st-pauls.jpg',
        'food_photo': 'egg-tart.jpg',
        'place_vocab': [
            _v('大三巴牌坊', 'ㄉㄚˋ ㄙㄢ ㄅㄚ ㄆㄞˊ ㄈㄤ', 'Dàsānbā Páifāng', 'the Ruins of St. Paul\u2019s'),
            _v('教堂', 'ㄐㄧㄠˋ ㄊㄤˊ', 'jiàotáng', 'church'),
            _v('老街', 'ㄌㄠˇ ㄐㄧㄝ', 'lǎojiē', 'old street'),
        ],
        'food': _v('葡式蛋撻', 'ㄆㄨˊ ㄕˋ ㄉㄢˋ ㄊㄚˋ', 'Púshì dàntà', 'Portuguese egg tart'),
        'food_note': 'A warm custard tart with a flaky crust and a caramel-spotted '
                     'top — Macau\u2019s favorite snack.',
        'food_vocab': [
            _v('蛋撻', 'ㄉㄢˋ ㄊㄚˋ', 'dàntà', 'egg tart'),
            _v('甜', 'ㄊㄧㄢˊ', 'tián', 'sweet'),
        ],
        'quiz': [
            _q('The Ruins of St. Paul\u2019s were part of a…',
               ['Palace', 'Market', 'Tea house', 'Church'], 3),
            _q('蛋撻 is a…',
               ['Spicy noodle', 'Meat bun', 'Sweet egg tart', 'Green tea'], 2),
        ],
        'pin': (64, 78),
    },
    {
        'slug': 'taipei-101',
        'city': _v('台北', 'ㄊㄞˊ ㄅㄟˇ', 'Táiběi', 'Taipei'),
        'region': 'Taiwan',
        'region_zh': '台灣',
        'landmark': _v('台北101', 'ㄊㄞˊ ㄅㄟˇ ㄧ ㄌㄧㄥˊ ㄧ', 'Táiběi Yīlíngyī', 'Taipei 101'),
        'intro': 'Taipei 101 was once the tallest building in the world. It is shaped '
                 'like a bamboo stalk, and on New Year\u2019s Eve fireworks burst '
                 'from its sides.',
        'photo': 'taipei-101.jpg',
        'food_photo': 'beef-noodle-soup.jpg',
        'place_vocab': [
            _v('台北101', 'ㄊㄞˊ ㄅㄟˇ ㄧ ㄌㄧㄥˊ ㄧ', 'Táiběi Yīlíngyī', 'Taipei 101'),
            _v('高', 'ㄍㄠ', 'gāo', 'tall'),
            _v('煙火', 'ㄧㄢ ㄏㄨㄛˇ', 'yānhuǒ', 'fireworks'),
        ],
        'food': _v('牛肉麵', 'ㄋㄧㄡˊ ㄖㄡˋ ㄇㄧㄢˋ', 'niúròu miàn', 'beef noodle soup'),
        'food_note': 'Tender beef and chewy noodles in a deep, savory broth — '
                     'Taiwan\u2019s most loved bowl.',
        'food_vocab': [
            _v('牛肉', 'ㄋㄧㄡˊ ㄖㄡˋ', 'niúròu', 'beef'),
            _v('麵', 'ㄇㄧㄢˋ', 'miàn', 'noodles'),
        ],
        'quiz': [
            _q('Taipei 101 is shaped like which plant?',
               ['Lotus', 'Bamboo', 'Pine tree', 'Plum blossom'], 1),
            _q('牛肉麵 is…',
               ['Duck soup', 'Rice noodles', 'Beef noodle soup', 'Dumplings'], 2),
        ],
        'pin': (83, 68),
    },
    {
        'slug': 'shilin',
        'city': _v('台北', 'ㄊㄞˊ ㄅㄟˇ', 'Táiběi', 'Taipei'),
        'region': 'Taiwan',
        'region_zh': '台灣',
        'landmark': _v('士林夜市', 'ㄕˋ ㄌㄧㄣˊ ㄧㄝˋ ㄕˋ', 'Shìlín Yèshì', 'Shilin Night Market'),
        'intro': 'When the sun goes down, Taipei\u2019s night markets light up. Shilin is '
                 'the most famous of all — rows of sizzling food stalls, games and '
                 'crowds of hungry visitors.',
        'photo': 'shilin-night-market.jpg',
        'food_photo': 'bubble-tea.jpg',
        'place_vocab': [
            _v('夜市', 'ㄧㄝˋ ㄕˋ', 'yèshì', 'night market'),
            _v('士林', 'ㄕˋ ㄌㄧㄣˊ', 'Shìlín', 'Shilin'),
            _v('小吃', 'ㄒㄧㄠˇ ㄔ', 'xiǎochī', 'snacks / street food'),
        ],
        'food': _v('珍珠奶茶', 'ㄓㄣ ㄓㄨ ㄋㄞˇ ㄔㄚˊ', 'zhēnzhū nǎichá', 'bubble tea'),
        'food_note': 'Sweet milk tea with chewy tapioca pearls, sipped through a '
                     'fat straw — Taiwan\u2019s gift to the world.',
        'food_vocab': [
            _v('珍珠', 'ㄓㄣ ㄓㄨ', 'zhēnzhū', 'pearls (tapioca pearls)'),
            _v('奶茶', 'ㄋㄞˇ ㄔㄚˊ', 'nǎichá', 'milk tea'),
        ],
        'quiz': [
            _q('夜市 means…',
               ['Night school', 'Night train', 'Night market', 'Night river'], 2),
            _q('The chewy pearls in bubble tea are made from…',
               ['Rice', 'Tapioca', 'Beans', 'Tea leaves'], 1),
        ],
        'pin': (87, 60),
    },
]

# Photo credits (Wikimedia Commons). Keyed by image file name.
PHOTO_CREDITS = {
    'great-wall.jpg': 'Severin.stalder, CC BY-SA 3.0',
    'peking-duck.jpg': 'City Foodsters, CC BY 2.0',
    'terracotta-army.jpg': 'xiquinhosilva, CC BY 2.0',
    'roujiamo.jpg': 'Gary Soup, CC BY 2.0',
    'panda-base.jpg': 'Hyjk2000, CC BY-SA 3.0',
    'hotpot.jpg': 'Praneeth Thalla, CC BY-SA 4.0',
    'the-bund.jpg': '钉钉, CC BY-SA 4.0',
    'xiaolongbao.jpg': 'Peachyeung316, CC BY-SA 4.0',
    'west-lake.jpg': 'Takashishin, CC BY 4.0',
    'longjing-tea.jpg': 'Difference engine, CC BY-SA 4.0',
    'li-river.jpg': 'xiquinhosilva, CC BY 2.0',
    'guilin-noodles.jpg': 'Popo le Chien, CC0',
    'victoria-harbour.jpg': 'Base64 / CarolSpears, CC BY-SA 3.0',
    'dim-sum.jpg': 'LeonardKong, CC BY 2.0',
    'st-pauls.jpg': 'Inaki.alegria, CC BY-SA 4.0',
    'egg-tart.jpg': 'Mon Œil, CC BY 2.0',
    'taipei-101.jpg': 'CEphoto, Uwe Aranas, CC BY-SA 3.0',
    'beef-noodle-soup.jpg': 'Jjj84206, CC BY-SA 4.0',
    'shilin-night-market.jpg': 'Public domain',
    'bubble-tea.jpg': 'SuperMidget, Public domain',
}
