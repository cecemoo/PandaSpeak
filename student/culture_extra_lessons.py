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
    {'slug':'treating-and-bill','level':'level2','category':'society','chinese_title':'請客與買單','title':'Treating & Paying the Bill','summary':'Learn why hosts often insist on treating, and how to respond graciously.','art':'🧾','theme':'food'},
    {'slug':'compliments-modesty','level':'level2','category':'society','chinese_title':'稱讚與謙虛','title':'Compliments & Modest Replies','summary':'See why compliments are often deflected, and learn graceful ways to give and receive them.','art':'💐','theme':'language'},
    {'slug':'filial-piety','level':'level2','category':'society','chinese_title':'孝道與現代家庭','title':'Filial Piety & Modern Families','summary':'Explore how respect and care for parents are changing in modern families.','art':'🏡','theme':'family'},
    {'slug':'group-harmony','level':'level2','category':'society','chinese_title':'群體和諧與個人','title':'Group Harmony & the Individual','summary':'Understand how group harmony and individual needs are balanced in social life.','art':'👥','theme':'work'},
    {'slug':'hot-pot','level':'level2','category':'food','chinese_title':'火鍋文化','title':'Hot Pot Culture','summary':'Discover why hot pot is one of the most social ways to eat.','art':'🍲','theme':'food'},
    {'slug':'breakfast-culture','level':'level2','category':'food','chinese_title':'早餐文化','title':'Breakfast Culture','summary':'Start the day with congee, soy milk, and other beloved morning foods.','art':'🥣','theme':'food'},
    {'slug':'greetings-small-talk','level':'level2','category':'language','chinese_title':'問候與寒暄','title':'Greetings & Small Talk','summary':'Go beyond 你好 with greetings that sound natural for the moment and the relationship.','art':'👋','theme':'language'},
    {'slug':'apologies-polite','level':'level2','category':'language','chinese_title':'不好意思與道歉','title':'Apologies & Polite Excuses','summary':'Learn the difference between 對不起, 不好意思, and 抱歉 — and when each one fits.','art':'🙇','theme':'language'},
    {'slug':'four-inventions','level':'level2','category':'history','chinese_title':'四大發明','title':'The Four Great Inventions','summary':'Meet the four famous inventions — paper, printing, gunpowder, and the compass.','art':'🧭','theme':'history'},
    {'slug':'silk-road','level':'level2','category':'history','chinese_title':'絲綢之路','title':'The Silk Road','summary':'Follow the routes that carried silk, spices, ideas, and stories between regions.','art':'🐫','theme':'history'},
    {'slug':'dialects-local-speech','level':'level2','category':'regional','chinese_title':'方言與地方話','title':'Dialects & Local Speech','summary':'Mandarin is widely shared, but local speech gives every place its own sound.','art':'🗣️','theme':'regional'},
    {'slug':'north-and-south','level':'level2','category':'regional','chinese_title':'南方與北方','title':'North & South','summary':'See how climate, staples, and daily rhythms differ between northern and southern regions.','art':'🧭','theme':'regional'},
    {'slug':'mobile-payments','level':'level2','category':'modern','chinese_title':'行動支付','title':'Mobile Payments','summary':'See how phones have replaced wallets in much of everyday life.','art':'📱','theme':'modern'},
    {'slug':'delivery-culture','level':'level2','category':'modern','chinese_title':'外送與快遞','title':'Delivery Culture','summary':'Food delivery and parcel couriers are part of everyday modern life.','art':'🛵','theme':'modern'},
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

'treating-and-bill': L('level2','Society & Relationships','🧾','請客與買單','Treating & Paying the Bill','Sharing a meal is also a way of sharing goodwill, and who pays can carry social meaning.',[
 S('🍽️','Treating as goodwill','請客 (qǐngkè), treating someone to a meal, can express welcome, thanks, celebration, or friendship. A host may insist on paying as a sign of warmth rather than a strict rule.'),
 S('🙋','The friendly contest','In some settings, guests may offer to pay and the host gently declines, and a short exchange around the bill can be playful politeness. How this plays out varies with age, relationship, and setting.'),
 S('🔄','Returning the gesture','A common way to respond is to thank the host and treat next time: 下次我請. Reciprocity over time keeps the relationship warm and balanced.'),
 S('⚖️','No single rule','Splitting the bill among close friends is completely ordinary, and mobile payments have made sharing costs effortless. Follow the group rather than assuming a contest will happen.')],
 [V('請客','qǐngkè','to treat someone to a meal'),V('買單','mǎidān','to pay the bill'),V('我請客','wǒ qǐngkè','I’ll treat; it’s on me'),V('下次我請','xià cì wǒ qǐng','my treat next time'),V('各付各的','gè fù gè de','each pays their own share')],E('這次我請客，下次你請。','Zhè cì wǒ qǐngkè, xià cì nǐ qǐng.','I’ll treat this time; you can treat next time.'),'The lighthearted phrase 下次我請 (my treat next time) turns one meal into an open door for the next gathering.','What is a gracious way to respond when someone treats you to a meal?',[('a','Demand that they pay next time too'),('b','Thank them and offer to treat next time'),('c','Refuse to eat anything'),('d','Complain about the restaurant')],'b'),

'compliments-modesty': L('level2','Society & Relationships','💐','稱讚與謙虛','Compliments & Modest Replies','How a compliment is received can say as much as the compliment itself, and modest replies are a familiar social art.',[
 S('💐','Giving a compliment','A sincere, specific compliment is welcome in most settings — about effort, cooking, taste, or a skill. Keeping it genuine matters more than making it grand.'),
 S('🙈','Deflecting with modesty','Traditional modest replies include 哪裡哪裡 (nǎlǐ nǎlǐ) and 還好啦. The deflection is often a polite ritual rather than a real denial of the fact.'),
 S('😊','Accepting is fine too','Many speakers today simply accept with a warm 謝謝. Accepting a compliment gracefully is increasingly common and is not considered arrogant.'),
 S('🎁','Compliments and generosity','Older etiquette tales warn that admiring an item too warmly might prompt its owner to offer it to you — a glimpse of how closely generosity and modesty were once linked.')],
 [V('稱讚','chēngzàn','praise; compliment'),V('謙虛','qiānxū','modest; humble'),V('哪裡哪裡','nǎlǐ nǎlǐ','not at all (a modest reply)'),V('還好啦','hái hǎo la','it’s just okay'),V('過獎了','guòjiǎng le','you flatter me')],E('你的中文很好！——哪裡哪裡，還在學習。','Nǐ de Zhōngwén hěn hǎo! —— Nǎlǐ nǎlǐ, hái zài xuéxí.','Your Chinese is very good! — Not at all, I’m still learning.'),'哪裡哪裡 literally means “where, where” — as if asking where the praised quality could possibly be found.','What does 哪裡哪裡 usually do in conversation?',[('a','Asks for directions'),('b','Modestly deflects a compliment'),('c','Ends a phone call'),('d','Orders food')],'b'),

'filial-piety': L('level2','Society & Relationships','🏡','孝道與現代家庭','Filial Piety & Modern Families','孝道 (xiàodào) — respect and care for parents and elders — has shaped family life for centuries, and it is still being reinterpreted today.',[
 S('🌳','Roots of the idea','Classical thought treated care for parents as a foundation of social order: respect, support in old age, gratitude, and remembering ancestors.'),
 S('🏠','Care in practice','Traditionally, adult children were expected to live near or with their parents and provide support. How this worked in practice differed widely by family, means, and era.'),
 S('📱','Modern negotiations','Urban work, migration, smaller families, and longer lives mean many families now share care among siblings, hired help, and retirement communities — while video calls keep distant families close.'),
 S('⚖️','Respect, not blind obedience','Modern readings often emphasize gratitude and care rather than unquestioning obedience. Each family negotiates what 孝 looks like in its own circumstances.')],
 [V('孝道','xiàodào','filial piety'),V('孝順','xiàoshùn','filial; caring toward parents'),V('父母','fùmǔ','parents'),V('照顧','zhàogù','to care for; look after'),V('長輩','zhǎngbèi','elder; senior family member')],E('他每個週末都回去陪父母。','Tā měi ge zhōumò dōu huíqù péi fùmǔ.','He goes back every weekend to spend time with his parents.'),'The character 孝 combines 老 (old) above 子 (child) — a picture of a younger person supporting an elder.','How is 孝道 best understood in many modern families?',[('a','Blind obedience to parents'),('b','Gratitude and care for parents, negotiated in modern life'),('c','Living in the same house forever'),('d','A duty only for sons')],'b'),

'group-harmony': L('level2','Society & Relationships','👥','群體和諧與個人','Group Harmony & the Individual','Many social settings prize 和諧 (harmony): keeping the group comfortable while still making room for individual needs.',[
 S('👥','The group as a unit','When families, friends, or colleagues decide together, the group’s comfort often counts alongside one person’s preference — choosing food everyone can share is a small everyday example.'),
 S('🗣️','Reading the room','Suggestions may be offered gently so others can agree or adjust without embarrassment. Noticing tone, timing, and who has not yet spoken is part of social skill.'),
 S('🔄','Flexibility in return','Going along with the group is often repaid later — your preference may lead another time. Reciprocity keeps harmony from being one-sided.'),
 S('⚖️','Harmony has limits','Many younger people and modern workplaces also value direct feedback and personal boundaries. Healthy groups balance belonging with honesty rather than silencing disagreement.')],
 [V('和諧','héxié','harmony; harmonious'),V('群體','qúntǐ','group; community'),V('配合','pèihé','to coordinate; go along with'),V('隨和','suíhé','easygoing'),V('尊重','zūnzhòng','respect')],E('大家方便就好，我都可以。','Dàjiā fāngbiàn jiù hǎo, wǒ dōu kěyǐ.','Whatever works for everyone is fine with me.'),'The phrase 以和為貴 — “harmony is precious” — comes from classical thought and still appears in everyday advice about getting along with others.','What does prizing group harmony usually encourage?',[('a','Ignoring everyone’s needs'),('b','Considering the group’s comfort when deciding'),('c','Never expressing any preference'),('d','Ending friendships quickly')],'b'),

'hot-pot': L('level2','Food & Dining','🍲','火鍋文化','Hot Pot Culture','Hot pot is a meal and a social event at the same time: everyone cooks together in one shared, simmering pot.',[
 S('🍲','One pot, shared by all','Diners sit around a bubbling broth and cook thin slices of meat, vegetables, tofu, and noodles themselves. The shared pot makes the meal naturally communal.'),
 S('🌶️','Broths and flavors','Broths range from mild and clear to famously spicy. A 鴛鴦鍋 (split pot) offers two broths at once, so different tastes can sit at the same table.'),
 S('🥣','Your own dipping sauce','Part of the fun is mixing a personal dipping sauce from ingredients such as sesame paste, garlic, chili, and herbs. Two people at the same pot may season completely differently.'),
 S('🎉','A meal that takes its time','Hot pot is rarely rushed. It suits long conversations, family gatherings, and celebrations, especially in cold weather — though fans enjoy it all year round.')],
 [V('火鍋','huǒguō','hot pot'),V('湯底','tāngdǐ','broth base'),V('鴛鴦鍋','yuānyuān guō','split pot with two broths'),V('蘸料','zhànliào','dipping sauce'),V('涮','shuàn','to swish-cook in hot broth')],E('我們今晚吃火鍋吧！','Wǒmen jīnwǎn chī huǒguō ba!','Let’s have hot pot tonight!'),'The name 鴛鴦鍋 borrows the mandarin duck, a symbol of pairs — two broths side by side in one pot.','What is a 鴛鴦鍋?',[('a','A dessert'),('b','A split pot with two broths'),('c','A kind of teapot'),('d','A rice cooker')],'b'),

'breakfast-culture': L('level2','Food & Dining','🥣','早餐文化','Breakfast Culture','Breakfast is taken seriously: a warm, filling start to the day is widely valued.',[
 S('🌅','Breakfast stalls and shops','Morning stalls and small breakfast shops serve commuters quickly and cheaply. For many people, breakfast is bought on the way to work or school rather than cooked at home.'),
 S('🥛','Classic combinations','Soy milk with 油條 (fried dough sticks), steamed buns, congee, egg pancakes, and rice rolls are all familiar morning foods, though menus vary by place.'),
 S('🗺️','Regional mornings','Wheat-based foods are common in many northern breakfasts, while rice-based dishes such as congee and rice noodles feature strongly in many southern ones. Every region has its own specialties.'),
 S('☕','Old and new together','Coffee, bakeries, and convenience-store breakfasts are now everyday sights too. Modern mornings mix long-loved classics with global habits.')],
 [V('早餐','zǎocān','breakfast'),V('豆漿','dòujiāng','soy milk'),V('油條','yóutiáo','fried dough stick'),V('包子','bāozi','steamed bun'),V('粥','zhōu','congee; rice porridge')],E('我早上喝豆漿，吃包子。','Wǒ zǎoshang hē dòujiāng, chī bāozi.','In the morning I drink soy milk and eat steamed buns.'),'Many people prefer a hot breakfast, believing warm food is a gentler, more energizing way to start the day — one reason congee and hot soy milk stay popular.','Which pair is a classic breakfast combination?',[('a','Soy milk and fried dough sticks'),('b','Hot pot and mooncakes'),('c','Red envelopes and tea'),('d','Dumplings and birthday cake')],'a'),

'greetings-small-talk': L('level2','Language & Communication','👋','問候與寒暄','Greetings & Small Talk','你好 is always correct, but everyday greetings often notice what the other person is doing right now.',[
 S('👋','More than 你好','With familiar people, greetings are often situational: 回來了 (“you’re back”), 出門啊 (“heading out?”), or 去買菜啊 (“off to buy groceries?”). They acknowledge the person rather than just saying hello.'),
 S('🍚','Have you eaten?','吃飽了嗎 has long been used as a warm greeting, especially among older speakers and familiar neighbors. It expresses care; it is not usually a literal question about your meal.'),
 S('🌤️','Small talk builds familiarity','Brief exchanges about weather, family, or the day ahead keep relationships warm. Among neighbors and colleagues, these small moments are part of social glue.'),
 S('🎯','Match the relationship','A boss, a close friend, and a neighbor each call for a slightly different greeting. Watching how others greet each other is the quickest way to learn.')],
 [V('寒暄','hánxuān','small talk; polite chat'),V('吃飽了嗎','chī bǎo le ma','have you eaten? (also a greeting)'),V('回來了','huílái le','you’re back'),V('出門啊','chūmén a','heading out?'),V('慢走','màn zǒu','take care (when seeing someone off)')],E('你回來了！——嗯，剛下班。','Nǐ huílái le! —— Ǹg, gāng xiàbān.','You’re back! — Mm, just got off work.'),'吃飽了嗎 became a greeting in times when food was scarce for many people — asking whether someone had eaten was a genuine way of asking whether they were well.','When a neighbor greets you with 吃飽了嗎, they most likely…',[('a','Want a detailed report of your lunch'),('b','Are greeting you warmly'),('c','Are asking you to cook for them'),('d','Are ending the conversation')],'b'),

'apologies-polite': L('level2','Language & Communication','🙇','不好意思與道歉','Apologies & Polite Excuses','Chinese has several ways to say sorry, and choosing the right weight matters more than translating word for word.',[
 S('🪶','不好意思 — the light apology','不好意思 covers small moments: squeezing past someone, arriving a little late, or asking for help. It can also express mild embarrassment, a bit like “excuse me” and “sorry” combined.'),
 S('🎯','對不起 — the real apology','對不起 is for genuine mistakes that affected someone. It carries more weight and invites a sincere response.'),
 S('💼','抱歉 — formal regret','抱歉 sounds more formal and is common in business, announcements, and writing: 非常抱歉. Companies and officials use it when expressing official regret.'),
 S('🤝','Answering an apology','The everyday response is 沒關係 — “it’s okay.” Small apologies and quick forgiveness keep daily interactions smooth, so both sides are used often.')],
 [V('對不起','duìbuqǐ','sorry (a real apology)'),V('不好意思','bù hǎoyìsi','excuse me; sorry (light)'),V('抱歉','bàoqiàn','regretful; sorry (formal)'),V('沒關係','méi guānxi','it’s okay; no problem'),V('原諒','yuánliàng','to forgive')],E('不好意思，我遲到了。','Bù hǎoyìsi, wǒ chídào le.','Sorry, I’m late.'),'不好意思 is famously flexible — depending on the moment it can mean “excuse me,” “sorry,” or even shy embarrassment at receiving praise or a gift.','You are a few minutes late meeting a friend. A fitting light apology is…',[('a','哪裡哪裡'),('b','不好意思，我遲到了'),('c','恭喜發財'),('d','請買單')],'b'),

'four-inventions': L('level2','History & Heritage','🧭','四大發明','The Four Great Inventions','Papermaking, printing, gunpowder, and the compass are remembered together as the Four Great Inventions of ancient China.',[
 S('📜','Papermaking','Paper existed in early forms before 蔡倫 (Cài Lún), who is traditionally credited with improving papermaking around 105 CE. Affordable paper changed how knowledge could be recorded and spread.'),
 S('🖨️','Printing','Woodblock printing came first; in the 1040s 畢昇 (Bì Shēng) created movable type with clay characters. Books became far easier to copy and share.'),
 S('🎆','Gunpowder','Gunpowder is said to have emerged from alchemists searching for an elixir of life. It gave the world fireworks — and later changed warfare everywhere.'),
 S('🧭','The compass','Early compasses used magnetic lodestone; over centuries the technology developed into navigation tools that helped sailors travel farther with confidence.')],
 [V('發明','fāmíng','invention; to invent'),V('造紙','zàozhǐ','papermaking'),V('印刷','yìnshuā','printing'),V('火藥','huǒyào','gunpowder'),V('指南針','zhǐnánzhēn','compass')],E('指南針幫助人們在大海上找到方向。','Zhǐnánzhēn bāngzhù rénmen zài dàhǎi shàng zhǎodào fāngxiàng.','The compass helped people find their direction at sea.'),'Movable type was used in China roughly four centuries before Gutenberg’s famous press in Europe — though each of the four inventions was really refined by many hands over long periods.','Which of these is one of the Four Great Inventions?',[('a','The telephone'),('b','The compass'),('c','The airplane'),('d','The bicycle')],'b'),

'silk-road': L('level2','History & Heritage','🐫','絲綢之路','The Silk Road','For over a thousand years, trade routes linked China with Central Asia, the Middle East, and Europe.',[
 S('🗺️','Not one road','The “Silk Road” was a network of land and sea routes, not a single highway. Goods were passed from merchant to merchant across deserts, mountains, and ports.'),
 S('🧵','What traveled west and east','Silk, tea, porcelain, and paper moved westward; glass, wool, spices, and new foods moved eastward. No single merchant usually carried goods the whole way.'),
 S('🎵','Ideas traveled too','Religions, music, art styles, technologies, and stories moved along the same routes. Grapes, musical instruments, and new crops all arrived through exchange.'),
 S('🐫','Opening the routes','The Han-dynasty envoy 張騫 (Zhāng Qiān), sent west in 138 BCE, is traditionally credited with opening the way for regular contact between China and Central Asia.')],
 [V('絲綢','sīchóu','silk'),V('絲路','Sīlù','the Silk Road'),V('貿易','màoyì','trade'),V('交流','jiāoliú','exchange; interaction'),V('駱駝','luòtuo','camel')],E('絲綢從中國運到很遠的地方。','Sīchóu cóng Zhōngguó yùn dào hěn yuǎn de dìfang.','Silk was carried from China to places far away.'),'The name “Silk Road” is modern — it was coined by a German geographer in 1877. Ancient merchants never called it that.','Besides goods, what else traveled along the Silk Road?',[('a','Only silk'),('b','Ideas, music, and foods'),('c','Nothing at all'),('d','Only soldiers')],'b'),

'dialects-local-speech': L('level2','Regional Culture','🗣️','方言與地方話','Dialects & Local Speech','Across Chinese-speaking regions, people share a written language while speaking in wonderfully different sounds.',[
 S('🗣️','A common language plus home speech','Mandarin serves as the shared language of school, media, and travel. Many people also grow up speaking a local variety at home — the two live side by side.'),
 S('🎶','Many varieties','Cantonese, Hokkien, Hakka, Shanghainese, and many others each have their own pronunciation, vocabulary, and flavor. Linguists debate whether to call them dialects or languages; locally they are simply home speech.'),
 S('🔤','Same characters, different sounds','A sentence written in characters can be read aloud in completely different pronunciations across regions. This is one reason written Chinese is such a strong shared link.'),
 S('💬','Local words as identity','Asking how to say something in the local variety is a friendly gesture. Local expressions carry hometown pride, humor, and belonging.')],
 [V('方言','fāngyán','dialect; local speech'),V('普通話','Pǔtōnghuà','Mandarin (the common speech)'),V('粵語','Yuèyǔ','Cantonese'),V('客家話','Kèjiāhuà','Hakka'),V('口音','kǒuyīn','accent')],E('這個詞用方言怎麼說？','Zhège cí yòng fāngyán zěnme shuō?','How do you say this word in the local dialect?'),'Films and songs in Cantonese and other varieties are loved far beyond their home regions, so many learners pick up a few famous phrases without ever studying them formally.','Why can readers from different dialect regions usually read the same newspaper?',[('a','Everyone speaks identically'),('b','They share a written language'),('c','Newspapers use only pictures'),('d','Dialects no longer exist')],'b'),

'north-and-south': L('level2','Regional Culture','🧭','南方與北方','North & South','People often describe China through a friendly north–south contrast — in weather, food, and everyday rhythms.',[
 S('❄️','Climate','Northern winters are cold and dry, with heating in homes; much of the south has milder winters but humid heat in summer, and homes traditionally have no central heating.'),
 S('🍚','Staples on the table','Wheat foods — noodles, dumplings, steamed buns — have deep roots in the north, while rice anchors meals in much of the south. Both regions, of course, happily eat everything today.'),
 S('🏠','Daily rhythms','Markets, seasonal foods, and even ideas about spice and tea follow local climate and history. Migration and modern cities keep mixing these habits together.'),
 S('⚖️','A rough sketch, not a rule','“North” and “south” are broad strokes over enormous diversity. Treat the contrast as a conversation starter, never a label for a person.')],
 [V('北方','běifāng','the north'),V('南方','nánfāng','the south'),V('氣候','qìhòu','climate'),V('暖氣','nuǎnqì','heating (in buildings)'),V('習慣','xíguàn','habit; custom')],E('北方的冬天很冷，家裡有暖氣。','Běifāng de dōngtiān hěn lěng, jiālǐ yǒu nuǎnqì.','Northern winters are cold, and homes have heating.'),'The traditional dividing line is the Qinling Mountains–Huai River line （秦嶺—淮河） — historically also the line north of which buildings received central heating.','The Qinling–Huai line is famous as…',[('a','A city wall'),('b','A traditional north–south dividing line'),('c','A boat route'),('d','A kind of dialect')],'b'),

'mobile-payments': L('level2','Modern Culture','📱','行動支付','Mobile Payments','In many cities, a phone has become the wallet: meals, markets, taxis, and friends are all paid by scan.',[
 S('📷','Scan and pay','Shops and stalls display a QR code; customers scan it, enter the amount, and confirm. Even a tiny street stall can accept phone payments with nothing more than a printed code.'),
 S('👛','A lighter wallet','Many people carry little cash day to day. Transfers between friends — splitting dinner, sending a gift, returning a favor — happen in seconds inside chat apps.'),
 S('🧧','New habits, old customs','Digital red envelopes turned an old Lunar New Year tradition into a phone game and greeting, showing how new tools reshape familiar customs rather than replacing them.'),
 S('🌏','Check the local system','Popular payment apps differ by region, and visitors may need cash or a card where their app does not work. Cash has not disappeared — it has simply stepped back.')],
 [V('行動支付','xíngdòng zhīfù','mobile payment'),V('掃碼','sǎomǎ','to scan a code'),V('錢包','qiánbāo','wallet'),V('轉帳','zhuǎnzhàng','to transfer money'),V('找零','zhǎolíng','to give change')],E('我用手機付錢。','Wǒ yòng shǒujī fù qián.','I pay with my phone.'),'During Lunar New Year, digital red envelopes fly between friends and family group chats — some workplaces even hold lucky-draw rounds for tiny amounts, purely for fun.','At a small market stall, paying by phone usually starts with…',[('a','Scanning a QR code'),('b','Writing a check'),('c','Mailing cash'),('d','Bartering goods')],'a'),

'delivery-culture': L('level2','Modern Culture','🛵','外送與快遞','Delivery Culture','Riders in bright jackets and parcel lockers at the gate: delivery is woven into everyday modern life.',[
 S('🥡','Food at the tap of a screen','Food delivery apps offer everything from noodles to bubble tea, often arriving within half an hour in dense cities. Ordering in is an ordinary weeknight choice, not a special treat.'),
 S('📦','Parcels and lockers','Online shopping runs on fast courier networks. Many neighborhoods and apartment complexes have parcel lockers （快遞櫃） or pickup stations where deliveries wait securely.'),
 S('🛵','The riders','Delivery riders are a visible part of the modern city. Their work is demanding, and public discussion increasingly covers their safety and working conditions, not just speed.'),
 S('♻️','Convenience and its questions','Packaging waste and traffic are the debated costs of convenience. Reusable containers and greener packaging are growing responses in many communities.')],
 [V('外送','wàisòng','food delivery'),V('快遞','kuàidì','express delivery; courier'),V('包裹','bāoguǒ','parcel; package'),V('外送員','wàisòngyuán','delivery rider'),V('訂餐','dìngcān','to order a meal')],E('我今天不想煮飯，叫外送吧。','Wǒ jīntiān bù xiǎng zhǔ fàn, jiào wàisòng ba.','I don’t feel like cooking today — let’s order delivery.'),'Some office buildings and campuses set up special shelves just for delivered lunches, labeled by phone number for quick pickup at noon.','What is a 快遞櫃?',[('a','A restaurant'),('b','A parcel pickup locker'),('c','A bus stop'),('d','A bank branch')],'b'),
}


def install(culture_views):
    """Merge extras once, preserving the display order above."""
    known = {card.get('slug') for card in culture_views.CULTURE_PREVIEW_CARDS}
    culture_views.CULTURE_PREVIEW_CARDS.extend(card for card in EXTRA_CARDS if card['slug'] not in known)
    culture_views.CULTURE_LESSONS.update(EXTRA_LESSONS)
