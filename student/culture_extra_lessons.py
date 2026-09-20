"""Additional PandaSpeak Cultural Insights.

Keep new lessons here so the core culture view stays manageable. StudentConfig.ready()
merges these cards and lessons into the shared cultural catalog at startup.
"""


def S(icon, title, text):
    return {'icon': icon, 'title': title, 'text': text}


def V(word, pinyin, meaning):
    return {'word': word, 'pinyin': pinyin, 'meaning': meaning}


def E(chinese, pinyin, english):
    return {'chinese': chinese, 'pinyin': pinyin, 'english': english}


def L(level, category, art, cn, title, intro, sections, vocab, example, fact, question, choices, answer):
    return {'level': level, 'category': category, 'art': art, 'chinese_title': cn, 'title': title,
            'intro': intro, 'sections': sections, 'vocabulary': vocab, 'example': example,
            'did_you_know': fact, 'quiz': {'question': question, 'choices': choices, 'answer': answer}}


EXTRA_CARDS = [
    {'slug':'visiting-home','level':'level2','category':'daily','chinese_title':'作客禮儀','title':'Visiting Someone’s Home','summary':'Learn polite customs for visiting friends and families.','art':'🏠','theme':'tea'},
    {'slug':'birthday-customs','level':'level2','category':'festival','chinese_title':'生日習俗','title':'Birthday Customs','summary':'Explore birthday wishes, foods, and changing traditions.','art':'🎂','theme':'gift'},
    {'slug':'chinese-zodiac','level':'level2','category':'festival','chinese_title':'十二生肖','title':'Chinese Zodiac','summary':'Discover the twelve zodiac animals and their cultural role.','art':'🐲','theme':'festival'},
    {'slug':'colors-symbolism','level':'level2','category':'society','chinese_title':'顏色與象徵','title':'Colors & Symbolism','summary':'See how colors can carry different cultural associations.','art':'🎨','theme':'lucky'},
    {'slug':'personal-space-politeness','level':'level2','category':'daily','chinese_title':'禮貌與人際距離','title':'Personal Space & Politeness','summary':'Understand everyday courtesy and interpersonal boundaries.','art':'🙋','theme':'family'},
    {'slug':'wedding-customs','level':'level2','category':'festival','chinese_title':'婚禮習俗','title':'Wedding Customs','summary':'Explore wedding symbols, family traditions, and modern celebrations.','art':'💒','theme':'red'},
    {'slug':'face-mianzi','level':'level3','category':'society','chinese_title':'面子文化','title':'Face (面子)','summary':'Understand dignity, reputation, and sensitivity in social interaction.','art':'🎭','theme':'language'},
    {'slug':'guanxi','level':'level3','category':'society','chinese_title':'關係與人情','title':'Guanxi (關係)','summary':'Explore relationships, trust, reciprocity, and social networks.','art':'🤝','theme':'work'},
    {'slug':'generational-differences','level':'level3','category':'modern','chinese_title':'世代差異','title':'Generational Differences','summary':'Compare changing values, lifestyles, and communication across generations.','art':'👵👩','theme':'modern'},
    {'slug':'regional-food-culture','level':'level3','category':'food','chinese_title':'地方飲食文化','title':'Regional Food Culture','summary':'Explore how geography and history shape regional food traditions.','art':'🍜','theme':'food'},
    {'slug':'humor-wordplay','level':'level3','category':'language','chinese_title':'幽默與文字遊戲','title':'Humor & Wordplay','summary':'Discover puns, homophones, internet humor, and playful language.','art':'😄','theme':'language'},
    {'slug':'digital-culture','level':'level3','category':'modern','chinese_title':'社群媒體與數位文化','title':'Social Media & Digital Culture','summary':'Explore how digital life shapes communication and contemporary culture.','art':'📱','theme':'modern'},
]


EXTRA_LESSONS = {
'visiting-home': L('level2','Daily Life & Etiquette','🏠','作客禮儀','Visiting Someone’s Home','Visiting a home is a chance to show warmth, consideration, and respect for the host.',[
 S('⏰','Arriving thoughtfully','Arriving around the agreed time is considerate. If plans change, sending a message helps the host prepare.'),
 S('🎁','A small host gift','Fruit, snacks, tea, or another modest gift may be appreciated, especially for a first visit or special occasion.'),
 S('👟','Follow the household','Some homes expect guests to remove shoes and may provide slippers. Watch what the host does or simply ask.'),
 S('🍵','Accepting hospitality','Hosts may offer tea, fruit, or food. Accepting a little can acknowledge their hospitality, while a polite refusal is also fine when necessary.')],
 [V('作客','zuòkè','to visit as a guest'),V('請進','qǐng jìn','please come in'),V('拖鞋','tuōxié','slippers'),V('招待','zhāodài','to host; entertain'),V('打擾了','dǎrǎo le','sorry to bother you')],E('謝謝你的招待。','Xièxie nǐ de zhāodài.','Thank you for your hospitality.'),'Home customs vary greatly by family and region, so observing and asking politely is often the best guide.','What is a good approach when you are unsure whether to remove your shoes?',[('a','Ignore the host'),('b','Observe or politely ask'),('c','Always keep them on'),('d','Leave immediately')],'b'),

'birthday-customs': L('level2','Festivals & Traditions','🎂','生日習俗','Birthday Customs','Birthday celebrations combine family traditions with many modern international customs.',[
 S('🎂','Modern celebrations','Birthday cakes, candles, restaurants, and gatherings with friends are common in many Chinese-speaking communities today.'),
 S('🍜','Long-life noodles','In some families, 長壽麵 or long noodles symbolize longevity. The custom is especially associated with wishing someone a long life.'),
 S('🧧','Gifts and wishes','Family members may give gifts or red envelopes. The style of celebration depends on age, family, and region.'),
 S('👵','Milestone birthdays','Certain birthdays may receive special attention, particularly for older family members, when longevity and family gathering become central themes.')],
 [V('生日','shēngrì','birthday'),V('生日快樂','shēngrì kuàilè','Happy Birthday'),V('長壽','chángshòu','longevity'),V('蛋糕','dàngāo','cake'),V('許願','xǔyuàn','make a wish')],E('祝你生日快樂，健康長壽！','Zhù nǐ shēngrì kuàilè, jiànkāng chángshòu!','Happy birthday; wishing you health and longevity!'),'Long noodles can symbolize a long life, but birthday traditions are not identical in every family.','What can long noodles symbolize at a birthday?',[('a','Travel'),('b','Longevity'),('c','Wealth only'),('d','A new job')],'b'),

'chinese-zodiac': L('level2','Festivals & Traditions','🐲','十二生肖','Chinese Zodiac','The Chinese zodiac connects each year in a repeating twelve-year cycle with an animal sign.',[
 S('🐭','Twelve animals','The cycle is Rat, Ox, Tiger, Rabbit, Dragon, Snake, Horse, Goat, Monkey, Rooster, Dog, and Pig.'),
 S('📅','Based on the lunar calendar','A zodiac year changes around Lunar New Year rather than January 1, so people born in January or February may need to check the exact date.'),
 S('🧧','Your zodiac year','本命年 refers to a year matching one’s own zodiac animal. Popular customs surrounding it vary among communities.'),
 S('🧠','Culture, not destiny','Zodiac signs are common in conversation and festive culture, but people differ widely in how seriously they interpret personality or fortune claims.')],
 [V('生肖','shēngxiào','Chinese zodiac'),V('屬','shǔ','to belong to a zodiac sign'),V('龍','lóng','dragon'),V('本命年','běnmìngnián','one’s zodiac year'),V('農曆','nónglì','traditional lunar calendar')],E('你屬什麼？','Nǐ shǔ shénme?','What is your Chinese zodiac sign?'),'Because Lunar New Year does not fall on January 1, Western birth year alone can be insufficient for January or February birthdays.','How many animals are in the Chinese zodiac cycle?',[('a','8'),('b','10'),('c','12'),('d','24')],'c'),

'colors-symbolism': L('level2','Society & Relationships','🎨','顏色與象徵','Colors & Symbolism','Colors can carry cultural associations, but meaning depends strongly on occasion and context.',[
 S('🔴','Red','Red is strongly associated with celebration, good fortune, weddings, and Lunar New Year.'),
 S('⚪','White','White can be associated with mourning and funerals in traditional contexts, although it is also an ordinary everyday color.'),
 S('🟡','Gold and yellow','Gold often suggests prosperity or prestige. Yellow has many historical and modern associations and should not be reduced to one meaning.'),
 S('🌈','Context matters','Fashion, branding, age, and personal taste constantly reshape color meanings. Symbolism is a cultural clue, not a rigid rule.')],
 [V('顏色','yánsè','color'),V('紅色','hóngsè','red'),V('白色','báisè','white'),V('金色','jīnsè','gold'),V('象徵','xiàngzhēng','symbolize')],E('紅色常常代表喜慶。','Hóngsè chángcháng dàibiǎo xǐqìng.','Red often represents celebration.'),'The same color can carry very different meanings depending on whether the setting is a wedding, funeral, fashion store, or everyday home.','Which color is especially associated with celebration and good fortune?',[('a','Red'),('b','Gray'),('c','Brown'),('d','Purple only')],'a'),

'personal-space-politeness': L('level2','Daily Life & Etiquette','🙋','禮貌與人際距離','Personal Space & Politeness','Politeness is expressed through words, tone, behavior, and sensitivity to the relationship.',[
 S('🙏','Polite language','請, 謝謝, 不好意思, and 麻煩你 are useful ways to soften requests and show consideration.'),
 S('👥','Physical distance','Comfort with personal space varies by person and situation. Crowded public settings can also create different expectations than private conversation.'),
 S('💬','Questions and familiarity','Questions about age, family, work, or relationships may feel more ordinary in some contexts, but learners should notice the individual’s comfort level.'),
 S('🌏','Avoid assumptions','There is no single Chinese rule for politeness. Region, generation, personality, and relationship all matter.')],
 [V('禮貌','lǐmào','polite; manners'),V('不好意思','bù hǎoyìsi','excuse me; sorry'),V('麻煩你','máfan nǐ','may I trouble you'),V('請','qǐng','please'),V('尊重','zūnzhòng','respect')],E('不好意思，麻煩你了。','Bù hǎoyìsi, máfan nǐ le.','Sorry to trouble you / Thank you for your trouble.'),'Tone and context can make the same sentence sound warm, neutral, or intrusive.','What is the best principle for personal boundaries?',[('a','Assume everyone is the same'),('b','Pay attention to the person and context'),('c','Never ask questions'),('d','Always stand very close')],'b'),

'wedding-customs': L('level2','Festivals & Traditions','💒','婚禮習俗','Wedding Customs','Weddings often blend family traditions, auspicious symbolism, and contemporary styles.',[
 S('❤️','Red and celebration','Red is traditionally prominent because it symbolizes joy and good fortune, though modern couples use many styles and colors.'),
 S('🍵','Tea ceremonies','Some families include a tea ceremony in which the couple serves tea to parents or elders as an expression of respect and family connection.'),
 S('🧧','Wedding gifts','Guests may give red envelopes rather than boxed gifts. Amounts and expectations depend on local custom and relationship.'),
 S('🌏','Many different weddings','Practices differ across Taiwan, Mainland China, Hong Kong, overseas communities, regions, religions, and individual families.')],
 [V('婚禮','hūnlǐ','wedding'),V('結婚','jiéhūn','get married'),V('新郎','xīnláng','groom'),V('新娘','xīnniáng','bride'),V('喜宴','xǐyàn','wedding banquet')],E('祝你們新婚快樂！','Zhù nǐmen xīnhūn kuàilè!','Wishing you a happy marriage!'),'Many contemporary weddings combine local traditions with international elements such as white wedding dresses and Western-style ceremonies.','What may a wedding tea ceremony express?',[('a','Respect for parents and elders'),('b','A business negotiation'),('c','A sports competition'),('d','A travel plan')],'a'),

'face-mianzi': L('level3','Society & Relationships','🎭','面子文化','Face (面子)','面子 refers broadly to social dignity, reputation, and the respect a person receives from others.',[
 S('🎭','Social dignity','Giving someone face can mean recognizing their status, contribution, or dignity in front of others.'),
 S('💬','Handling disagreement','In some situations, criticizing someone publicly can feel more damaging than discussing the same issue privately.'),
 S('🤝','Not uniquely Chinese','Concern for reputation exists everywhere. 面子 is useful because it gives learners vocabulary for discussing how reputation can shape interaction.'),
 S('⚖️','Context and personality','Directness varies enormously. Do not use “face” to assume that every Chinese speaker avoids disagreement or criticism.')],
 [V('面子','miànzi','face; social dignity'),V('丟臉','diūliǎn','lose face; be embarrassed'),V('尊重','zūnzhòng','respect'),V('名聲','míngshēng','reputation'),V('尷尬','gāngà','awkward; embarrassed')],E('我們私下談比較好。','Wǒmen sīxià tán bǐjiào hǎo.','It would be better for us to discuss it privately.'),'The English expression “saving face” is closely related to concepts that appear in many cultures, not only Chinese-speaking ones.','Which action may help protect someone’s 面子 in a sensitive disagreement?',[('a','Publicly embarrassing them'),('b','Discussing the issue privately'),('c','Posting it online'),('d','Ignoring all problems forever')],'b'),

'guanxi': L('level3','Society & Relationships','🤝','關係與人情','Guanxi (關係)','關係 can simply mean “relationship,” but cultural discussions often use it for networks of trust, familiarity, and reciprocal support.',[
 S('🔗','Relationships matter','Repeated interaction can build trust and make cooperation easier in social and professional life.'),
 S('🎁','Reciprocity','人情 can describe human feelings, favors, or social obligations. Returning kindness appropriately can help maintain a relationship.'),
 S('⚖️','Not the same as corruption','Healthy relationship-building is different from bribery or improper favoritism. Ethical and legal boundaries still matter.'),
 S('🌱','Built over time','Genuine relationships usually grow through reliability, mutual help, communication, and shared experience rather than one transaction.')],
 [V('關係','guānxì','relationship; connection'),V('人情','rénqíng','favor; human feeling; social obligation'),V('信任','xìnrèn','trust'),V('幫忙','bāngmáng','help'),V('互相','hùxiāng','mutually')],E('我們互相幫忙。','Wǒmen hùxiāng bāngmáng.','We help each other.'),'關係 is an everyday Chinese word with many meanings; the special English-language idea of “guanxi” represents only part of its usage.','What is a healthy foundation for long-term 關係?',[('a','Trust and reciprocity'),('b','One expensive gift'),('c','Avoiding communication'),('d','Breaking promises')],'a'),

'generational-differences': L('level3','Modern Culture','👵👩','世代差異','Generational Differences','Rapid social, economic, and technological change has shaped different experiences across generations.',[
 S('📱','Technology','Younger generations often grew up with smartphones, social media, and online services, while older generations experienced a very different communication environment.'),
 S('🏠','Family expectations','Ideas about marriage, careers, living with parents, and caregiving continue to evolve and can create negotiation within families.'),
 S('💼','Work and lifestyle','Attitudes toward job stability, work-life balance, consumption, and mobility vary within as well as between generations.'),
 S('🧠','No generation is uniform','Age is only one influence. Education, region, class, family, and personality can be equally important.')],
 [V('世代','shìdài','generation'),V('年輕人','niánqīngrén','young people'),V('長輩','zhǎngbèi','elder; senior family member'),V('觀念','guānniàn','idea; concept'),V('改變','gǎibiàn','change')],E('不同世代的觀念可能不一樣。','Bùtóng shìdài de guānniàn kěnéng bù yíyàng.','Different generations may have different ideas.'),'Many families negotiate old expectations and new lifestyles rather than simply choosing one or the other.','What is the best way to understand generational differences?',[('a','Assume everyone of one age thinks alike'),('b','Notice trends while allowing individual variation'),('c','Ignore social change'),('d','Use stereotypes')],'b'),

'regional-food-culture': L('level3','Food & Dining','🍜','地方飲食文化','Regional Food Culture','Chinese food is not one cuisine; geography, migration, climate, history, and local ingredients create enormous regional diversity.',[
 S('🗺️','Regional traditions','Sichuan, Cantonese, Jiangsu, Fujian, Taiwanese, Hakka, northern wheat-based traditions, and many others have distinctive histories and flavors.'),
 S('🌶️','Flavor and climate','Spice, preservation methods, staple grains, seafood, and cooking techniques often reflect local environment and historical trade.'),
 S('🥟','Staples differ','Rice is central in many southern areas, while wheat foods such as noodles, dumplings, and buns have deep roots in many northern regions.'),
 S('✈️','Food travels','Migration creates new versions of dishes abroad and across regions. “Authentic” food can therefore have more than one legitimate form.')],
 [V('地方菜','dìfāngcài','regional cuisine'),V('口味','kǒuwèi','flavor; taste'),V('米飯','mǐfàn','cooked rice'),V('麵食','miànshí','wheat-based foods'),V('特色','tèsè','special characteristic')],E('每個地方都有自己的飲食特色。','Měi ge dìfang dōu yǒu zìjǐ de yǐnshí tèsè.','Every region has its own food characteristics.'),'Restaurant menus outside Asia often combine dishes whose places of origin are hundreds or thousands of kilometers apart.','Why are regional Chinese cuisines so diverse?',[('a','Only because of restaurant marketing'),('b','Geography, history, migration, and local ingredients'),('c','Everyone cooks the same food'),('d','Only because of chopsticks')],'b'),

'humor-wordplay': L('level3','Language & Communication','😄','幽默與文字遊戲','Humor & Wordplay','Chinese humor often plays creatively with sounds, characters, idioms, memes, and shared cultural references.',[
 S('🔊','Homophones','Because many Chinese syllables sound alike, homophones create puns in advertising, holiday greetings, jokes, and internet language.'),
 S('🔢','Numbers as language','Online users sometimes use numbers for sound-based shorthand. Meanings depend on community and can change quickly.'),
 S('📝','Characters and idioms','Writers can alter familiar idioms or characters for comic effect. Understanding the original expression makes the joke easier to recognize.'),
 S('😂','Humor is contextual','A joke that works in Taiwan may not work the same way in Mainland China, Hong Kong, Singapore, or an overseas community.')],
 [V('幽默','yōumò','humor'),V('笑話','xiàohuà','joke'),V('諧音','xiéyīn','homophone; similar sound'),V('雙關語','shuāngguānyǔ','pun'),V('梗','gěng','meme; recurring joke/reference')],E('這個笑話用了諧音。','Zhège xiàohuà yòng le xiéyīn.','This joke uses a homophone.'),'The number 520 is sometimes used online as a playful sound association with 我愛你, though it is not an exact pronunciation match.','Why are homophones especially useful for Chinese wordplay?',[('a','Chinese has no written language'),('b','Many words and syllables can sound similar'),('c','Numbers have no meaning'),('d','All jokes are four characters')],'b'),

'digital-culture': L('level3','Modern Culture','📱','社群媒體與數位文化','Social Media & Digital Culture','Digital platforms shape how people socialize, shop, learn, work, and create new language across Chinese-speaking communities.',[
 S('📲','Different platform ecosystems','Popular services differ by region. Learners should not assume that the same apps dominate Taiwan, Mainland China, Hong Kong, and overseas communities.'),
 S('💬','Language changes quickly','Memes, abbreviations, emojis, slang, and new expressions spread rapidly online and may disappear just as quickly.'),
 S('🛍️','Everyday digital life','Mobile payments, delivery, livestreaming, online shopping, and messaging are deeply integrated into daily life in many communities, though usage patterns vary.'),
 S('🔎','Media literacy','Online trends do not represent everyone. Good cultural learning distinguishes viral content from broader social behavior.')],
 [V('社群媒體','shèqún méitǐ','social media'),V('網路','wǎnglù','internet'),V('短影音','duǎn yǐngyīn','short-form video'),V('行動支付','xíngdòng zhīfù','mobile payment'),V('流行語','liúxíngyǔ','popular expression; buzzword')],E('這個流行語在網路上很常見。','Zhège liúxíngyǔ zài wǎnglù shàng hěn chángjiàn.','This popular expression is common online.'),'Digital culture can differ substantially even among communities that share written Chinese or Mandarin.','What is important when learning culture from social media?',[('a','Assume every viral post represents everyone'),('b','Distinguish online trends from broader behavior'),('c','Ignore regional differences'),('d','Treat slang as permanent')],'b'),
}


def install(culture_views):
    """Merge extras once, preserving the display order above."""
    known = {card.get('slug') for card in culture_views.CULTURE_PREVIEW_CARDS}
    culture_views.CULTURE_PREVIEW_CARDS.extend(card for card in EXTRA_CARDS if card['slug'] not in known)
    culture_views.CULTURE_LESSONS.update(EXTRA_LESSONS)
